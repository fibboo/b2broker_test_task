from decimal import Decimal
from uuid import uuid4

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class WalletTransactionTests(APITestCase):
    def create_wallet(self, label='Test Wallet'):
        url = reverse('wallet-list')
        payload = {
            'data': {
                'type': 'Wallet',
                'attributes': {
                    'label': label
                }
            }
        }
        response = self.client.post(url, payload, format='vnd.api+json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response.data

    def create_transaction(self, wallet_id, txid, amount):
        url = reverse('transaction-list')
        payload = {
            'data': {
                'type': 'Transaction',
                'attributes': {
                    'txid': txid,
                    'amount': str(amount)
                },
                'relationships': {
                    'wallet': {
                        'data': {
                            'type': 'Wallet',
                            'id': wallet_id
                        }
                    }
                }
            }
        }
        return self.client.post(url, payload, format='vnd.api+json')

    def test_create_and_update_transaction_ok(self):
        wallet_data = self.create_wallet()
        wallet_id = wallet_data['id']

        response = self.create_transaction(wallet_id, 'tx1', Decimal('100'))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        wallet_detail = self.client.get(reverse('wallet-detail', kwargs={'pk': wallet_id}), format='vnd.api+json')
        self.assertNotEqual(Decimal(wallet_detail.data['balance']), Decimal('0'))
        self.assertEqual(Decimal(wallet_detail.data['balance']), Decimal('100'))

        tx_id = response.data['id']
        update_url = reverse('transaction-detail', kwargs={'pk': tx_id})
        update_payload = {
            'data': {
                'id': tx_id,
                'type': 'Transaction',
                'attributes': {
                    'txid': 'tx1',
                    'amount': str(150)
                },
                'relationships': {
                    'wallet': {
                        'data': {
                            'type': 'Wallet',
                            'id': wallet_id
                        }
                    }
                }
            }
        }
        update_response = self.client.put(update_url, update_payload, format='vnd.api+json')
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)

        wallet_detail = self.client.get(reverse('wallet-detail', kwargs={'pk': wallet_id}), format='vnd.api+json')
        self.assertEqual(Decimal(wallet_detail.data['balance']), Decimal('150'))

    def test_create_transaction_zero_amount_error(self):
        wallet_data = self.create_wallet()
        wallet_id = wallet_data['id']

        response = self.create_transaction(wallet_id, 'tx_zero', Decimal('0'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Transaction amount cannot be zero.', str(response.data))

    def test_create_transaction_causing_zero_balance_ok(self):
        wallet_data = self.create_wallet()
        wallet_id = wallet_data['id']

        response1 = self.create_transaction(wallet_id, 'tx_positive_zero', Decimal('100'))
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        response2 = self.create_transaction(wallet_id, 'tx_negative_zero', Decimal('-100'))
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

        wallet_detail = self.client.get(reverse('wallet-detail', kwargs={'pk': wallet_id}), format='vnd.api+json')
        self.assertEqual(Decimal(wallet_detail.data['balance']), Decimal('0'))

    def test_create_transaction_insufficient_funds(self):
        wallet_data = self.create_wallet()
        wallet_id = wallet_data['id']

        response1 = self.create_transaction(wallet_id, 'tx_positive', Decimal('50'))
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        response2 = self.create_transaction(wallet_id, 'tx_overdraw', Decimal('-60'))
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Insufficient wallet balance. Wallet balance cannot be negative.', str(response2.data))

    def test_update_transaction_causing_zero_balance_ok(self):
        wallet_data = self.create_wallet()
        wallet_id = wallet_data['id']

        response1 = self.create_transaction(wallet_id, 'tx1', Decimal('100'))
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        response2 = self.create_transaction(wallet_id, 'tx2', Decimal('100'))
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

        tx2_id = response2.data['id']
        update_url = reverse('transaction-detail', kwargs={'pk': tx2_id})
        update_payload = {
            'data': {
                'id': tx2_id,
                'type': 'Transaction',
                'attributes': {
                    'txid': 'tx2',
                    'amount': str(-100)
                },
                'relationships': {
                    'wallet': {
                        'data': {
                            'type': 'Wallet',
                            'id': wallet_id
                        }
                    }
                }
            }
        }
        update_response = self.client.put(update_url, update_payload, format='vnd.api+json')
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)

        wallet_detail = self.client.get(reverse('wallet-detail', kwargs={'pk': wallet_id}), format='vnd.api+json')
        self.assertEqual(Decimal(wallet_detail.data['balance']), Decimal('0'))

    def test_update_transaction_insufficient_funds(self):
        wallet_data = self.create_wallet()
        wallet_id = wallet_data['id']

        response = self.create_transaction(wallet_id, 'tx_update2', Decimal('100'))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        tx_id = response.data['id']
        update_url = reverse('transaction-detail', kwargs={'pk': tx_id})
        update_payload = {
            'data': {
                'id': tx_id,
                'type': 'Transaction',
                'attributes': {
                    'txid': 'tx_update2',
                    'amount': str(-10)
                },
                'relationships': {
                    'wallet': {
                        'data': {
                            'type': 'Wallet',
                            'id': wallet_id
                        }
                    }
                }
            }
        }
        update_response = self.client.put(update_url, update_payload, format='vnd.api+json')
        self.assertEqual(update_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Insufficient wallet balance. Wallet balance cannot be negative.', str(update_response.data))

    def test_get_transaction_by_id_ok(self):
        wallet_data = self.create_wallet()
        wallet_id = wallet_data['id']

        create_response = self.create_transaction(wallet_id, 'tx_get_id', Decimal('75'))
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        tx_id = create_response.data['id']
        get_url = reverse('transaction-detail', kwargs={'pk': tx_id})
        get_response = self.client.get(get_url, format='vnd.api+json')

        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data['id'], tx_id)
        self.assertEqual(get_response.data['txid'], 'tx_get_id')
        self.assertEqual(get_response.data['amount'], '75.000000000000000000')

    def test_get_transaction_by_txid_ok(self):
        wallet_data = self.create_wallet()
        wallet_id = wallet_data['id']

        txid = 'tx_get_txid'
        create_response = self.create_transaction(wallet_id, txid, Decimal('85'))
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        get_url = reverse('transaction-detail-by-txid', kwargs={'txid': txid})
        get_response = self.client.get(get_url, format='vnd.api+json')

        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data['txid'], txid)
        self.assertEqual(get_response.data['amount'], '85.000000000000000000')

    def test_get_transaction_not_found_by_id(self):
        random_id = uuid4()
        get_url = reverse('transaction-detail', kwargs={'pk': random_id})
        response = self.client.get(get_url, format='vnd.api+json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_transaction_not_found_by_txid(self):
        get_url = reverse('transaction-detail-by-txid', kwargs={'txid': 'nonexistent_txid'})
        response = self.client.get(get_url, format='vnd.api+json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_transactions_empty(self):
        response = self.client.get(reverse('transaction-list'), format='vnd.api+json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], [])

    def test_list_transactions_filtering_sorting(self):
        wallet_data = self.create_wallet()
        wallet_id = wallet_data['id']

        amounts = [10, 20, 30, 40]
        txids = ['tx10', 'tx20', 'tx30', 'tx40']
        for txid, amount in zip(txids, amounts):
            resp = self.create_transaction(wallet_id, txid, Decimal(str(amount)))
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        url = reverse('transaction-list')
        params = '?filter[min_amount]=15&sort=amount&filter[wallet]={}'.format(wallet_id)
        response = self.client.get(url + params, format='vnd.api+json')

        data = response.data['results']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 3)
        expected_amounts = [Decimal('20'), Decimal('30'), Decimal('40')]
        for item, expected in zip(data, expected_amounts):
            self.assertEqual(Decimal(item['amount']), expected)

    def test_list_transactions_pagination_sorting(self):
        wallet_data = self.create_wallet()
        wallet_id = wallet_data['id']

        total_transactions = 15
        amounts = [i * 10 for i in range(1, total_transactions + 1)]
        for i, amount in enumerate(amounts, start=1):
            txid = 'tx_pag_{}'.format(i)
            resp = self.create_transaction(wallet_id, txid, Decimal(str(amount)))
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        url = reverse('transaction-list')
        params_page1 = '?sort=amount&page[number]=1'
        response1 = self.client.get(url + params_page1, format='vnd.api+json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        data1 = response1.data['results']
        self.assertEqual(len(data1), 10)
        expected_page1_amounts = [Decimal(str(i * 10)) for i in range(1, 11)]
        for item, expected in zip(data1, expected_page1_amounts):
            self.assertEqual(Decimal(item['amount']), expected)

        params_page2 = '?sort=amount&page[number]=2'
        response2 = self.client.get(url + params_page2, format='vnd.api+json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        data2 = response2.data['results']
        self.assertEqual(len(data2), 5)
        expected_page2_amounts = [Decimal(str(i * 10)) for i in range(11, 16)]
        for item, expected in zip(data2, expected_page2_amounts):
            self.assertEqual(Decimal(item['amount']), expected)
