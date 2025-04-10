from django.shortcuts import render
from django.views.generic import ListView,CreateView
from ecom_app.models import Customer, Product
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
    model = Customer
    template_name = "register.html"
    form_class = UserCreationForm
    sucess_url = reverse_lazy('login')
    
    
    
     