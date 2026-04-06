# lastfm_ranking

Last.fm の API を使って指定ユーザーのトップトラック（ランキング）を取得し、ツイート用のテキストを生成するシンプルな Python スクリプト群です。

主に個人用の自動投稿やランキング確認用に想定されています。

## 経緯
昔作ったランキングなうぷれをリファクタリングした記念でGithubに上げました。


---

## 概要

- スクリプト: `lastfm_lanking.py`
- 機能: Last.fm API を叩いてトップトラックを取得し、ランキング形式のテキスト（ツイート用）を標準出力に出力します。
- 出力例（例示）:  
  {ニックネーム}の今週ランキング {TAG} #NowPlaying  
  1. [再生回数回] 曲名
  🎤アーティスト名
  2. ...

---

## 前提条件

- Python 3.8 以上を推奨
- Last.fm API キーを取得済みであること。[last.fm API](https://www.last.fm/api/account/create)より取得してください
- ネットワーク接続があること

---

## セットアップ

1. レポジトリをクローン／取得する
2. 仮想環境を作成して有効化（任意だが推奨）
3. 依存パッケージをインストールする:

- 依存関係は `requirements.txt` に記載されています。インストールは次を実行してください。:
  `pip install -r requirements.txt`

---

## 環境変数

スクリプトは環境変数から API キーやユーザー名を読み込みます。`.env`（dotenv）を使う想定です。

必須環境変数:
- `API_KEY` — Last.fm の API キー
- `USER_NAME` — Last.fm のユーザー名

例（プロジェクトルートに `.env` を作る）:
`API_KEY=your_lastfm_api_key`
`USER_NAME=your_lastfm_username`
`NICKNAME=your_nickname`

---

## 実行方法

プロジェクトルートで次を実行します:
```powershell
$env:PYTHONUTF8=1
```

```bash
export PYTHONUTF8=1
```

`python lastfm_lanking.py`


実行すると標準出力に生成されたランキングテキストが表示されます。  
ログは `lastfm_ranking.log` に出力されます。

## Misskey使用例(bash)
```bash
# 環境変数
INSTALL_DIR=/path/to/repo/root # 例: /home/user/repo
MISSKEY_API=your_misskey_api_key # 例: 1234567890abcdef1234567890abcdef12345678
MISSKEY_URL=your_misskey_instance_url # 例: https://misskey.io
VISIBLE=public # 例: public, followers, specified
export PYTHONUTF8=1

# セットアップ
sudo apt update
sudo apt -y install jq curl python3-venv

cd $INSTALL_DIR
git clone https://github.com/letwir/lastfm_ranking.git
python -m venv lastfm_ranking/.venv
. $INSTALL_DIR/.venv/bin/activate
pip install -r $INSTALL_DIR/lastfm_ranking/requirements.txt

# スクリプト実行と Misskey への投稿
$INSTALL_DIR/.venv/bin/python3 $INSTALL_DIR/lastfm_ranking/lastfm_ranking.py | jq -Rs '{i: "$MISSKEY_API", text: ., visibility: "$VISIBLE"}' | curl -X POST -H "Content-Type: application/json" -d @- $MISSKEY_URL/api/notes/create
```
---

## ランキング期間の自動判定ロジック

スクリプトは実行日（今日の日付）に応じて取得する期間（period）を自動で決定します:

- 年末（12月23日〜12月31日）: 過去12ヶ月のランキング（`period = "12month"`、見出し = `今年`）
- 毎月23日〜31日: 過去1ヶ月のランキング（`period = "1month"`、見出し = `今月`）
- それ以外: 直近1週間のランキング（`period = "7day"`、見出し = `今週`）

この判定は `lastfm_lanking.py` 内の条件分岐で行われています。

---

## 出力と整形

- 出力テキストは Unicode 正規化（NFKC）され、曲名・アーティスト名・再生回数を整形して結合します。
- `LIMIT`（デフォルト 5）で上位何位まで取得するかを制御しています。
- 生成テキストの長さ調整ロジックにより、ツイート向けの文字数（約 500 文字を目安）に調整されます。

---

## ログ

- ログファイル: `lastfm_ranking.log`
- デバッグやエラーはファイルに出力されます。

---

## トラブルシューティング

- API からの応答が 200 以外の場合はスクリプトが終了し、ログに詳細が残ります。
- `API_KEY` や `USER_NAME` が設定されていない場合は正しい値を `.env` に設定してください。
- ネットワーク接続や Last.fm サービスの状態も確認してください。

---

## 注意点 / TODO / 備考

- 現在は標準出力にテキストを出すのみで、Twitter 等への投稿機能は含まれていません。自動投稿を行いたい場合は OAuth 周りの実装を追加してください。
- エラーハンドリングやテスト、設定の柔軟化（コマンドライン引数対応など）は拡張余地があります。

---

## ライセンス

- GPLv3 ライセンスで公開しています。詳細は LICENSE ファイルを参照してください。

---

Contributions welcome — 簡単な変更や改善提案は Pull Request をお送りください。
