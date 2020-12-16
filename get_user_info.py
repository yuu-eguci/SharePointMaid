import requests
import util

# このモジュール用のロガーを取得します。
logger = util.get_my_logger(__name__)


def run(access_token: str) -> dict:
    """Graph API 用のアクセストークンを取得します。

    Args:
        access_token (str): Access token

    Raises:
        Exception: Failed to get user info

    Returns:
        dict: User info
    """

    url = f'{util.GRAPH_API_URL}/users/{util.USER_OBJECT_ID}'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        logger.error('ユーザ情報の取得がうまくいかんかった。')
        logger.error(res.status_code)
        # NOTE: グローバル管理者の許可がないときは code Authorization_RequestDenied が出ます。
        raise Exception(res.json())
    logger.info('ユーザ情報の取得成功しました。')
    res_json = res.json()
    return res_json


if __name__ == '__main__':
    import get_access_token
    access_token = get_access_token.run()
    logger.debug(run(access_token))
