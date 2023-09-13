from http import HTTPStatus


import pytest
from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse
from django.contrib.auth import get_user_model


from news.models import Comment
from news.forms import BAD_WORDS, WARNING

User = get_user_model()
NEW_COMMENT_TEXT = 'Обновлённый комментарий'
COMMENT_TEXT = 'Just text'


@pytest.mark.django_db(True)
def test_anonymous_user_cant_create_comment(client, news, form_data):
    url = reverse('news:detail', args=(news.pk,))
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(author_client, news, author, form_data):
    url = reverse('news:detail', args=(news.pk,))
    author_client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment_for_check = Comment.objects.get()
    assert comment_for_check.text == form_data['text']
    assert comment_for_check.news == news
    assert comment_for_check.author == author


def test_user_cant_use_bad_words(admin_client, news):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=(news.pk,))
    response = admin_client.post(url, data=bad_words_data)
    assertFormError(response, form='form', field='text', errors=WARNING)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client, news, comment):
    url = reverse('news:delete', args=(comment.id,))
    new_url = reverse('news:detail', args=(news.id,))
    url_to_comments = new_url + '#comments'
    response = author_client.delete(url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_edit_comment(author_client, form_data, news, comment):
    new_url = reverse('news:detail', args=(news.id,))
    url_to_comments = new_url + '#comments'
    edit_url = reverse('news:edit', args=(comment.id,))
    form_data = {'text': NEW_COMMENT_TEXT}
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT


def test_user_cant_edit_comment_of_another_user(admin_client, news, author):
    comment = Comment.objects.create(
        news=news, author=author, text=COMMENT_TEXT,
    )
    edit_url = reverse('news:edit', args=(comment.id,))
    form_data = {'text': NEW_COMMENT_TEXT}

    response = admin_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT


def test_user_cant_delete_comment_of_another_user(admin_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    admin_client.delete(url)
    comments_count = Comment.objects.count()
    assert comments_count == 1
