"""
FastAPI Backend — Grid Site Analysis & Deployment Intelligence API
Endpoints for site data, scoring, filtering, and export.
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import pandas as pd
import numpy as np
import io
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from backend.database import init_db, load_sites_df, load_load_profiles_df

app = FastAPI(
    title="Grid Site Deployment Intelligence API",
    description="Backend API for grid site feasibility analysis and deployment scoring.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Init DB on startup
@app.on_event("startup")
def startup_event():
    init_db()


# ── Health ──────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "service": "Grid Site Intelligence API"}


# ── Sites ────────────────────────────────────────────────────────
@app.get("/api/sites")
def get_sites(
    state: str = Query(None),
    site_type: str = Query(None),
    status: str = Query(None),
    min_score: float = Query(0),
    max_score: float = Query(100),
    min_capacity: float = Query(0),
    sort_by: str = Query("composite_viability_score"),
    ascending: bool = Query(False),
    limit: int = Query(100)
):
    df = load_sites_df()

    if state and state != "All":
        df = df[df["state"] == state]
    if site_type and site_type != "All":
        df = df[df["site_type"] == site_type]
    if status and status != "All":
        df = df[df["status"] == status]
    df = df[(df["composite_viability_score"] >= min_score) & 
            (df["composite_viability_score"] <= max_score)]
    df = df[df["capacity_mw"] >= min_capacity]

    if sort_by in df.columns:
        df = df.sort_values(sort_by, ascending=ascending)

    return df.head(limit).to_dict(orient="records")


@app.get("/api/sites/{site_id}")
def get_site(site_id: str):
    df = load_sites_df()
    site = df[df["site_id"] == site_id]
    if site.empty:
        raise HTTPException(status_code=404, detail="Site not found")
    return site.iloc[0].to_dict()


@app.get("/api/sites/{site_id}/load_profile")
def get_load_profile(site_id: str):
    df = load_load_profiles_df(site_id)
    if df.empty:
        return {"site_id": site_id, "records": []}
    return {"site_id": site_id, "records": df.to_dict(orient="records")}


# ── Summary Stats ────────────────────────────────────────────────
@app.get("/api/summary")
def get_summary():
    df = load_sites_df()
    return {
        "total_sites": int(len(df)),
        "avg_viability_score": round(float(df["composite_viability_score"].mean()), 1),
        "total_capacity_mw": round(float(df["capacity_mw"].sum()), 1),
        "total_est_investment_m": round(float(df["est_cost_million_usd"].sum()), 1),
        "avg_irr_percent": round(float(df["irr_percent"].mean()), 1),
        "status_breakdown": df["status"].value_counts().to_dict(),
        "type_breakdown": df["site_type"].value_counts().to_dict(),
        "state_breakdown": df["state"].value_counts().to_dict(),
        "top_sites": df.nlargest(5, "composite_viability_score")[
            ["site_id", "site_name", "state", "composite_viability_score", "status"]
        ].to_dict(orient="records"),
    }


@app.get("/api/score_distribution")
def score_distribution():
    df = load_sites_df()
    bins = [0, 40, 55, 70, 85, 100]
    labels = ["Critical (<40)", "Low (40-55)", "Moderate (55-70)", "Good (70-85)", "Excellent (85+)"]
    df["bucket"] = pd.cut(df["composite_viability_score"], bins=bins, labels=labels)
    dist = df["bucket"].value_counts().sort_index()
    return {"distribution": dist.to_dict()}


@app.get("/api/scoring_factors")
def scoring_factors():
    """Return average scores per dimension for radar chart."""
    df = load_sites_df()
    factors = [
        "land_availability_score", "grid_proximity_score",
        "load_demand_score", "environmental_score",
        "permit_ease_score", "infrastructure_readiness_score"
    ]
    return {f: round(float(df[f].mean()), 1) for f in factors}


# ── Export ───────────────────────────────────────────────────────
@app.get("/api/export/csv")
def export_csv(
    state: str = Query(None),
    status: str = Query(None),
    min_score: float = Query(0)
):
    df = load_sites_df()
    if state and state != "All":
        df = df[df["state"] == state]
    if status and status != "All":
        df = df[df["status"] == status]
    df = df[df["composite_viability_score"] >= min_score]

    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=grid_sites_report.csv"}
    )


# ── Compare ──────────────────────────────────────────────────────
@app.get("/api/compare")
def compare_sites(site_ids: str = Query(...)):
    ids = [s.strip() for s in site_ids.split(",")]
    df = load_sites_df()
    subset = df[df["site_id"].isin(ids)]
    if subset.empty:
        raise HTTPException(status_code=404, detail="No matching sites")
    return subset.to_dict(orient="records")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.api:app", host="0.0.0.0", port=8000, reload=True)
