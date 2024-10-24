from django.urls import path
from . import views

urlpatterns = [
    path('accounts/', views.AccountListView.as_view(), name='account-list'),
    path('accounts/<int:pk>/', views.AccountRetrieveView.as_view(), name='account-detail'),
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    path('transactions/<int:pk>/', views.TransactionRetrieveView.as_view(), name='transaction-detail'),
]