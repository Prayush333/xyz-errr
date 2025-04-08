from django.db import models
import datetime


class Category(models.Model): # categories of products
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

class Customer(models.Model): # customers details
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
      


class Product(models.Model): # products 
    name = models.CharField(max_length=100)
    price = models.DecimalField(default=0,decimal_places=2,max_digits=8)
    Category = models.ForeignKey(Category,on_delete=models.CASCADE, default=1)
    description = models.CharField(max_length=300, default='', null=True)
    image = models.ImageField(upload_to='uploads/product/')
    is_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(default=0,decimal_places=2,max_digits=8)

    def __str__(self):
        return self.name


class Order(models.Model): # product order details
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    address = models.CharField(max_length=200,  blank=False)
    phone = models.CharField(max_length=15,blank=False)
    date = models.DateField(default=datetime.datetime.today)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.product