import requests
import util

# このモジュール用のロガーを取得します。
logger = util.get_my_logger(__name__)


def run() -> str:
    """Graph API 用のアクセストークンを取得します。
    参考: https://qiita.com/massie_g/items/fe7540161aa4a5f86bf5#アクセストークンの取得

    Returns:
        str: Access token
    """

    url = ('https://login.microsoftonline.com'
           f'/{util.TENANT_ID}/oauth2/v2.0/token')
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    payload = {
        'client_id': util.CLIENT_ID,
        'scope': 'https://graph.microsoft.com/.default',
        'client_secret': util.CLIENT_SECRET,
        'grant_type': 'client_credentials',
    }
    res = requests.post(url, headers=headers, data=payload)
    if res.status_code != 200:
        logger.error('アクセストークンの取得がうまくいかんかった。')
        logger.error(res.status_code)
        raise Exception(res.json())
    logger.info('アクセストークンの取得成功しました。')
    res_json = res.json()
    access_token = res_json['access_token']
    return access_token


if __name__ == '__main__':
    logger.debug(run())
