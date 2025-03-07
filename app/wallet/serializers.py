from decimal import Decimal

from django.db import transaction as db_transaction
from rest_framework.exceptions import ValidationError
from rest_framework_json_api import serializers

from app.wallet.models import Transaction, Wallet


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'
        read_only_fields = ['id', 'balance', 'created_at', 'updated_at']


class TransactionSerializer(serializers.ModelSerializer):
    included_serializers = {'wallet': WalletSerializer}
    wallet = serializers.ResourceRelatedField(queryset=Wallet.objects.all(),
                                              many=False)

    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        wallet = attrs.get('wallet') or self.instance.wallet
        new_amount = attrs.get('amount', self.instance.amount if self.instance else Decimal('0'))
        previous_amount = self.instance.amount if self.instance else Decimal('0')

        if new_amount == Decimal('0'):
            raise ValidationError('Transaction amount cannot be zero.')

        balance_change = new_amount - previous_amount

        if (wallet.balance + balance_change) < 0:
            raise ValidationError('Insufficient wallet balance. Wallet balance cannot be negative.')

        return attrs

    def create(self, validated_data):
        with db_transaction.atomic():
            # Using select for update to avoid race conditions when there is more than one replica of the application
            wallet = Wallet.objects.select_for_update().get(id=validated_data['wallet'].id)

            transaction = Transaction.objects.create(
                wallet=wallet,
                txid=validated_data['txid'],
                amount=validated_data['amount']
            )

            wallet.balance += transaction.amount
            wallet.save()

        return transaction

    def update(self, instance, validated_data):
        with db_transaction.atomic():
            # Using select for update to avoid race conditions when there is more than one replica of the application
            wallet = Wallet.objects.select_for_update().get(id=instance.wallet.id)

            previous_amount = instance.amount
            new_amount = validated_data.get('amount', previous_amount)
            amount_change = new_amount - previous_amount

            if new_amount == Decimal('0'):
                raise ValidationError('Transaction amount cannot be zero.')

            if (wallet.balance + amount_change) < 0:
                raise ValidationError('Insufficient wallet balance. Wallet balance cannot be negative.')

            instance = super().update(instance, validated_data)

            wallet.balance += amount_change
            wallet.save()

        return instance
