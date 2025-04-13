from ecom_app.cart import Cart


#creating a context processor so cart can work on all pages

def cart(request):
    return {'cart': Cart(request)} #to deturn default data from our Cart
