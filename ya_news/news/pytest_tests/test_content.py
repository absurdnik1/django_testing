from datetime import datetime, timedelta


import pytest
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model


from news.models import News

User = get_user_model()
NEWS_COUNT_ON_HOME_PAGE = 10


@pytest.mark.django_db(True)
def test_news_count(client):
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count <= NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db(True)
def test_news_order(client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('pk')),
    )
)
def test_comments_order(client, name, args, list_comments):
    url = reverse(name, args=args)
    response = client.get(url)
    assert 'news' in response.context
    all_comments = response.context['news'].comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('pk')),
    )
)
def test_anonymous_client_has_no_form(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('pk')),
    )
)
def test_authorized_client_has_form(admin_client, name, args):
    url = reverse(name, args=args)
    response = admin_client.get(url)
    assert 'form' in response.context
