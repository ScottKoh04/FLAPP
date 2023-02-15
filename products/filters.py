import django_filters
from django_filters import DateFilter
from .models import *

#filter for invoice generator

class OrderFilter(django_filters.FilterSet):
    start_date = DateFilter(field_name='transactionTime', lookup_expr='gte')
    end_date = DateFilter(field_name='transactionTime', lookup_expr='lte')
    class Meta:
        model = Order
        fields = 'customer',

