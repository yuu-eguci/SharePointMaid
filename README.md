SharePointMaid
===

A repository to access files on SharePoint site using Graph API, SharePoint REST API v2, by Python.

SharePoint 上の Excel ファイルをダウンロードして、`Format base` シートを複製した「M月第N月曜日」シートを追加し、アップロードし直します。結果は Slack に通知します。

![readme](https://user-images.githubusercontent.com/28250432/102326219-77730300-3fc7-11eb-8a42-8b0b5ae0822a.png)

## ステータス

- Docker: 対応!
- Python: 3.15 (uv で管理)
- Linter / Formatter: Ruff
- テスト: pytest
- 主なライブラリ: requests 2.34 / openpyxl 3.1 / slack-sdk 3.46
- クイックスタート: `docker compose run --rm app uv run pytest`

## 開発

Docker で動かします。

```bash
docker compose build
docker compose run --rm app uv run ruff check .
docker compose run --rm app uv run ruff format --check .
docker compose run --rm app uv run pytest
```

ローカルに uv があれば `uv sync` してから同じコマンドを `uv run ...` で動かせます。

## 本番実行

`.env` を作ってから実行します。実際に SharePoint のファイルを更新して Slack に送信するので注意してください。

```
TENANT_ID=***
CLIENT_ID=***
CLIENT_SECRET=***
USER_OBJECT_ID=***
TARGET_SITE_ID=***
TARGET_FILE_PATH=***
SLACK_BOT_TOKEN=***
SLACK_MESSAGE_CHANNEL=***
SLACK_MESSAGE_SUCCESS=***
SLACK_MESSAGE_FAILURE=***
```

```bash
docker compose run --rm app
```

- ダウンロードしたファイルは一時ディレクトリで処理して、終わったら消します。
- 通信は 60 秒でタイムアウトします。
- `python util.py` で設定を確認できます。シークレットとトークンはマスクして表示します。

GitHub Actions の `pythonapp.yml` は同じ処理を週 1 回動かすワークフローです。いまは手動で無効にしてあります。

## Microsoft Entra ID アプリの準備

- グローバル管理者ロールがあるか確認します。
- Microsoft Entra ID を開きます。
- 左ペインの App registrations > New registration でアプリを作ります。
- 左ペインの API permissions > Add permission で Microsoft Graph のアプリケーション権限を追加します。
    - `Sites.ReadWrite.All`: ファイルの取得と更新に使います。
    - `User.Read.All`: `get_user_info.py` を使うときだけ追加します。
    - Grant admin consent for TENANT_NAME を押します。
- 左ペインの Certificates & secrets > + New client secret でシークレットを作ります。

これで次の値がそろいます。環境変数に登録してください。

- TENANT_ID
- CLIENT_ID
- CLIENT_SECRET

## 参考リンク

- [SharePoint APIs](https://learn.microsoft.com/ja-jp/sharepoint/dev/sp-add-ins/sharepoint-net-server-csom-jsom-and-rest-api-index)
- [Graph REST API v1.0](https://learn.microsoft.com/ja-jp/graph/api/overview?view=graph-rest-1.0) (このリポジトリで使っている API)
- [Graph Explorer](https://developer.microsoft.com/ja-jp/graph/graph-explorer) (Graph API をブラウザで試せます)
