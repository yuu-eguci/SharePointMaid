import os
import tempfile

import requests

import copy_xlsx_sheet
import get_access_token
import get_file_info
import put_file
import util


def main() -> None:
    """SharePoint のファイルに来週分のシートを追加してアップロードし直します。"""

    # 必要な環境変数がそろっているか先に確認します。
    util.check_settings()

    # アクセストークン。
    access_token = get_access_token.run()

    # ファイル情報取得。
    file_info = get_file_info.run(access_token)
    file_id = file_info['id']
    # NOTE: パス区切りが混ざっていても一時ディレクトリの外に出ないようにします。
    file_name = os.path.basename(file_info['name'])
    download_url = file_info['@microsoft.graph.downloadUrl']

    # 業務ファイルを手元に残さないよう、一時ディレクトリで処理します。
    with tempfile.TemporaryDirectory() as tmp_dir:
        file_path = os.path.join(tmp_dir, file_name)

        # ファイルダウンロード。
        res = requests.get(download_url, timeout=util.REQUEST_TIMEOUT_SECONDS)
        res.raise_for_status()
        with open(file_path, 'wb') as f:
            f.write(res.content)

        # ファイル書き換え。
        copy_xlsx_sheet.run(file_path)

        # ファイル更新。
        put_file.run(access_token, file_id, file_path)


if __name__ == '__main__':
    main()
