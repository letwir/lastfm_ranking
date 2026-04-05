# Last.fmのAPIを使用して、ユーザーのトップトラックランキングを取得し、ツイート用のテキストを生成するPythonスクリプト。
import datetime
import logging
import os
import sys
import unicodedata

import requests
from dotenv import load_dotenv

load_dotenv()
# ---- 環境変数の読み込み ----
API_KEY = os.getenv("API_KEY")
USER_NAME = os.getenv("USER_NAME")
NICK_NAME = os.getenv("NICK_NAME")
LIMIT = os.getenv("LIMIT", "5")  # ランキングに表示する曲の数を指定（デフォルトは5）
# ---- 定数の定義 ----
PERIOD: str = (
    ""  # ランキングの期間を指定する変数（例: "7day", "1month", "12month"など）
)
KIKAN: str = ""  # ランキングの期間を表す文字列（例: "今週", "今月", "今年"など）

# ---- ログの設定 ----
logging.basicConfig(
    level=logging.WARN,  # ログレベルをWARNINGに設定（必要に応じてDEBUGなどに変更可能）
    format="%(asctime)s - %(levelname)s - %(message)s",  # ログのフォーマット
    handlers=[
        logging.FileHandler("lastfm_ranking.log"),  # ログをファイルに出力
        logging.StreamHandler(sys.stdout),  # ログをコンソールにも出力
    ],
)


# ---- 関数の定義 ----
def fetch_lastfm_json() -> dict:
    """
    Last.fmのAPIからユーザーのトップトラックランキングを取得する関数。
    """
    url = f"http://ws.audioscrobbler.com/2.0/?method=user.gettoptracks&format=json&api_key={API_KEY}&user={USER_NAME}&period={PERIOD}&limit={LIMIT}"
    r = requests.get(url)
    if r.status_code != 200:
        logging.fatal(f"Error fetching data from Last.fm API: {r.text}")
        sys.exit(1)
    return r.json()


def make_text(data: str, KIKAN: str, max_char_len: int) -> str:
    """
    データからランキングを作成し、ツイート用の文字列を生成する関数。
    曲名とアーティスト名をmax_char_len文字に切り詰めることで、ツイートの文字数を調整する。
    """
    pre_text = f"{NICK_NAME}の{KIKAN}ランキング #ラズラン #NowPlaying\n"

    result = data.get("toptracks", {}).get("track", [])
    for i in range(len(result)):
        track = result[i]
        name = track.get("name", "")  # 曲名をmax_char_len文字に切り詰める
        artist = track.get("artist", {}).get("name", "")[
            :max_char_len
        ]  # アーティスト名をmax_char_len文字に切り詰める
        playcount = track.get("playcount", "0")[
            :max_char_len
        ]  # 再生回数を取得（存在しない場合は0を使用）
        pre_ranking = f"{i + 1}. {name} - {artist} {playcount}回\n"
        pre_text += unicodedata.normalize(
            "NFKC", pre_ranking
        )  # Unicode正規化pre_ranking
    logging.debug(f"text length: {len(pre_text)} characters")
    return pre_text[:-1]  # 最後の改行を削除して返す


def text_length_fix(text: str, data: dict, kikan: str, char_len: int) -> str:
    """
    ツイートの文字数を500文字程度に調整
    """
    while len(text) < 500:
        char_len += 1
        text = make_text(data, kikan, max_char_len=char_len)
        if len(text) <= 500:
            char_len -= 1
            text = make_text(data, kikan, max_char_len=char_len)
            break
    while len(text) > 500:
        char_len -= 1
        text = make_text(data, kikan, max_char_len=char_len)
        if len(text) <= 500:
            break
    return text


def main():
    char_len = 30  # 曲名とアーティスト名の最大文字数を初期値として設定
    data = fetch_lastfm_json()
    logging.debug(f"Fetched data: {data}")
    text: str = make_text(data, KIKAN, max_char_len=char_len)
    logging.debug(f"Initial text length: {len(text)} characters")
    text = text_length_fix(text, data, KIKAN, char_len)
    logging.debug(f"Final text length: {len(text)} characters")
    print(text)


if __name__ == "__main__":
    today = datetime.date.today()
    day = today.day
    month = today.month
    logging.debug(f"Today: {month}/{day}")
    if month == 12 and 23 < day < 31:  # 年末に過去12ヶ月分のランキング
        PERIOD = "12month"
        KIKAN = "今年"
    elif 1 < day < 8:  # 毎月1日に過去1ヶ月分のランキング
        PERIOD = "1month"
        KIKAN = "今月"
    else:
        PERIOD = "7day"
        KIKAN = "今週"
    main()
