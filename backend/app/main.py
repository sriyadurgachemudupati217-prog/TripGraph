"""
main.py

TripGraph FastAPI application. Exposes the travel knowledge graph stored in
CognoDB (Neo4j/Bolt compatible) as a clean REST + JSON graph API for the
React frontend.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.database import connect_to_db, close_db, verify_database_connection
from app import queries
from app import graph_schema
from app.database import run_query

app = FastAPI(title="TripGraph API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    connect_to_db()


@app.on_event("shutdown")
def shutdown_event():
    close_db()


# ---------------------------------------------------------------------------
# Root + health
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {"message": "TripGraph API is running"}


@app.get("/db-test")
def db_test():
    return verify_database_connection()


# ---------------------------------------------------------------------------
# Graph
# ---------------------------------------------------------------------------

@app.get("/graph")
def graph():
    try:
        return queries.get_graph()
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=str(e))


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

@app.get("/search")
def search(q: str = Query(..., min_length=1)):
    try:
        return {"results": queries.search_nodes(q)}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=str(e))


# ---------------------------------------------------------------------------
# Destinations
# ---------------------------------------------------------------------------

@app.get("/destinations")
def destinations():
    try:
        return queries.get_all_destinations()
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/destinations/{destination_id}")
def destination_detail(destination_id: str):
    try:
        result = queries.get_destination(destination_id)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=str(e))
    if not result:
        raise HTTPException(status_code=404, detail="Destination not found")
    return result


@app.get("/destinations/{destination_id}/connections")
def destination_connections(destination_id: str):
    try:
        result = queries.get_destination_connections(destination_id)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=str(e))
    if not result:
        raise HTTPException(status_code=404, detail="Destination not found")
    return result


# ---------------------------------------------------------------------------
# Countries / Cities
# ---------------------------------------------------------------------------

@app.get("/countries")
def countries():
    try:
        return queries.get_all_countries()
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/cities")
def cities():
    try:
        return queries.get_all_cities()
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=str(e))


# ---------------------------------------------------------------------------
# Activities / Hotels / Restaurants
# ---------------------------------------------------------------------------

@app.get("/activities")
def activities():
    try:
        return queries.get_all_activities()
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/hotels")
def hotels():
    try:
        return queries.get_all_hotels()
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/restaurants")
def restaurants():
    try:
        return queries.get_all_restaurants()
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=str(e))


# ---------------------------------------------------------------------------
# Trips
# ---------------------------------------------------------------------------

@app.get("/trips")
def trips():
    try:
        return queries.get_all_trips()
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/trips/{trip_id}")
def trip_detail(trip_id: str):
    try:
        result = queries.get_trip(trip_id)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=str(e))
    if not result:
        raise HTTPException(status_code=404, detail="Trip not found")
    return result


# ---------------------------------------------------------------------------
# Node details (generic - used by graph click-through)
# ---------------------------------------------------------------------------

@app.get("/nodes/{node_id}")
def node_details(node_id: str):
    try:
        result = queries.get_node_details(node_id)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=str(e))
    if not result:
        raise HTTPException(status_code=404, detail="Node not found")
    return result


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

@app.get("/stats")
def stats():
    try:
        return queries.get_travel_statistics()
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=str(e))


# ---------------------------------------------------------------------------
# One-off schema setup endpoint (constraints only, no data) - handy for
# environments where you cannot run the seed script directly.
# ---------------------------------------------------------------------------

@app.get("/setup-constraints")
def setup_constraints():
    try:
        graph_schema.create_constraints(run_query)
        return {"status": "constraints created"}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=str(e))
