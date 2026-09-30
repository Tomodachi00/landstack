import os
import random, psycopg2
from shapely.geometry import box

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:landstack@localhost:5432/landstack")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

NAMES = ["Rajesh Kumar", "Sunita Devi", "Harpreet Singh", "Meena Sharma", "Anil Verma"]
ZONES = ["RESIDENTIAL", "RESIDENTIAL", "COMMERCIAL", "AGRI", "GREEN"]

lon0, lat0 = 76.7794, 30.7333
step = 0.0004
n = 0

for r in range(15):
    for c in range(15):
        n += 1
        x, y = lon0 + c * step, lat0 + r * step
        poly = box(x, y, x + step * 0.85, y + step * 0.85)
        ulpin = f"CHD{n:05d}"

        cur.execute(
            "INSERT INTO parcel VALUES (%s, %s, %s, %s, ST_GeomFromText(%s, 4326))",
            (ulpin, "Chandigarh", f"{r+1}/{c+1}", round(random.uniform(100, 500), 1), poly.wkt)
        )
        cur.execute(
            "INSERT INTO ror(ulpin, owner_name, tenure) VALUES (%s, %s, 'FREEHOLD')",
            (ulpin, random.choice(NAMES))
        )
        cur.execute(
            "INSERT INTO landuse_zone(ulpin, zone) VALUES (%s, %s)",
            (ulpin, random.choice(ZONES))
        )
        if random.random() < 0.15:
            cur.execute(
                "INSERT INTO encumbrance(ulpin, kind) VALUES (%s, 'MORTGAGE')",
                (ulpin,)
            )
        if random.random() < 0.05:
            cur.execute(
                "INSERT INTO dispute(ulpin, status) VALUES (%s, 'PENDING')",
                (ulpin,)
            )

conn.commit()
print(f"seeded {n} parcels")