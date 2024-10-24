import logging
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from django.db.models import Max, Value
from django.db.models.functions import Coalesce
from rest_framework.filters import OrderingFilter
from rest_framework.exceptions import PermissionDenied
from .models import Account, Transaction
from .serializers import AccountSerializer, TransactionSerializer
from .permissions import IsOwnerOrAdmin
from .pagination import AccountsCursorPagination, TransactionsCursorPagination
from .filters import TransactionFilter

# Get a logger instance
logger = logging.getLogger(__name__)

class AccountListView(generics.ListAPIView):
    """
    View to list accounts for the authenticated user or all accounts for staff users.
    """
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = AccountsCursorPagination
    ordering = ['-latest_transaction_timestamp']

    def get_queryset(self):
        user = self.request.user
        logger.info(f"User '{user.username}' is requesting account list.")

        # Annotate each account with the latest transaction timestamp
        queryset = Account.objects.annotate(
            latest_transaction_timestamp=Coalesce(
                Max('transaction__timestamp'),
                Value('1970-01-01'),
                output_field=models.DateTimeField()
            )
        )

        if user.is_staff:
            logger.info(f"Staff user '{user.username}' is accessing all accounts.")
            return queryset.order_by('-latest_transaction_timestamp')
        else:
            logger.info(f"User '{user.username}' is accessing their own accounts.")
            accounts = queryset.filter(user=user).order_by('-latest_transaction_timestamp')
            logger.info(f"User '{user.username}' retrieved {accounts.count()} accounts.")
            return accounts


class AccountRetrieveView(generics.RetrieveAPIView):
    """
    View to retrieve a single account by ID for the authenticated user or for staff users.
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_object(self):
        account = super().get_object()
        logger.info(f"User '{self.request.user.username}' retrieved account '{account.name}'.")
        return account


class TransactionListView(generics.ListAPIView):
    """
    View to list transactions for the authenticated user or all transactions for staff users.
    Supports filtering by date range and transaction category.
    """
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = TransactionsCursorPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = TransactionFilter
    ordering_fields = ['timestamp']

    def get_queryset(self):
        user = self.request.user
        logger.info(f"User '{user.username}' is requesting transaction list.")
        queryset = Transaction.objects.select_related('account').all()
        account_id = self.request.query_params.get('account')

        if not user.is_staff:
            logger.info(f"User '{user.username}' is accessing their own transactions.")
            queryset = queryset.filter(account__user=user)
        if account_id:
            logger.info(f"User '{user.username}' is requesting transactions for account '{account_id}'.")
            if not queryset.filter(account_id=account_id).exists():
                logger.warning(f"User '{user.username}' tried to access transactions for account '{account_id}' without permission.")
                raise PermissionDenied("You do not have permission to access transactions for this account.")
        logger.info(f"User '{user.username}' retrieved {queryset.count()} transactions.")
        return queryset


class TransactionRetrieveView(generics.RetrieveAPIView):
    """
    View to retrieve a single transaction by ID for the authenticated user or for staff users.
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_object(self):
        transaction = super().get_object()
        logger.info(f"User '{self.request.user.username}' retrieved transaction '{transaction.description}'.")
        return transaction