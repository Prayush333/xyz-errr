
from django.contrib import admin
from django.urls import path,include
from . import settings
from django.conf.urls.static import static 
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include('ecom_app.urls')),
    
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
