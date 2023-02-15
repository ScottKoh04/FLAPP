from django.forms import ModelForm
from .models import Order, Customer, Product
from django import forms

#making new order manually
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
        fields = ['firstname', 'lastname', 'phone', 'email', 'companyName', 'companyPhone', 'companyAddress', 'tier',]
        widgets = {
            'tier': forms.RadioSelect()
        }

class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['productName', 'grade', 'tier', 'unitPrice',]
        widgets = {
            'grade': forms.RadioSelect(),
            'tier': forms.RadioSelect()
        }