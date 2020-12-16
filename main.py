import requests
import get_access_token
import get_file_info
import copy_xlsx_sheet
import put_file

# アクセストークン。
access_token = get_access_token.run()

# ファイル情報取得。
file_info = get_file_info.run(access_token)
file_id = file_info['id']
file_name = file_info['name']
download_url = file_info['@microsoft.graph.downloadUrl']

# ファイルダウンロード。
res = requests.get(download_url)
with open(f'./{file_name}', 'wb') as f:
    f.write(res.content)

# ファイル書き換え。
copy_xlsx_sheet.run(f'./{file_name}')

# ファイル更新。
put_file.run(access_token, file_id, f'./{file_name}')
