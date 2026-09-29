import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import icon from "leaflet/dist/images/marker-icon.png";
import iconShadow from "leaflet/dist/images/marker-shadow.png";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: icon,
  shadowUrl: iconShadow,
});

const zoneColors = {
  RESIDENTIAL: "#f4d35e",
  COMMERCIAL: "#ee6c4d",
  GREEN: "#70a37f",
  AGRI: "#b7d968",
};

export default function App() {
  const mapEl = useRef(null);
  const mapRef = useRef(null);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
  let cancelled = false;
  const map = L.map(mapEl.current).setView([30.74, 76.786], 15);
  mapRef.current = map;

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);

  fetch("http://localhost:8000/parcels/bbox?minx=76.775&miny=30.730&maxx=76.790&maxy=30.740")
    .then((r) => r.json())
    .then((geojson) => {
      if (cancelled) return;   // map was already torn down, do nothing
      L.geoJSON(geojson, {
        style: (feature) => ({
          fillColor: zoneColors[feature.properties.zone] || "#cccccc",
          fillOpacity: 0.55,
          color: feature.properties.disputed ? "#d00000" : feature.properties.encumbered ? "#6a00f4" : "#444",
          weight: feature.properties.disputed || feature.properties.encumbered ? 2.5 : 1,
        }),
        onEachFeature: (feature, layer) => {
          layer.on("click", () => {
            const ulpin = feature.properties.ulpin;
            fetch(`http://localhost:8000/parcels/${ulpin}`)
              .then((r) => r.json())
              .then(setSelected);
          });
        },
      }).addTo(map);
    });

  return () => {
    cancelled = true;
    map.remove();
  };
}, []);
  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <div ref={mapEl} style={{ flex: 1 }} />
      <div style={{ width: 300, padding: 16, overflowY: "auto", background: "#fafafa" }}>
        <h3>Parcel details</h3>
        {selected ? (
          <pre style={{ whiteSpace: "pre-wrap", fontSize: 12 }}>
            {JSON.stringify(selected, null, 2)}
          </pre>
        ) : (
          <p>Click a parcel on the map</p>
        )}
      </div>
    </div>
  );
}