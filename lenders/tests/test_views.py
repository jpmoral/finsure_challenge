import csv
import io
import os
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase

from lenders.models import Lender


class LenderViewSetTests(APITestCase):
    fields = ['name', 'code', 'upfront_commission', 'high_trail_commission', 'low_trail_commission', 'is_active', 'is_hidden','balance_multiplier']

    def setUp(self):
        self.lender_a = Lender.objects.create(name='A', code='A', upfront_commission=2, high_trail_commission=2, low_trail_commission=1, is_active=True)
        Lender.objects.create(name='B', code='B', upfront_commission=2, high_trail_commission=2, low_trail_commission=1, is_active=True)
        Lender.objects.create(name='C', code='C', upfront_commission=2, high_trail_commission=2, low_trail_commission=1, is_active=True)
        Lender.objects.create(name='D', code='D', upfront_commission=2, high_trail_commission=2, low_trail_commission=1, is_active=True)
        Lender.objects.create(name='E', code='E', upfront_commission=2, high_trail_commission=2, low_trail_commission=1, is_active=True)
        Lender.objects.create(name='F', code='F', upfront_commission=2, high_trail_commission=2, low_trail_commission=1, is_active=True)
        self.list_url = reverse('lender-list')
        self.detail_url = reverse('lender-detail', args=(self.lender_a.id,))

    def test_create(self):
        self.assertFalse(Lender.objects.filter(name='New Lender').exists())

        data = {
            'attributes': {
                'name': 'New Lender',
                'code': 'NLN',
                'upfront_commission': 5,
                'high_trail_commission': 1,
                'low_trail_commission': 0.5,
                'is_active': 'true',
            },
            'id': None,
            'type': 'lenders',
        }
        response = self.client.post(self.list_url, {'data': data})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Lender.objects.filter(name='New Lender').exists())
        lender = Lender.objects.get(name='New Lender')
        self.assertFalse(lender.is_hidden)
        self.assertEqual(lender.balance_multiplier, Decimal('0'))

    def test_create_bad_data(self):
        self.assertFalse(Lender.objects.filter(name='New Lender').exists())

        data = {
            'attributes': {'name': 'New Lender'},
            'id': None,
            'type': 'lenders',
        }

        response = self.client.post(self.list_url, {})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Lender.objects.filter(name='New Lender').exists())

    def test_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertTrue('self' in data['links'])
        self.assertTrue('first' in data['links'])
        self.assertTrue('last' in data['links'])
        self.assertTrue('next' in data['links'])
        self.assertTrue('prev' in data['links'])
        lender_data = data['data']
        self.assertEqual(len(lender_data), 5)
        self.assertEqual(set(self.fields + ['id']), set(lender_data[0].keys()))

    def test_get_single(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'A')

    def test_update(self):
        self.assertEqual(self.lender_a.name, 'A')
        update_data = {
            'attributes': {
                'name': 'New Lender',
                'code': 'NLN',
                'upfront_commission': 5,
                'high_trail_commission': 1,
                'low_trail_commission': 0.5,
                'is_active': 'false',
            },
            'id': self.lender_a.id,
            'type': 'lenders',
        }
        response = self.client.put(self.detail_url, {'data': update_data})
        self.lender_a.refresh_from_db()
        self.assertEqual(self.lender_a.name, 'New Lender')
        self.assertEqual(self.lender_a.code, 'NLN')
        self.assertEqual(self.lender_a.upfront_commission, Decimal('5'))
        self.assertEqual(self.lender_a.high_trail_commission, Decimal('1'))
        self.assertEqual(self.lender_a.low_trail_commission, Decimal('0.5'))
        self.assertFalse(self.lender_a.is_active)

    def test_update_partial(self):
        self.assertEqual(self.lender_a.name, 'A')
        update_data = {
            'attributes': {'name': 'New Lender'},
            'id': self.lender_a.id,
            'type': 'lenders',
        }
        response = self.client.patch(self.detail_url, {'data': update_data})
        self.lender_a.refresh_from_db()
        self.assertEqual(self.lender_a.name, 'New Lender')
        self.assertEqual(self.lender_a.code, 'A')
        self.assertEqual(self.lender_a.upfront_commission, Decimal('2'))
        self.assertEqual(self.lender_a.high_trail_commission, Decimal('2'))
        self.assertEqual(self.lender_a.low_trail_commission, Decimal('1'))
        self.assertTrue(self.lender_a.is_active)

    def test_delete(self):
        self.assertTrue(Lender.objects.filter(name=self.lender_a.name).exists())
        self.client.delete(self.detail_url)
        self.assertFalse(Lender.objects.filter(name=self.lender_a.name).exists())

    def test_bulk_create(self):
        self.assertFalse(Lender.objects.filter(name='ANZ').exists())
        self.assertFalse(Lender.objects.filter(name='CBA').exists())

        file_name = 'bulk_create.csv'
        with open(file_name, 'w') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(self.fields)
            writer.writerow(['ANZ','ANZ', '1', '1', '0.5', 'true', 'false', '0'])
            writer.writerow(['CBA','CBA', '1', '1', '0.5', 'true', 'false', '0'])

        csv_file = open(file_name, 'rb')
        upload = SimpleUploadedFile(content=csv_file.read(), name=csv_file.name)

        bulk_create_url = reverse('lender-bulk-create')
        response = self.client.post(bulk_create_url, {'file': upload}, format='multipart')
        self.assertEqual(response.status_code, 201)
        lender_data = response.data['data']
        self.assertEqual(len(lender_data), 2)
        self.assertEqual(lender_data[0]['name'], 'ANZ')
        self.assertEqual(lender_data[1]['name'], 'CBA')
        self.assertTrue(Lender.objects.filter(name='ANZ').exists())
        self.assertTrue(Lender.objects.filter(name='CBA').exists())

        os.remove(file_name)

    def test_download_csv(self):
        csv_url = reverse('lender-download-csv')
        response = self.client.get(csv_url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(content))
        lender_data = list(reader)
        self.assertEqual(len(lender_data), 6)
        self.assertEqual(lender_data[0]['name'], 'A')
        self.assertEqual(lender_data[1]['name'], 'B')
        self.assertEqual(lender_data[2]['name'], 'C')
        self.assertEqual(lender_data[3]['name'], 'D')
        self.assertEqual(lender_data[4]['name'], 'E')
        self.assertEqual(lender_data[5]['name'], 'F')
        self.assertEqual(set(self.fields + ['id']), set(lender_data[0].keys()))
