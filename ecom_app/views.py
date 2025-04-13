from django.shortcuts import render,get_object_or_404
from django.views.generic import ListView,CreateView,DetailView,DeleteView
from ecom_app.models import Customer, Product,Category,Cart
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
    

# cart-section

class MainCart(ListView):
    model = Cart
    template_name = "cart/cart_main.html"
    

class AddCart(CreateView):
   pass

class DeleteCart(DeleteView):
    pass

class UpdateCart(DetailView):
   pass


    
