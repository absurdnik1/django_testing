from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client


from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Просто автор')
        cls.note = Note.objects.create(title='Заголовок', text='Текст',
                                       author=cls.author)
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

    def test_notes_list_for_different_users(self):
        urls = ((self.author_client, True),
                (self.auth_client, False),
                )

        for name, args in urls:
            with self.subTest(name=name, args=args):
                url = reverse('notes:list')
                response = name.get(url)
                object_list = response.context['object_list']
                self.assertEqual(self.note in object_list, args)

    def test_pages_contains_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
