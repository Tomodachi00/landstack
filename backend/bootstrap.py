import os
import subprocess
import sys
from pathlib import Path

import psycopg2


BACKEND_DIR = Path(__file__).parent
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:landstack@localhost:5432/landstack"
)

with psycopg2.connect(DATABASE_URL) as connection:
    with connection.cursor() as cursor:
        cursor.execute((BACKEND_DIR / "init.sql").read_text(encoding="utf-8"))
        cursor.execute("SELECT COUNT(*) FROM parcel")
        should_seed = cursor.fetchone()[0] == 0

if should_seed:
    subprocess.run([sys.executable, str(BACKEND_DIR / "seed.py")], check=True)