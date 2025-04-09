from django.shortcuts import render
from django.views.generic import ListView
from ecom_app.models import Product




class HomePage(ListView):
    model = Product
    template_name = "home.html"
    context_object_name = "products"


class AboutPage(ListView):
    model= Product
    template_name = "about.html"

    

    
     