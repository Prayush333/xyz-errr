from django.db import models
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
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    address = models.CharField(max_length=200,  blank=False)
    phone = models.CharField(max_length=15, blank=False)
    date = models.DateField(default=datetime.datetime.today)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.product
    
class Cart(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.product.name} - Cart'

    def get_total_price(self):
        # Method to calculate the total price of this item in the cart
        return self.quantity * self.product.price if not self.product.is_sale else self.quantity * self.product.sale_price
    