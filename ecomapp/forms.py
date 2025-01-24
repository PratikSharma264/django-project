from django import forms
from .models import Order,Customer,Contact
from django.forms import TextInput, EmailInput
from django.contrib.auth.models import User
import re

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['ordered_by', 'shipping_address', 'mobile', 'email','payment_method']
        widgets = {
            'mobile': TextInput(attrs={'placeholder': 'Enter your mobile number'}),
            'email': EmailInput(attrs={'placeholder': 'Enter your email address'}),
        }
        help_texts = {
            'mobile': 'Please enter a 10-digit mobile number.',
        }

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if not mobile.isdigit() or len(mobile) != 10:  # Phone No. length validation
            raise forms.ValidationError("Please enter a valid 10-digit mobile number.")
        return mobile

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email or '@' not in email:  # Basic email validation
            raise forms.ValidationError("Please enter a valid email address.")
        return email
    

    
# class CustomerRegistrationForm(forms.ModelForm):
#     username = forms.CharField(widget=forms.TextInput())
#     password = forms.CharField(widget=forms.PasswordInput())
#     email = forms.CharField(widget=forms.EmailInput())

#     class Meta:
#         model = Customer
#         fields=["username","password","email","full_name","address"]
    
#     def clean_username(self):
#         uname = self.cleaned_data.get("username")
#         if User.objects.filter(username=uname).exists():
#             raise forms.ValidationError("Customer with this name already exists.")
        
#         return uname

class CustomerRegistrationForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "placeholder": "Enter username", 
            "class": "form-control"
        }),
        label="Username"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Enter password", 
            "class": "form-control"
        }),
        label="Password"
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "placeholder": "Enter email address", 
            "class": "form-control"
        }),
        label="Email Address"
    )

    class Meta:
        model = Customer
        fields = ["username", "password", "email", "full_name", "address"]
        widgets = {
            "full_name": forms.TextInput(attrs={
                "placeholder": "Enter full name", 
                "class": "form-control"
            }),
            "address": forms.TextInput(attrs={
                "placeholder": "Enter address", 
                "class": "form-control"
            })
        }

    def clean_username(self):
        uname = self.cleaned_data.get("username")
        if User.objects.filter(username=uname).exists():
            raise forms.ValidationError("A user with this username already exists.")
        return uname

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", password):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r"[0-9]", password):
            raise forms.ValidationError("Password must contain at least one number.")
        if not re.search(r"[_!@#$%^&*(),.?\":{}|<>]", password):
            raise forms.ValidationError("Password must contain at least one special character.")
        return password
    

class CustomerLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "placeholder": "Enter username", 
            "class": "form-control"
        }),
        label="Username"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Enter password", 
            "class": "form-control"
        }),
        label="Password"
    )

class AdminLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "placeholder": "Enter username", 
            "class": "form-control"
        }),
        label="Username"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Enter password", 
            "class": "form-control"
        }),
        label="Password"
    )



class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter your name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email address'}),
            'message': forms.Textarea(attrs={'placeholder': 'Enter your message'}),
        }
        help_texts = {
            'name': 'Please enter your full name.',
            'email': 'We will use this email to contact you.',
            'message': 'Please enter your message or inquiry.',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email or '@' not in email:  # Basic email validation
            raise forms.ValidationError("Please enter a valid email address.")
        return email
    


