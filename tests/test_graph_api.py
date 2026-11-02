import pytest
from conftest import FakeResponse

import get_access_token
import get_file_info
import get_user_info
import put_file
import util


def test_get_access_token(settings, http_calls):
    calls, responses = http_calls
    responses['post'] = FakeResponse(json_data={'access_token': 'token'})

    assert get_access_token.run() == 'token'

    ((method, url, kwargs),) = calls
    assert method == 'post'
    assert url == (
        'https://login.microsoftonline.com/dummy-tenant_id/oauth2/v2.0/token'
    )
    assert kwargs['data']['client_secret'] == 'dummy-client_secret'
    assert kwargs['timeout'] == util.REQUEST_TIMEOUT_SECONDS


def test_get_access_token_raises_on_error(settings, http_calls):
    _, responses = http_calls
    responses['post'] = FakeResponse(401, {'error': 'invalid_client'})

    with pytest.raises(Exception, match='invalid_client'):
        get_access_token.run()


def test_get_file_info(settings, http_calls):
    calls, responses = http_calls
    responses['get'] = FakeResponse(json_data={'id': 'item-1'})

    assert get_file_info.run('token') == {'id': 'item-1'}

    ((_, url, kwargs),) = calls
    assert url.endswith(
        '/sites/dummy-target_site_id/drive/root:/dummy-target_file_path'
    )
    assert kwargs['headers'] == {'Authorization': 'Bearer token'}
    assert kwargs['timeout'] == util.REQUEST_TIMEOUT_SECONDS


def test_get_file_info_raises_on_error(settings, http_calls):
    _, responses = http_calls
    responses['get'] = FakeResponse(404, {'error': 'itemNotFound'})

    with pytest.raises(Exception, match='itemNotFound'):
        get_file_info.run('token')


def test_get_user_info(settings, http_calls):
    calls, responses = http_calls
    responses['get'] = FakeResponse(json_data={'id': 'user-1'})

    assert get_user_info.run('token') == {'id': 'user-1'}

    ((_, url, kwargs),) = calls
    assert url.endswith('/users/dummy-user_object_id')
    assert kwargs['timeout'] == util.REQUEST_TIMEOUT_SECONDS


def test_put_file_uploads_and_notifies_success(
    settings, http_calls, slack_messages, tmp_path
):
    calls, responses = http_calls
    responses['put'] = FakeResponse(json_data={'id': 'item-1'})
    path = tmp_path / 'book.xlsx'
    path.write_bytes(b'xlsx-bytes')

    assert put_file.run('token', 'item-1', str(path)) == {'id': 'item-1'}

    ((_, url, kwargs),) = calls
    assert url.endswith('/sites/dummy-target_site_id/drive/items/item-1/content')
    assert kwargs['data'] == b'xlsx-bytes'
    assert kwargs['timeout'] == util.REQUEST_TIMEOUT_SECONDS
    assert slack_messages == ['dummy-slack_message_success']


def test_put_file_notifies_failure(settings, http_calls, slack_messages, tmp_path):
    _, responses = http_calls
    responses['put'] = FakeResponse(423, {'error': 'resourceLocked'})
    path = tmp_path / 'book.xlsx'
    path.write_bytes(b'xlsx-bytes')

    with pytest.raises(Exception, match='resourceLocked'):
        put_file.run('token', 'item-1', str(path))

    assert slack_messages == ['dummy-slack_message_failure']
