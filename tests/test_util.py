import logging

import pytest

import util


def test_get_env_returns_value(monkeypatch):
    monkeypatch.setenv('TENANT_ID', 'tenant')
    assert util.get_env('TENANT_ID') == 'tenant'


def test_get_env_raises_when_missing(monkeypatch):
    monkeypatch.delenv('TENANT_ID', raising=False)
    with pytest.raises(KeyError):
        util.get_env('TENANT_ID')


def test_get_env_raises_when_empty(monkeypatch):
    # GitHub Actions では未設定の secret が空文字列になります。
    monkeypatch.setenv('TENANT_ID', '')
    with pytest.raises(KeyError, match='TENANT_ID is empty'):
        util.get_env('TENANT_ID')


def test_settings_are_read_lazily(monkeypatch):
    monkeypatch.setenv('TARGET_SITE_ID', 'site-1')
    assert util.TARGET_SITE_ID == 'site-1'
    monkeypatch.setenv('TARGET_SITE_ID', 'site-2')
    assert util.TARGET_SITE_ID == 'site-2'


def test_unknown_attribute_raises_attribute_error():
    with pytest.raises(AttributeError):
        _ = util.NOT_A_SETTING


def test_graph_api_url_is_constant():
    assert util.GRAPH_API_URL == 'https://graph.microsoft.com/v1.0'


def test_get_my_logger_does_not_propagate():
    logger = util.get_my_logger('test_util_logger')
    assert isinstance(logger, logging.Logger)
    assert logger.propagate is False


def test_send_slack_message_uses_env_settings(monkeypatch):
    monkeypatch.setenv('SLACK_BOT_TOKEN', 'xoxb-test')
    monkeypatch.setenv('SLACK_MESSAGE_CHANNEL', '#maid')
    calls = []

    class FakeWebClient:
        def __init__(self, token):
            calls.append(('init', token))

        def chat_postMessage(self, **kwargs):
            calls.append(('post', kwargs))

    monkeypatch.setattr(util, 'WebClient', FakeWebClient)

    util.send_slack_message('hello')

    assert calls == [
        ('init', 'xoxb-test'),
        ('post', {'channel': '#maid', 'text': 'hello', 'unfurl_links': False}),
    ]


def test_check_settings_passes_when_all_set(monkeypatch):
    for name in util._ENV_SETTINGS:
        monkeypatch.setenv(name, 'value')
    util.check_settings()


def test_check_settings_reports_all_missing(monkeypatch):
    for name in util._ENV_SETTINGS:
        monkeypatch.setenv(name, 'value')
    monkeypatch.delenv('CLIENT_SECRET')
    monkeypatch.setenv('SLACK_BOT_TOKEN', '')
    with pytest.raises(KeyError, match='CLIENT_SECRET, SLACK_BOT_TOKEN'):
        util.check_settings()


def test_masked_settings_hides_secrets(settings):
    masked = util.masked_settings()

    assert masked['TENANT_ID'] == 'dummy-tenant_id'
    assert masked['CLIENT_SECRET'] == '***'
    assert masked['SLACK_BOT_TOKEN'] == '***'
    assert 'dummy-client_secret' not in repr(masked)


def test_masked_settings_shows_missing(monkeypatch, settings):
    monkeypatch.delenv('CLIENT_SECRET')
    monkeypatch.setenv('TENANT_ID', '')

    masked = util.masked_settings()

    assert masked['CLIENT_SECRET'] == '(未設定)'
    assert masked['TENANT_ID'] == '(未設定)'


def test_get_my_logger_does_not_duplicate_handlers():
    first = util.get_my_logger('test_util_dup_logger')
    second = util.get_my_logger('test_util_dup_logger')

    assert first is second
    assert len(second.handlers) == 1


def test_send_slack_message_logs_api_error(monkeypatch, settings):
    class FakeWebClient:
        def __init__(self, token):
            pass

        def chat_postMessage(self, **kwargs):
            raise util.SlackApiError('error', {'ok': False, 'error': 'invalid_auth'})

    monkeypatch.setattr(util, 'WebClient', FakeWebClient)
    errors = []
    monkeypatch.setattr(util.logger, 'error', errors.append)

    util.send_slack_message('hello')

    assert errors == ['Got an error: invalid_auth']
