import requests
import util

# このモジュール用のロガーを取得します。
logger = util.get_my_logger(__name__)


def run(
        access_token: str,
        target_file_item_id: str,
        upload_file_path: str) -> dict:
    """SharePoint の既存ファイルを指定して更新します。

    Args:
        access_token (str): Access token
        target_file_item_id (str): 対象ファイルの item-id
        upload_file_path (str): ローカルのファイルパス

    Raises:
        Exception: [description]

    Returns:
        dict: [description]
    """

    url = f'{util.GRAPH_API_URL}/sites/{util.TARGET_SITE_ID}/drive/items/{target_file_item_id}/content'  # noqa: E501
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    binary = open(upload_file_path, 'rb').read()
    res = requests.put(url, headers=headers, data=binary)
    if res.status_code != 200:
        logger.error('アップロードがうまくいかんかった。')
        logger.error(res.status_code)
        # NOTE: resourceLocked とかありえます。
        raise Exception(res.json())
    logger.info('アップロード成功しました。')
    res_json = res.json()
    return res_json


if __name__ == '__main__':
    import get_access_token
    import get_file_info
    access_token = get_access_token.run()
    file_info = get_file_info.run(access_token)
    logger.debug(file_info['id'])
    logger.debug(file_info['name'])
    logger.debug(file_info['@microsoft.graph.downloadUrl'])
