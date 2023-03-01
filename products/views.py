from django.shortcuts import render, redirect
from django.template import RequestContext

from .models import Order, User, Product, Customer, Invoice
from django.db.models import Q
from .forms import OrderForm, CustomerForm, ProductForm
from .utilities import searchItems, paginateItems, searchOrdersForInvoice, assigningDiscount

from datetime import date, datetime, timedelta

# for login logout features
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

# for converting html page to pdf
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.views.generic import ListView
from django.http import HttpResponse

# for graphing
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy as np

import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import base64
# Create your views here.

# logging in
def loginUser(request):
    if request.user.is_authenticated:
        return redirect('home')

    # validating username and password entered
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

    return render(request, "login.html")

# logging out
@login_required(login_url='login')  # page can only be seen if user is logged in
def logoutUser(request):
    logout(request)
    messages.info(request, 'User was logged out!')
    return redirect('login')

# render basic home page
def home(request):
    return render(request, 'home.html')

# displays orders filtered by search and paginated
@login_required(login_url='login')
def orders(request):
    orders, search_query = searchItems(request, 'search_order')
    custom_range, orders = paginateItems(request, orders)
    context = {'orders': orders, 'search_query': search_query, 'custom_range': custom_range}
    return render(request, 'orders.html', context)

# create new order form
@login_required(login_url='login')
def createOrder(request):
    # generates empty form
    form = OrderForm()

    # user fills up form and submits
    if request.method == 'POST':
        form = OrderForm(request.POST)
        # saves form once all fields are valid
        if form.is_valid():
            order = form.save()
            # assigning discount to order based on customer tier (function imported from utilities)
            assigningDiscount(order)
            return redirect('orders')

    context = {'form': form}
    return render(request, "order_form.html", context)

# creates new order via QR code - once scanned, form is prefilled with data from QR code
@login_required(login_url='login')
def createQROrder(request):
    # example url encoded in qr code
    # https://flapp-app.herokuapp.com/create-QR-order/?productName=Guava&grade=AA&weight=40
    # only works provided user is logged in already, or else link will redirect to login

    # extracts data from url based on QR code
    productName = request.GET.get('productName')
    grade = request.GET.get('grade')
    weight = request.GET.get('weight')
    # finds product object in database
    product = Product.objects.get(Q(productName=productName) & Q(grade=grade))

    # creates new order, assigns values extracted
    order = Order()
    order.product = product
    order.weight = weight

    # produces prefilled order form, allows users to input customer or make changes, saves form once valid
    form = OrderForm(instance=order)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            order = form.save()
            assigningDiscount(order)
            return redirect('orders')
    context = {'form':form}
    return render(request, "order_form.html", context)

@login_required(login_url='login')
@user_passes_test(lambda u: u.is_superuser)  # page can only be accessed by superusers
def updateOrder(request, pk):
    # finds single order which matches selected pk
    order = Order.objects.get(id=pk)
    # displays original saved form
    form = OrderForm(instance=order)

    # saves updates to form
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            order = form.save()
            assigningDiscount(order)
            return redirect('orders')

    context = {'form': form}
    return render(request, "order_form.html", context)

# allows user to view orders
@login_required(login_url='login')
def retrieveOrder(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)

    context = {'form': form}
    return render(request, "view_order.html", context)

# delete order
@login_required(login_url='login')
@user_passes_test(lambda u: u.is_superuser)
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)

    if request.method == 'POST':
        order.delete()
        return redirect('orders')
    context = {'form':form}
    return render(request, 'delete_order.html', context)

# displays invoices filtered by search and paginated
@login_required(login_url='login')
def invoices(request):
    invoices, search_query = searchItems(request, 'search_invoice')
    custom_range, invoices = paginateItems(request, invoices)
    context = {'invoices': invoices, 'search_query': search_query, 'custom_range': custom_range}
    return render(request, 'invoices.html', context)

class InvoiceListView(ListView):
    model = Invoice
    template_name = 'invoices.html'

# generating pdf for viewing invoices using xhtml2pdf library
@login_required(login_url='login')
# sample code from xhtml2pdf's documentation
def render_pdf_view(request, *args, **kwargs):
    # finds relevant invoice and its orders
    pk = kwargs.get('pk')
    invoice = Invoice.objects.get(pk=pk)
    orders = Order.objects.filter(invoice=pk)

    # calculate the amount of discount applied in format XX%
    percentDiscount = str(round((1-orders[0].discount)*100))+'%'

    context = {'orders': orders, 'invoice': invoice, 'percentDiscount':percentDiscount}

    template_path = 'pdfInvoice.html'
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')

    # to download
    # response['Content-Disposition'] = 'attachment; filename="report.pdf"'

    # to display (for now)
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

# generate invoice page - filter orders, and allow new invoice to be created
@login_required(login_url='login')
@user_passes_test(lambda u: u.is_superuser)
def generateInvoices(request):
    # gets all selected orders
    if request.method == "POST":
        id_list = request.POST.getlist('boxes')
        orders = [Order.objects.get(id=id) for id in id_list]

        # customer for invoice will just be customer of first order selected
        # will need to improve on this later
        # for now I assume user will create invoices with orders all from the same customer
        mainOrder = orders[0]
        customer = mainOrder.customer

        # create new invoice and assign customer with customer of first order
        invoice = Invoice()
        invoice.customer = customer

        # determine invoice grand total
        grandTotal = 0
        for order in orders:
            grandTotal += order.subtotal
        invoice.grandTotal = grandTotal

        # calculate discounted total
        discountedTotal = grandTotal * mainOrder.discount
        invoice.discountedTotal = discountedTotal

        # save invoice
        invoice.save()

        # update flag to false once order has been assigned to an invoice
        for order in id_list:
            Order.objects.filter(pk=int(order)).update(flag=True)
            Order.objects.filter(pk=int(order)).update(invoice=invoice)

        messages.success(request, ("Invoice generated successfully"))
        return redirect('invoices')

    # filter orders based on customer and time frame
    else:
        orders, customer, selected_days = searchOrdersForInvoice(request)
        context = {'orders': orders, 'customer': customer, 'selected_days':selected_days}
        return render(request, 'generateInvoices.html', context)

# similar to orders
@login_required(login_url='login')
def products(request):
    products, search_query = searchItems(request, 'search_product')
    custom_range, products = paginateItems(request, products)
    context = {'products': products, 'search_query': search_query, 'custom_range': custom_range}
    return render(request, 'products.html', context)

@login_required(login_url='login')
@user_passes_test(lambda u: u.is_superuser)
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
@user_passes_test(lambda u: u.is_superuser)
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

# no view single product as all fields can be clearly seen in table already
# no delete product as product object needs to be protected (and is quite a rare occasion)

# similar to orders as well
@login_required(login_url='login')
@user_passes_test(lambda u: u.is_superuser)
def customers(request):
    customers, search_query = searchItems(request, 'search_customer')
    custom_range, customers = paginateItems(request, customers)
    context = {'customers': customers, 'search_query': search_query, 'custom_range': custom_range}
    return render(request, 'customers.html', context)

@login_required(login_url='login')
@user_passes_test(lambda u: u.is_superuser)
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
@user_passes_test(lambda u: u.is_superuser)
def retrieveCustomer(request, pk):
    customer = Customer.objects.get(id=pk)
    form = CustomerForm(instance=customer)

    context = {'form': form}
    return render(request, "view_customer.html", context)

@login_required(login_url='login')
@user_passes_test(lambda u: u.is_superuser)
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
@user_passes_test(lambda u: u.is_superuser)
def deleteCustomer(request, pk):
    customer = Customer.objects.get(id=pk)
    form = CustomerForm(instance=customer)
    if request.method == 'POST':
        customer.delete()
        return redirect('customers')
    context = {'form':form}
    return render(request, 'delete_customer.html', context)

# the reports page
@login_required(login_url='login')
@user_passes_test(lambda u: u.is_superuser)
def reports(request):
    # get current date and figure out tomorrow's date, and the date of the start of the year
    today = datetime.now().date()
    tomorrow = datetime.now().date() + timedelta(days=1)
    startOfYear = today.replace(month=1, day=1)

    # assigning revenues
    dailyRevenue = 0
    monthlyRevenue = 0
    yearlyRevenue = 0

    orders = Order.objects.filter(transactionTime__range=[startOfYear, tomorrow])
    for order in orders:
        # for daily
        if order.transactionTime.day == today.day and order.transactionTime.month == today.month and order.transactionTime.year == today.year:
            dailyRevenue += order.discountedTotal()
        # for monthly
        if order.transactionTime.month == today.month and order.transactionTime.year == today.year:
            monthlyRevenue += order.discountedTotal()
        # for yearly
        if order.transactionTime.year == today.year:
            yearlyRevenue += order.discountedTotal()

    # round to two decimal places
    dailyRevenue = round(dailyRevenue, 2)
    monthlyRevenue = round(monthlyRevenue, 2)
    yearlyRevenue = round(yearlyRevenue, 2)

    # calculating date 30 days ago
    monthToDate = tomorrow - timedelta(days=30)

    # function returns every single day between given range
    def daterange(start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    # calculating data for 2 barcharts, including: number of sales and total revenues for the last 30 days
    def dailyRevsAndSales():
        days = []
        revenues = []
        sales = []

        # assigning days to days list (for x-axis of barcharts)
        for singleDay in daterange(monthToDate, tomorrow):
            days.append(singleDay.strftime("%m-%d"))

            # calculating data for y-axis (sales and revenue)
            orders = Order.objects.filter(transactionTime__range=[singleDay, singleDay + timedelta(days=1)])
            dayRevenue = 0
            daySales = 0

            for order in orders:
                dayRevenue += order.discountedTotal()
                daySales += order.weight

            revenues.append(dayRevenue)
            sales.append(daySales)

        return days, revenues, sales

    # calculating data for 2 piecharts
    # finding the top customers by revenue (last 30 days)
    def listOfTopCustomers():
        customers = {}

        # calculating total spending by each customer in last 30 days and adding to dictionary
        orders = Order.objects.filter(transactionTime__range=[monthToDate, tomorrow])
        for order in orders:
            if order.customer.fullname() not in customers:
                customers.update({order.customer.fullname(): order.discountedTotal()})
            elif order.customer.fullname() in customers:
                customers[order.customer.fullname()] += order.discountedTotal()

        # sorting dict in descending order - greatest spenders first
        sorted_customers = dict(sorted(customers.items(), key=lambda item: item[1], reverse=True))

        topCustomers = {}
        # return top 10 customers from sorted dict
        for key in list(sorted_customers.keys())[:10]:
            topCustomers[key] = sorted_customers[key]
        return topCustomers


    # finding the top products by revenue (last 30 days)
    def listOfTopProducts():
        products = {}
        orders = Order.objects.filter(transactionTime__range=[monthToDate, tomorrow])
        for order in orders:
            if order.product.product() not in products:
                products.update({order.product.product(): order.discountedTotal()})
            elif order.product.product() in products:
                products[order.product.product()] += order.discountedTotal()

        sorted_products = dict(sorted(products.items(), key=lambda item: item[1], reverse=True))

        topProducts = {}
        # return top 10 customers
        for key in list(sorted_products.keys())[:10]:
            topProducts[key] = sorted_products[key]
        return topProducts

    # assigning function call to variable so can pass in context to template
    topCustomers = listOfTopCustomers()
    topProducts = listOfTopProducts()

    # generating actual chart - 2 barcharts, 2 piecharts
    def generate_charts():
        days, revenues, sales = dailyRevsAndSales()

        topCustomersList = list(topCustomers.keys())
        totalCustomerRevenues = list(topCustomers.values())

        topProductsList = list(topProducts.keys())
        totalProductRevenues = list(topProducts.values())

        chart_images = []

        # chart 1 : barchart of Daily Revenues for past 30 days
        fig = Figure()
        ax = fig.add_subplot()
        ax.bar(days, revenues)
        ax.set_title('30 Days - Daily Revenues')
        ax.set_xlabel('Date')
        ax.set_ylabel('Revenue')

        ax.set_xticks(days[::5])
        ax.set_xticklabels(days[::5])

        ax.tick_params(axis='x', labelsize=6)

        ax.tick_params(axis='y', which='major', labelsize=6)

        canvas = FigureCanvas(fig)
        buffer = io.BytesIO()
        canvas.print_png(buffer)

        image_content = buffer.getvalue()
        base64_image = base64.b64encode(image_content).decode('utf-8')
        chart_images.append({'title': '30 Days - Daily Revenues', 'base64_image': base64_image})

        # chart 2 : barchart of Daily Sales (quantity) for past 30 days
        fig = Figure()
        ax = fig.add_subplot()
        ax.bar(days, sales)
        ax.set_title('30 Days - Daily Sales')
        ax.set_xlabel('Date')
        ax.set_ylabel('Sales')

        ax.set_xticks(days[::5])
        ax.set_xticklabels(days[::5])

        ax.tick_params(axis='x', labelsize=6)

        ax.tick_params(axis='y', which='major', labelsize=6)

        canvas = FigureCanvas(fig)
        buffer = io.BytesIO()
        canvas.print_png(buffer)

        image_content = buffer.getvalue()
        base64_image = base64.b64encode(image_content).decode('utf-8')
        chart_images.append({'title': '30 Days - Daily Sales', 'base64_image': base64_image})

        # chart 3 : piechart of Top Customers for past 30 days
        fig = Figure()
        ax = fig.add_subplot()
        ax.pie(totalCustomerRevenues, labels=topCustomersList, autopct='%1.1f%%', startangle=90)
        ax.set_title('Top Customers By Revenue')
        ax.axis('equal')

        canvas = FigureCanvas(fig)
        buffer = io.BytesIO()
        canvas.print_png(buffer)

        image_content = buffer.getvalue()
        base64_image = base64.b64encode(image_content).decode('utf-8')
        chart_images.append({'title': 'Top Customers By Revenue', 'base64_image': base64_image})

        # chart 4 : piechart of Top Products for past 30 days
        fig = Figure()
        ax = fig.add_subplot()
        ax.pie(totalProductRevenues, labels=topProductsList, autopct='%1.1f%%', startangle=90)
        ax.set_title('Top Products By Revenue')
        ax.axis('equal')

        canvas = FigureCanvas(fig)
        buffer = io.BytesIO()
        canvas.print_png(buffer)

        image_content = buffer.getvalue()
        base64_image = base64.b64encode(image_content).decode('utf-8')
        chart_images.append({'title': 'Top Products By Revenue', 'base64_image': base64_image})

        return chart_images

    # assign function call to variable, which will store charts
    chart_images = generate_charts()

    context = {'dailyRevenue': dailyRevenue, 'monthlyRevenue': monthlyRevenue, 'yearlyRevenue': yearlyRevenue, 'topCustomers': topCustomers, 'topProducts':topProducts, 'chart_images': chart_images}
    return render(request, 'reports.html', context)



