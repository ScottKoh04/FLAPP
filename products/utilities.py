from .models import Order, Invoice, Customer, Product
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views import View

#converting html to pdf
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def searchItems(request, search_type):
    search_query = ''

    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')
        print(search_query)
    if search_type == 'search_order':
        orders = Order.objects.distinct().filter(
            Q(customer__firstname__icontains=search_query) |
            Q(product__productName__icontains=search_query)
        )
        return orders, search_query

    elif search_type == 'search_customer':
        customers = Customer.objects.distinct().filter(
            Q(firstname__icontains=search_query) |
            Q(lastname__icontains=search_query) |
            Q(companyName__icontains=search_query)
        )
        return customers, search_query

    elif search_type == 'search_product':
        products = Product.objects.distinct().filter(
            Q(productName__icontains=search_query)
        )
        return products, search_query


def paginateItems(request, items):
    page = request.GET.get('page')
    results = 10
    paginator = Paginator(items, results)

    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        items = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        items = paginator.page(page)

    leftIndex = int(page) - 4

    if leftIndex < 1:
        leftIndex = 1

    rightIndex = int(page) + 5

    if rightIndex > paginator.num_pages:
        rightIndex = paginator.num_pages + 1

    custom_range = range(leftIndex, rightIndex)

    return custom_range, items

