import phonenumber_field.validators
from django.db import models
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
    def __str__(self):
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
        )
    TIERS = (
        ('1', 'Tier 1'),
        ('2', 'Tier 2'),
        ('3', 'Market'),
    )
    firstname = models.CharField(max_length=50, null=True)
    lastname = models.CharField(max_length=50, null=True)
    deliveryAddress = models.CharField(max_length=200, null=True, default='N/A')
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

    @property
    def fullname(self):
        return f"{self.firstname} {self.lastname}"
    def __str__(self):
        return f"{self.firstname} {self.lastname}"
    class Meta:
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

    def __str__(self):
        return f"{self.productName} {self.grade}"


class Invoice(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    timeGenerated = models.DateTimeField(auto_now_add=True)
    grandTotal = models.FloatField(null=True)
    discountedTotal = models.FloatField(null=True)
    class Meta:
        ordering = ['-id']

class Order(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, null=True)
    transactionTime = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    weight = models.IntegerField(null=True)
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



