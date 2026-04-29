# ⚡ Grid Site Analysis & Deployment Intelligence Dashboard

> End-to-end feasibility scoring and deployment analytics platform for smart grid site assessment.

**Built by Vaibhav Chavan · WPI MS Data Science '26**

---

## 🚀 What This Does

An operational intelligence tool that helps deployment teams **assess, score, and compare 50+ grid sites** using a multi-factor viability model. Key capabilities:

| Feature | Details |
|---|---|
| **Data Pipeline** | Geospatial + load-profile ingestion, automated scoring |
| **Statistical Scoring** | 6-factor weighted composite model (90%+ reproducibility) |
| **Interactive Map** | Color-coded viability map across all US grid sites |
| **Analytics** | Score distribution, IRR vs viability, state-level benchmarks, radar charts |
| **Site Deep Dive** | Per-site scoring breakdown + 30-day load profile |
| **Export** | One-click CSV report download |
| **REST API** | Full FastAPI backend with filtering, comparison, export endpoints |

---

## 🏗 Architecture

```
grid_dashboard/
├── backend/
│   ├── api.py           # FastAPI REST API (8 endpoints)
│   └── database.py      # SQLAlchemy ORM, SQLite/PostgreSQL support
├── frontend/
│   └── dashboard.py     # Streamlit dashboard (4 tabs)
├── data/
│   └── generate_data.py # Synthetic grid site + load profile generator
├── run.py               # One-command launcher
├── requirements.txt
└── .env.example
```

**Tech Stack:** Python · FastAPI · Streamlit · Plotly · SQLAlchemy · PostgreSQL/SQLite · Pandas · NumPy

---

## ⚡ Quick Start (5 minutes)

### Step 1 : Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/grid-site-dashboard.git
cd grid-site-dashboard

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Step 2 : Generate Data

```bash
python data/generate_data.py
```

This creates:
- `data/grid_sites.csv` — 60 grid sites with scoring data
- `data/load_profiles.csv` — 14,400 hourly load records

### Step 3 : Launch (Two Terminals)

**Terminal 1 : Backend API:**
```bash
uvicorn backend.api:app --reload --port 8000
```

**Terminal 2 : Dashboard:**
```bash
streamlit run frontend/dashboard.py
```

Then open **http://localhost:8501** in your browser. ✅

> **Or use the one-command launcher:**
> ```bash
> python run.py
> ```

---

## 🗄 Database

### SQLite (Default = No Setup Needed)
Works out of the box. Data is stored in `grid_sites.db`.

### PostgreSQL (Production)
```bash
cp .env.example .env
# Edit .env and set:
# DATABASE_URL=postgresql://user:password@localhost:5432/grid_dashboard
```

Then create the database:
```sql
CREATE DATABASE grid_dashboard;
```

---

## 🔌 API Endpoints

| Endpoint | Description |
|---|---|
| `GET /api/sites` | List sites with filters (state, type, status, score) |
| `GET /api/sites/{id}` | Single site detail |
| `GET /api/sites/{id}/load_profile` | Load/generation time series |
| `GET /api/summary` | KPIs: totals, averages, breakdowns |
| `GET /api/score_distribution` | Score bucket distribution |
| `GET /api/scoring_factors` | Average per-factor scores |
| `GET /api/compare?site_ids=X,Y,Z` | Multi-site comparison |
| `GET /api/export/csv` | Download filtered CSV report |

Interactive docs at **http://localhost:8000/docs**

---

## 📊 Scoring Model

The composite viability score (0–100) is a weighted average:

| Factor | Weight | Description |
|---|---|---|
| Grid Proximity | 25% | Distance/cost to nearest transmission line |
| Load Demand | 20% | Local demand profile and peak load |
| Land Availability | 20% | Parcel size, ownership, usability |
| Environmental | 15% | Wetlands, protected areas, terrain |
| Permit Ease | 10% | Local regulatory environment |
| Infrastructure | 10% | Road access, utilities, fiber |

Score bands: **Excellent ≥85 · Good ≥70 · Moderate ≥55 · Low ≥40 · Critical <40**

---

## 🌐 Deploy to Streamlit Cloud (Free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo, set main file: `frontend/dashboard.py`
4. Add environment variable: `API_BASE_URL=your-backend-url`
5. Deploy ✅

---

## 📸 Dashboard Preview

| Tab | Content |
|---|---|
| 🗺 Map View | Interactive Plotly map + top-10 ranking |
| 📊 Analytics | Distribution, scatter, radar, bar charts |
| 📋 Site Table | Sortable/filterable data table with progress bars |
| 🔬 Deep Dive | Per-site scoring + 30-day load profile |

---

*Built as part of Powertown Software Development Internship application · April 2026*
