"""
Supabase クライアントファクトリ
api.py / crawl_hf.py の両方から参照する共通モジュール
"""

import os

from supabase import create_client, Client


def get_supabase() -> Client:
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_KEY"]
    return create_client(url, key)
