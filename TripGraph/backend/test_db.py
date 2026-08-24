"""
test_db.py

Independently tests the CognoDB connection, without going through FastAPI.

Run with:
    python test_db.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import connect_to_db, close_db, verify_database_connection  # noqa: E402


def main():
    print("Connecting to CognoDB...")
    connect_to_db()

    status = verify_database_connection()

    if status["connected"]:
        print("CognoDB connection successful.")
        print(f"Query result: {status['result']}")
    else:
        print("CognoDB connection failed.")
        print(status["error"])

    close_db()


if __name__ == "__main__":
    main()
