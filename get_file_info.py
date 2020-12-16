import requests
import util

# このモジュール用のロガーを取得します。
logger = util.get_my_logger(__name__)


def run(access_token: str) -> dict:
    """SharePoint ファイルの情報を取得します。

    Args:
        access_token (str): Access token

    Raises:
        Exception: Failed to get file info

    Returns:
        dict: File info
    """

    url = f'{util.GRAPH_API_URL}/sites/{util.TARGET_SITE_ID}/drive/root:/{util.TARGET_FILE_PATH}'  # noqa: E501
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        logger.error('ファイル情報取得がうまくいかんかった。')
        logger.error(res.status_code)
        # NOTE: グローバル管理者の許可がないときは code Authorization_RequestDenied が出ます。
        raise Exception(res.json())
    logger.info('ファイル情報の取得成功しました。')
    res_json = res.json()
    return res_json


if __name__ == '__main__':
    import get_access_token
    access_token = get_access_token.run()
    file_info = run(access_token)
    logger.debug(file_info['id'])
    logger.debug(file_info['name'])
    logger.debug(file_info['@microsoft.graph.downloadUrl'])
