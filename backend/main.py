import json
import os
import psycopg2, psycopg2.extras
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:landstack@localhost:5432/landstack")

def q(sql, params=None):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql, params or ())
    rows = cur.fetchall()
    conn.close()
    return rows

@app.get("/parcels/bbox")
def parcels_bbox(minx: float, miny: float, maxx: float, maxy: float):
    rows = q("""
        SELECT p.ulpin, p.survey_no, z.zone,
               EXISTS(SELECT 1 FROM encumbrance e WHERE e.ulpin = p.ulpin AND e.active) AS encumbered,
               EXISTS(SELECT 1 FROM dispute d WHERE d.ulpin = p.ulpin AND d.status = 'PENDING') AS disputed,
               ST_AsGeoJSON(p.geom) AS g
        FROM parcel p
        LEFT JOIN landuse_zone z ON z.ulpin = p.ulpin
        WHERE p.geom && ST_MakeEnvelope(%s, %s, %s, %s, 4326)
    """, (minx, miny, maxx, maxy))
    feats = []
    for r in rows:
        geom = json.loads(r.pop("g"))
        feats.append({"type": "Feature", "geometry": geom, "properties": r})
    return {"type": "FeatureCollection", "features": feats}

@app.get("/parcels/{ulpin}")
def parcel_detail(ulpin: str):
    owner = q("SELECT owner_name, tenure FROM ror WHERE ulpin = %s", (ulpin,))
    zone = q("SELECT zone FROM landuse_zone WHERE ulpin = %s", (ulpin,))
    enc = q("SELECT kind FROM encumbrance WHERE ulpin = %s AND active", (ulpin,))
    dis = q("SELECT status FROM dispute WHERE ulpin = %s AND status = 'PENDING'", (ulpin,))
    return {"ulpin": ulpin, "owners": owner, "zone": zone, "encumbrances": enc, "disputes": dis}