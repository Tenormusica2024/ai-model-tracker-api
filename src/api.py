"""
AI Model Tracker API
FastAPI application serving trending/new model data from Supabase.

Endpoints:
  GET /models/trending  - Top models by likes growth over N days
  GET /models/new       - Recently first-seen models
  GET /models/{model_id}/history - Snapshot history for a specific model
"""

from collections import defaultdict
from datetime import date, timedelta
from typing import Optional

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from db import get_supabase

app = FastAPI(
    title="AI Model Tracker API",
    description="Track trending AI models on HuggingFace with historical data",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/models/trending")
def get_trending(
    pipeline_tag: Optional[str] = Query(None, description="Filter by task type e.g. text-generation"),
    days: int = Query(7, ge=1, le=90, description="Lookback window in days"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
):
    """
    Return models ranked by likes increase over the past N days.
    Requires at least two snapshots (today and N days ago) to compute delta.
    """
    sb = get_supabase()

    cutoff = (date.today() - timedelta(days=days)).isoformat()
    # days × limit でスナップショット行数を上限設定（例: 7日×20件 = 上限140行）
    # モデル数が増えても OOM / タイムアウトを防ぐ
    row_cap = days * limit

    query = (
        sb.table("model_snapshots")
        .select("model_id, snapshot_date, likes, pipeline_tag")
        .gte("snapshot_date", cutoff)
        .order("snapshot_date", desc=False)
        .limit(row_cap)
    )
    if pipeline_tag:
        query = query.eq("pipeline_tag", pipeline_tag)

    resp = query.execute()
    rows = resp.data

    # model_id ごとにスナップショットをまとめて likes の増分（最新 - 最古）を計算
    model_snapshots: dict[str, list] = defaultdict(list)
    for row in rows:
        model_snapshots[row["model_id"]].append(row)

    deltas = []
    for model_id, snaps in model_snapshots.items():
        if len(snaps) < 2:
            continue
        oldest = snaps[0]
        latest = snaps[-1]
        delta = (latest["likes"] or 0) - (oldest["likes"] or 0)
        deltas.append({
            "model_id": model_id,
            "pipeline_tag": latest.get("pipeline_tag"),
            "likes_latest": latest["likes"],
            "likes_delta": delta,
            "snapshot_date_from": oldest["snapshot_date"],
            "snapshot_date_to": latest["snapshot_date"],
        })

    deltas.sort(key=lambda x: x["likes_delta"], reverse=True)
    return deltas[:limit]


@app.get("/models/new")
def get_new(
    pipeline_tag: Optional[str] = Query(None, description="Filter by task type"),
    days: int = Query(7, ge=1, le=90, description="Lookback window in days"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
):
    """
    Return models first seen within the past N days, sorted by likes descending.
    """
    cutoff = (date.today() - timedelta(days=days)).isoformat()

    sb = get_supabase()
    query = (
        sb.table("models")
        .select("id, name, author, pipeline_tag, first_seen_at")
        .gte("first_seen_at", cutoff)
        .order("first_seen_at", desc=True)
        .limit(limit)
    )
    if pipeline_tag:
        query = query.eq("pipeline_tag", pipeline_tag)

    resp = query.execute()
    return resp.data


@app.get("/models/{model_id:path}/history")
def get_history(
    model_id: str,
    limit: int = Query(30, ge=1, le=180, description="Max snapshot records"),
):
    """
    Return time-series snapshots for a specific model.
    model_id uses path param to support 'author/model-name' format.
    """
    sb = get_supabase()
    resp = (
        sb.table("model_snapshots")
        .select("snapshot_date, downloads_30d, likes, pipeline_tag, tags")
        .eq("model_id", model_id)
        .order("snapshot_date", desc=True)
        .limit(limit)
        .execute()
    )
    if not resp.data:
        raise HTTPException(status_code=404, detail=f"No snapshots found for model '{model_id}'")
    return resp.data
