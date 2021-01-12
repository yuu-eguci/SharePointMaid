import os
import logging
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
        # NOTE: 改行は逆に見づらいので E501 を無視します。
        '%(asctime)s - %(levelname)s - %(filename)s - %(name)s - %(funcName)s - %(message)s')  # noqa: E501
    handler.setFormatter(formatter)
    # ハンドラをロガーへセットします。
    logger.addHandler(handler)
    # 親ロガーへの(伝播をオフにします。
    logger.propagate = False
    return logger


def send_slack_message(message: str) -> None:

    slack_client = WebClient(token=SLACK_BOT_TOKEN)

    try:
        response = slack_client.chat_postMessage(
            channel='#mailbox_yuu-eguci', text=message)
        assert response['message']['text'] == message
    except SlackApiError as e:
        assert e.response['ok'] is False
        # str like 'invalid_auth', 'channel_not_found'
        assert e.response['error']
        print(f'Got an error: {e.response["error"]}')


# Directory (tenant) ID: AAD app overview で取得可能。
TENANT_ID = get_env('TENANT_ID')
# Application (client) ID: 同上。
CLIENT_ID = get_env('CLIENT_ID')
# Certificates & secrets で取得可能。
CLIENT_SECRET = get_env('CLIENT_SECRET')
# Object ID: AAD Users で取得可能。
USER_OBJECT_ID = get_env('USER_OBJECT_ID')
# アクセスする SharePoint site の site-id: Graph Explorer で site を検索することで取得可能。
TARGET_SITE_ID = get_env('TARGET_SITE_ID')
# Maid に取得させる SharePoint site 内ファイルのパス。
# SharePoint サイトにおける Shared%20Documents より下のパスを書く。例: FILE-STORAGE/sample.xlsx
TARGET_FILE_PATH = get_env('TARGET_FILE_PATH')
# Graph API の url。
GRAPH_API_URL = 'https://graph.microsoft.com/v1.0'
# python-slack-sdk 用のアクセストークン。
SLACK_BOT_TOKEN = get_env('SLACK_BOT_TOKEN')
# 成功時の Slack メッセージ。
SLACK_MESSAGE_SUCCESS = get_env('SLACK_MESSAGE_SUCCESS')
# 失敗時の Slack メッセージ。
SLACK_MESSAGE_FAILURE = get_env('SLACK_MESSAGE_FAILURE')

if __name__ == '__main__':
    logger = get_my_logger(__name__)
    logger.critical(repr(TENANT_ID))
    logger.error(repr(CLIENT_ID))
    logger.warning(repr(CLIENT_SECRET))
    logger.info(repr(USER_OBJECT_ID))
    logger.debug(repr(TARGET_SITE_ID))
    logger.debug(repr(TARGET_FILE_PATH))
    logger.debug(repr(GRAPH_API_URL))
    logger.debug(repr(SLACK_BOT_TOKEN))
    logger.debug(repr(SLACK_MESSAGE_SUCCESS))
    logger.debug(repr(SLACK_MESSAGE_FAILURE))
