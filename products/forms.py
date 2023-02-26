from .models import Order, Customer, Product
#django forms
from django.forms import ModelForm
from django import forms

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
        fields = ['firstname', 'lastname', 'phone', 'email', 'deliveryAddress', 'companyName', 'companyPhone', 'companyAddress', 'city', 'state', 'postcode', 'tier']
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

