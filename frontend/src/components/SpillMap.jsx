import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

export default function SpillMap({ spill, candidates }) {
  const containerRef = useRef(null);
  const mapRef = useRef(null);

  useEffect(() => {
    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!containerRef.current || !spill) {
      return;
    }

    if (!mapRef.current) {
      mapRef.current = L.map(containerRef.current, { scrollWheelZoom: true });
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors",
      }).addTo(mapRef.current);
    }

    const map = mapRef.current;
    const layer = L.layerGroup().addTo(map);
    const center = [spill.center.lat, spill.center.lon];

    L.circle(center, {
      radius: Math.sqrt(spill.estimated_area_km2 / Math.PI) * 1000,
      color: "#f5c542",
      fillColor: "#f5c542",
      fillOpacity: 0.25,
      weight: 2,
    })
      .bindPopup(
        `<strong>Simulated spill</strong><br/>${spill.center.lat}, ${spill.center.lon}`
      )
      .addTo(layer);

    L.circleMarker(center, {
      radius: 8,
      color: "#f5c542",
      fillColor: "#fff3b0",
      fillOpacity: 1,
      weight: 2,
    })
      .bindPopup("Simulated spill center")
      .addTo(layer);

    const bounds = [center];

    candidates.forEach((vessel, index) => {
      const point = [vessel.coordinates.lat, vessel.coordinates.lon];
      bounds.push(point);
      L.circleMarker(point, {
        radius: 9,
        color: index === 0 ? "#4cc9f0" : "#90e0ef",
        fillColor: index === 0 ? "#4cc9f0" : "#caf0f8",
        fillOpacity: 1,
        weight: 2,
      })
        .bindPopup(
          `<strong>${vessel.name}</strong><br/>${vessel.vessel_id}<br/>Demo score: ${vessel.attribution_score}`
        )
        .addTo(layer);
    });

    map.invalidateSize();
    map.fitBounds(bounds, { padding: [40, 40], maxZoom: 10 });

    return () => {
      map.removeLayer(layer);
    };
  }, [spill, candidates]);

  return (
    <div className="map-wrap">
      <div className="map-badge">SIMULATED / DEMO DATA</div>
      <div ref={containerRef} className="map-canvas" />
    </div>
  );
}
