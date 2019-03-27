from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicIngredientsApiTests(TestCase):
    """ Test publically available ingredients API """

    def setUp(self):
        self.client = APIClient()

    def test_login_requried(self):
        """ test that login required for retreiving ingredients """
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code,  status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTest(TestCase):
    """ test ingredient APIs requring authorization """

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test4@fake.com',
            password='testpass123',
            name='not realname0'
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_ingredient_list(self):
        """ test retrieving a list of ingredients """
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_by_user(self):
        """ Test that returned tags are for authed user """
        user2 = get_user_model().objects.create_user(
            'test33@fake.com',
            'password456'
        )
        Ingredient.objects.create(user=user2, name='Vinegar')
        ingredient = Ingredient.objects.create(user=self.user, name='Tumeric')

        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        """ Test creating a new ingredient """
        payload = {'name': 'Cabbage'}
        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_invalid_ingredient_fails(self):
        """ Test that creating an invalid tag will fail"""
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
