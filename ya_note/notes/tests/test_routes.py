from http import HTTPStatus


from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.test import Client


from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Просто автор')
        cls.note = Note.objects.create(title='Заголовок', text='Текст',
                                       author=cls.author)
        cls.reader = User.objects.create(username='Читатель простой')
        cls.user = User.objects.create(username='Просто юзер')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        urls = (('notes:edit', (self.note.slug,)),
                ('notes:delete', (self.note.slug,)),
                ('notes:detail', (self.note.slug,)),
                ('notes:list', None),
                ('notes:success', None),
                ('notes:add', None),
                )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.reader_client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_pages_availability_for_author(self):
        urls = (
            ('notes:detail', self.note.slug,),
            ('notes:edit', self.note.slug,),
            ('notes:delete', self.note.slug,),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=(args,))
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_avialability_for_auth_user(self):
        urls = ('notes:list', 'notes:add', 'notes:success',)

        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_avialibility_for_anonymous_user(self):
        urls = ('notes:home', 'users:login', 'users:logout', 'users:signup')
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
