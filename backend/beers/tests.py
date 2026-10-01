from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Brand, Beer
from .serializers import BeerSerializer


class BrandModelTests(TestCase):
    def setUp(self):
        self.brand = Brand.objects.create(name='Guinness', country='Irlanda', founded_year=1759)

    def test_str_returns_name(self):
        self.assertEqual(str(self.brand), 'Guinness')

    def test_name_is_unique(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Brand.objects.create(name='Guinness')


class BeerModelTests(TestCase):
    def setUp(self):
        self.brand = Brand.objects.create(name='Guinness')
        self.beer = Beer.objects.create(name='Draught', brand=self.brand, alcohol_content='4.20')

    def test_str_includes_brand(self):
        self.assertEqual(str(self.beer), 'Draught (Guinness)')

    def test_defaults(self):
        self.assertTrue(self.beer.is_active)
        self.assertEqual(self.beer.beer_type, 'lager')
        self.assertIsNotNone(self.beer.created_at)
        self.assertIsNotNone(self.beer.updated_at)

    def test_deleting_brand_deletes_its_beers(self):
        self.brand.delete()
        self.assertEqual(Beer.objects.count(), 0)

    def test_related_name_returns_beers(self):
        self.assertEqual(list(self.brand.beers.all()), [self.beer])


class BrandAPITests(APITestCase):
    def setUp(self):
        self.brand = Brand.objects.create(name='Guinness', country='Irlanda', founded_year=1759)
        Beer.objects.create(name='Draught', brand=self.brand, alcohol_content='4.20')
        Beer.objects.create(name='Extra Stout', brand=self.brand, alcohol_content='5.60', is_active=False)

    def test_list_returns_paginated_payload(self):
        response = self.client.get(reverse('brand-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['beers_count'], 2)

    def test_create(self):
        response = self.client.post(
            reverse('brand-list'),
            {'name': 'Asahi', 'country': 'Japon', 'founded_year': 1889},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Brand.objects.filter(name='Asahi').exists())

    def test_create_without_name_returns_400(self):
        response = self.client.post(reverse('brand-list'), {'country': 'Japon'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_detail_and_partial_update(self):
        url = reverse('brand-detail', args=[self.brand.id])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)

        response = self.client.patch(url, {'country': 'Irlanda'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['country'], 'Irlanda')
        self.assertEqual(response.data['name'], 'Guinness')

    def test_search_filter(self):
        response = self.client.get(reverse('brand-list'), {'search': 'guin'})
        self.assertEqual(response.data['count'], 1)

        response = self.client.get(reverse('brand-list'), {'search': 'no-existe'})
        self.assertEqual(response.data['count'], 0)

    def test_beers_action_returns_only_active_beers(self):
        response = self.client.get(reverse('brand-beers', args=[self.brand.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([beer['name'] for beer in response.data], ['Draught'])

    def test_delete(self):
        url = reverse('brand-detail', args=[self.brand.id])

        self.assertEqual(self.client.delete(url).status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Brand.objects.filter(id=self.brand.id).exists())


class BeerAPITests(APITestCase):
    def setUp(self):
        self.brand = Brand.objects.create(name='Guinness')
        self.other_brand = Brand.objects.create(name='Asahi')
        self.beer = Beer.objects.create(
            name='Draught',
            brand=self.brand,
            beer_type='lager',
            alcohol_content='4.20',
            ibu=30,
        )
        self.ipa = Beer.objects.create(
            name='Hoppy',
            brand=self.other_brand,
            beer_type='ipa',
            alcohol_content='6.00',
            ibu=60,
        )

    def payload(self, **overrides):
        data = {
            'name': 'New Beer',
            'brand': self.brand.id,
            'beer_type': 'ale',
            'alcohol_content': '5.00',
            'ibu': 25,
        }
        data.update(overrides)
        return data

    def test_list_includes_brand_name(self):
        response = self.client.get(reverse('beer-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertIn('brand_name', response.data['results'][0])

    def test_create(self):
        response = self.client.post(reverse('beer-list'), self.payload(), format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['brand_name'], 'Guinness')
        self.assertEqual(Beer.objects.count(), 3)

    def test_create_requires_name(self):
        response = self.client.post(reverse('beer-list'), self.payload(name=''), format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_create_rejects_unknown_brand(self):
        response = self.client.post(reverse('beer-list'), self.payload(brand=9999), format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('brand', response.data)

    def test_create_rejects_invalid_alcohol_content(self):
        response = self.client.post(
            reverse('beer-list'), self.payload(alcohol_content='120'), format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('alcohol_content', response.data)

    def test_create_rejects_negative_ibu(self):
        response = self.client.post(reverse('beer-list'), self.payload(ibu=-5), format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('ibu', response.data)

    def test_filter_by_type_and_brand(self):
        response = self.client.get(reverse('beer-list'), {'beer_type': 'ipa'})
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Hoppy')

        response = self.client.get(reverse('beer-list'), {'brand': self.other_brand.id})
        self.assertEqual(response.data['count'], 1)

        response = self.client.get(reverse('beer-list'), {'brand_id': self.other_brand.id})
        self.assertEqual(response.data['count'], 1)

    def test_filter_by_is_active(self):
        Beer.objects.filter(id=self.ipa.id).update(is_active=False)

        response = self.client.get(reverse('beer-list'), {'is_active': 'true'})
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Draught')

    def test_search_filter(self):
        response = self.client.get(reverse('beer-list'), {'search': 'hoppy'})
        self.assertEqual(response.data['count'], 1)

        response = self.client.get(reverse('beer-list'), {'search': 'guinness'})
        self.assertEqual(response.data['count'], 1)

    def test_ordering(self):
        response = self.client.get(reverse('beer-list'), {'ordering': '-ibu'})
        self.assertEqual(response.data['results'][0]['name'], 'Hoppy')

    def test_types_action(self):
        response = self.client.get(reverse('beer-types'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn({'value': 'ipa', 'label': 'IPA'}, response.data)

    def test_update_and_delete(self):
        url = reverse('beer-detail', args=[self.beer.id])

        response = self.client.patch(url, {'name': 'Draught Special'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.beer.refresh_from_db()
        self.assertEqual(self.beer.name, 'Draught Special')

        self.assertEqual(self.client.delete(url).status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Beer.objects.filter(id=self.beer.id).exists())


class BeerSerializerTests(TestCase):
    def test_valid_payload(self):
        brand = Brand.objects.create(name='Guinness')
        serializer = BeerSerializer(data={'name': 'Draught', 'brand': brand.id, 'alcohol_content': '4.20'})

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_alcohol_content_above_limit(self):
        serializer = BeerSerializer(data={'name': 'X', 'brand': 1, 'alcohol_content': '101'})

        self.assertFalse(serializer.is_valid())
        self.assertIn('alcohol_content', serializer.errors)

    def test_negative_ibu(self):
        serializer = BeerSerializer(data={'name': 'X', 'brand': 1, 'alcohol_content': '4.20', 'ibu': -1})

        self.assertFalse(serializer.is_valid())
        self.assertIn('ibu', serializer.errors)
