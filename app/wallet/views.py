from django.shortcuts import get_object_or_404
from django_filters import NumberFilter, UUIDFilter
from django_filters.rest_framework import FilterSet
from rest_framework import mixins, viewsets
from rest_framework_json_api.django_filters import DjangoFilterBackend
from rest_framework_json_api.filters import OrderingFilter
from rest_framework_json_api.pagination import JsonApiPageNumberPagination
from rest_framework_json_api.parsers import JSONParser

from app.wallet.models import Transaction, Wallet
from app.wallet.serializers import TransactionSerializer, WalletSerializer


class Pagination(JsonApiPageNumberPagination):
    page_size = 10
    max_page_size = 100


class WalletFilter(FilterSet):
    min_balance = NumberFilter(field_name='balance', lookup_expr='gt')
    max_balance = NumberFilter(field_name='balance', lookup_expr='lt')


class WalletView(mixins.CreateModelMixin,
                 mixins.RetrieveModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    pagination_class = Pagination
    parser_classes = [JSONParser]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = WalletFilter
    ordering_fields = ['balance', 'created_at']


class TransactionFilter(FilterSet):
    min_amount = NumberFilter(field_name='amount', lookup_expr='gt')
    max_amount = NumberFilter(field_name='amount', lookup_expr='lt')
    wallet = UUIDFilter(field_name='wallet__id')

    class Meta:
        model = Transaction
        fields = ['min_amount', 'max_amount', 'wallet']


class TransactionView(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    pagination_class = Pagination
    parser_classes = [JSONParser]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = TransactionFilter
    ordering_fields = ['amount', 'created_at']

    def get_object(self):
        # If URL has txid parameter, searching transaction by txid
        if 'txid' in self.kwargs:
            txid = self.kwargs['txid']
            obj = get_object_or_404(Transaction, txid=txid)
            self.check_object_permissions(self.request, obj)
            return obj
        return super().get_object()
