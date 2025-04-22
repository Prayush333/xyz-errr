from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from .models import EmployeeProfile

class EmployeeLoginForm(AuthenticationForm):
    """
    Custom authentication form for employees, including Employee ID.
    """
    employee_id = forms.CharField(
        label=_("Employee ID"),
        strip=True,
        widget=forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control'})
    )

    error_messages = {
        **AuthenticationForm.error_messages, # Inherit default messages
        'invalid_employee_id': _(
            "Please enter the correct username, password, and employee ID for "
            "a staff account. Note that all fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive."),
    }

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        employee_id = self.cleaned_data.get('employee_id')

        if username is not None and password and employee_id:
            # Authenticate using username and password first
            self.user_cache = authenticate(self.request, username=username, password=password)

            if self.user_cache is None:
                # Standard authentication failed
                raise self.get_invalid_login_error()
            elif not self.user_cache.is_active:
                 # User is inactive
                raise forms.ValidationError(
                    self.error_messages['inactive'],
                    code='inactive',
                )
            elif not self.user_cache.is_staff:
                 # User is not staff, cannot use employee login
                 raise forms.ValidationError(
                    self.error_messages['invalid_login'], # Use standard invalid login message
                    code='invalid_login',
                 )
            else:
                # User is authenticated and is staff, now check Employee ID
                try:
                    profile = EmployeeProfile.objects.get(user=self.user_cache, employee_id=employee_id)
                    # Employee ID matches the authenticated user
                    self.confirm_login_allowed(self.user_cache) # Check if login is allowed (e.g., email verified)
                except EmployeeProfile.DoesNotExist:
                    # Employee ID does not match the user or profile doesn't exist
                    raise forms.ValidationError(
                        self.error_messages['invalid_employee_id'],
                        code='invalid_employee_id',
                    )
        else:
             # Handle case where fields are missing (should be caught by field validation)
             pass # Let default field validation handle missing required fields

        return self.cleaned_data


# Form for Employee OTP Verification
class OTPVerificationForm(forms.Form):
    otp_code = forms.CharField(
        label=_("OTP Code"),
        max_length=6,
        min_length=6, # Ensure exactly 6 digits
        required=True,
        widget=forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control', 'placeholder': 'Enter 6-digit OTP'})
    )

    def clean_otp_code(self):
        """Ensure OTP contains only digits."""
        otp = self.cleaned_data.get('otp_code')
        if not otp.isdigit():
            raise forms.ValidationError(_("OTP must contain only digits."))
        return otp