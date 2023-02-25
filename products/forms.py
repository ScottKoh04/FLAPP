from django.forms import ModelForm
from django import forms
from .models import Order, Customer, Product

from django.core import validators

#forms for making new entries to models
class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'product', 'weight']
        widgets = {
            'product': forms.RadioSelect()
        }

class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = ['firstname', 'lastname', 'phone', 'email', 'address', 'companyName', 'companyPhone', 'companyAddress', 'city', 'state', 'postcode', 'tier']
        widgets = {
            'tier': forms.RadioSelect()
        }
class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['productName', 'grade', 'unitPrice',]
        widgets = {
            'grade': forms.RadioSelect()
        }

