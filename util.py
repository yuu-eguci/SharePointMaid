import logging
import os

import dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# .env で環境変数を取得する場合に対応します。
# raise_error_if_not_found: .env が見つからなくてもエラーを起こさない。
dotenv.load_dotenv(dotenv.find_dotenv(raise_error_if_not_found=False))


def get_env(keyname: str) -> str:
    """環境変数を取得します。
    GitHub Actions では環境変数が設定されていなくても yaml 内で空文字列が入ってしまう。空欄チェックも行います。

    Arguments:
        keyname {str} -- 環境変数名。

    Raises:
        KeyError: 環境変数が見つからない。

    Returns:
        str -- 環境変数の値。
    """
    _ = os.environ[keyname]
    if not _:
        raise KeyError(f'{keyname} is empty.')
    return _


def get_my_logger(logger_name: str) -> logging.Logger:
    """モジュール用のロガーを作成します。

    Args:
        logger_name (str): getLogger にわたす名前。 __name__ を想定しています。

    Returns:
        logging.Logger: モジュール用のロガー。
    """

    """
    メインの処理とは別に関係ない。

    Returns:
        Logger -- モジュール用のロガー。
    """

    # ルートロガーを作成します。ロガーはモジュールごとに分けるもの。
    logger = logging.getLogger(logger_name)
    # ルートロガーのログレベルは DEBUG。
    logger.setLevel(logging.DEBUG)
    # コンソールへ出力するハンドラを作成。
    handler = logging.StreamHandler()
    # ハンドラもログレベルを持ちます。
    handler.setLevel(logging.DEBUG)
    # ログフォーマットをハンドラに設定します。
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s - %(name)s - %(funcName)s - %(message)s'
    )
    handler.setFormatter(formatter)
    # ハンドラをロガーへセットします。
    logger.addHandler(handler)
    # 親ロガーへの(伝播をオフにします。
    logger.propagate = False
    return logger


# このモジュール用のロガーを取得します。
logger = get_my_logger(__name__)


def send_slack_message(message: str) -> None:
    """slack_sdk を用いたメッセージ送信を行います。
    Document: https://github.com/slackapi/python-slack-sdk/blob/main/tutorial/01-creating-the-slack-app.md

    Args:
        message (str): 送信したいメッセージ。
    """

    slack_client = WebClient(token=get_env('SLACK_BOT_TOKEN'))

    try:
        # NOTE: unfurl_links は時折鬱陶しいと思っている「リンクの展開機能」です。不要です。 False.
        slack_client.chat_postMessage(
            channel=get_env('SLACK_MESSAGE_CHANNEL'), text=message, unfurl_links=False
        )
        # 返却値の確認は行いません。
        # NOTE: Slack api のドキュメントにあるコードなので追加していましたが排除します。
        #       リンクの含まれるメッセージを送信すると、返却値が勝手に変更されるため絶対一致しないからです。
        #       - リンクの前後に <, > がつく
        #       - & -> &amp; エスケープが起こる
        # assert response['message']['text'] == message
    except SlackApiError as e:
        assert e.response['ok'] is False
        # str like 'invalid_auth', 'channel_not_found'
        assert e.response['error']
        logger.error(f'Got an error: {e.response["error"]}')


# Graph API の url。
GRAPH_API_URL = 'https://graph.microsoft.com/v1.0'

# 環境変数から読む設定です。 util.TENANT_ID のように参照したときに読み込みます。
# import しただけでは環境変数を要求しないので、テストから import できます。
_ENV_SETTINGS = (
    # Directory (tenant) ID: Entra ID アプリの Overview で取得可能。
    'TENANT_ID',
    # Application (client) ID: 同上。
    'CLIENT_ID',
    # Certificates & secrets で取得可能。
    'CLIENT_SECRET',
    # Object ID: Entra ID の Users で取得可能。
    'USER_OBJECT_ID',
    # アクセスする SharePoint site の site-id: Graph Explorer で site を検索することで取得可能。
    'TARGET_SITE_ID',
    # Maid に取得させる SharePoint site 内ファイルのパス。
    # SharePoint サイトにおける Shared%20Documents より下のパスを書く。例: FILE-STORAGE/sample.xlsx
    'TARGET_FILE_PATH',
    # python-slack-sdk 用のアクセストークン。
    'SLACK_BOT_TOKEN',
    # Slack メッセージを送信する channel。
    'SLACK_MESSAGE_CHANNEL',
    # 成功時の Slack メッセージ。
    'SLACK_MESSAGE_SUCCESS',
    # 失敗時の Slack メッセージ。
    'SLACK_MESSAGE_FAILURE',
)


def __getattr__(name: str) -> str:
    if name in _ENV_SETTINGS:
        return get_env(name)
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')


def check_settings() -> None:
    """必要な環境変数がそろっているか、処理を始める前にまとめて確認します。

    Raises:
        KeyError: 未設定か空の環境変数がある。
    """

    missing = [name for name in _ENV_SETTINGS if not os.environ.get(name)]
    if missing:
        raise KeyError(f'Missing environment variables: {", ".join(missing)}')


if __name__ == '__main__':
    logger.debug(repr(GRAPH_API_URL))
    for name in _ENV_SETTINGS:
        logger.debug(f'{name}: {get_env(name)!r}')
