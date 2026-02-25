"""
HF Models API 日次クロールスクリプト
毎日 UTC 00:00 に GitHub Actions から実行される

取得対象: text-generation / text-to-image / multimodal 上位モデル
保存先: Supabase (環境変数 SUPABASE_URL / SUPABASE_KEY)
"""

import sys
import time
import logging
from datetime import date

import requests
from supabase import Client

from db import get_supabase

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# 取得するパイプラインタグ（= タスク種別）
TARGET_PIPELINE_TAGS = [
    "text-generation",
    "text2text-generation",
    "image-text-to-text",  # multimodal VLM
    "text-to-image",
]

# 1タグあたりの取得件数（急上昇モデルを検出するには上位で十分）
LIMIT_PER_TAG = 200

HF_API_BASE = "https://huggingface.co/api"

# crawl() でエラー率がこの閾値を超えた場合に非ゼロ終了（GitHub Actions でアラートを出すため）
ERROR_RATE_THRESHOLD = 0.1


def fetch_hf_models(pipeline_tag: str, limit: int = LIMIT_PER_TAG) -> list[dict]:
    """
    HF Models API からモデル一覧を取得する
    ソート: likes 降順（人気度順）
    """
    params = {
        "pipeline_tag": pipeline_tag,
        "sort": "likes",
        "direction": -1,
        "limit": limit,
        "cardData": False,
        "full": False,
    }
    url = f"{HF_API_BASE}/models"
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        logger.error(f"HF API fetch failed for {pipeline_tag}: {e}")
        return []


def upsert_model(sb: Client, model: dict) -> None:
    """
    モデルマスタに upsert する（既存なら author/pipeline_tag を更新しない）
    """
    model_id = model.get("modelId") or model.get("id")
    if not model_id:
        return

    author = model_id.split("/")[0] if "/" in model_id else None
    sb.table("models").upsert(
        {
            "id": model_id,
            "name": model_id.split("/")[-1] if "/" in model_id else model_id,
            "author": author,
            "pipeline_tag": model.get("pipeline_tag"),
        },
        on_conflict="id",
        ignore_duplicates=True,  # 初回登録のみ。更新は snapshot 側で管理
    ).execute()


def upsert_snapshot(sb: Client, model: dict, today: date) -> None:
    """
    今日分の日次スナップショットを upsert する
    同日の重複実行は上書き（UNIQUE制約でupsert）
    """
    model_id = model.get("modelId") or model.get("id")
    if not model_id:
        return

    downloads = model.get("downloads")         # None の場合あり
    likes = model.get("likes", 0)
    tags = model.get("tags", [])

    sb.table("model_snapshots").upsert(
        {
            "model_id": model_id,
            "snapshot_date": today.isoformat(),
            "downloads_30d": downloads,
            "likes": likes,
            "pipeline_tag": model.get("pipeline_tag"),
            "tags": tags,
            # business_score / business_summary は別バッチ（LLM処理）で付与
        },
        on_conflict="model_id,snapshot_date",
    ).execute()


def crawl(pipeline_tags: list[str] = TARGET_PIPELINE_TAGS) -> None:
    """
    メイン処理: 全タグを走査してSupabaseに保存
    """
    sb = get_supabase()
    today = date.today()
    total_models = 0
    total_errors = 0

    for tag in pipeline_tags:
        logger.info(f"Fetching tag={tag} ...")
        models = fetch_hf_models(tag)
        logger.info(f"  Got {len(models)} models")

        for model in models:
            try:
                upsert_model(sb, model)
                upsert_snapshot(sb, model, today)
                total_models += 1
            except Exception as e:
                model_id = model.get("modelId") or model.get("id", "unknown")
                logger.warning(f"  Failed to upsert {model_id}: {e}")
                total_errors += 1

        # タグ間に短いインターバル（HF APIへの配慮）
        time.sleep(1)

    total_processed = total_models + total_errors
    error_rate = total_errors / total_processed if total_processed > 0 else 0.0
    logger.info(
        f"Crawl complete: date={today}, "
        f"models={total_models}, errors={total_errors}, "
        f"error_rate={error_rate:.1%}"
    )

    # エラー率が閾値を超えた場合は非ゼロ終了して GitHub Actions にアラートを出す
    if error_rate > ERROR_RATE_THRESHOLD:
        logger.error(
            f"Error rate {error_rate:.1%} exceeded threshold "
            f"{ERROR_RATE_THRESHOLD:.1%} — exiting with code 1"
        )
        sys.exit(1)


if __name__ == "__main__":
    crawl()
