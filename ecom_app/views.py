from django.http import JsonResponse 
from django.shortcuts import render,get_object_or_404
from django.views.generic import ListView,CreateView,DetailView
from ecom_app.models import Customer, Product,Category,CartItem
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import View
from .cart import Cart



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
class CartListView(ListView):
    model= CartItem
    template_name = "cart/cart_list.html"

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
             # return response
             # response = JsonResponse({'Product Name':product.name})
            response = JsonResponse({'quantity':cart_quantity})
           
            return response
        
        return JsonResponse({'error': 'Invalid action'}, status=400)


    

class DeleteCart(View):
    pass

class UpdateCart(View):
    pass
    
 
