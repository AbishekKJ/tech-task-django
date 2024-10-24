from rest_framework.pagination import CursorPagination
from rest_framework.response import Response


class AccountsCursorPagination(CursorPagination):
    page_size = 10
    ordering = '-latest_transaction_timestamp'

    def get_paginated_response(self, data):
        return Response({
            'results': data,  # All the paginated data will be placed under 'results'
            'next': self.get_next_link(),  # Pagination link for the next set of results
            'previous': self.get_previous_link()  # Pagination link for the previous set of results
        })


class TransactionsCursorPagination(CursorPagination):
    page_size = 10
    ordering = '-timestamp'

    def get_paginated_response(self, data):
        return Response({
            'results': data,  # All the paginated data will be placed under 'results'
            'next': self.get_next_link(),  # Pagination link for the next set of results
            'previous': self.get_previous_link()  # Pagination link for the previous set of results
        })