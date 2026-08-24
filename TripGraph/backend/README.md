# TripGraph Backend

FastAPI service that exposes the TripGraph travel knowledge graph, stored in
CognoDB (Neo4j/Bolt compatible), as a REST + JSON graph API.

## Setup

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configure

Copy `.env.example` to `.env` and fill in your CognoDB credentials (already
done for you in this project — `.env` is pre-filled, but **never commit it**
to source control).

```env
COGNODB_URI=bolt+s://YOUR_DATABASE_HOST
COGNODB_USERNAME=cognodb
COGNODB_PASSWORD=YOUR_PASSWORD
```

## Test the database connection independently

```powershell
python test_db.py
```

## Seed the database

```powershell
python -m app.seed_data
```

Safe to run multiple times — every write uses `MERGE`, so nothing is
duplicated.

## Run the API

```powershell
uvicorn app.main:app --reload
```

* API: http://127.0.0.1:8000
* Swagger docs: http://127.0.0.1:8000/docs

## Key endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/` | Health message |
| GET | `/db-test` | Database connectivity status |
| GET | `/graph` | Full graph as `{nodes, edges}` |
| GET | `/search?q=` | Search nodes by name |
| GET | `/destinations` | All destinations |
| GET | `/destinations/{id}` | Single destination |
| GET | `/destinations/{id}/connections` | Everything connected to a destination |
| GET | `/countries` | All countries |
| GET | `/cities` | All cities |
| GET | `/activities` | All activities |
| GET | `/hotels` | All hotels |
| GET | `/restaurants` | All restaurants |
| GET | `/trips` | All trips |
| GET | `/trips/{id}` | Single trip |
| GET | `/nodes/{id}` | Generic node detail (any type) |
| GET | `/stats` | Dynamic counts of every entity type |
