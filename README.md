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
GET /models/trending?days=7&limit=3
```

```json
[
  {
    "model_id": "Nanbeige/Nanbeige4.1-3B",
    "pipeline_tag": "text-generation",
    "likes_latest": 811,
    "likes_delta": 33,
    "snapshot_date_from": "2026-02-24",
    "snapshot_date_to": "2026-02-27"
  },
  {
    "model_id": "google/translategemma-4b-it",
    "pipeline_tag": "image-text-to-text",
    "likes_latest": 643,
    "likes_delta": 12,
    "snapshot_date_from": "2026-02-24",
    "snapshot_date_to": "2026-02-27"
  },
  {
    "model_id": "stabilityai/stable-diffusion-xl-base-1.0",
    "pipeline_tag": "text-to-image",
    "likes_latest": 7473,
    "likes_delta": 8,
    "snapshot_date_from": "2026-02-24",
    "snapshot_date_to": "2026-02-27"
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
GET /models/new?days=4&limit=3
```

```json
[
  {
    "id": "unsloth/Qwen3.5-35B-A3B-GGUF",
    "name": "Qwen3.5-35B-A3B-GGUF",
    "author": "unsloth",
    "pipeline_tag": "image-text-to-text",
    "first_seen_at": "2026-02-26T01:02:11.396791+00:00"
  },
  {
    "id": "Qwen/Qwen3.5-27B",
    "name": "Qwen3.5-27B",
    "author": "Qwen",
    "pipeline_tag": "image-text-to-text",
    "first_seen_at": "2026-02-25T01:10:33.171452+00:00"
  },
  {
    "id": "Qwen/Qwen3.5-122B-A10B",
    "name": "Qwen3.5-122B-A10B",
    "author": "Qwen",
    "pipeline_tag": "image-text-to-text",
    "first_seen_at": "2026-02-25T01:10:27.512855+00:00"
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
GET /models/Nanbeige/Nanbeige4.1-3B/history?limit=3
```

```json
[
  {
    "snapshot_date": "2026-02-27",
    "downloads_30d": 255172,
    "likes": 811,
    "pipeline_tag": "text-generation",
    "tags": ["transformers", "safetensors", "llama", "text-generation", "llm", "conversational"]
  },
  {
    "snapshot_date": "2026-02-26",
    "downloads_30d": 255172,
    "likes": 805,
    "pipeline_tag": "text-generation",
    "tags": ["transformers", "safetensors", "llama", "text-generation", "llm", "conversational"]
  },
  {
    "snapshot_date": "2026-02-25",
    "downloads_30d": 202462,
    "likes": 778,
    "pipeline_tag": "text-generation",
    "tags": ["transformers", "safetensors", "llama", "text-generation", "llm", "conversational"]
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
GET /papers/recent?category=cs.CV&days=3&limit=2
```

```json
[
  {
    "arxiv_id": "2602.22212",
    "title": "Neu-PiG: Neural Preconditioned Grids for Fast Dynamic Surface Reconstruction on Long Sequences",
    "authors": ["Julian Kaltheuner", "Hannah Dröge", "Markus Plack", "Patrick Stotko", "Reinhard Klein"],
    "submitted_at": "2026-02-25T18:59:53+00:00",
    "category": "cs.CV",
    "pwc_sota_flag": false
  },
  {
    "arxiv_id": "2602.22209",
    "title": "WHOLE: World-Grounded Hand-Object Lifted from Egocentric Videos",
    "authors": ["Yufei Ye", "Jiaman Li", "Ryan Rong", "C. Karen Liu"],
    "submitted_at": "2026-02-25T18:59:10+00:00",
    "category": "cs.CV",
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
