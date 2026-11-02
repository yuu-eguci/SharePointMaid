import pytest
import requests

import util


class FakeResponse:
    def __init__(self, status_code=200, json_data=None, content=b''):
        self.status_code = status_code
        self._json_data = json_data if json_data is not None else {}
        self.content = content

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f'{self.status_code} Error')


@pytest.fixture
def settings(monkeypatch):
    """全ての環境変数をダミー値で設定します。"""
    for name in util._ENV_SETTINGS:
        monkeypatch.setenv(name, f'dummy-{name.lower()}')


@pytest.fixture
def http_calls(monkeypatch):
    """requests の get / post / put を記録して、決めたレスポンスを返します。"""
    calls = []
    responses = {}

    def make(method):
        def fake(url, **kwargs):
            calls.append((method, url, kwargs))
            return responses[method]

        return fake

    for method in ('get', 'post', 'put'):
        monkeypatch.setattr(requests, method, make(method))
    return calls, responses


@pytest.fixture
def slack_messages(monkeypatch):
    messages = []
    monkeypatch.setattr(util, 'send_slack_message', messages.append)
    return messages
