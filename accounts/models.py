from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta


class Account(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, help_text="The name of the account owner")

    def transaction_count_last_thirty_days(self):
        thirty_days_ago = timezone.now() - timedelta(days=30)
        return self.transaction_set.filter(timestamp__gte=thirty_days_ago).count()

    def balance_change_last_thirty_days(self):
        thirty_days_ago = timezone.now() - timedelta(days=30)
        return self.transaction_set.filter(timestamp__gte=thirty_days_ago).aggregate(
            balance_change=models.Sum('amount')
        )['balance_change'] or 0


class TransactionCategory(models.TextChoices):
    # Deposit or withdrawal of funds using an ATM (Automated Teller Machine)
    ATM = "ATM", _("Atm")
    # Payment of a bill
    BILL_PAYMENT = "BILL_PAYMENT", _("Bill Payment")
    # Cash deposited over the branch counter or using a Cash & Deposit Machines
    CASH = "CASH", _("Cash")
    # An option retailers offer to withdraw cash while making a debit card purchase
    CASHBACK = "CASHBACK", _("Cashback")
    # A document ordering the payment of money from a bank account to another person or organization
    CHEQUE = "CHEQUE", _("Cheque")
    # Correction of a transaction error
    CORRECTION = "CORRECTION", _("Correction")
    # Funds added to your account
    CREDIT = "CREDIT", _("Credit")
    # An automatic withdrawal of funds initiated by a third party at regular intervals
    DIRECT_DEBIT = "DIRECT_DEBIT", _("Direct_Debit")
    # A payment to your account from shares you hold
    DIVIDEND = "DIVIDEND", _("Dividend")
    # Fees or charges in relation to a transaction
    FEE_CHARGE = "FEE_CHARGE", _("Fee_Charge")
    # Credit or debit associated with interest earned or incurred
    INTEREST = "INTEREST", _("Interest")
    # Miscellaneous credit or debit
    OTHER = "OTHER", _("Other")
    # A payment made with your debit or credit card
    PURCHASE = "PURCHASE", _("Purchase")
    # A payment instructed by the account-holder to a third party at regular intervals
    STANDING_ORDER = "STANDING_ORDER", _("Standing Order")
    # Transfer of money between accounts
    TRANSFER = "TRANSFER", _("Transfer")
    # Funds taken out from your account, uncategorised by the bank
    DEBIT = "DEBIT", _("Debit")
    # No classification of transaction category known
    UNKNOWN = "UNKNOWN", _("Unknown")


class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(
        help_text="Date the transaction was posted on the account."
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text=(
            "The transaction amount. Positive amounts are deposits or "
            "transfers into the account while negative amounts are payments or "
            "transfers out of the account."
        ),
    )
    description = models.CharField(
        max_length=100,
        help_text="Original description of the transaction as reported by the provider.",
    )
    transaction_category = models.CharField(
        max_length=20, choices=TransactionCategory.choices
    )
