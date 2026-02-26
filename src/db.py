"""
Supabase クライアントファクトリ
api.py / crawl_hf.py の両方から参照する共通モジュール
"""

import os
import threading

from supabase import create_client, Client

# モジュールレベルでキャッシュし、リクエストごとに新規接続を生成しない
_client: Client | None = None
# 複数スレッドからの同時初期化を防ぐロック
_client_lock = threading.Lock()


def get_supabase() -> Client:
    global _client
    with _client_lock:
        if _client is None:
            url = os.environ["SUPABASE_URL"]
            key = os.environ["SUPABASE_KEY"]
            _client = create_client(url, key)
    return _client
