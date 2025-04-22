from .cart import Cart
from .models import Order, Customer # Import Order and Customer models


#creating a context processor so cart can work on all pages

def cart(request):
    return {'cart': Cart(request)} #to return default data from our Cart


def latest_order_status(request):
    """
    Adds the status of the most recent order for a logged-in customer to the context.
    """
    latest_order = None
    if request.user.is_authenticated and not request.user.is_staff:
        try:
            customer = Customer.objects.get(email=request.user.email)
            # Fetch the most recent order for this customer
            latest_order = Order.objects.filter(customer=customer).order_by('-date', '-id').first()
        except Customer.DoesNotExist:
            latest_order = None # No customer profile found
        except Exception: # Catch potential errors during query
             latest_order = None

    return {'latest_order': latest_order}
