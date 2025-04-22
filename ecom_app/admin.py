from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin # Import BaseUserAdmin
from django.contrib.auth.models import User # Import User model

# Import EmployeeProfile and other models
from ecom_app.models import Category, Customer, Order, Product, ShippingAddress, EmployeeProfile

# Mixin to restrict access to superusers only
class RestrictedAdminMixin:
    def has_module_permission(self, request):
        """Return True if user is superuser, False otherwise."""
        return request.user.is_superuser

    

# Register standard models that SHOULD be accessible to staff
admin.site.register(ShippingAddress) # ShippingAddress remains accessible

# Custom Admin for Order model (Accessible to staff)
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'product', 'date', 'status', 'processed_by')
    list_filter = ('status', 'date')
    list_editable = ('status',) # Allow editing status directly in the list view
    search_fields = ('id', 'customer__first_name', 'customer__last_name', 'product__name', 'processed_by__username')
    readonly_fields = ('date',) # Make the order date read-only after creation

    # Automatically set processed_by to the current user when saving
    def save_model(self, request, obj, form, change):
        if change: # Only set processed_by on updates, not creation (or adjust logic as needed)
             # Check if status is being changed or if processed_by is not already set
            if 'status' in form.changed_data or not obj.processed_by:
                 obj.processed_by = request.user
        super().save_model(request, obj, form, change)

# Define an inline admin descriptor for EmployeeProfile
# This will allow editing EmployeeProfile from the User admin page
class EmployeeProfileInline(admin.StackedInline): # Or use admin.TabularInline for a more compact view
    model = EmployeeProfile
    can_delete = False # Prevent deleting the profile from the user page
    verbose_name_plural = 'Employee Profile'
    fk_name = 'user' # Explicitly specify the foreign key name

# Define a new User admin (Restricted to superusers)
class UserAdmin(RestrictedAdminMixin, BaseUserAdmin): # Inherit from mixin
    inlines = (EmployeeProfileInline,) # Add the EmployeeProfile inline

    # Optionally, customize the list display for the User admin (only seen by superusers)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_employee_id')

    @admin.display(description='Employee ID')
    def get_employee_id(self, obj):
        # Safely access employee_id, handling cases where the profile might not exist yet
        try:
            return obj.employee_profile.employee_id
        except EmployeeProfile.DoesNotExist:
            return None

# Re-register UserAdmin
admin.site.unregister(User) # Unregister the default User admin
admin.site.register(User, UserAdmin) # Register User with the custom admin

# Remove the standalone EmployeeProfile registration if it exists (it was commented out, but good practice)
# admin.site.unregister(EmployeeProfile)


# --- Register models with restricted access ---

@admin.register(Category)
class CategoryAdmin(RestrictedAdminMixin, admin.ModelAdmin):
    list_display = ('name',) # Basic display for superusers
    search_fields = ('name',)

@admin.register(Customer)
class CustomerAdmin(RestrictedAdminMixin, admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone') # Basic display for superusers
    search_fields = ('first_name', 'last_name', 'email', 'phone')

@admin.register(Product)
class ProductAdmin(RestrictedAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'Category', 'price', 'is_sale', 'sale_price') # Basic display for superusers
    list_filter = ('Category', 'is_sale')
    search_fields = ('name', 'description')