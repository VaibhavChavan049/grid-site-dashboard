"""
Database setup for Grid Site Dashboard.
Supports PostgreSQL (production) and SQLite (local dev).
"""

import os
import pandas as pd
from sqlalchemy import (
    create_engine, Column, String, Float, Integer,
    DateTime, Text, MetaData, Table, inspect
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import text
from datetime import datetime

Base = declarative_base()

def get_engine():
    db_url = os.environ.get("DATABASE_URL", "sqlite:///grid_sites.db")
    # SQLAlchemy 1.4+ fix for postgres
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    return create_engine(db_url, echo=False)


def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def init_db():
    """Create tables and load CSV data if not already loaded."""
    engine = get_engine()
    Base.metadata.create_all(engine)

    inspector = inspect(engine)
    with engine.connect() as conn:
        # Create grid_sites table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS grid_sites (
                site_id TEXT PRIMARY KEY,
                site_name TEXT,
                state TEXT,
                latitude REAL,
                longitude REAL,
                site_type TEXT,
                grid_zone TEXT,
                capacity_mw REAL,
                est_cost_million_usd REAL,
                irr_percent REAL,
                payback_years REAL,
                land_availability_score REAL,
                grid_proximity_score REAL,
                load_demand_score REAL,
                environmental_score REAL,
                permit_ease_score REAL,
                infrastructure_readiness_score REAL,
                composite_viability_score REAL,
                status TEXT,
                assessment_date TEXT,
                analyst TEXT
            )
        """))

        # Create load_profiles table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS load_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_id TEXT,
                timestamp TEXT,
                load_mw REAL,
                generation_mw REAL
            )
        """))
        conn.commit()

        # Seed data if empty
        result = conn.execute(text("SELECT COUNT(*) FROM grid_sites")).fetchone()
        if result[0] == 0:
            csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "grid_sites.csv")
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                df.to_sql("grid_sites", engine, if_exists="append", index=False)
                print(f"✅ Seeded {len(df)} grid sites into DB")

            load_path = os.path.join(os.path.dirname(__file__), "..", "data", "load_profiles.csv")
            if os.path.exists(load_path):
                df2 = pd.read_csv(load_path)
                df2.to_sql("load_profiles", engine, if_exists="append", index=False)
                print(f"✅ Seeded {len(df2)} load records into DB")

    print("✅ Database ready")
    return engine


def load_sites_df():
    """Load all grid sites as a DataFrame."""
    engine = get_engine()
    return pd.read_sql("SELECT * FROM grid_sites", engine)


def load_load_profiles_df(site_id=None):
    """Load load profiles, optionally filtered by site."""
    engine = get_engine()
    if site_id:
        return pd.read_sql(
            f"SELECT * FROM load_profiles WHERE site_id = '{site_id}' ORDER BY timestamp",
            engine
        )
    return pd.read_sql("SELECT * FROM load_profiles ORDER BY timestamp", engine)
