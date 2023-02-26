from .models import Order, Invoice, Customer, Product
# django Q class allows complex queries to be made using and/or conditions, '|' represents or, '&' represents and
from django.db.models import Q
# django paginator class
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
# datetime functions
from datetime import datetime, timedelta

# below are the utility functions

# general search function for all pages - search database and return results which matches search_query given
def searchItems(request, search_type):
    search_query = ''

    # get search query user has inputted and assign to variable search_query
    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')

    # separate searches for separate pages and models

    # for orders page
    if search_type == 'search_order':
        orders = Order.objects.distinct().filter(
            Q(customer__firstname__icontains=search_query) |
            Q(customer__lastname__icontains=search_query) |
            Q(customer__companyName__icontains=search_query) |
            Q(product__productName__icontains=search_query) |
            Q(product__grade__icontains=search_query)
        )
        return orders, search_query

    # for customers page
    elif search_type == 'search_customer':
        customers = Customer.objects.distinct().filter(
            Q(firstname__icontains=search_query) |
            Q(lastname__icontains=search_query) |
            Q(companyName__icontains=search_query)
        )
        return customers, search_query

    # for products page
    elif search_type == 'search_product':
        products = Product.objects.distinct().filter(
            Q(productName__icontains=search_query) |
            Q(grade__icontains=search_query)
        )
        return products, search_query

    # for invoices page
    elif search_type == 'search_invoice':
        invoices = Invoice.objects.distinct().filter(
            Q(customer__firstname__icontains=search_query) |
            Q(customer__lastname__icontains=search_query) |
            Q(customer__companyName__icontains=search_query)
        )
        return invoices, search_query

# paginate orders using Django paginator function
def paginateItems(request, items):
    page = request.GET.get('page')  # gets the current page number
    results = 10  # number of entries per page
    paginator = Paginator(items, results)  # django Paginator class

    # execute paginator
    try:
        items = paginator.page(page)
    # exceptions
    # if current page number is not a valid integer, returns first page
    except PageNotAnInteger:
        page = 1
        items = paginator.page(page)
    # if current page number is beyond total number of pages, returns final page
    except EmptyPage:
        page = paginator.num_pages
        items = paginator.page(page)

    # displays pages on left of current
    leftIndex = int(page) - 4

    if leftIndex < 1:
        leftIndex = 1

    # displays pages on right of current
    rightIndex = int(page) + 5

    if rightIndex > paginator.num_pages:
        rightIndex = paginator.num_pages + 1

    custom_range = range(leftIndex, rightIndex)

    return custom_range, items

# search function for searching for orders using multiple filters (in the generate invoices page)
def searchOrdersForInvoice(request):
    customer = ''  # customer search query
    selected_days = ''  # results for previous () days

    # assigning search query values
    if request.GET.get('search_customer'):
        customer = request.GET.get('search_customer')

    if request.GET.get('selected_days'):
        selected_days = request.GET.get('selected_days')

    # setting start date for filtering
    if selected_days == '1': # today
        startDate = datetime.now().date()
    elif selected_days == '7': # last 7 days
        startDate = datetime.now().date() - timedelta(days=7)
    elif selected_days == '30':  # last 30 days
        startDate = datetime.now().date() - timedelta(days=30)
    else: # all days
        startDate = datetime.now().date() - timedelta(days=999)

    # setting end date for filtering
    endDate = datetime.now().date() + timedelta(days=1)

    # return query for relevant orders for different search scenarios
    if customer == '':  # customer field is empty
        if selected_days == '0':  # and selected days is all days
            orders = Order.objects.filter(flag=False)
        else:  # or selected days either today, last 7 days, or last 30 days
            orders = Order.objects.filter(Q(flag=False) & Q(transactionTime__range=[startDate, endDate]))
    else:  # customer field not empty
        if selected_days == '0':  # and selected days is all days
            orders = Order.objects.filter(Q(flag=False) & (Q(customer__firstname__icontains=customer) | Q(customer__lastname__icontains=customer) | Q(customer__companyName__icontains=customer)))
        else:  # or selected days either today, last 7 days, or last 30 days
            orders = Order.objects.filter(Q(flag=False) & Q(transactionTime__range=[startDate, endDate]) & (Q(customer__firstname__icontains=customer) | Q(customer__lastname__icontains=customer) | Q(customer__companyName__icontains=customer)))

    return orders, customer, selected_days

# assigning discount to order based on customer tier
def assigningDiscount(order):
    if order.customer.tier == '1':
        Order.objects.filter(pk=order.pk).update(discount=0.8)
    elif order.customer.tier == '2':
        Order.objects.filter(pk=order.pk).update(discount=0.9)
