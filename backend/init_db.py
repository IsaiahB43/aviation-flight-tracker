import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

create_table_sql = """
CREATE TABLE IF NOT EXISTS aircraft_meta (
    icao24 VARCHAR(10) PRIMARY KEY,
    registration VARCHAR(20),
    type_code VARCHAR(20),
    type_name VARCHAR(100),
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    category VARCHAR(50),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
        cur.execute(create_table_sql)
    conn.commit()

print("aircraft_meta table created successfully.")
