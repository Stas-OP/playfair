from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Text, UserProfile, RequestHistory
from .views import playfair_cipher, prepare_key, generate_random_key

class CipherTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.profile = UserProfile.objects.create(user=self.user)

    def test_prepare_key(self):
        key = "HELLO WORLD"
        prepared_key = prepare_key(key)
        self.assertEqual(prepared_key, "HELOWRDABCFGIKMNPQSTUVXYZ")

    def test_playfair_cipher_encrypt(self):
        key = "KEYWORD"
        plaintext = "HELLO WORLD"
        encrypted = playfair_cipher(key, plaintext, mode='encrypt')
        self.assertNotEqual(encrypted, plaintext)

    def test_playfair_cipher_decrypt(self):
        key = "KEYWORD"
        plaintext = "HELLO WORLD"
        encrypted = playfair_cipher(key, plaintext, mode='encrypt')
        decrypted = playfair_cipher(key, encrypted, mode='decrypt')
        self.assertEqual(decrypted, "HELLOWORLD")

    def test_generate_random_key(self):
        key = generate_random_key()
        self.assertEqual(len(key), 10)
        self.assertTrue(all(c.isupper() and c.isalpha() for c in key))

    def test_register_user(self):
        response = self.client.post(reverse('register_user'), 
                                    {'username': 'newuser', 'password': 'newpassword'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_encrypt_text_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('encrypt_text'), 
                                    {'text': 'HELLO', 'key': 'KEYWORD'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('encrypted', response.json())

    def test_decrypt_text_view(self):
        self.client.login(username='testuser', password='12345')
        encrypted = playfair_cipher('KEYWORD', 'HELLO', mode='encrypt')
        response = self.client.post(reverse('decrypt_text'), 
                                    {'text': encrypted, 'key': 'KEYWORD'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('decrypted', response.json())

    def test_manage_text_create(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('add_text'), 
                                    {'title': 'Test Text', 'content': 'Hello World'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Text.objects.filter(title='Test Text').exists())

    def test_user_history(self):
        self.client.login(username='testuser', password='12345')
        RequestHistory.objects.create(user=self.user, request_type='Шифрование')
        response = self.client.get(reverse('user_history'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['history']), 1)

    def test_change_password(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.patch(reverse('change_password'), 
                                     {'old_password': '12345', 'new_password': 'newpassword'},
                                     content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword'))
