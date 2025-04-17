from django.urls import path

from ecom_app import views

urlpatterns = [

    # home page and others views
   path("", views.HomePage.as_view(), name="home"),
   path("about/",views.AboutPage.as_view(),name="about"),
   path("register/",views.UserResister.as_view(), name="register"),
   path("product/<int:pk>",views.ProductDetail.as_view(), name="product-detail"),
   path("category/<str:id>", views.CategoryView.as_view(), name="category"),

    #cart views
   path('cart/',views.CartListView.as_view(),name="cart_list"),
    path('add/',views.AddCart.as_view(),name="cart_add"),
    path('delete/',views.DeleteCart.as_view(),name="cart_delete"),
    path('update/',views.UpdateCart.as_view(),name="cart_update"),
]