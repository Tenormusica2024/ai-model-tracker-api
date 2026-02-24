-- AIモデルトラッカーAPI データベーススキーマ

-- モデルマスタ（初回発見時に登録）
CREATE TABLE IF NOT EXISTS models (
  id TEXT PRIMARY KEY,                  -- HF model_id (例: "Qwen/Qwen2.5-72B")
  name TEXT,
  author TEXT,
  pipeline_tag TEXT,                    -- タスク種別 (text-generation, etc.)
  first_seen_at TIMESTAMPTZ DEFAULT NOW(),
  arxiv_id TEXT,                        -- 紐付け済みarXiv論文ID
  pwc_id TEXT                           -- PapersWithCode ID
);

-- 日次スナップショット（歴史データの本体・差別化の核心）
CREATE TABLE IF NOT EXISTS model_snapshots (
  id BIGSERIAL PRIMARY KEY,
  model_id TEXT REFERENCES models(id) ON DELETE CASCADE,
  snapshot_date DATE NOT NULL,
  downloads_30d INTEGER,                -- 直近30日DL数
  likes INTEGER,                        -- ライク数
  pipeline_tag TEXT,
  tags TEXT[],
  business_score INTEGER,               -- LLMビジネス影響スコア (1-10)
  business_summary TEXT,                -- LLMによる要約
  UNIQUE (model_id, snapshot_date)
);

-- arXiv論文
CREATE TABLE IF NOT EXISTS papers (
  arxiv_id TEXT PRIMARY KEY,
  title TEXT,
  abstract TEXT,
  submitted_at TIMESTAMPTZ,
  authors TEXT[],
  pwc_sota_flag BOOLEAN DEFAULT FALSE
);

-- LMSYS Arenaランキングスナップショット
CREATE TABLE IF NOT EXISTS arena_rankings (
  id BIGSERIAL PRIMARY KEY,
  snapshot_date DATE NOT NULL,
  model_name TEXT,
  rank INTEGER,
  elo_score INTEGER,
  UNIQUE (snapshot_date, model_name)
);

-- 成長率計算用インデックス（クエリ高速化）
CREATE INDEX IF NOT EXISTS idx_snapshots_model_date
  ON model_snapshots (model_id, snapshot_date DESC);

CREATE INDEX IF NOT EXISTS idx_snapshots_date
  ON model_snapshots (snapshot_date DESC);

CREATE INDEX IF NOT EXISTS idx_models_pipeline
  ON models (pipeline_tag);
