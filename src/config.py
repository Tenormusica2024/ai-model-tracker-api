"""
クロール設定の定数
crawl_hf.py / crawl_arxiv.py / api.py の共通設定
"""

# ---------- HuggingFace ----------

# 取得するパイプラインタグ（= タスク種別）
TARGET_PIPELINE_TAGS = [
    "text-generation",
    "text2text-generation",
    "image-text-to-text",  # multimodal VLM
    "text-to-image",
]

# 1タグあたりの取得件数
LIMIT_PER_TAG = 200

# ---------- arXiv ----------

# 取得する arXiv カテゴリ（AI/ML 系）
ARXIV_CATEGORIES = ["cs.AI", "cs.LG", "cs.CL", "cs.CV", "stat.ML"]

# 1カテゴリあたりの取得件数
PAPERS_PER_CATEGORY = 100

# ---------- 共通 ----------

# crawl() でエラー率がこの閾値を超えた場合に非ゼロ終了（GitHub Actions アラート用）
ERROR_RATE_THRESHOLD = 0.1
