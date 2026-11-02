import pathlib

import pytest
import requests
from conftest import FakeResponse

import copy_xlsx_sheet
import get_access_token
import get_file_info
import main
import put_file
import util


@pytest.fixture
def pipeline(monkeypatch, settings, http_calls):
    """main から呼ぶ各モジュールを差し替えて、受け取った値を記録します。"""
    calls, responses = http_calls
    record = {'calls': calls, 'responses': responses}
    monkeypatch.setattr(get_access_token, 'run', lambda: 'token')
    monkeypatch.setattr(
        get_file_info,
        'run',
        lambda token: {
            'id': 'item-1',
            'name': 'book.xlsx',
            '@microsoft.graph.downloadUrl': 'https://download.example/book',
        },
    )

    def fake_copy(path):
        record['copied'] = pathlib.Path(path).read_bytes()

    def fake_put(token, item_id, path):
        record['put'] = (token, item_id, pathlib.Path(path))

    monkeypatch.setattr(copy_xlsx_sheet, 'run', fake_copy)
    monkeypatch.setattr(put_file, 'run', fake_put)
    return record


def test_main_downloads_edits_and_uploads_in_temp_dir(pipeline, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    pipeline['responses']['get'] = FakeResponse(content=b'xlsx-bytes')

    main.main()

    ((_, url, kwargs),) = pipeline['calls']
    assert url == 'https://download.example/book'
    assert kwargs['timeout'] == util.REQUEST_TIMEOUT_SECONDS
    assert pipeline['copied'] == b'xlsx-bytes'
    token, item_id, path = pipeline['put']
    assert (token, item_id, path.name) == ('token', 'item-1', 'book.xlsx')
    # 一時ディレクトリは片付けられ、作業ディレクトリにも残りません。
    assert not path.exists()
    assert list(tmp_path.iterdir()) == []


def test_main_stops_when_download_fails(pipeline):
    pipeline['responses']['get'] = FakeResponse(status_code=403)

    with pytest.raises(requests.HTTPError):
        main.main()

    assert 'copied' not in pipeline
    assert 'put' not in pipeline


def test_main_checks_settings_first(monkeypatch):
    for name in util._ENV_SETTINGS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(
        get_access_token, 'run', lambda: pytest.fail('should not be called')
    )

    with pytest.raises(KeyError, match='Missing environment variables'):
        main.main()
