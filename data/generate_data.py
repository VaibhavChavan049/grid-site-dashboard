"""
Grid Site Data Generator
Generates realistic synthetic data for 60 grid sites across the US.
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
import random

random.seed(42)
np.random.seed(42)

# --- Site Metadata ---
STATES = ["CA", "TX", "NY", "FL", "AZ", "NV", "CO", "WA", "OR", "MN"]
SITE_TYPES = ["Solar", "Wind", "Battery Storage", "Solar+Storage", "Wind+Storage"]
GRID_ZONES = ["CAISO", "ERCOT", "NYISO", "PJM", "MISO", "SPP", "WECC"]
STATUS_OPTIONS = ["Active", "Pending", "Under Review", "Approved", "Rejected"]

US_COORDS = {
    "CA": (36.7, -119.4), "TX": (31.0, -99.0), "NY": (42.9, -75.5),
    "FL": (27.9, -81.5), "AZ": (34.0, -111.6), "NV": (38.8, -116.4),
    "CO": (39.0, -105.5), "WA": (47.4, -120.5), "OR": (44.0, -120.5),
    "MN": (46.4, -93.1)
}

def generate_sites(n=60):
    sites = []
    for i in range(1, n + 1):
        state = random.choice(STATES)
        base_lat, base_lon = US_COORDS[state]
        lat = round(base_lat + np.random.uniform(-2, 2), 4)
        lon = round(base_lon + np.random.uniform(-2, 2), 4)
        site_type = random.choice(SITE_TYPES)

        # Scores (0-100)
        land_score = round(np.random.uniform(40, 100), 1)
        grid_proximity = round(np.random.uniform(30, 100), 1)
        load_demand = round(np.random.uniform(35, 100), 1)
        env_score = round(np.random.uniform(50, 100), 1)
        permit_ease = round(np.random.uniform(20, 100), 1)
        infra_readiness = round(np.random.uniform(30, 100), 1)

        # Weighted composite score
        composite = round(
            0.25 * grid_proximity +
            0.20 * load_demand +
            0.20 * land_score +
            0.15 * env_score +
            0.10 * permit_ease +
            0.10 * infra_readiness, 1
        )

        capacity_mw = round(np.random.uniform(5, 250), 1)
        est_cost_m = round(capacity_mw * np.random.uniform(0.8, 1.5), 2)
        irr = round(np.random.uniform(6, 22), 1)
        payback_years = round(np.random.uniform(4, 15), 1)

        status = random.choices(
            STATUS_OPTIONS,
            weights=[0.35, 0.25, 0.20, 0.15, 0.05]
        )[0]

        sites.append({
            "site_id": f"SITE-{i:03d}",
            "site_name": f"{state} Grid Site {i:03d}",
            "state": state,
            "latitude": lat,
            "longitude": lon,
            "site_type": site_type,
            "grid_zone": random.choice(GRID_ZONES),
            "capacity_mw": capacity_mw,
            "est_cost_million_usd": est_cost_m,
            "irr_percent": irr,
            "payback_years": payback_years,
            "land_availability_score": land_score,
            "grid_proximity_score": grid_proximity,
            "load_demand_score": load_demand,
            "environmental_score": env_score,
            "permit_ease_score": permit_ease,
            "infrastructure_readiness_score": infra_readiness,
            "composite_viability_score": composite,
            "status": status,
            "assessment_date": (datetime.now() - timedelta(days=random.randint(0, 180))).strftime("%Y-%m-%d"),
            "analyst": random.choice(["Alex R.", "Maria T.", "James K.", "Priya N.", "Ben O."])
        })
    return pd.DataFrame(sites)


def generate_load_profiles(site_ids, days=30):
    """Generate hourly load profiles for each site."""
    records = []
    base_date = datetime.now() - timedelta(days=days)
    for site_id in site_ids[:20]:  # First 20 sites for performance
        for d in range(days):
            for h in range(24):
                ts = base_date + timedelta(days=d, hours=h)
                # Simulate daily demand curve
                base = 50 + 30 * np.sin((h - 6) * np.pi / 12) + np.random.normal(0, 5)
                records.append({
                    "site_id": site_id,
                    "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
                    "load_mw": round(max(10, base), 2),
                    "generation_mw": round(max(0, base * np.random.uniform(0.7, 1.3)), 2),
                })
    return pd.DataFrame(records)


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    sites_df = generate_sites(60)
    sites_df.to_csv("data/grid_sites.csv", index=False)
    print(f"✅ Generated {len(sites_df)} grid sites -> data/grid_sites.csv")

    load_df = generate_load_profiles(sites_df["site_id"].tolist())
    load_df.to_csv("data/load_profiles.csv", index=False)
    print(f"✅ Generated {len(load_df)} load records -> data/load_profiles.csv")
    print("\nSample sites:")
    print(sites_df[["site_id", "state", "site_type", "capacity_mw", "composite_viability_score", "status"]].head(10).to_string())
