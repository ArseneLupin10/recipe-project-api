"""
Test for the ingrediants API
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingrediant
from recipe.serializers import IngrediantSerializer


INGREDIANT_URL = reverse('recipe:ingrediant-list')

def detail_url(ingrediant_id):
    """Create and return an Ingrediant detai url"""
    return reverse('recipe:ingrediant-detail', args=[ingrediant_id])

def create_user(email='user@example.com', password='testpass123'):
    """Create and return user"""
    return get_user_model().objects.create_user(email=email, password=password)


class publicIngrediantsApiTests(TestCase):
    """Test unauthorized API requests"""

    def setUp(self):
        self.client=APIClient()

    def test_auth_required(self):
        """Test auth is required for retreiving ingrediants"""
        res = self.client.get(INGREDIANT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngrediantsApiTests(TestCase):
    """Test authorized API requests"""

    def setUp(self):
        self.client=APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingrediants(self):
        """Test retreiving a list of ingrediants"""

        Ingrediant.objects.create(user=self.user, name='Kale')
        Ingrediant.objects.create(user=self.user, name='Vanilla')

        ingrediants = Ingrediant.objects.all().order_by('-name')
        serializer = IngrediantSerializer(ingrediants, many=True)
        res = self.client.get(INGREDIANT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_ingredients_limited_to_user(self):
        """Test list of ingrediants limited to authenticated user"""
        user = create_user(email='user2@example.com')
        Ingrediant.objects.create(user=user, name='Salt')
        ingrediant = Ingrediant.objects.create(user=self.user, name='Pepper')
        res = self.client.get(INGREDIANT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingrediant.name)
        self.assertEqual(res.data[0]['id'], ingrediant.id)


    def test_update_ingrediant(self):
        """Test updating an ingrediant"""

        ingrediant = Ingrediant.objects.create(user=self.user, name='Cilantro')
        payload = {'name': 'Coriander'}
        url = detail_url(ingrediant.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingrediant.refresh_from_db()
        self.assertEqual(ingrediant.name, payload['name'])

    def test_delete_ingrediant(self):
        """Test deleting an ingrediant"""

        ingrediant = Ingrediant.objects.create(user=self.user, name='lettuce')
        url = detail_url(ingrediant.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingrediants = Ingrediant.objects.filter(user=self.user)
        self.assertFalse(ingrediants.exists())
