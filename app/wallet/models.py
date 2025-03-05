from uuid import uuid4

from django.db import models


# About indexes:
# The task description does not specify whether read or write operations will be more frequent.
# Therefore, I cannot confidently determine the best indexing strategy.
#
# - If read operations are more frequent, I prefer indexing every field used for filtering or ordering.
# - If write operations are more frequent, I prefer carefully choosing indexes to balance read and write performance.
#
# The optimal indexing strategy depends on the API usage scenarios, which are not provided in the task description.


class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)  # noqa: A003
    label = models.CharField(max_length=255)
    balance = models.DecimalField(decimal_places=18, max_digits=33, default=0, null=False, blank=False, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'wallets'
        ordering = ['-created_at', 'id']


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)  # noqa: A003
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions', null=False, blank=False)
    txid = models.CharField(max_length=64, unique=True, null=False, blank=False, db_index=True)
    amount = models.DecimalField(decimal_places=18, max_digits=33, null=False, blank=False, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at', 'id']
