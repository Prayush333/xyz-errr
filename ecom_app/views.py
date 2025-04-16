from django.http import JsonResponse
from django.shortcuts import render,get_object_or_404
from django.views.generic import ListView,CreateView,DetailView,DeleteView
from ecom_app.models import Customer, Product,Category,Cart
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import View



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
    success_url = reverse_lazy('login')


class ProductDetail(DetailView):
    model = Product
    template_name = "items.html"
    context_object_name = "product"
 
    def get_object(self):
        return Product.objects.get(id=self.kwargs["id"])


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
class MainCart(View):
    def get(self,request,*args,**kwargs):
        customer = request.user.customer
        cart_items = Cart.objects.filter(customer=customer)
        total_price = sum([item.get_total_price() for item in cart_items]) 
        return render(
            request, 
            "cart/cart_main.html",
              {
                "cart_items":cart_items,
               "total_price":total_price
               })
   
    

class AddCart(View):

    def post(self,request,*args,**kwargs):
        data = json.loads(request.body)
        product_id = data.get('product_id')
        customer = request.user.customer #  user is login then only

        # to check if product exists
        product = Product.objects.get(id = product_id)

        # checking if product is already on cart
        cart_item, created = Cart.objects.get_or_create(customer=customer, product=product)

        if not created:
            cart_item.quantity += 1 # to increase the quantity if it is already in cart
            cart_item.save()

        cart_count = Cart.objects.filter(customer=customer).count()

        return JsonResponse({
            "status":"success",
            "quantity":cart_item.quantity,
            "cart_count":cart_count
            })



class DeleteCart(View):

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        cart_id = data.get('cart_id')

        #  to Remove the cart item
        cart_item = Cart.objects.get(id=cart_id)
        cart_item.delete()

        cart_count = Cart.objects.filter(customer=request.user.customer).count()
       
        return JsonResponse({
            "status": "success",
              "cart_count": cart_count
              })




class UpdateCart(View):
    
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        cart_id = data.get('cart_id')
        new_quantity = data.get('quantity')

        #  to Update cart item quantity
        cart_item = Cart.objects.get(id=cart_id)
        cart_item.quantity = new_quantity
        cart_item.save()

        cart_count = Cart.objects.filter(customer=request.user.customer).count()
       
        return JsonResponse({
            "status": "success",
              "quantity": cart_item.quantity,
                "cart_count": cart_count
                })

