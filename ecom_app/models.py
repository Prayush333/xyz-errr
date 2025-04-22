from django.db import models
from django.conf import settings # Import settings
import datetime

# categories of products
 # to spicify the product and manage it
class Category(models.Model): 
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
# customers details 
# for registration
class Customer(models.Model): 
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
      

 # products 
 # details of product
class Product(models.Model): 
    name = models.CharField(max_length=100)
    price = models.DecimalField(default=0,decimal_places=2,max_digits=8)
    Category = models.ForeignKey(Category,on_delete=models.CASCADE, default=1)
    description = models.CharField(max_length=300, default='', null=True)
    image = models.ImageField(upload_to='uploads/product/')
    is_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(default=0,decimal_places=2,max_digits=8)
    

    def __str__(self):
        return self.name

 # product order details 
 #  for delevery
class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    shipping_address = models.ForeignKey('ShippingAddress', on_delete=models.SET_NULL, null=True, blank=True) # Link to ShippingAddress, allow null if address deleted
    quantity = models.IntegerField(default=1)
    date = models.DateField(default=datetime.date.today) # Use datetime.date.today for DateField
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending' # Default status when an order is created
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # Keep order record even if employee account is deleted
        null=True,
        blank=True,
        limit_choices_to={'is_staff': True}, # Only allow staff users to be assigned
        related_name='processed_orders',
        help_text='Employee who processed the order status (e.g., shipped).'
    )
    # OTP fields
    otp_code = models.CharField(max_length=6, null=True, blank=True, help_text="OTP sent to customer for verification")
    otp_expiry = models.DateTimeField(null=True, blank=True, help_text="Time when the OTP expires")


    def __str__(self):
        return f"Order {self.id} ({self.status}) for {self.customer}" # Include status in __str__

class CartItem(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.product.name} - CartItem'

    def get_total_price(self):
        # Method to calculate the total price of this item in the cart
        return self.quantity * self.product.price if not self.product.is_sale else self.quantity * self.product.sale_price
    
# Shipping Address Model
# Allows users to save multiple shipping addresses
class ShippingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True) # Use settings.AUTH_USER_MODEL
    # If you want guests to checkout, user can be null. Otherwise, remove null=True, blank=True.
    full_name = models.CharField(max_length=255)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, null=True, blank=True) # Optional second address line
    city = models.CharField(max_length=100)
    state_province_region = models.CharField(max_length=100) # State, Province, or Region
    postal_zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100) # Consider using django-countries for a dropdown
    phone = models.CharField(max_length=20, blank=True) # Optional phone specific to address

    # You might want a field to mark a default address
    # default = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Shipping Addresses" # Correct plural name in Admin

    def __str__(self):
        return f"Shipping Address for {self.user.username if self.user else 'Guest'} - {self.address_line_1}"
# Employee Profile Model
# Stores additional information for staff users, like Employee ID
class EmployeeProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee_profile')
    employee_id = models.CharField(max_length=50, unique=True, help_text="Unique ID assigned to the employee")
    is_verified = models.BooleanField(default=False, help_text="Designates whether the employee is verified to perform certain actions.")
    # Add other employee-specific fields here if needed (e.g., department, job title)

    def __str__(self):
        return f"Employee Profile for {self.user.username} (ID: {self.employee_id}, Verified: {self.is_verified})"

    # Ensure this profile is only created for staff users.
    # You might enforce this via signals or admin forms.