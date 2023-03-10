from django.db import models

# validators
import phonenumber_field.validators
from django.core import validators
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from phonenumber_field.modelfields import PhoneNumberField

# register models here
class User(models.Model):
    firstname = models.CharField(max_length=50, null=True)
    lastname = models.CharField(max_length=50, null=True)
    phone = models.IntegerField(null=True)
    email = models.CharField(max_length=50, null=True)
    username = models.CharField(max_length=50, null=True)
    password = models.CharField(max_length=50, null=True)
    accountType = models.CharField(max_length=50, null=True)
    def __str__(self):  # string returned when object is referenced
        return self.firstname + ' ' + self.lastname

class Customer(models.Model):
    STATES = (
        ('Johor', 'Johor'),
        ('Kedah', 'Kedah'),
        ('Kelantan', 'Kelantan'),
        ('Malacca', 'Malacca'),
        ('Negeri Sembilan', 'Negeri Sembilan'),
        ('Pahang', 'Pahang'),
        ('Penang', 'Penang'),
        ('Perak', 'Perak'),
        ('Perlis', 'Perlis'),
        ('Sabah', 'Sabah'),
        ('Sarawak', 'Sarawak'),
        ('Selangor', 'Selangor'),
        ('Terengganu', 'Terengganu'),
        )  # choices for 'state' attribute
    TIERS = (
        ('1', 'Tier 1'),
        ('2', 'Tier 2'),
        ('3', 'Market'),
    )  # choices for 'tier' attribute
    firstname = models.CharField(max_length=50, null=True)
    lastname = models.CharField(max_length=50, null=True)
    deliveryAddress = models.CharField(max_length=200, null=True, default='N/A')
    # phone validator for a 10-digit string - groups of 3,3,4 digits.
    phone_regex = RegexValidator(regex=r'^\d{3}\d{3}\d{4}$')
    phone = models.CharField(null=True, max_length=30, validators=[phone_regex])
    email = models.EmailField(null=True, validators=[validators.EmailValidator()])
    companyName = models.CharField(max_length=100, null=True, default='N/A')
    companyPhone = models.CharField(null=True, max_length=30, validators=[phone_regex])
    companyAddress = models.CharField(max_length=200, null=True, default='N/A')
    city = models.CharField(max_length=20, null=True, default='N/A')
    state = models.CharField(max_length=15, choices=STATES, null=True)
    postcode = models.IntegerField(null=True)
    tier = models.CharField(max_length=10, choices=TIERS, default='3')

    # defines a read-only attribute of the model which can then be accessed elsewhere

    def fullname(self):
        return f"{self.firstname} {self.lastname}"

    def __str__(self):
        return f"{self.firstname} {self.lastname}"

    class Meta: # orders entries by firstname ASC
        ordering = ['firstname']
class Product(models.Model):
    GRADES = (
        ('AA', 'Grade AA'),
        ('A', 'Grade A'),
        ('B', 'Grade B'),
        ('Bk', 'Grade Bk'),
        ('C', 'Grade C')
    )
    productName = models.CharField(max_length=20, null=True)
    grade = models.CharField(max_length=10, choices=GRADES, null=True)
    unitPrice = models.FloatField(null=True)

    def product(self):
        return f"{self.productName} {self.grade}"

    def __str__(self):
        return f"{self.productName} {self.grade}"

    class Meta:
        ordering = ['productName', '-unitPrice']

class Invoice(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, null=True)
    # protects customer instance from being deleted
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    # protects user instance from being deleted
    timeGenerated = models.DateTimeField(auto_now_add=True)
    grandTotal = models.FloatField(null=True)
    discountedTotal = models.FloatField(null=True)
    class Meta:
        ordering = ['-id']  # order starting with latest

class Order(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, null=True)
    transactionTime = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    weight = models.IntegerField(null=True)
    # flag highlights whether an order is already part of an invoice (one order only linked to one invoice)
    flag = models.BooleanField(default=False)
    discount = models.FloatField(default=1)
    @property
    def subtotal(self):
        subtotal = round(self.product.unitPrice * self.weight, 2)
        return subtotal
    def discountedTotal(self):
        discountedTotal = round(self.subtotal * self.discount, 2)
        return discountedTotal
    def __str__(self):
        return 'Order ' + str(self.id)

    class Meta:
        ordering = ['-transactionTime']



