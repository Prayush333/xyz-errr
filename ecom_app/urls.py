from django.urls import path

from ecom_app import views

urlpatterns = [

    # home page and others views
   path("", views.HomePage.as_view(), name="home"),
   path("about/",views.AboutPage.as_view(),name="about"),
   path("register/",views.UserResister.as_view(), name="register"),
   path("product/<int:pk>",views.ProductDetail.as_view(), name="product-detail"),
   path("category/<str:id>", views.CategoryView.as_view(), name="category"),
   path("my-orders/", views.CustomerOrderListView.as_view(), name="customer_order_list"), # Added URL for customer orders

    #cart views
   path('cart/',views.CartListView.as_view(),name="cart_list"),
    path('add/',views.AddCart.as_view(),name="cart_add"),
    path('cart/delete/<int:product_id>/', views.DeleteCart.as_view(), name='cart_delete'), # Updated path
    path('update/',views.UpdateCart.as_view(),name="cart_update"),

    #buy views
    path('buy/<int:product_id>/', views.BuyProductView.as_view(), name='buy_product'),

    # Payment URLs (Removed PayPal and Esewa URLs)
    # Only COD is handled directly in the BuyProductView now.
]

# Add URLs for OTP workflow
urlpatterns += [
    # URL for customer to trigger OTP sending (e.g., via a button POSTing here)
    path('order/confirm/<int:order_id>/', views.customer_confirm_order, name='customer_confirm_order'),
    # URL for employee to enter OTP
    path('order/verify/<int:order_id>/', views.employee_verify_order, name='employee_verify_order'),
]