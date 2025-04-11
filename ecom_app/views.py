from django.shortcuts import render
from django.views.generic import ListView,CreateView,DetailView
from ecom_app.models import Customer, Product
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy



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
        
    
     