# HuggingFace Daily Insights API

Track trending AI models on HuggingFace and recent arXiv papers via a REST API — with **historical time-series data** that the official HuggingFace API does not provide.

**Available on RapidAPI**: https://rapidapi.com/dragonrondo/api/huggingface-daily-insights-api

**Base URL**: https://web-production-af174.up.railway.app

---

## Why This API?

The official HuggingFace API returns only the current state of a model (likes, downloads, tags). It provides no history. This API crawls HuggingFace daily and stores snapshots in a database, enabling:

- **Trend detection**: Which models gained the most likes over the past 7/30/90 days?
- **Discovery**: Which models were first published this week?
- **Time-series analysis**: How did a specific model's popularity change over time?

---

## Endpoints

### `GET /health`

Returns service status.

```
GET /health
→ {"status": "ok"}
```

---

### `GET /models/trending`

Returns models ranked by likes increase over the past N days.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `pipeline_tag` | string | — | Filter by task type (e.g. `text-generation`) |
| `days` | int | 7 | Lookback window (1–90) |
| `limit` | int | 20 | Max results (1–100) |

```
GET /models/trending?pipeline_tag=text-generation&days=7&limit=5
```

```json
[
  {
    "model_id": "Qwen/Qwen2.5-7B-Instruct",
    "pipeline_tag": "text-generation",
    "likes_latest": 4821,
    "likes_delta": 312,
    "snapshot_date_from": "2026-02-19",
    "snapshot_date_to": "2026-02-26"
  }
]
```

**Available pipeline tags**: `text-generation`, `text2text-generation`, `image-text-to-text`, `text-to-image`

---

### `GET /models/new`

Returns models first seen within the past N days.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `pipeline_tag` | string | — | Filter by task type |
| `days` | int | 7 | Lookback window (1–90) |
| `limit` | int | 20 | Max results (1–100) |

```
GET /models/new?days=3&limit=5
```

```json
[
  {
    "id": "Qwen/Qwen3.5-7B",
    "name": "Qwen3.5-7B",
    "author": "Qwen",
    "pipeline_tag": "text-generation",
    "first_seen_at": "2026-02-25"
  }
]
```

---

### `GET /models/{model_id}/history`

Returns daily snapshots for a specific model (likes, downloads, tags over time).

| Parameter | Type | Default | Description |
|---|---|---|---|
| `model_id` | path | required | HuggingFace model ID (e.g. `Qwen/Qwen2.5-7B-Instruct`) |
| `limit` | int | 30 | Max snapshot records (1–180) |

```
GET /models/Qwen/Qwen2.5-7B-Instruct/history?limit=7
```

```json
[
  {
    "snapshot_date": "2026-02-26",
    "downloads_30d": 128453,
    "likes": 4821,
    "pipeline_tag": "text-generation",
    "tags": ["transformers", "pytorch", "safetensors"]
  }
]
```

---

### `GET /papers/recent`

Returns recently submitted arXiv papers in AI/ML.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `category` | string | — | Filter by arXiv category (e.g. `cs.AI`) |
| `days` | int | 7 | Lookback window (1–90) |
| `limit` | int | 20 | Max results (1–100) |

```
GET /papers/recent?category=cs.AI&days=3&limit=5
```

```json
[
  {
    "arxiv_id": "2602.22149",
    "title": "Enhancing Framingham Cardiovascular Risk Score Transparency through Logic-Based XAI",
    "authors": ["Emannuel L. de A. Bezerra", "..."],
    "submitted_at": "2026-02-25T17:58:11+00:00",
    "category": "cs.AI",
    "pwc_sota_flag": false
  }
]
```

**Available categories**: `cs.AI`, `cs.LG`, `cs.CL`, `cs.CV`, `stat.ML`

---

### `GET /arena/rankings`

Returns LMArena ELO rankings from the latest available snapshot.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `limit` | int | 50 | Max results (1–200) |
| `snapshot_date` | string | — | Specific date (YYYY-MM-DD). Defaults to latest. |

```
GET /arena/rankings?limit=10
```

```json
[
  {
    "snapshot_date": "2025-08-29",
    "model_name": "gemini-2.5-pro",
    "rank": 1,
    "elo_score": 1466
  }
]
```

**Note**: Source data (`lmarena-ai/lmarena-leaderboard` HF Space) is updated irregularly. Latest available snapshot: 2025-08-29.

---

## Architecture

```
GitHub Actions (daily, UTC 00:00 / JST 09:00)
  ├── crawl_hf.py     → HuggingFace Hub API → models / model_snapshots (Supabase)
  ├── crawl_arxiv.py  → arXiv Atom XML API  → papers (Supabase)
  └── crawl_arena.py  → lmarena-ai HF Space → arena_rankings (Supabase)

Railway (FastAPI + uvicorn)
  └── Serves API requests from Supabase
```

**Data collection**:
- HuggingFace: top 200 models per pipeline tag, 4 tags daily
- arXiv: top 100 papers per category, 5 categories daily
- Retention: indefinite (time-series accumulates daily)

---

## Tech Stack

- **Runtime**: Python 3.11
- **Framework**: FastAPI + uvicorn
- **Database**: Supabase (PostgreSQL)
- **Hosting**: Railway
- **CI/CD**: GitHub Actions (daily crawl + on-push deploy)

---

## RapidAPI Plans

| Plan | Price | Quota |
|---|---|---|
| Free | $0 | 100 requests/month |
| PRO | $9/month | 1,000 requests/month |

https://rapidapi.com/dragonrondo/api/huggingface-daily-insights-api
