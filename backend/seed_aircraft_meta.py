import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

sample_aircraft = [
    {
        "icao24": "a16db9",
        "registration": None,
        "type_code": "B738",
        "type_name": "Boeing 737-800",
        "manufacturer": "Boeing",
        "model": "737-800",
        "category": "Airliner",
    },
    {
        "icao24": "a04e24",
        "registration": None,
        "type_code": "B763",
        "type_name": "Boeing 767-300",
        "manufacturer": "Boeing",
        "model": "767-300",
        "category": "Cargo",
    },
    {
        "icao24": "a61187",
        "registration": None,
        "type_code": "E55P",
        "type_name": "Embraer Phenom 300",
        "manufacturer": "Embraer",
        "model": "Phenom 300",
        "category": "Business Jet",
    },
    {
        "icao24": "aab276",
        "registration": None,
        "type_code": "B763",
        "type_name": "Boeing 767-300",
        "manufacturer": "Boeing",
        "model": "767-300",
        "category": "Cargo",
    },
    {
        "icao24": "aaf503",
        "registration": None,
        "type_code": "C208",
        "type_name": "Cessna 208 Caravan",
        "manufacturer": "Cessna",
        "model": "208 Caravan",
        "category": "Turboprop",
    },
    {
        "icao24": "a728a9",
        "registration": "N560TX",
        "type_code": "C560",
        "type_name": "Cessna Citation V / Ultra",
        "manufacturer": "Cessna",
        "model": "560",
        "category": "Business Jet",
    },
    {
        "icao24": "a35b42",
        "registration": None,
        "type_code": "B738",
        "type_name": "Boeing 737-800",
        "manufacturer": "Boeing",
        "model": "737-800",
        "category": "Airliner",
    },
    {
        "icao24": "a32bf3",
        "registration": None,
        "type_code": "B38M",
        "type_name": "Boeing 737 MAX 8",
        "manufacturer": "Boeing",
        "model": "737 MAX 8",
        "category": "Airliner",
    },
    {
        "icao24": "a0cdf3",
        "registration": None,
        "type_code": "A32X",
        "type_name": "Airbus A320 Family",
        "manufacturer": "Airbus",
        "model": "A320 Family",
        "category": "Airliner",
    },
]

upsert_sql = """
INSERT INTO aircraft_meta (
    icao24,
    registration,
    type_code,
    type_name,
    manufacturer,
    model,
    category
)
VALUES (
    %(icao24)s,
    %(registration)s,
    %(type_code)s,
    %(type_name)s,
    %(manufacturer)s,
    %(model)s,
    %(category)s
)
ON CONFLICT (icao24) DO UPDATE SET
    registration = EXCLUDED.registration,
    type_code = EXCLUDED.type_code,
    type_name = EXCLUDED.type_name,
    manufacturer = EXCLUDED.manufacturer,
    model = EXCLUDED.model,
    category = EXCLUDED.category,
    last_updated = CURRENT_TIMESTAMP;
"""

with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
        for aircraft in sample_aircraft:
            cur.execute(upsert_sql, aircraft)
    conn.commit()

print(f"Seeded {len(sample_aircraft)} aircraft metadata records.")
