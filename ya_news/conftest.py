from datetime import timedelta


import pytest
from django.utils import timezone


from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news(author):
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
        date='2023-04-23',
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='text',
    )
    return comment


@pytest.fixture
def list_comments(news, author):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now - timedelta(days=index)
        comment.save()


@pytest.fixture
def pk(news):
    return news.pk,


@pytest.fixture
def pk_comment(comment):
    return comment.pk,


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст',
    }
