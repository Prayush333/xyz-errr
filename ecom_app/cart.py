
class Cart():
    def __init__(self, request):
        self.session = request.session

        # taking the current session key if available
        cart = self.session.get('session_key')

        # if user is new then there will be no session key ,creating new one!
        cart = self.session['session_key'] = {}

        #making sure if cart is available in each page of site!
        self.cart = cart

    def add(self, product):
        product_id = str(product.id)

        if product_id in self.cart:
            pass
        else:
            self.cart[product_id] = {'price': str(product.price)}
        
        self.session.modified = True
