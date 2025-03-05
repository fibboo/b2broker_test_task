from django.urls import path

from app.wallet.views import TransactionView, WalletView

urlpatterns = [
    path('wallets',
         WalletView.as_view({'get': 'list', 'post': 'create'}),
         name='wallet-list'),
    path('wallets/<uuid:pk>',
         WalletView.as_view({'get': 'retrieve', 'put': 'update'}),
         name='wallet-detail'),

    path('transactions',
         TransactionView.as_view({'get': 'list', 'post': 'create'}),
         name='transaction-list'),
    path('transactions/<uuid:pk>',
         TransactionView.as_view({'get': 'retrieve', 'put': 'update'}),
         name='transaction-detail'),
    path('transactions/txid/<str:txid>',
         TransactionView.as_view({'get': 'retrieve'}),
         name='transaction-detail-by-txid'),
]
