from django.contrib.auth import get_user_model
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import Account, Transaction
from django.utils import timezone
from datetime import timedelta


class TestAccountsApiAsStaff(APITestCase):

    # this line loads the fixture data with sample users, accounts and transactions
    fixtures = ["sample.json"]

    def setUp(self):
        super().setUp()
        # this user exists in the fixtures
        admin_user = get_user_model().objects.get(username="test-admin")
        self.client.force_authenticate(admin_user)

    def test_accounts_list(self):
        response = self.client.get("/api/accounts/")

        assert response.status_code == status.HTTP_200_OK
        print(response.json())

        # there should be a list of transactions for this page in the 'results' field
        assert len(response.json()["results"]) > 0

    # the freeze_time annotation ensures that the test always runs as if stuck at a
    # specific point in time, so assertions about the transaction_count_last_thirty_days
    # and balance_change_last_thirty_days fields will work predictably.
    @freeze_time("2022-06-14 18:00:00")
    def test_retrieve_account(self):
        response = self.client.get("/api/accounts/1/")

        assert response.status_code == status.HTTP_200_OK

        assert response.json() == {
            "id": 1,
            "user": 2,
            "name": "John Smith",
            "transaction_count_last_thirty_days": 119,
            "balance_change_last_thirty_days": "-1304.67",
        }

    @freeze_time("2022-06-14 18:00:00")
    def test_retrieve_account_with_transactions_added_during_test(self):
        """Test retrieving an account after adding transactions manually, checking if the calculations are updated."""
        # Add transactions during the test, within the last 30 days window
        account = Account.objects.get(id=1)
        now = timezone.now()

        # Add a transaction within the last 30 days
        Transaction.objects.create(
            account=account,
            timestamp=now - timedelta(days=10),
            amount=200.00,
            description="Test transaction",
            transaction_category="PURCHASE"
        )

        # Add a transaction outside the last 30 days
        Transaction.objects.create(
            account=account,
            timestamp=now - timedelta(days=40),
            amount=100.00,
            description="Old transaction",
            transaction_category="SALE"
        )

        # Retrieve the account again
        response = self.client.get("/api/accounts/1/")
        assert response.status_code == status.HTTP_200_OK

        # Check that the new transaction within the last 30 days is included
        account_data = response.json()
        assert account_data["transaction_count_last_thirty_days"] == 120  # 119 from fixture + 1 added
        assert account_data["balance_change_last_thirty_days"] == "-1104.67"  # Updated balance (-1304.67 + 200.00)


class TestTransactionListView(APITestCase):
    fixtures = ["sample.json"]  # Load your fixtures if you have them

    def setUp(self):
        # Load users and accounts from fixtures
        self.user1 = User.objects.get(username="user1")
        self.user2 = User.objects.get(username="user2")
        self.admin = User.objects.get(username="test-admin")
        self.account1 = Account.objects.get(name="John Smith")  # user1's account
        self.account2 = Account.objects.get(name="Jane Doe")  # user2's account
        self.transactions_url = reverse('transaction-list')

    # Test: Admin can retrieve all transactions
    def test_admin_can_retrieve_all_transactions(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.transactions_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0

    # Test: User can retrieve their own transactions
    def test_user_can_retrieve_their_own_transactions(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.transactions_url)
        assert response.status_code == status.HTTP_200_OK

        # Check all transactions belong to the user's account
        for transaction in response.data['results']:
            assert transaction['account'] in [1, 2]

    # Test: User cannot access another user's transactions
    def test_user_cannot_access_another_users_transactions(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.transactions_url, {'account': self.account2.id})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # Test: Filter transactions by account
    def test_filter_transactions_by_account(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.transactions_url, {'account': self.account1.id})
        assert response.status_code == status.HTTP_200_OK

        # Ensure all transactions belong to account1
        for transaction in response.data['results']:
            assert transaction['account'] == self.account1.id

    # Test: Filter transactions by date range
    def test_filter_transactions_by_date_range(self):
        self.client.force_authenticate(user=self.user1)
        start_date = '2023-01-01'
        end_date = '2023-01-31'
        response = self.client.get(self.transactions_url, {
            'account': self.account1.id,
            'start': start_date,
            'end': end_date
        })
        assert response.status_code == status.HTTP_200_OK

        # Ensure transactions fall within the specified date range
        for transaction in response.data['results']:
            assert start_date <= transaction['timestamp'] <= end_date

    # Test: Filter transactions by category
    def test_filter_transactions_by_category(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.transactions_url, {
            'account': self.account1.id,
            'transaction_category': 'PURCHASE'
        })
        assert response.status_code == status.HTTP_200_OK

        # Ensure all transactions are of category 'PURCHASE'
        for transaction in response.data['results']:
            assert transaction['transaction_category'] == 'PURCHASE'

    # Test: Paginated transaction list
    def test_paginated_transaction_list(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.transactions_url)
        assert response.status_code == status.HTTP_200_OK
        assert 'next' in response.data
        assert 'previous' in response.data
        assert 'results' in response.data

    # Test: Invalid date format
    def test_invalid_date_format(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.transactions_url, {
            'account': self.account1.id,
            'start': 'invalid-date'
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
