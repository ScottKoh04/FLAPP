from .models import Order, Invoice
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views import View

#converting html to pdf
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def searchOrders(request):
    search_query = ''

    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')

    orders = Order.objects.distinct().filter(
        Q(customer__firstname__icontains=search_query) |
        Q(product__productName__icontains=search_query)
    )
    return orders, search_query

def paginateOrders(request, orders):
    page = request.GET.get('page')
    results = 10
    paginator = Paginator(orders, results)

    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        orders = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        orders = paginator.page(page)

    leftIndex = int(page) - 4

    if leftIndex < 1:
        leftIndex = 1

    rightIndex = int(page) + 5

    if rightIndex > paginator.num_pages:
        rightIndex = paginator.num_pages + 1

    custom_range = range(leftIndex, rightIndex)

    return custom_range, orders

