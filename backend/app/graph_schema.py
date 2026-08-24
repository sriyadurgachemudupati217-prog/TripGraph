"""
graph_schema.py

Uniqueness constraints for every node type in the TripGraph data model.
Constraints are idempotent (IF NOT EXISTS) so this is safe to run every
time the seed script executes.
"""

CONSTRAINTS = [
    "CREATE CONSTRAINT country_id_unique IF NOT EXISTS FOR (n:Country) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT city_id_unique IF NOT EXISTS FOR (n:City) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT destination_id_unique IF NOT EXISTS FOR (n:Destination) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT attraction_id_unique IF NOT EXISTS FOR (n:Attraction) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT activity_id_unique IF NOT EXISTS FOR (n:Activity) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT hotel_id_unique IF NOT EXISTS FOR (n:Hotel) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT restaurant_id_unique IF NOT EXISTS FOR (n:Restaurant) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT trip_id_unique IF NOT EXISTS FOR (n:Trip) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT concept_id_unique IF NOT EXISTS FOR (n:TravelConcept) REQUIRE n.id IS UNIQUE",
]


def create_constraints(run_query_fn):
    for statement in CONSTRAINTS:
        run_query_fn(statement)
