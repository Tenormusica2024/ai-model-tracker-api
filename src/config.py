"""
クロール設定の定数
crawl_hf.py と api.py の両方から参照する共通設定
"""

# 取得するパイプラインタグ（= タスク種別）
TARGET_PIPELINE_TAGS = [
    "text-generation",
    "text2text-generation",
    "image-text-to-text",  # multimodal VLM
    "text-to-image",
]

# 1タグあたりの取得件数
LIMIT_PER_TAG = 200
