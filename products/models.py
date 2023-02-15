from django.db import models

# Create your models here.
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

class Tier(models.Model):
    TIERS = (
        ('1', 'Tier 1'),
        ('2', 'Tier 2'),
        ('3', 'Market'),
    )
    tier = models.CharField(max_length=10, choices=TIERS, null=True)

    def __str__(self):
        return 'Tier ' + self.tier

class Customer(models.Model):
    firstname = models.CharField(max_length=50, null=True)
    lastname = models.CharField(max_length=50, null=True)
    companyName = models.CharField(max_length=100, null=True, default='N/A')
    companyPhone = models.IntegerField(null=True, default='N/A')
    companyAddress = models.CharField(max_length=200, null=True, default='N/A')
    phone = models.IntegerField(null=True)
    email = models.CharField(max_length=50, null=True)
    tier = models.ForeignKey(Tier, on_delete=models.PROTECT)

    def __str__(self):
        return self.firstname + ' ' + self.lastname

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
    tier = models.ForeignKey(Tier, on_delete=models.PROTECT)
    unitPrice = models.FloatField(null=True)

    def __str__(self):
        return self.productName + '-' + self.grade + '-' + str(self.tier)

class Invoice(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    timeGenerated = models.DateTimeField(auto_now_add=True)
    grandTotal = models.FloatField(null=True)
    summary = models.CharField(max_length=500, null=True)
    class Meta:
        ordering = ['-id']

class Order(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    transactionTime = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    weight = models.IntegerField(null=True)
    flag = models.BooleanField(null=True)

    @property
    def subtotal(self):
        subtotal = round(self.product.unitPrice * self.weight, 2)
        return subtotal
    def __str__(self):
        return 'Order ' + str(self.id)

    class Meta:
        ordering = ['-transactionTime']


