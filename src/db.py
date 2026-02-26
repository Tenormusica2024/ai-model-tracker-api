"""
Supabase クライアントファクトリ
api.py / crawl_hf.py の両方から参照する共通モジュール
"""

import os

from supabase import create_client, Client

# モジュールレベルでキャッシュし、リクエストごとに新規接続を生成しない
_client: Client | None = None


def get_supabase() -> Client:
    global _client
    if _client is None:
        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_KEY"]
        _client = create_client(url, key)
    return _client
