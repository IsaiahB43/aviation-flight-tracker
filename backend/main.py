import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import psycopg
import httpx

load_dotenv()

app = FastAPI()
DATABASE_URL = os.getenv("DATABASE_URL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DFW_BBOX = {
    "lamin": 32.5,
    "lamax": 33.1,
    "lomin": -97.6,
    "lomax": -96.8,
}


def meters_to_feet(value):
    if value is None:
        return None
    return round(value * 3.28084)


def mps_to_knots(value):
    if value is None:
        return None
    return round(value * 1.94384)


def load_aircraft_metadata():
    metadata = {}

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    icao24,
                    registration,
                    type_code,
                    type_name,
                    manufacturer,
                    model,
                    category
                FROM aircraft_meta
            """)
            rows = cur.fetchall()

    for row in rows:
        metadata[row[0]] = {
            "registration": row[1],
            "type_code": row[2],
            "type_name": row[3],
            "manufacturer": row[4],
            "model": row[5],
            "category_label": row[6],
        }

    return metadata


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/db-check")
def db_check():
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT current_database(), current_user;")
                row = cur.fetchone()

        return {
            "status": "ok",
            "database": row[0],
            "user": row[1]
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@app.get("/aircraft/dfw")
async def get_dfw_aircraft():
    url = "https://opensky-network.org/api/states/all"

    try:
        aircraft_metadata = load_aircraft_metadata()

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(url, params=DFW_BBOX)
            response.raise_for_status()
            data = response.json()

        states = data.get("states") or []
        aircraft = []

        for s in states:
            if not s:
                continue

            longitude = s[5]
            latitude = s[6]

            if latitude is None or longitude is None:
                continue

            icao24 = s[0].lower() if s[0] else None
            meta = aircraft_metadata.get(icao24, {})

            aircraft.append({
                "icao24": icao24,
                "callsign": s[1].strip() if s[1] else None,
                "origin_country": s[2],
                "latitude": latitude,
                "longitude": longitude,
                "altitude_ft": meters_to_feet(s[13] if s[13] is not None else s[7]),
                "speed_kt": mps_to_knots(s[9]),
                "heading_deg": round(s[10], 1) if s[10] is not None else None,
                "vertical_rate_fpm": round((s[11] or 0) * 196.850394) if s[11] is not None else None,
                "on_ground": s[8],
                "squawk": s[14],

                "registration": meta.get("registration"),
                "type_code": meta.get("type_code"),
                "type_name": meta.get("type_name"),
                "manufacturer": meta.get("manufacturer"),
                "model": meta.get("model"),
                "category_label": meta.get("category_label"),
            })

        return {
            "count": len(aircraft),
            "aircraft": aircraft
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
@app.get("/aircraft-meta")
def aircraft_meta():
    return load_aircraft_metadata()
