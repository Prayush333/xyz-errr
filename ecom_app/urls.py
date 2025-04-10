from django.urls import path

from ecom_app import views

urlpatterns = [
   path("", views.HomePage.as_view(), name="home"),
   path("about/",views.AboutPage.as_view(),name="about"),
   path("register/",views.UserResister.as_view(), name="register"),
]