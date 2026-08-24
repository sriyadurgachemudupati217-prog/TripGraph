"""
database.py

Handles the single shared Neo4j (CognoDB) driver used across the TripGraph
backend. CognoDB is Neo4j/Bolt compatible, so the official `neo4j` Python
driver is used directly.

The server is designed to start even if the database connection fails, so
that /db-test can report the real underlying error to the caller instead of
the whole API refusing to boot.
"""

import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

COGNODB_URI = os.getenv("COGNODB_URI")
COGNODB_USERNAME = os.getenv("COGNODB_USERNAME")
COGNODB_PASSWORD = os.getenv("COGNODB_PASSWORD")

driver = None
connection_error = None


def connect_to_db():
    """Create the shared driver and verify connectivity. Never raises."""
    global driver, connection_error

    if not COGNODB_URI or not COGNODB_USERNAME or not COGNODB_PASSWORD:
        driver = None
        connection_error = (
            "Missing CognoDB configuration. Check COGNODB_URI, "
            "COGNODB_USERNAME and COGNODB_PASSWORD in backend/.env"
        )
        print("CognoDB connection FAILED.")
        print(f"Reason: {connection_error}")
        return

    try:
        new_driver = GraphDatabase.driver(
            COGNODB_URI,
            auth=(COGNODB_USERNAME, COGNODB_PASSWORD),
        )
        new_driver.verify_connectivity()
        driver = new_driver
        connection_error = None
        print("CognoDB connection successful.")
    except Exception as e:  # noqa: BLE001 - we deliberately surface the real error
        driver = None
        connection_error = str(e)
        print("CognoDB connection FAILED.")
        print(f"Reason: {e}")


def close_db():
    global driver
    if driver is not None:
        driver.close()
        driver = None


def run_query(query: str, parameters: dict | None = None):
    """Run a parameterized Cypher query and return a list of plain dicts."""
    if driver is None:
        raise RuntimeError(connection_error or "Database driver is not connected.")

    with driver.session() as session:
        result = session.run(query, parameters or {})
        return [record.data() for record in result]


def verify_database_connection():
    """Used by GET /db-test. Returns a sanitized (no secrets) status dict."""
    if driver is None:
        return {
            "connected": False,
            "error": connection_error or "Database driver is not connected.",
        }

    try:
        with driver.session() as session:
            result = session.run("RETURN 1 AS result")
            record = result.single()
            return {"connected": True, "result": record["result"]}
    except Exception as e:  # noqa: BLE001
        return {"connected": False, "error": str(e)}
