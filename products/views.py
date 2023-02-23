from django.shortcuts import render, redirect
from .models import Order, User, Product, Customer, Invoice
from .forms import OrderForm, CustomerForm, ProductForm
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .utilities import searchItems, paginateItems, searchOrdersForInvoice
from django.template import RequestContext

from datetime import date, datetime, timedelta

# for converting html page to pdf
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.views.generic import ListView
from django.http import HttpResponse

import random
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy as np

# Create your views here.
def loginUser(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password is incorrect')

    return render(request, "login_register.html")
@login_required(login_url='login')
def logoutUser(request):
    logout(request)
    messages.info(request, 'User was logged out!')
    return redirect('login')

def home(request):
    return render(request, 'home.html')

@login_required(login_url='login')
def orders(request):
    orders, search_query = searchItems(request, 'search_order')
    custom_range, orders = paginateItems(request, orders)
    context = {'orders': orders, 'search_query': search_query, 'custom_range': custom_range}
    return render(request, 'orders.html', context)
@login_required(login_url='login')
def createOrder(request):
    form = OrderForm()

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():

            form.save()
            return redirect('orders')
    context = {'form': form}
    return render(request, "order_form.html", context)

@login_required(login_url='login')
def createQROrder(request):
    productName = request.GET.get('productName')
    grade = request.GET.get('grade')
    weight = request.GET.get('weight')

    return render(request, "order_form.html")
@login_required(login_url='login')
def updateOrder(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('orders')

    context = {'form': form}
    return render(request, "order_form.html", context)
@login_required(login_url='login')
def retrieveOrder(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)

    context = {'form': form}
    return render(request, "view-order.html", context)
@login_required(login_url='login')
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)

    if request.method == 'POST':
        order.delete()
        return redirect('orders')
    context = {'form':form}
    return render(request, 'delete_order.html', context)
@login_required(login_url='login')
def invoices(request):
    invoices, search_query = searchItems(request, 'search_invoice')
    custom_range, invoices = paginateItems(request, invoices)
    context = {'invoices': invoices, 'search_query': search_query, 'custom_range': custom_range}
    return render(request, 'invoices.html', context)

class InvoiceListView(ListView):
    model = Invoice
    template_name = 'invoices.html'
@login_required(login_url='login')
# sample code from xhtml2pdf's documentation
def render_pdf_view(request, *args, **kwargs):
    pk = kwargs.get('pk')
    invoice = Invoice.objects.get(pk=pk)
    orders = Order.objects.filter(invoice=pk)

    context = {'orders': orders, 'invoice': invoice}
    template_path = 'pdfInvoice.html'
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')

    #to download
    #response['Content-Disposition'] = 'attachment; filename="report.pdf"'

    #to display
    response['Content-Disposition'] = 'filename="invoice.pdf"'

    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)

    # if error
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@login_required(login_url='login')
def generateInvoices(request):
    # generate actual invoice
    if request.method == "POST":
        id_list = request.POST.getlist('boxes')
        orders = [Order.objects.get(id=id) for id in id_list]

        customer = orders[0].customer

        # create new invoice and assign customer with customer of first order (assume user will create invoices with orders from same customer)
        invoice = Invoice()
        invoice.customer = customer

        # determine invoice grand total
        grandTotal = 0
        for order in orders:
            grandTotal += order.subtotal
        invoice.grandTotal = grandTotal

        # form invoice summary
        summary = str(orders[0].product.productName)
        for order in orders:
            summary = summary + ' ' + str(order.product.grade) + ' ' + str(order.weight) + 'kg ,'
        invoice.summary = summary

        invoice.save()

        # update flag to false once order has been assigned to an invoice
        for order in id_list:
            Order.objects.filter(pk=int(order)).update(flag=True)
            Order.objects.filter(pk=int(order)).update(invoice=invoice)

        messages.success(request, ("Invoice generated successfully"))
        context = {'invoice':invoice, 'orders':orders}
        return redirect('invoices')
        #return render(request, 'singleInvoice.html', context)

    # search for orders to generate invoice
    else:
        orders, customer, startDate, endDate = searchOrdersForInvoice(request)
        context = {'orders': orders, 'customer': customer, 'startDate': startDate, 'endDate': endDate}
        return render(request, 'generateInvoices.html', context)

@login_required(login_url='login')
def products(request):
    products, search_query = searchItems(request, 'search_product')
    custom_range, products = paginateItems(request, products)
    context = {'products': products, 'search_query': search_query, 'custom_range': custom_range}
    return render(request, 'products.html', context)
@login_required(login_url='login')
def createProduct(request):
    form = ProductForm()

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():

            form.save()
            return redirect('products')
    context = {'form': form}
    return render(request, "product_form.html", context)
@login_required(login_url='login')
def updateProduct(request, pk):
    product = Product.objects.get(id=pk)
    form = ProductForm(instance=product)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('products')

    context = {'form': form}
    return render(request, "product_form.html", context)

@login_required(login_url='login')
def customers(request):
    customers, search_query = searchItems(request, 'search_customer')
    custom_range, customers = paginateItems(request, customers)
    context = {'customers': customers, 'search_query': search_query, 'custom_range': custom_range}
    return render(request, 'customers.html', context)
@login_required(login_url='login')
def createCustomer(request):
    form = CustomerForm()

    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():

            form.save()
            return redirect('customers')
    context = {'form': form}
    return render(request, "customer_form.html", context)
@login_required(login_url='login')
def updateCustomer(request, pk):
    customer = Customer.objects.get(id=pk)
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customers')

    context = {'form': form}
    return render(request, "customer_form.html", context)
@login_required(login_url='login')
def deleteCustomer(request, pk):
    customer = Customer.objects.get(id=pk)
    form = CustomerForm(instance=customer)
    if request.method == 'POST':
        customer.delete()
        return redirect('customers')
    context = {'form':form}
    return render(request, 'delete_customer.html', context)


@login_required(login_url='login')
def reports(request):
    today = datetime.now().date()
    year = str(today.year)
    month = str(today.month)
    # +1 to include today
    day = str(today.day + 1)
    todayDateString = year + '-' + month + '-' + day
    startDayOfYear = year + '-01-01'

    dailyRevenue = 0
    monthlyRevenue = 0
    yearlyRevenue = 0

    orders = Order.objects.filter(transactionTime__range=[startDayOfYear, todayDateString])

    for order in orders:
        if order.transactionTime.day == today.day and order.transactionTime.month == today.month and order.transactionTime.year == today.year:
            dailyRevenue += order.subtotal
        if order.transactionTime.month == today.month and order.transactionTime.year == today.year:
            monthlyRevenue += order.subtotal
        if order.transactionTime.year == today.year:
            yearlyRevenue += order.subtotal

    monthToDate = today - timedelta(30)
    def daterange(start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)
    def dailySalesChart():
        days = []
        sales = []
        for singleDay in daterange(monthToDate, today):
            days.append(singleDay.strftime("%m-%d"))
            orders = Order.objects.filter(transactionTime__range=[singleDay, singleDay + timedelta(days=1)])

            daySales = 0
            for order in orders:
                daySales += order.weight
            sales.append(daySales)

        # create a figure and a subplot
        fig, ax = plt.subplots()

        # plot the data as a line
        ax.bar(days, sales)

        # set the title and axis labels
        ax.set_title('30 Days - Daily Sales')
        ax.set_xlabel('Date')
        ax.set_ylabel('Sales')

        ax.set_xticks(days[::5])
        ax.set_xticklabels(days[::5])

        ax.tick_params(axis='x', labelsize=6)

        ax.tick_params(axis='y', which='major', labelsize=6)

        plt.savefig('static/charts/daily-sales.png')

    dailySalesChart()

    def listOfTopCustomers():
        customers = {}
        orders = Order.objects.filter(transactionTime__range=[monthToDate, todayDateString])
        for order in orders:
            if order.customer.fullname not in customers:
                customers.update({order.customer.fullname: order.subtotal})
            elif order.customer.fullname in customers:
                customers[order.customer.fullname] += order.subtotal

        sorted_customers = dict(sorted(customers.items(), key=lambda item: item[1], reverse=True))

        topCustomers = {}
        # return top 10 customers
        for key in list(sorted_customers.keys())[:10]:
            topCustomers[key] = sorted_customers[key]
        return topCustomers

    def listOfTopProducts():
        products = {}
        orders = Order.objects.filter(transactionTime__range=[monthToDate, todayDateString])
        for order in orders:
            if order.product.nameAndGrade not in products:
                products.update({order.product.nameAndGrade: order.subtotal})
            elif order.product.nameAndGrade in products:
                products[order.product.nameAndGrade] += order.subtotal

        sorted_products = dict(sorted(products.items(), key=lambda item: item[1], reverse=True))

        topProducts = {}
        # return top 10 customers
        for key in list(sorted_products.keys())[:10]:
            topProducts[key] = sorted_products[key]
        return topProducts

    topCustomers = listOfTopCustomers()
    topProducts = listOfTopProducts()
    context = {'dailyRevenue': dailyRevenue, 'monthlyRevenue': monthlyRevenue, 'yearlyRevenue': yearlyRevenue, 'topCustomers': topCustomers, 'topProducts':topProducts}
    return render(request, 'reports.html', context)



