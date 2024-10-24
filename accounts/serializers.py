from rest_framework import serializers
from .models import Account, Transaction


class AccountSerializer(serializers.ModelSerializer):
    transaction_count_last_thirty_days = serializers.SerializerMethodField()
    balance_change_last_thirty_days = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ['id', 'user', 'name', 'transaction_count_last_thirty_days', 'balance_change_last_thirty_days']

    def get_transaction_count_last_thirty_days(self, obj):
        return obj.transaction_count_last_thirty_days()

    def get_balance_change_last_thirty_days(self, obj):
        return str(round(obj.balance_change_last_thirty_days(), 2))


class TransactionSerializer(serializers.ModelSerializer):
    transaction_category = serializers.CharField()

    class Meta:
        model = Transaction
        fields = ['id', 'account', 'timestamp', 'amount', 'description', 'transaction_category']
