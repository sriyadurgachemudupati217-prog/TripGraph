# TripGraph

**Explore the world through connections.**

TripGraph is an interactive travel knowledge graph. Search for a place,
theme, or trip, and see how countries, cities, destinations, attractions,
activities, hotels, restaurants, trips, and travel concepts connect to each
other — visually, as a graph.

## Fix history

### v2 — Edges were invisible (nodes rendered, no lines)

**Root cause:** the custom React Flow node component (`TripGraphNode` in
`frontend/src/components/GraphView.jsx`) rendered plain `<div>`s with no
`<Handle>` elements inside them. React Flow computes every edge's anchor
point from a `<Handle>` DOM node inside each endpoint node — without one,
it has nothing to draw a connection line from or to, so **every edge failed
silently** (React Flow only logs a console warning per edge, it doesn't
throw). This was purely a rendering-layer bug: the backend's `/graph`
response already contained real, valid edges the whole time — 96 nodes and
214 edges in the current seed dataset (see below for the full breakdown),
each `Country|City|Destination|...` node connected exactly like the real
CognoDB relationships (`India → Delhi`, `Paris → Restaurant`, etc.).

**What changed:**

* `frontend/src/components/GraphView.jsx` — added a `target` Handle
  (`Position.Top`) and a `source` Handle (`Position.Bottom`) to the custom
  `TripGraphNode` component, and gave edges a more visible stroke color/width.
* `frontend/src/index.css` — added a `.tg-handle` style so the connection
  points blend into the node design instead of looking like default React
  Flow dots.
* No backend files, no CognoDB query logic, and no `{nodes, edges}` API
  shape were touched — the fix is entirely in how the frontend graph
  library renders data it was already receiving correctly.

### v1 — Graph container had no height (nothing rendered at all)

Two nested `<div>`s both used the same `.graph-canvas` CSS class, which had
no explicit `height`; the grid-stretched height from the layout never
cascaded down to the React Flow canvas, which collapsed to 0px. Fixed by
splitting the outer wrapper into its own `.graph-panel` class with an
explicit `height: 100%`.

### v0 — `/graph` returned a 500 error

`database.run_query()` flattens every Neo4j Node/Relationship into a plain
properties dict via `record.data()`, which strips `.labels`/`.type`
metadata. `get_graph()` and `search_nodes()` were still trying to read
`.labels`/`.type` off those flattened Python values. Fixed by pulling
`labels(n)` / `type(r)` explicitly inside the Cypher query itself.

## Architecture

```text
React (Vite, React Flow)
   ↓  REST / JSON
FastAPI
   ↓  Bolt protocol
Neo4j Python Driver
   ↓
CognoDB
```

The backend never exposes raw Neo4j records to the frontend — `/graph`
transforms everything into a simple `{ nodes, edges }` shape.

## Expected data volume (current seed dataset)

Running `python -m app.seed_data` against a fresh database produces:

| Nodes | Count | | Edges (relationship) | Count |
|---|---|---|---|---|
| Country | 8 | | CONTAINS (Country→City) | 12 |
| City | 12 | | City RELATED_TO City | 5 |
| Destination | 14 | | HAS_DESTINATION (City→Destination) | 14 |
| Attraction | 14 | | HAS_ATTRACTION (Destination→Attraction) | 14 |
| Activity | 12 | | Destination RELATED_TO Destination | 10 |
| Hotel | 8 | | Activity RELATED_TO TravelConcept | 21 |
| Restaurant | 8 | | Hotel/Restaurant LOCATED_IN City | 16 |
| TravelConcept | 12 | | Trip VISITS Destination | 14 |
| Trip | 8 | | Trip SUITABLE_FOR TravelConcept | 23 |
| **Total** | **96** | | Destination OFFERS Activity | 29 |
| | | | Destination SUITABLE_FOR TravelConcept | 32 |
| | | | Destination HAS_HOTEL/HAS_RESTAURANT | 24 |
| | | | **Total** | **214** |

If your `GET /graph` returns fewer than this, the database likely just
needs (re-)seeding: `python -m app.seed_data` (safe to re-run, uses
`MERGE`). I can't reach your live CognoDB instance from here to confirm
your actual live counts — check them directly with `GET /stats` or
`GET /graph` once running.

## Project structure

```text
TripGraph/
├── backend/
│   ├── app/
│   │   ├── main.py          FastAPI app + all endpoints
│   │   ├── database.py      Shared CognoDB driver, connection handling
│   │   ├── queries.py       Parameterized Cypher query layer
│   │   ├── graph_schema.py  Uniqueness constraints
│   │   └── seed_data.py     Idempotent demo dataset (MERGE-based)
│   ├── test_db.py           Standalone connection test
│   ├── .env                 Pre-filled with your CognoDB credentials
│   ├── .env.example
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/      Header, Sidebar, GraphView, SearchBar, ...
│   │   ├── services/api.js  Single place all API calls go through
│   │   └── App.jsx
│   ├── .env                 VITE_API_URL
│   └── package.json
│
└── .gitignore
```

## 1. Install (Windows PowerShell)

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

```powershell
cd ..\frontend
npm install
```

## 2. Configuration

`backend\.env` is already filled in with your CognoDB connection details:

```env
COGNODB_URI=bolt+s://db-b2748099.bravo.databases.cognodb.com
COGNODB_USERNAME=cognodb
COGNODB_PASSWORD=cffe958b1337cdf055a8820a6a406f1c
```

`frontend\.env`:

```env
VITE_API_URL=http://127.0.0.1:8000
```

**Security note:** this password has been shared in plain text in chat, so
treat it as already exposed and rotate it in your CognoDB dashboard once
you're up and running. `.env` files are excluded via `.gitignore` so they
won't get committed if you push this to Git — double check before your
first commit.

## 3. Test the database connection independently

```powershell
cd ..\backend
python test_db.py
```

Expected output:

```text
Connecting to CognoDB...
CognoDB connection successful.
Query result: 1
```

## 4. Seed the database (if not already seeded)

```powershell
python -m app.seed_data
```

Safe to re-run any time — every write uses `MERGE`, so nothing duplicates.

## 5. Start the backend

```powershell
uvicorn app.main:app --reload
```

* API: http://127.0.0.1:8000
* Swagger docs: http://127.0.0.1:8000/docs

## 6. Verify the graph endpoint directly

```powershell
curl http://127.0.0.1:8000/graph
curl http://127.0.0.1:8000/stats
```

`nodes.length` should be 96 and `edges.length` should be 214 against the
default seed dataset (see the table above). If `edges` is an empty array,
that's a data problem (re-seed); if `edges` has entries but they weren't
visible in the browser before this fix, that was the React Flow Handle bug.

## 7. Start the frontend

```powershell
cd ..\frontend
npm run dev
```

Open **http://localhost:5173** — you should see the TripGraph header, a
"● Connected" status pill, the graph rendering immediately fitted to the
viewport, nodes grouped by type, and now visible arrowed lines connecting
related nodes (e.g. a country to its cities, a destination to its hotels).

## Data model

**Node types:** Country, City, Destination, Attraction, Activity, Hotel,
Restaurant, Trip, TravelConcept.

**Relationships:**

```text
(:Country)-[:CONTAINS]->(:City)
(:City)-[:HAS_DESTINATION]->(:Destination)
(:Destination)-[:HAS_ATTRACTION]->(:Attraction)
(:Destination)-[:OFFERS]->(:Activity)
(:Destination)-[:HAS_HOTEL]->(:Hotel)
(:Destination)-[:HAS_RESTAURANT]->(:Restaurant)
(:Destination)-[:RELATED_TO]->(:Destination)
(:Destination)-[:SUITABLE_FOR]->(:TravelConcept)
(:Activity)-[:RELATED_TO]->(:TravelConcept)
(:Hotel)-[:LOCATED_IN]->(:City)
(:Restaurant)-[:LOCATED_IN]->(:City)
(:Trip)-[:VISITS]->(:Destination)
(:Trip)-[:SUITABLE_FOR]->(:TravelConcept)
(:City)-[:RELATED_TO]->(:City)
```

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Header shows "API Offline" | FastAPI isn't running | `uvicorn app.main:app --reload` in `backend/` |
| Header shows "Database Offline" | CognoDB unreachable, or wrong credentials | Run `python test_db.py`, check `backend/.env` |
| Header shows "Connected" but graph area is blank | Should now be fixed — check `.graph-panel` / `.graph-canvas` in `index.css` both have `height: 100%` |
| Nodes render but no edges/lines | Should now be fixed — check `TripGraphNode` in `GraphView.jsx` still has both `<Handle>` elements | Re-add if a future edit removes them |
| "Couldn't load the travel graph" message | Backend + DB reachable, but `/graph` or `/stats` itself errored | Check the FastAPI terminal for a traceback |
| Graph is empty (0 nodes) | Database hasn't been seeded | `python -m app.seed_data` |
| CORS errors in browser console | Frontend running on a different port | Vite must run on `5173` (the default) |
| `npm run dev` fails | Dependencies not installed | `npm install` in `frontend/` |
| Graph nodes drift or overlap oddly | Layout only recalculates when data/filter changes — click "Reset graph" in the toolbar | n/a |


