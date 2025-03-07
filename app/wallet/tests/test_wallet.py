from uuid import uuid4

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class WalletTests(APITestCase):
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
        return self.client.post(url, payload, format='vnd.api+json')

    def test_create_wallet_ok(self):
        response = self.create_wallet('My Wallet')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['label'], 'My Wallet')
        self.assertEqual(response.data['balance'], '0.000000000000000000')

    def test_update_wallet_ok(self):
        create_response = self.create_wallet('Initial Label')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        wallet_id = create_response.data['id']

        url = reverse('wallet-detail', kwargs={'pk': wallet_id})
        payload = {
            'data': {
                'id': wallet_id,
                'type': 'Wallet',
                'attributes': {
                    'label': 'Updated Label'
                }
            }
        }
        update_response = self.client.put(url, payload, format='vnd.api+json')
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data['label'], 'Updated Label')

    def test_get_wallet_by_id_ok(self):
        create_response = self.create_wallet('Test Wallet')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        wallet_id = create_response.data['id']

        url = reverse('wallet-detail', kwargs={'pk': wallet_id})
        get_response = self.client.get(url, format='vnd.api+json')
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data['id'], wallet_id)
        self.assertEqual(get_response.data['label'], 'Test Wallet')

    def test_get_wallet_by_id_not_found(self):
        nonexistent_uuid = uuid4()
        url = reverse('wallet-detail', kwargs={'pk': nonexistent_uuid})
        response = self.client.get(url, format='vnd.api+json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_wallets_empty(self):
        url = reverse('wallet-list')
        response = self.client.get(url, format='vnd.api+json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], [])

    def test_list_wallets_with_multiple_wallets(self):
        self.create_wallet('Wallet 1')
        self.create_wallet('Wallet 2')
        self.create_wallet('Wallet 3')

        url = reverse('wallet-list')
        response = self.client.get(url, format='vnd.api+json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

        labels = [wallet['label'] for wallet in response.data['results']]
        self.assertIn('Wallet 1', labels)
        self.assertIn('Wallet 2', labels)
        self.assertIn('Wallet 3', labels)

    def test_update_wallet_not_found(self):
        nonexistent_uuid = uuid4()
        url = reverse('wallet-detail', kwargs={'pk': nonexistent_uuid})
        payload = {
            'data': {
                'id': 'nonexistent-uuid',
                'type': 'Wallet',
                'attributes': {
                    'label': 'Updated Label'
                }
            }
        }
        response = self.client.put(url, payload, format='vnd.api+json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
