import django_filters
from .models import Transaction


class TransactionFilter(django_filters.FilterSet):
    start = django_filters.DateFilter(field_name="timestamp", lookup_expr='gte')
    end = django_filters.DateFilter(field_name="timestamp", lookup_expr='lte')

    class Meta:
        model = Transaction
        fields = ['account', 'transaction_category', 'start', 'end']