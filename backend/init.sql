CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS parcel (
  ulpin        TEXT PRIMARY KEY,
  district     TEXT,
  survey_no    TEXT,
  area_sqm     NUMERIC,
  geom         geometry(Polygon, 4326)
);

CREATE TABLE IF NOT EXISTS ror (
  id SERIAL PRIMARY KEY,
  ulpin TEXT REFERENCES parcel(ulpin),
  owner_name TEXT,
  tenure TEXT
);

CREATE TABLE IF NOT EXISTS landuse_zone (
  id SERIAL PRIMARY KEY,
  ulpin TEXT REFERENCES parcel(ulpin),
  zone TEXT
);

CREATE TABLE IF NOT EXISTS encumbrance (
  id SERIAL PRIMARY KEY,
  ulpin TEXT REFERENCES parcel(ulpin),
  kind TEXT,
  active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS dispute (
  id SERIAL PRIMARY KEY,
  ulpin TEXT REFERENCES parcel(ulpin),
  status TEXT
);