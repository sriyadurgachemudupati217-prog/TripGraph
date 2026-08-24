# TripGraph Frontend

A React + Vite + React Flow dashboard for exploring the TripGraph travel
knowledge graph.

## Setup

```powershell
cd frontend
npm install
```

## Configure

`.env` already points at the local backend:

```env
VITE_API_URL=http://127.0.0.1:8000
```

## Run

```powershell
npm run dev
```

Open http://localhost:5173

The backend must be running (see `../backend/README.md`) and seeded with
`python -m app.seed_data` for the graph to have data.
