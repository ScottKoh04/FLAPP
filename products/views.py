#this is the real working FLAPP
from django.shortcuts import render, redirect
from .models import Order, User, Product, Customer, Invoice
from .forms import OrderForm, CustomerForm, ProductForm
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from .utilities import searchItems, paginateItems
from .filters import OrderFilter
from django.template import RequestContext

#converting html to pdf
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.views.generic import ListView
# Create your views here.
from django.http import HttpResponse

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
def orders(request):
    orders, search_query = searchItems(request, 'search_order')
    custom_range, orders = paginateItems(request, orders)
    context = {'orders': orders, 'search_query': search_query, 'custom_range': custom_range}
    return render(request, 'orders.html', context)


def invoices(request):
    invoices, search_query = searchItems(request, 'search_invoice')
    custom_range, invoices = paginateItems(request, invoices)
    context = {'invoices': invoices, 'search_query': search_query, 'custom_range': custom_range}
    return render(request, 'invoices.html', context)

'''
@login_required(login_url='login')
def singleInvoice2(request):
    #orders = Order.objects.get(invoice=pk)
    #invoice = Invoice.objects.get(id=pk)

    #context = {'orders': orders, 'invoice': invoice}
    return render(request, "singleInvoice2.html")
@login_required(login_url='login')
def generateInvoices2(request):
    orders = Order.objects.filter(flag=False)
    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs

    if request.method == "POST":
        id_list = request.POST.getlist('boxes')
        selectedOrders = [Order.objects.get(id=id) for id in id_list]

        customer = selectedOrders[0].customer

        grandTotal = 0
        for order in selectedOrders:
            grandTotal += order.subtotal
        #save id_list to sessions

        #request.session['id_list'] = id_list
        #id_list = request.session['id_list']

        #create new invoice
        newInvoice = Invoice()
        newInvoice.customer = customer
        newInvoice.save()
        Invoice.objects.filter(pk=newInvoice.id).update(customer=customer)
        #request.session['invoice_id'] = newInvoice.id
        #invoice_id = request.session['invoice_id']

        #slow inefficent way to uncheck boxes
        orders.update(flag=False)

        for order in id_list:
            Order.objects.filter(pk=int(order)).update(flag=True)
            Order.objects.filter(pk=int(order)).update(invoice=newInvoice)

        messages.success(request, ("Invoice generated successfully"))
        context = {'newInvoice':newInvoice, 'selectedOrders':selectedOrders, 'grandTotal':grandTotal}
        return render(request, 'singleInvoice.html', context)
    else:
        context = {'orders': orders, 'myFilter': myFilter}
        return render(request, 'generateInvoices.html', context)
'''
'''
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def singleInvoice(pk):
    invoice = Invoice.objects.get(id=pk)
    #orders = Order.objects.filter(invoice=pk)

    #context = {'orders': orders, 'invoice': invoice}
    return invoice
@login_required(login_url='login')
class ViewPDF(View):
    def get(self, request, *args, **kwargs):
        #id = kwargs.get('id')
        pdf = render_to_pdf('pdf_template.html', 'hello')
        return HttpResponse(pdf, content_type='application/pdf')

class DownloadPDF(View):
    def get(self, request, *args, **kwargs):
        pdf = render_to_pdf('pdf_template.html')
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Invoice.pdf"
        content = "attachment; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
'''
class InvoiceListView(ListView):
    model = Invoice
    template_name = 'invoices.html'
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
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@login_required(login_url='login')
def generateInvoices(request):
    orders = Order.objects.filter(flag=False)
    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs

    if request.method == "POST":
        id_list = request.POST.getlist('boxes')
        orders = [Order.objects.get(id=id) for id in id_list]

        customer = orders[0].customer

        #create new invoice
        invoice = Invoice()
        invoice.customer = customer

        grandTotal = 0
        for order in orders:
            grandTotal += order.subtotal
        invoice.grandTotal = grandTotal
        print(invoice.grandTotal)
        summary = str(orders[0].product.productName)
        for order in orders:
            summary = summary + ' ' + str(order.product.grade) + ' ' + str(order.weight) + 'kg ,'
        invoice.summary = summary
        print(invoice.summary)
        invoice.save()

        #Invoice.objects.filter(pk=invoice.id).update(customer=customer)

        #slow inefficent way to uncheck boxes
        #orders.update(flag=False)

        for order in id_list:
            Order.objects.filter(pk=int(order)).update(flag=True)
            Order.objects.filter(pk=int(order)).update(invoice=invoice)

        messages.success(request, ("Invoice generated successfully"))
        context = {'invoice':invoice, 'orders':orders}
        return render(request, 'singleInvoice.html', context)
    else:
        context = {'orders': orders, 'myFilter': myFilter}
        return render(request, 'generateInvoices.html', context)

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
    if request.method == 'POST':
        customer.delete()
        return redirect('customers')
    context = {'object': customer}
    return render(request, 'delete_template.html', context)

@login_required(login_url='login')
def users(request):
    return render(request, 'users.html')

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

'''
def order(request, pk):
    orderObj = Order.objects.get(id=pk)
    return render(request, 'single-order.html', {'order': orderObj})
    '''
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
    return render(request, "single-order.html", context)

@login_required(login_url='login')
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('orders')
    context = {'object': order}
    return render(request, 'delete_template.html', context)