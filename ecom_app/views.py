# Removed requests, json, HttpResponse as they are no longer needed for payment processing
from django.conf import settings # Keep settings if needed elsewhere, remove if not
from django.urls import reverse
from django.http import JsonResponse # Keep JsonResponse for cart views
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
# Import TemplateView
from django.views.generic import ListView, CreateView, DetailView, TemplateView
# Import Order, ShippingAddress, EmployeeProfile models
from ecom_app.models import Customer, Product, Category, Order, ShippingAddress, EmployeeProfile
from django.contrib.auth.models import User
# Import standard AuthenticationForm along with UserCreationForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.urls import reverse_lazy, reverse # Import reverse
from django.views import View
from .cart import Cart
from django.contrib.auth import views as auth_views # Import auth_views
from django.shortcuts import HttpResponseRedirect # Import HttpResponseRedirect
# Import the custom employee login form
from .forms import EmployeeLoginForm, OTPVerificationForm # Add OTPVerificationForm later

# Additional imports for OTP and Email
import random
import string
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin # Ensure LoginRequiredMixin is imported if not already


# --- Helper Functions ---

def generate_otp(length=6):
    """Generate a random OTP."""
    characters = string.digits
    return ''.join(random.choice(characters) for i in range(length))

def send_otp_email(order):
    """Generate OTP, save it to the order, and email it to the customer."""
    if not order.customer.email:
        messages.error(request, "Customer email address not found.") # Add request if used in view context
        return False # Indicate failure

    otp = generate_otp()
    expiry_time = timezone.now() + timedelta(minutes=10) # OTP valid for 10 minutes

    # Save OTP and expiry to the order
    order.otp_code = otp
    order.otp_expiry = expiry_time
    order.save(update_fields=['otp_code', 'otp_expiry'])

    # Send email
    subject = f'Your Order Confirmation OTP for Order #{order.id}'
    message = f'Hello {order.customer.first_name},\n\nYour OTP for confirming the delivery of order #{order.id} is: {otp}\n\nThis OTP will expire in 10 minutes.\n\nPlease provide this code to the delivery personnel.'
    from_email = settings.DEFAULT_FROM_EMAIL # Make sure this is set in settings.py
    recipient_list = [order.customer.email]

    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        return True # Indicate success
    except Exception as e:
        # Log the error (implement proper logging)
        print(f"Error sending OTP email for order {order.id}: {e}")
        # Optionally: messages.error(request, "Failed to send OTP email.")
        return False # Indicate failure


# --- Views ---

class HomePage(ListView):
    model = Product
    template_name = "home.html"
    context_object_name = "products"


class AboutPage(ListView):
    model= Product
    template_name = "about.html"

    
class UserResister(CreateView):
    model = User
    template_name = "register.html"
    form_class = UserCreationForm
    # Redirect to login selection after successful registration
    success_url = reverse_lazy('select_login_type')


class ProductDetail(DetailView):
    model = Product
    template_name = "items.html"
    context_object_name = "product"
 


class CategoryView(DetailView):
    model = Category
    template_name = "category.html"
    context_object_name = "category"

    def get_object(self, queryset=None):
        name = self.kwargs['id'].replace('-', ' ')
        return get_object_or_404(Category, name=name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.filter(Category=self.object)
        return context
    

#cart views
class CartListView(View):
    def get(self, request):
        cart = Cart(request)
        cart_products = cart.get_prods
        return render(request, "cart/cart_list.html", {"cart_products": cart_products})

   

class AddCart(View):

    def post(self, request):
        return self.cart_add(request)
    

    def cart_add(self, request):
        cart= Cart(request)

        if request.POST.get('action')=='post':
           
            product_id = int(request.POST.get('product_id'))
            # look for a product in a DB
            product = get_object_or_404(Product, id=product_id)
                # save to session
            cart.add(product=product)
             # get the quantity
            cart_quantity = cart.__len__()
             # return response including product name and quantity
            response = JsonResponse({'quantity': cart_quantity, 'product_name': product.name})
            
            return response
        
        return JsonResponse({'error': 'Invalid action'}, status=400)


    

class DeleteCart(View):
    def get(self, request, product_id): # Accept product_id from URL
        cart = Cart(request)
        cart.delete(product_id=product_id) # Corrected: Call the delete method with product_id
        return redirect('cart_list') # Redirect back to the cart list

class UpdateCart(View):
    pass


class BuyProductView(LoginRequiredMixin, View):
    """Handles displaying the purchase confirmation and processing the purchase."""
    template_name = 'buy_product.html'
    # Point login_url to the selection page
    login_url = reverse_lazy('select_login_type') # Redirect if not logged in

    def get(self, request, *args, **kwargs):
        """Displays the product confirmation and payment selection page."""
        product_id = self.kwargs.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        context = {
            'product': product,
            # Removed paypal_client_id as PayPal is no longer used
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """Handles the submission of the purchase form."""
        product_id = self.kwargs.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        payment_method = request.POST.get('payment_method')

        if payment_method == 'COD':
            # Get shipping address details from the form
            full_name = request.POST.get('full_name')
            address_line_1 = request.POST.get('address_line_1')
            address_line_2 = request.POST.get('address_line_2')
            city = request.POST.get('city')
            state_province_region = request.POST.get('state_province_region')
            postal_zip_code = request.POST.get('postal_zip_code')
            country = request.POST.get('country')
            phone = request.POST.get('phone')

            # Basic validation (consider using a Django Form for robust validation)
            if not all([full_name, address_line_1, city, state_province_region, postal_zip_code, country]):
                messages.error(request, "Please fill in all required shipping address fields.")
                return redirect('buy_product', product_id=product_id)

            # Create ShippingAddress object
            shipping_address = ShippingAddress.objects.create(
                user=request.user, # Link to the logged-in user
                full_name=full_name,
                address_line_1=address_line_1,
                address_line_2=address_line_2,
                city=city,
                state_province_region=state_province_region,
                postal_zip_code=postal_zip_code,
                country=country,
                phone=phone
            )

            # Get or create the Customer associated with the User
            # Assuming Customer email is unique and matches User email
            customer, created = Customer.objects.get_or_create(
                email=request.user.email,
                defaults={
                    'first_name': request.user.first_name or 'N/A',
                    'last_name': request.user.last_name or 'N/A',
                    'phone': phone or 'N/A', # Use shipping phone if available
                    'password': 'N/A' # Password not needed here, handle separately
                }
            )

            # Create the Order object
            order = Order.objects.create(
                product=product,
                customer=customer,
                shipping_address=shipping_address,
                quantity=1 # Assuming quantity is 1 for direct buy, adjust if needed
                # status defaults to False (or 'Pending' if you change the field)
            )

            messages.success(request, f'Your order for "{product.name}" has been placed successfully! It will be shipped to {shipping_address.address_line_1}.')
            # Consider clearing the cart or specific item here if applicable
            # Example: cart = Cart(request); cart.delete(product_id=product_id)
            return redirect('home') # Redirect home after successful order

        else:
            # Handle unexpected payment method
            messages.error(request, f"Invalid payment method selected: {payment_method}")
            return redirect('buy_product', product_id=product_id)

# --- Removed PayPal and Esewa specific views and helper functions ---


# View for the initial login type selection
class SelectLoginTypeView(TemplateView):
    template_name = 'registration/select_login_type.html'


# View for Customer Login
class CustomerLoginView(auth_views.LoginView):
    """
    Login view specifically for customers (non-staff users).
    """
    template_name = 'registration/login.html'
    # Use standard AuthenticationForm
    form_class = AuthenticationForm

    def form_valid(self, form):
        """Ensure the user logging in is NOT staff."""
        user = form.get_user()
        if user is not None and user.is_staff:
            # Staff user trying to use customer login
            messages.error(self.request, "Staff members should use the Employee Login.")
            # Log them out if they were somehow logged in by the form validation
            # auth_logout(self.request) # Optional: Force logout
            # Redirect to the selection page or employee login
            return HttpResponseRedirect(reverse('select_login_type'))
        elif user is not None:
            # Regular customer, proceed with login
            return super().form_valid(form)
        else:
            # Handle other cases like inactive user if needed,
            # though form validation should catch most.
            return super().form_valid(form) # Let parent handle


# View for Employee Login
class EmployeeLoginView(auth_views.LoginView):
    """
    Login view specifically for employees (staff users) using EmployeeLoginForm.
    """
    template_name = 'registration/employee_login.html'
    # Use the custom EmployeeLoginForm
    form_class = EmployeeLoginForm

    def form_valid(self, form):
        """
        User is authenticated, is staff, and Employee ID matches.
        Redirect to the admin index.
        """
        # The EmployeeLoginForm already validated that the user is staff
        # and the employee ID matches. We just need to log them in
        # and redirect to the admin.
        super().form_valid(form) # Logs the user in
        return HttpResponseRedirect(reverse('admin:index'))

# Ensure you have a login template at templates/registration/login.html
# You might need to create this file if it doesn't exist.


# --- Customer Order Confirmation (Triggers OTP) ---
@login_required(login_url=reverse_lazy('customer_login')) # Redirect non-logged-in users
def customer_confirm_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer__email=request.user.email) # Ensure user owns the order

    # Check if order status allows confirmation (e.g., 'Shipped')
    if order.status != 'Shipped': # Adjust this condition based on your workflow
         messages.warning(request, f"Order #{order.id} cannot be confirmed at this stage (Status: {order.status}).")
         # Redirect to customer's order list or detail page
         return redirect('home') # Replace 'home' with the actual URL name for customer orders

    if request.method == 'POST':
        # Send OTP email
        if send_otp_email(order):
            messages.success(request, f"An OTP has been sent to your email address ({order.customer.email}) for order #{order.id}.")
        else:
            messages.error(request, "There was an issue sending the OTP email. Please try again later.")
        # Redirect back or to a specific page after attempting to send OTP
        return redirect('home') # Replace 'home' with the actual URL name

    # If GET request, maybe display a confirmation page before POST?
    # For simplicity, this view currently only handles POST to send OTP.
    # You might need a template and GET handler if you want a confirmation step.
    messages.info(request, "Clicking 'Confirm Delivery' will send an OTP to your email.")
    # Redirect or render a template for confirmation button
    # This redirect assumes the button was on another page and submitted here via POST.
    return redirect('home') # Replace 'home'


# --- Employee OTP Verification ---
@login_required(login_url=reverse_lazy('employee_login'))
def employee_verify_order(request, order_id):
    # 1. Check if user is staff
    if not request.user.is_staff:
        raise PermissionDenied("You do not have permission to access this page.")

    # 2. Check if employee profile exists and is verified
    try:
        employee_profile = request.user.employee_profile
        if not employee_profile.is_verified:
             messages.error(request, "Your employee account is not verified for this action.")
             # Redirect to employee dashboard or admin index
             return redirect('admin:index') # Or another appropriate employee page
    except EmployeeProfile.DoesNotExist:
        messages.error(request, "Employee profile not found for your user account.")
        return redirect('admin:index') # Or another appropriate employee page

    order = get_object_or_404(Order, id=order_id)

    # Check if order is in a state that requires OTP verification (e.g., 'Shipped')
    if order.status != 'Shipped': # Or maybe 'Processing' depending on when OTP is needed
        messages.warning(request, f"Order #{order.id} does not require OTP verification at this time (Status: {order.status}).")
        return redirect('admin:index') # Or employee order list

    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp_code']

            # Validate OTP
            if order.otp_code == entered_otp:
                # Check expiry
                if order.otp_expiry and timezone.now() <= order.otp_expiry:
                    # OTP is valid and not expired
                    order.status = 'Delivered' # Update status
                    order.processed_by = request.user # Record verifying employee
                    order.otp_code = None # Clear OTP
                    order.otp_expiry = None # Clear expiry
                    order.save()
                    messages.success(request, f"Order #{order.id} successfully verified and marked as Delivered.")
                    # Redirect to admin order list or employee dashboard
                    return redirect('admin:ecom_app_order_changelist') # Redirect to admin order list
                else:
                    messages.error(request, "The OTP has expired. Please ask the customer to request a new one.")
            else:
                messages.error(request, "Invalid OTP entered. Please try again.")
        else:
            # Form is invalid (e.g., OTP format wrong)
            messages.error(request, "Invalid OTP format.") # Or rely on form errors

    else: # GET request
        form = OTPVerificationForm()

    context = {
        'form': form,
        'order': order,
    }
    # Create this template: templates/ecom_app/employee_verify_order.html
    return render(request, 'ecom_app/employee_verify_order.html', context)


# --- Customer Order History View ---

class CustomerOrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'ecom_app/customer_order_list.html' # Specify template path
    context_object_name = 'orders'
    login_url = reverse_lazy('customer_login') # Redirect to customer login if not authenticated

    def get_queryset(self):
        """
        Return orders belonging to the currently logged-in user's customer profile.
        """
        try:
            # Find the Customer profile linked by email to the logged-in User
            customer = Customer.objects.get(email=self.request.user.email)
            # Filter orders by this customer, order by date descending
            queryset = Order.objects.filter(customer=customer).order_by('-date', '-id')
        except Customer.DoesNotExist:
            # If no matching customer profile, return an empty queryset
            queryset = Order.objects.none()
            messages.warning(self.request, "Could not find a customer profile associated with your account.")
        except AttributeError:
             # Handle cases where request.user might not be fully populated or is AnonymousUser
             queryset = Order.objects.none()
             messages.error(self.request, "Error retrieving user information.")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "My Orders" # Add a title for the page
        # You could add more context if needed, e.g., customer details
        # try:
        #     context['customer'] = Customer.objects.get(email=self.request.user.email)
        # except Customer.DoesNotExist:
        #     context['customer'] = None
        return context
