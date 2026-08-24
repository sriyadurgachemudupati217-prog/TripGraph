"""
queries.py

All Cypher access for TripGraph goes through this module. Every query is
parameterized - user input is NEVER concatenated into Cypher strings.
"""

from app.database import run_query

# ---------------------------------------------------------------------------
# Graph transformation helpers
# ---------------------------------------------------------------------------

NODE_LABELS = [
    "Country",
    "City",
    "Destination",
    "Attraction",
    "Activity",
    "Hotel",
    "Restaurant",
    "Trip",
    "TravelConcept",
]


def _props_to_node(props: dict, node_type: str):
    """
    Build the frontend-facing node shape from a plain properties dict plus
    a node_type string.

    IMPORTANT: database.run_query() calls record.data() under the hood,
    which recursively flattens Neo4j Node/Relationship objects into plain
    Python dicts of their properties - the .labels / .type metadata is
    NOT preserved on those flattened values. So node type must always be
    pulled out via labels(n) in the Cypher query itself (a plain string
    the driver returns as-is), never via attribute access on the node
    value in Python. This generically detects type for ANY label the
    database returns, without hard-coding individual node types.
    """
    props = props or {}
    return {
        "id": props.get("id"),
        "label": props.get("name", props.get("id")),
        "type": node_type or "Unknown",
        "description": props.get("description", ""),
        **{k: v for k, v in props.items() if k not in ("id", "name", "description")},
    }


# ---------------------------------------------------------------------------
# Full graph
# ---------------------------------------------------------------------------

def get_graph():
    """Return the whole graph transformed into {nodes, edges} shape."""
    query = """
    MATCH (n)-[r]->(m)
    RETURN n, labels(n) AS n_labels, type(r) AS r_type, m, labels(m) AS m_labels
    """
    records = run_query(query)

    nodes = {}
    edges = []

    for record in records:
        n_props, m_props = record["n"], record["m"]
        n_type = (record["n_labels"] or ["Unknown"])[0]
        m_type = (record["m_labels"] or ["Unknown"])[0]

        n_dict = _props_to_node(n_props, n_type)
        m_dict = _props_to_node(m_props, m_type)

        if n_dict["id"]:
            nodes[n_dict["id"]] = n_dict
        if m_dict["id"]:
            nodes[m_dict["id"]] = m_dict

        if n_dict["id"] and m_dict["id"]:
            edges.append(
                {
                    "id": f"{n_dict['id']}-{record['r_type']}-{m_dict['id']}",
                    "source": n_dict["id"],
                    "target": m_dict["id"],
                    "label": record["r_type"],
                }
            )

    return {"nodes": list(nodes.values()), "edges": edges}


# ---------------------------------------------------------------------------
# Entity listings
# ---------------------------------------------------------------------------

def get_all_countries():
    return run_query("MATCH (n:Country) RETURN n ORDER BY n.name")


def get_all_cities():
    query = """
    MATCH (c:City)
    OPTIONAL MATCH (co:Country)-[:CONTAINS]->(c)
    RETURN c, co.name AS country ORDER BY c.name
    """
    return run_query(query)


def get_all_destinations():
    query = """
    MATCH (d:Destination)
    OPTIONAL MATCH (c:City)-[:HAS_DESTINATION]->(d)
    RETURN d, c.name AS city ORDER BY d.name
    """
    return run_query(query)


def get_all_activities():
    return run_query("MATCH (n:Activity) RETURN n ORDER BY n.name")


def get_all_hotels():
    query = """
    MATCH (h:Hotel)
    OPTIONAL MATCH (h)-[:LOCATED_IN]->(c:City)
    RETURN h, c.name AS city ORDER BY h.name
    """
    return run_query(query)


def get_all_restaurants():
    query = """
    MATCH (r:Restaurant)
    OPTIONAL MATCH (r)-[:LOCATED_IN]->(c:City)
    RETURN r, c.name AS city ORDER BY r.name
    """
    return run_query(query)


def get_all_trips():
    return run_query("MATCH (n:Trip) RETURN n ORDER BY n.name")


# ---------------------------------------------------------------------------
# Single entity lookups
# ---------------------------------------------------------------------------

def get_destination(destination_id: str):
    query = """
    MATCH (d:Destination {id: $id})
    OPTIONAL MATCH (c:City)-[:HAS_DESTINATION]->(d)
    OPTIONAL MATCH (co:Country)-[:CONTAINS]->(c)
    RETURN d, c.name AS city, co.name AS country
    """
    result = run_query(query, {"id": destination_id})
    return result[0] if result else None


def get_city(city_id: str):
    query = """
    MATCH (c:City {id: $id})
    OPTIONAL MATCH (co:Country)-[:CONTAINS]->(c)
    RETURN c, co.name AS country
    """
    result = run_query(query, {"id": city_id})
    return result[0] if result else None


def get_country(country_id: str):
    query = "MATCH (co:Country {id: $id}) RETURN co"
    result = run_query(query, {"id": country_id})
    return result[0] if result else None


def get_trip(trip_id: str):
    query = """
    MATCH (t:Trip {id: $id})
    OPTIONAL MATCH (t)-[:VISITS]->(d:Destination)
    OPTIONAL MATCH (t)-[:SUITABLE_FOR]->(tc:TravelConcept)
    RETURN t,
           collect(DISTINCT d.name) AS destinations,
           collect(DISTINCT tc.name) AS concepts
    """
    result = run_query(query, {"id": trip_id})
    return result[0] if result else None


# ---------------------------------------------------------------------------
# Connections / details
# ---------------------------------------------------------------------------

def get_destination_connections(destination_id: str):
    query = """
    MATCH (d:Destination {id: $id})
    OPTIONAL MATCH (d)-[:HAS_ATTRACTION]->(a:Attraction)
    OPTIONAL MATCH (d)-[:OFFERS]->(act:Activity)
    OPTIONAL MATCH (d)-[:HAS_HOTEL]->(h:Hotel)
    OPTIONAL MATCH (d)-[:HAS_RESTAURANT]->(r:Restaurant)
    OPTIONAL MATCH (d)-[:SUITABLE_FOR]->(tc:TravelConcept)
    OPTIONAL MATCH (d)-[:RELATED_TO]->(rd:Destination)
    RETURN
      collect(DISTINCT a.name) AS attractions,
      collect(DISTINCT act.name) AS activities,
      collect(DISTINCT h.name) AS hotels,
      collect(DISTINCT r.name) AS restaurants,
      collect(DISTINCT tc.name) AS travel_concepts,
      collect(DISTINCT rd.name) AS related_destinations
    """
    result = run_query(query, {"id": destination_id})
    return result[0] if result else None


def get_node_details(node_id: str):
    """Generic node lookup used by the details panel, regardless of type."""
    query = """
    MATCH (n {id: $id})
    OPTIONAL MATCH (n)-[r]->(m)
    OPTIONAL MATCH (n2)-[r2]->(n)
    RETURN n,
           collect(DISTINCT {type: type(r), name: m.name, id: m.id, label: labels(m)[0]}) AS outgoing,
           collect(DISTINCT {type: type(r2), name: n2.name, id: n2.id, label: labels(n2)[0]}) AS incoming
    """
    result = run_query(query, {"id": node_id})
    return result[0] if result else None


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def search_nodes(term: str):
    query = """
    MATCH (n)
    WHERE toLower(n.name) CONTAINS toLower($term)
    RETURN n, labels(n) AS n_labels LIMIT 25
    """
    records = run_query(query, {"term": term})
    results = []
    for record in records:
        node_type = (record["n_labels"] or ["Unknown"])[0]
        results.append(_props_to_node(record["n"], node_type))
    return results


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def get_travel_statistics():
    """
    Uses one MATCH per label rather than the newer COUNT{} subquery syntax,
    for broad compatibility with Neo4j/Bolt-compatible databases like
    CognoDB, and computes everything dynamically (never hard-coded).
    """
    labels = {
        "countries": "Country",
        "cities": "City",
        "destinations": "Destination",
        "activities": "Activity",
        "hotels": "Hotel",
        "restaurants": "Restaurant",
        "trips": "Trip",
    }
    stats = {}
    for key, label in labels.items():
        result = run_query(f"MATCH (n:{label}) RETURN count(n) AS total")
        stats[key] = result[0]["total"] if result else 0
    return stats
