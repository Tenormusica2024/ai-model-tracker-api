-- papers テーブルに category カラムを追加
-- 既存データは NULL のまま（次回クロール時に埋まる）
ALTER TABLE papers
  ADD COLUMN IF NOT EXISTS category TEXT;

-- category 絞り込み用インデックス
CREATE INDEX IF NOT EXISTS idx_papers_category
  ON papers (category);
