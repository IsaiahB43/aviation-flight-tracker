import { useEffect, useMemo, useRef, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet-rotatedmarker";
import "./App.css";

const DFW_CENTER = [32.8998, -97.0403];

const planeIcon = new L.DivIcon({
  className: "plane-icon",
  html: "✈",
  iconSize: [24, 24],
  iconAnchor: [12, 12],
});

function RotatedPlaneMarker({ plane }) {
  const markerRef = useRef(null);

  useEffect(() => {
    const marker = markerRef.current;
    if (marker && typeof marker.setRotationAngle === "function") {
      marker.setRotationAngle(plane.heading_deg ?? 0);
      marker.setRotationOrigin("center center");
    }
  }, [plane.heading_deg]);

  return (
    <Marker
      ref={markerRef}
      position={[plane.latitude, plane.longitude]}
      icon={planeIcon}
    >
      <Popup>
        <div>
          <strong>{plane.callsign || "Unknown"}</strong>
          <br />
          ICAO24: {plane.icao24}
          <br />
          Country: {plane.origin_country}
          <br />
          Altitude: {plane.altitude_ft ?? "N/A"} ft
          <br />
          Speed: {plane.speed_kt ?? "N/A"} kt
          <br />
          Heading: {plane.heading_deg ?? "N/A"}°
          <br />
          On ground: {plane.on_ground ? "Yes" : "No"}
          <br />
          Type Code: {plane.type_code || "Unknown"}
          <br />
          Type Name: {plane.type_name || "Unknown"}
          <br />
          Manufacturer: {plane.manufacturer || "Unknown"}
          <br />
          Model: {plane.model || "Unknown"}
          <br />
          Category: {plane.category_label || "Unknown"}
        </div>
      </Popup>
    </Marker>
  );
}

function App() {
  const [aircraft, setAircraft] = useState([]);
  const [error, setError] = useState("");
  const [airborneOnly, setAirborneOnly] = useState(false);

  async function fetchAircraft() {
    try {
      const res = await fetch("http://127.0.0.1:8000/aircraft/dfw");
      const data = await res.json();
      setAircraft(data.aircraft || []);
      setError("");
    } catch (err) {
      console.error(err);
      setError("Failed to load aircraft data.");
    }
  }

  useEffect(() => {
    fetchAircraft();
    const interval = setInterval(fetchAircraft, 15000);
    return () => clearInterval(interval);
  }, []);

  const filteredAircraft = useMemo(() => {
    if (!airborneOnly) return aircraft;
    return aircraft.filter((plane) => plane.on_ground === false);
  }, [aircraft, airborneOnly]);

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>DFW Live Flight Tracker</h1>
          <p>Aircraft visible: {filteredAircraft.length}</p>
          {error && <p className="error-text">{error}</p>}
        </div>

        <label className="toggle">
          <input
            type="checkbox"
            checked={airborneOnly}
            onChange={(e) => setAirborneOnly(e.target.checked)}
          />
          Airborne only
        </label>
      </header>

      <MapContainer center={DFW_CENTER} zoom={10} className="map">
        <TileLayer
          attribution="© OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {filteredAircraft.map((plane) => (
          <RotatedPlaneMarker key={plane.icao24} plane={plane} />
        ))}
      </MapContainer>
    </div>
  );
}

export default App;
