"""
seed_data.py

Populates CognoDB with a meaningful, idempotent TripGraph demo dataset.
Uses MERGE everywhere so running this script multiple times never creates
duplicate nodes or relationships.

Run with:
    python -m app.seed_data
"""

from app.database import connect_to_db, close_db, run_query
from app.graph_schema import create_constraints

# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------

COUNTRIES = [
    {"id": "india", "name": "India", "continent": "Asia",
     "description": "A vast and diverse country known for its ancient history, spirituality, cuisine and landscapes."},
    {"id": "france", "name": "France", "continent": "Europe",
     "description": "Renowned for its art, cuisine, fashion and iconic landmarks."},
    {"id": "japan", "name": "Japan", "continent": "Asia",
     "description": "A blend of ultra-modern cities and centuries-old traditions."},
    {"id": "italy", "name": "Italy", "continent": "Europe",
     "description": "Home to Renaissance art, ancient ruins and celebrated cuisine."},
    {"id": "uae", "name": "United Arab Emirates", "continent": "Asia",
     "description": "A modern desert nation known for luxury, skyscrapers and shopping."},
    {"id": "thailand", "name": "Thailand", "continent": "Asia",
     "description": "Famous for tropical beaches, ornate temples and vibrant street life."},
    {"id": "australia", "name": "Australia", "continent": "Oceania",
     "description": "An island continent with iconic coastlines and unique wildlife."},
    {"id": "switzerland", "name": "Switzerland", "continent": "Europe",
     "description": "Known for the Alps, precision, and picturesque alpine towns."},
]

CITIES = [
    {"id": "hyderabad", "name": "Hyderabad", "country": "india", "latitude": 17.385, "longitude": 78.4867,
     "description": "A city blending Nizami heritage with a booming tech industry."},
    {"id": "delhi", "name": "Delhi", "country": "india", "latitude": 28.6139, "longitude": 77.2090,
     "description": "India's capital, layered with centuries of history."},
    {"id": "mumbai", "name": "Mumbai", "country": "india", "latitude": 19.0760, "longitude": 72.8777,
     "description": "India's financial capital and home of Bollywood."},
    {"id": "paris", "name": "Paris", "country": "france", "latitude": 48.8566, "longitude": 2.3522,
     "description": "The capital of France, celebrated for art, romance and architecture."},
    {"id": "tokyo", "name": "Tokyo", "country": "japan", "latitude": 35.6762, "longitude": 139.6503,
     "description": "Japan's futuristic capital, blending neon streets with quiet shrines."},
    {"id": "kyoto", "name": "Kyoto", "country": "japan", "latitude": 35.0116, "longitude": 135.7681,
     "description": "Japan's former capital, famed for temples and traditional culture."},
    {"id": "rome", "name": "Rome", "country": "italy", "latitude": 41.9028, "longitude": 12.4964,
     "description": "The Eternal City, filled with ancient ruins and timeless art."},
    {"id": "venice", "name": "Venice", "country": "italy", "latitude": 45.4408, "longitude": 12.3155,
     "description": "A romantic city built on canals in northeastern Italy."},
    {"id": "dubai", "name": "Dubai", "country": "uae", "latitude": 25.2048, "longitude": 55.2708,
     "description": "A glittering desert metropolis known for luxury and innovation."},
    {"id": "bangkok", "name": "Bangkok", "country": "thailand", "latitude": 13.7563, "longitude": 100.5018,
     "description": "Thailand's vibrant capital, famous for temples and street food."},
    {"id": "sydney", "name": "Sydney", "country": "australia", "latitude": -33.8688, "longitude": 151.2093,
     "description": "Australia's harbour city, home to the Opera House and beaches."},
    {"id": "zurich", "name": "Zurich", "country": "switzerland", "latitude": 47.3769, "longitude": 8.5417,
     "description": "Switzerland's largest city, a gateway to the Alps."},
]

# type is one of: Historical, Cultural, Nature, Adventure, Beach, Mountain
DESTINATIONS = [
    {"id": "eiffel-tower", "name": "Eiffel Tower", "city": "paris", "type": "Historical",
     "best_time": "April - October",
     "description": "Paris's iron landmark and one of the most visited monuments in the world."},
    {"id": "louvre-museum", "name": "Louvre Museum", "city": "paris", "type": "Cultural",
     "best_time": "Year-round",
     "description": "The world's largest art museum, home to the Mona Lisa."},
    {"id": "seine-river", "name": "Seine River", "city": "paris", "type": "Nature",
     "best_time": "May - September",
     "description": "The river winding through Paris, best explored by evening boat cruise."},
    {"id": "tokyo-tower", "name": "Tokyo Tower", "city": "tokyo", "type": "Historical",
     "best_time": "March - May, September - November",
     "description": "An iconic communications tower with sweeping views of Tokyo."},
    {"id": "mount-fuji", "name": "Mount Fuji", "city": "tokyo", "type": "Mountain",
     "best_time": "July - September",
     "description": "Japan's highest peak and an enduring symbol of the country."},
    {"id": "fushimi-inari-shrine", "name": "Fushimi Inari Shrine", "city": "kyoto", "type": "Cultural",
     "best_time": "October - April",
     "description": "Famed for thousands of vermillion torii gates winding up the mountain."},
    {"id": "colosseum", "name": "Colosseum", "city": "rome", "type": "Historical",
     "best_time": "April - June, September - October",
     "description": "The largest ancient amphitheatre ever built, at the heart of Rome."},
    {"id": "venice-grand-canal", "name": "Venice Grand Canal", "city": "venice", "type": "Cultural",
     "best_time": "April - June, September - October",
     "description": "The main waterway through Venice, lined with historic palaces."},
    {"id": "burj-khalifa", "name": "Burj Khalifa", "city": "dubai", "type": "Historical",
     "best_time": "November - March",
     "description": "The tallest building in the world, offering panoramic desert and sea views."},
    {"id": "palm-jumeirah", "name": "Palm Jumeirah", "city": "dubai", "type": "Beach",
     "best_time": "November - March",
     "description": "An artificial island famed for resorts and beach clubs."},
    {"id": "grand-palace-bangkok", "name": "Grand Palace Bangkok", "city": "bangkok", "type": "Cultural",
     "best_time": "November - February",
     "description": "The ornate former royal residence and spiritual heart of Thailand."},
    {"id": "bondi-beach", "name": "Bondi Beach", "city": "sydney", "type": "Beach",
     "best_time": "September - April",
     "description": "One of the world's most famous beaches, popular for surfing."},
    {"id": "swiss-alps", "name": "Swiss Alps", "city": "zurich", "type": "Mountain",
     "best_time": "December - March, June - September",
     "description": "A dramatic mountain range offering skiing, hiking and alpine scenery."},
    {"id": "charminar", "name": "Charminar", "city": "hyderabad", "type": "Historical",
     "best_time": "October - February",
     "description": "A 16th-century mosque and monument, the symbol of Hyderabad."},
]

ACTIVITIES = [
    {"id": "sightseeing", "name": "Sightseeing", "category": "General",
     "description": "Guided or self-paced exploration of a destination's landmarks."},
    {"id": "museum-visit", "name": "Museum Visit", "category": "Cultural",
     "description": "Exploring art, history and culture inside a museum."},
    {"id": "hiking", "name": "Hiking", "category": "Adventure",
     "description": "Trekking scenic trails, often in mountains or nature reserves."},
    {"id": "beach-activities", "name": "Beach Activities", "category": "Leisure",
     "description": "Swimming, sunbathing and beach games by the coast."},
    {"id": "scuba-diving", "name": "Scuba Diving", "category": "Adventure",
     "description": "Exploring underwater reefs and marine life."},
    {"id": "food-tour", "name": "Food Tour", "category": "Culinary",
     "description": "Guided tasting of a destination's signature dishes and street food."},
    {"id": "shopping", "name": "Shopping", "category": "Leisure",
     "description": "Browsing local markets, malls and boutiques."},
    {"id": "photography", "name": "Photography", "category": "Creative",
     "description": "Capturing landmarks, landscapes and street scenes."},
    {"id": "temple-visit", "name": "Temple Visit", "category": "Cultural",
     "description": "Visiting sacred temples and shrines."},
    {"id": "skiing", "name": "Skiing", "category": "Adventure",
     "description": "Downhill or cross-country skiing on mountain slopes."},
    {"id": "desert-safari", "name": "Desert Safari", "category": "Adventure",
     "description": "Dune bashing and camping under the stars in the desert."},
    {"id": "boat-ride", "name": "Boat Ride", "category": "Leisure",
     "description": "Cruising along rivers, canals or coastlines."},
]

HOTELS = [
    {"id": "paris-central-stay", "name": "Paris Central Stay", "city": "paris", "rating": 4.5, "price_range": "$$$",
     "description": "A boutique hotel steps away from central Paris landmarks."},
    {"id": "tokyo-garden-hotel", "name": "Tokyo Garden Hotel", "city": "tokyo", "rating": 4.6, "price_range": "$$$",
     "description": "A serene hotel with a traditional garden in the heart of Tokyo."},
    {"id": "kyoto-heritage-inn", "name": "Kyoto Heritage Inn", "city": "kyoto", "rating": 4.7, "price_range": "$$",
     "description": "A traditional ryokan-style inn near Kyoto's historic shrines."},
    {"id": "rome-city-suites", "name": "Rome City Suites", "city": "rome", "rating": 4.4, "price_range": "$$$",
     "description": "Modern suites within walking distance of ancient Rome."},
    {"id": "dubai-skyline-hotel", "name": "Dubai Skyline Hotel", "city": "dubai", "rating": 4.8, "price_range": "$$$$",
     "description": "A luxury tower hotel with views of the Dubai skyline."},
    {"id": "bangkok-riverside-stay", "name": "Bangkok Riverside Stay", "city": "bangkok", "rating": 4.3, "price_range": "$$",
     "description": "A relaxed riverside hotel close to Bangkok's cultural sites."},
    {"id": "sydney-harbour-hotel", "name": "Sydney Harbour Hotel", "city": "sydney", "rating": 4.6, "price_range": "$$$",
     "description": "Waterfront hotel with views over Sydney Harbour."},
    {"id": "zurich-alpine-lodge", "name": "Zurich Alpine Lodge", "city": "zurich", "rating": 4.5, "price_range": "$$$",
     "description": "A cozy alpine-style lodge on the edge of Zurich."},
]

RESTAURANTS = [
    {"id": "paris-table", "name": "Paris Table", "city": "paris", "cuisine": "French", "price_range": "$$$",
     "description": "Classic French fine dining near the Seine."},
    {"id": "tokyo-bento-house", "name": "Tokyo Bento House", "city": "tokyo", "cuisine": "Japanese", "price_range": "$$",
     "description": "A casual spot serving fresh bento boxes and sushi."},
    {"id": "kyoto-garden-kitchen", "name": "Kyoto Garden Kitchen", "city": "kyoto", "cuisine": "Japanese", "price_range": "$$",
     "description": "Traditional kaiseki-style dining overlooking a garden."},
    {"id": "roma-bistro", "name": "Roma Bistro", "city": "rome", "cuisine": "Italian", "price_range": "$$",
     "description": "Family-run trattoria serving classic Roman pasta dishes."},
    {"id": "dubai-spice-house", "name": "Dubai Spice House", "city": "dubai", "cuisine": "Middle Eastern", "price_range": "$$$",
     "description": "Aromatic Middle Eastern cuisine in an elegant setting."},
    {"id": "bangkok-street-kitchen", "name": "Bangkok Street Kitchen", "city": "bangkok", "cuisine": "Thai", "price_range": "$",
     "description": "Authentic Thai street food in a lively market setting."},
    {"id": "sydney-harbour-grill", "name": "Sydney Harbour Grill", "city": "sydney", "cuisine": "Seafood", "price_range": "$$$",
     "description": "Fresh seafood grill with harbour views."},
    {"id": "zurich-alpine-kitchen", "name": "Zurich Alpine Kitchen", "city": "zurich", "cuisine": "Swiss", "price_range": "$$$",
     "description": "Hearty Swiss classics like fondue and rösti."},
]

TRAVEL_CONCEPTS = [
    {"id": "luxury-travel", "name": "Luxury Travel", "description": "High-end travel with premium comfort and service."},
    {"id": "budget-travel", "name": "Budget Travel", "description": "Cost-conscious travel that maximizes value."},
    {"id": "adventure-travel", "name": "Adventure Travel", "description": "Travel centered on outdoor thrills and exploration."},
    {"id": "solo-travel", "name": "Solo Travel", "description": "Independent travel designed for a single traveler."},
    {"id": "family-travel", "name": "Family Travel", "description": "Travel suited for groups with children."},
    {"id": "romantic-travel", "name": "Romantic Travel", "description": "Travel designed for couples and romantic getaways."},
    {"id": "cultural-tourism", "name": "Cultural Tourism", "description": "Travel focused on heritage, art and local traditions."},
    {"id": "nature-travel", "name": "Nature Travel", "description": "Travel centered on landscapes and the outdoors."},
    {"id": "beach-vacation", "name": "Beach Vacation", "description": "Relaxed travel centered on coastlines and beaches."},
    {"id": "winter-travel", "name": "Winter Travel", "description": "Travel built around snow, skiing and winter scenery."},
    {"id": "food-tourism", "name": "Food Tourism", "description": "Travel centered on regional cuisine and culinary experiences."},
    {"id": "photography-travel", "name": "Photography Travel", "description": "Travel planned around capturing iconic and scenic shots."},
]

TRIPS = [
    {"id": "paris-cultural-escape", "name": "Paris Cultural Escape", "duration_days": 7, "budget": 150000,
     "description": "A week of art, history and romance in the French capital.",
     "destinations": ["eiffel-tower", "louvre-museum", "seine-river"],
     "concepts": ["cultural-tourism", "romantic-travel", "photography-travel"]},
    {"id": "japan-adventure", "name": "Japan Adventure", "duration_days": 10, "budget": 220000,
     "description": "From Tokyo's neon streets to Kyoto's ancient shrines and Mount Fuji.",
     "destinations": ["tokyo-tower", "mount-fuji", "fushimi-inari-shrine"],
     "concepts": ["adventure-travel", "cultural-tourism", "photography-travel"]},
    {"id": "italian-heritage-tour", "name": "Italian Heritage Tour", "duration_days": 8, "budget": 180000,
     "description": "Ancient ruins in Rome and romantic canals in Venice.",
     "destinations": ["colosseum", "venice-grand-canal"],
     "concepts": ["cultural-tourism", "romantic-travel", "food-tourism"]},
    {"id": "dubai-luxury-weekend", "name": "Dubai Luxury Weekend", "duration_days": 4, "budget": 200000,
     "description": "A short, indulgent escape to the top of the Burj Khalifa and beyond.",
     "destinations": ["burj-khalifa", "palm-jumeirah"],
     "concepts": ["luxury-travel", "beach-vacation"]},
    {"id": "thailand-beach-trip", "name": "Thailand Beach Trip", "duration_days": 6, "budget": 90000,
     "description": "Temples, street food and tropical beach time in Thailand.",
     "destinations": ["grand-palace-bangkok"],
     "concepts": ["budget-travel", "beach-vacation", "food-tourism"]},
    {"id": "swiss-alpine-journey", "name": "Swiss Alpine Journey", "duration_days": 6, "budget": 250000,
     "description": "Skiing and alpine scenery through the Swiss mountains.",
     "destinations": ["swiss-alps"],
     "concepts": ["winter-travel", "nature-travel", "adventure-travel"]},
    {"id": "australian-coastal-adventure", "name": "Australian Coastal Adventure", "duration_days": 9, "budget": 210000,
     "description": "Surf, sun and harbour views along Australia's east coast.",
     "destinations": ["bondi-beach"],
     "concepts": ["adventure-travel", "beach-vacation", "nature-travel"]},
    {"id": "india-heritage-explorer", "name": "India Heritage Explorer", "duration_days": 8, "budget": 80000,
     "description": "A journey through Hyderabad's Nizami monuments and local cuisine.",
     "destinations": ["charminar"],
     "concepts": ["cultural-tourism", "budget-travel", "food-tourism"]},
]

# Destination -> activities offered (by destination id)
DESTINATION_ACTIVITIES = {
    "eiffel-tower": ["sightseeing", "photography"],
    "louvre-museum": ["museum-visit", "sightseeing"],
    "seine-river": ["boat-ride", "photography"],
    "tokyo-tower": ["sightseeing", "photography"],
    "mount-fuji": ["hiking", "photography"],
    "fushimi-inari-shrine": ["temple-visit", "hiking"],
    "colosseum": ["sightseeing", "museum-visit"],
    "venice-grand-canal": ["boat-ride", "photography"],
    "burj-khalifa": ["sightseeing", "shopping"],
    "palm-jumeirah": ["beach-activities", "scuba-diving"],
    "grand-palace-bangkok": ["temple-visit", "sightseeing"],
    "bondi-beach": ["beach-activities", "scuba-diving"],
    "swiss-alps": ["skiing", "hiking"],
    "charminar": ["sightseeing", "shopping", "food-tour"],
}

# Destination -> suitable travel concepts
DESTINATION_CONCEPTS = {
    "eiffel-tower": ["romantic-travel", "cultural-tourism", "photography-travel"],
    "louvre-museum": ["cultural-tourism", "photography-travel"],
    "seine-river": ["romantic-travel", "photography-travel"],
    "tokyo-tower": ["photography-travel", "cultural-tourism"],
    "mount-fuji": ["adventure-travel", "nature-travel", "photography-travel"],
    "fushimi-inari-shrine": ["cultural-tourism", "photography-travel"],
    "colosseum": ["cultural-tourism", "family-travel"],
    "venice-grand-canal": ["romantic-travel", "cultural-tourism"],
    "burj-khalifa": ["luxury-travel", "photography-travel"],
    "palm-jumeirah": ["luxury-travel", "beach-vacation"],
    "grand-palace-bangkok": ["cultural-tourism", "budget-travel"],
    "bondi-beach": ["beach-vacation", "adventure-travel"],
    "swiss-alps": ["winter-travel", "nature-travel", "adventure-travel"],
    "charminar": ["cultural-tourism", "budget-travel", "food-tourism"],
}

# Activity -> related travel concepts
ACTIVITY_CONCEPTS = {
    "sightseeing": ["cultural-tourism", "family-travel"],
    "museum-visit": ["cultural-tourism"],
    "hiking": ["adventure-travel", "nature-travel"],
    "beach-activities": ["beach-vacation", "family-travel"],
    "scuba-diving": ["adventure-travel", "beach-vacation"],
    "food-tour": ["food-tourism"],
    "shopping": ["luxury-travel", "budget-travel"],
    "photography": ["photography-travel"],
    "temple-visit": ["cultural-tourism", "solo-travel"],
    "skiing": ["winter-travel", "adventure-travel"],
    "desert-safari": ["adventure-travel", "luxury-travel"],
    "boat-ride": ["romantic-travel", "nature-travel"],
}

# Pairs of cities that are thematically related (cross-country connections)
RELATED_CITIES = [
    ("paris", "venice"),
    ("tokyo", "bangkok"),
    ("dubai", "zurich"),
    ("sydney", "bangkok"),
    ("hyderabad", "delhi"),
]


# ---------------------------------------------------------------------------
# Seeding functions
# ---------------------------------------------------------------------------

def seed_countries():
    for c in COUNTRIES:
        run_query(
            """
            MERGE (n:Country {id: $id})
            SET n.name = $name, n.continent = $continent, n.description = $description
            """,
            c,
        )


def seed_cities():
    for c in CITIES:
        run_query(
            """
            MERGE (n:City {id: $id})
            SET n.name = $name, n.description = $description,
                n.latitude = $latitude, n.longitude = $longitude
            WITH n
            MATCH (co:Country {id: $country})
            MERGE (co)-[:CONTAINS]->(n)
            """,
            c,
        )

    for city_a, city_b in RELATED_CITIES:
        run_query(
            """
            MATCH (a:City {id: $a}), (b:City {id: $b})
            MERGE (a)-[:RELATED_TO]->(b)
            """,
            {"a": city_a, "b": city_b},
        )


def seed_destinations():
    for d in DESTINATIONS:
        run_query(
            """
            MERGE (n:Destination {id: $id})
            SET n.name = $name, n.description = $description,
                n.type = $type, n.best_time = $best_time
            WITH n
            MATCH (c:City {id: $city})
            MERGE (c)-[:HAS_DESTINATION]->(n)
            """,
            d,
        )
        # Every destination gets a matching Attraction record.
        run_query(
            """
            MATCH (d:Destination {id: $id})
            MERGE (a:Attraction {id: $id + '-attraction'})
            SET a.name = $name, a.description = $description, a.category = $type
            MERGE (d)-[:HAS_ATTRACTION]->(a)
            """,
            d,
        )

    # Related destinations: link destinations that share a city.
    by_city = {}
    for d in DESTINATIONS:
        by_city.setdefault(d["city"], []).append(d["id"])
    for city_id, dest_ids in by_city.items():
        for i in range(len(dest_ids)):
            for j in range(len(dest_ids)):
                if i != j:
                    run_query(
                        """
                        MATCH (a:Destination {id: $a}), (b:Destination {id: $b})
                        MERGE (a)-[:RELATED_TO]->(b)
                        """,
                        {"a": dest_ids[i], "b": dest_ids[j]},
                    )


def seed_activities():
    for a in ACTIVITIES:
        run_query(
            """
            MERGE (n:Activity {id: $id})
            SET n.name = $name, n.description = $description, n.category = $category
            """,
            a,
        )

    for activity_id, concept_ids in ACTIVITY_CONCEPTS.items():
        for concept_id in concept_ids:
            run_query(
                """
                MATCH (a:Activity {id: $activity_id}), (c:TravelConcept {id: $concept_id})
                MERGE (a)-[:RELATED_TO]->(c)
                """,
                {"activity_id": activity_id, "concept_id": concept_id},
            )


def seed_hotels():
    for h in HOTELS:
        run_query(
            """
            MERGE (n:Hotel {id: $id})
            SET n.name = $name, n.description = $description,
                n.rating = $rating, n.price_range = $price_range
            WITH n
            MATCH (c:City {id: $city})
            MERGE (n)-[:LOCATED_IN]->(c)
            """,
            h,
        )


def seed_restaurants():
    for r in RESTAURANTS:
        run_query(
            """
            MERGE (n:Restaurant {id: $id})
            SET n.name = $name, n.description = $description,
                n.cuisine = $cuisine, n.price_range = $price_range
            WITH n
            MATCH (c:City {id: $city})
            MERGE (n)-[:LOCATED_IN]->(c)
            """,
            r,
        )


def seed_travel_concepts():
    for tc in TRAVEL_CONCEPTS:
        run_query(
            """
            MERGE (n:TravelConcept {id: $id})
            SET n.name = $name, n.description = $description
            """,
            tc,
        )


def seed_trips():
    for t in TRIPS:
        run_query(
            """
            MERGE (n:Trip {id: $id})
            SET n.name = $name, n.description = $description,
                n.duration_days = $duration_days, n.budget = $budget
            """,
            {k: v for k, v in t.items() if k not in ("destinations", "concepts")},
        )
        for dest_id in t["destinations"]:
            run_query(
                """
                MATCH (t:Trip {id: $trip_id}), (d:Destination {id: $dest_id})
                MERGE (t)-[:VISITS]->(d)
                """,
                {"trip_id": t["id"], "dest_id": dest_id},
            )
        for concept_id in t["concepts"]:
            run_query(
                """
                MATCH (t:Trip {id: $trip_id}), (c:TravelConcept {id: $concept_id})
                MERGE (t)-[:SUITABLE_FOR]->(c)
                """,
                {"trip_id": t["id"], "concept_id": concept_id},
            )


def create_relationships():
    """Cross-cutting relationships that depend on multiple entity sets."""
    # Destination -> Activity (OFFERS)
    for dest_id, activity_ids in DESTINATION_ACTIVITIES.items():
        for activity_id in activity_ids:
            run_query(
                """
                MATCH (d:Destination {id: $dest_id}), (a:Activity {id: $activity_id})
                MERGE (d)-[:OFFERS]->(a)
                """,
                {"dest_id": dest_id, "activity_id": activity_id},
            )

    # Destination -> TravelConcept (SUITABLE_FOR)
    for dest_id, concept_ids in DESTINATION_CONCEPTS.items():
        for concept_id in concept_ids:
            run_query(
                """
                MATCH (d:Destination {id: $dest_id}), (c:TravelConcept {id: $concept_id})
                MERGE (d)-[:SUITABLE_FOR]->(c)
                """,
                {"dest_id": dest_id, "concept_id": concept_id},
            )

    # Destination -> Hotel / Restaurant (same city)
    dest_by_city = {}
    for d in DESTINATIONS:
        dest_by_city.setdefault(d["city"], []).append(d["id"])

    for h in HOTELS:
        for dest_id in dest_by_city.get(h["city"], []):
            run_query(
                """
                MATCH (d:Destination {id: $dest_id}), (h:Hotel {id: $hotel_id})
                MERGE (d)-[:HAS_HOTEL]->(h)
                """,
                {"dest_id": dest_id, "hotel_id": h["id"]},
            )

    for r in RESTAURANTS:
        for dest_id in dest_by_city.get(r["city"], []):
            run_query(
                """
                MATCH (d:Destination {id: $dest_id}), (r:Restaurant {id: $restaurant_id})
                MERGE (d)-[:HAS_RESTAURANT]->(r)
                """,
                {"dest_id": dest_id, "restaurant_id": r["id"]},
            )


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def run_seed():
    print("Connecting to CognoDB...")
    connect_to_db()

    print("Creating schema...")
    create_constraints(run_query)

    print("Seeding countries...")
    seed_countries()

    print("Seeding cities...")
    seed_cities()

    print("Seeding destinations...")
    seed_destinations()

    print("Seeding activities...")
    seed_activities()

    print("Seeding hotels...")
    seed_hotels()

    print("Seeding restaurants...")
    seed_restaurants()

    print("Seeding travel concepts...")
    seed_travel_concepts()

    print("Seeding trips...")
    seed_trips()

    print("Creating relationships...")
    create_relationships()

    print("Seed completed successfully.")
    close_db()


if __name__ == "__main__":
    run_seed()
