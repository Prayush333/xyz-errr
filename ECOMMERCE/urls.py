 
from django.contrib import admin
from django.urls import path, include
from . import settings
from django.conf.urls.static import static
# Import the new login views from ecom_app
from ecom_app.views import SelectLoginTypeView, CustomerLoginView, EmployeeLoginView
# Keep auth_views for logout or other views if needed
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include('ecom_app.urls')),
    
    # --- Authentication URLs ---
    # Step 1: Select login type (replaces the old 'login' named URL)
    path("accounts/login/", SelectLoginTypeView.as_view(), name="select_login_type"),

    # Step 2a: Customer Login Form
    path("accounts/login/customer/", CustomerLoginView.as_view(), name="customer_login"),

    # Step 2b: Employee Login Form
    path("accounts/login/employee/", EmployeeLoginView.as_view(), name="employee_login"),

    # Logout URL (remains the same)
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    # --- End Authentication URLs ---
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
