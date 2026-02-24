"""
AI Model Tracker API
FastAPI application serving trending/new model data from Supabase.

Endpoints:
  GET /models/trending  - Top models by likes growth over N days
  GET /models/new       - Recently first-seen models
  GET /models/{id}/history - Snapshot history for a specific model
"""

import os
from typing import Optional

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client

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


def get_supabase() -> Client:
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_KEY"]
    return create_client(url, key)


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

    # Fetch snapshots from last N+1 days to compute delta
    query = (
        sb.table("model_snapshots")
        .select("model_id, snapshot_date, likes, pipeline_tag")
        .order("snapshot_date", desc=False)
    )
    if pipeline_tag:
        query = query.eq("pipeline_tag", pipeline_tag)

    # Limit date range on Supabase side using gte filter
    from datetime import date, timedelta
    cutoff = (date.today() - timedelta(days=days)).isoformat()
    query = query.gte("snapshot_date", cutoff)

    resp = query.execute()
    rows = resp.data

    # Group by model_id and compute delta (latest - earliest likes in window)
    from collections import defaultdict
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
    from datetime import date, timedelta
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
