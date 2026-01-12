from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from rest_framework import status
from core.models import Family, Parent


class AuthenticationAPITests(APITestCase):
    """Tests for authentication endpoints"""

    def setUp(self):
        """Set up test client"""
        self.client = APIClient()

    def test_register_new_parent(self):
        """Test registering a new parent account"""
        data = {
            "email": "newparent@test.com",
            "password": "securepass123",
            "name": "New Parent",
            "family_name": "New Family"
        }
        response = self.client.post('/api/auth/register/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('parent', response.data)
        self.assertEqual(response.data['parent']['email'], 'newparent@test.com')

        # Verify user was created
        self.assertTrue(User.objects.filter(email='newparent@test.com').exists())

        # Verify family was created
        self.assertTrue(Family.objects.filter(name='New Family').exists())

        # Verify parent was created
        self.assertTrue(Parent.objects.filter(email='newparent@test.com').exists())

    def test_register_duplicate_email(self):
        """Test registering with duplicate email fails"""
        User.objects.create_user(username='existing@test.com', email='existing@test.com')

        data = {
            "email": "existing@test.com",
            "password": "securepass123",
            "name": "Test",
            "family_name": "Test Family"
        }
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        """Test successful login"""
        # Create user
        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )
        family = Family.objects.create(name="Test Family")
        Parent.objects.create(
            email='test@example.com',
            name='Test Parent',
            family=family
        )

        # Login
        data = {
            "email": "test@example.com",
            "password": "testpass123"
        }
        response = self.client.post('/api/auth/login/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('parent', response.data)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {
            "email": "nonexistent@test.com",
            "password": "wrongpassword"
        }
        response = self.client.post('/api/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout(self):
        """Test logout endpoint"""
        # Create user and token
        user = User.objects.create_user(username='test@test.com', password='test123')
        token = Token.objects.create(user=user)

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        # Logout
        response = self.client.post('/api/auth/logout/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify token was deleted
        self.assertFalse(Token.objects.filter(key=token.key).exists())
