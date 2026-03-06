import { useEffect, useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "./App.css";

const DFW_CENTER = [32.8998, -97.0403];

function App() {
  const [aircraft, setAircraft] = useState([]);
  const [error, setError] = useState("");

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

  return (
    <div className="app">
      <header className="header">
        <h1>DFW Live Flight Tracker</h1>
        <p>Aircraft visible: {aircraft.length}</p>
        {error && <p>{error}</p>}
      </header>

      <MapContainer center={DFW_CENTER} zoom={10} className="map">
        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {aircraft.map((plane) => (
          <CircleMarker
            key={plane.icao24}
            center={[plane.latitude, plane.longitude]}
            radius={6}
          >
            <Popup>
              <div>
                <strong>{plane.callsign || "Unknown"}</strong>
                <br />
                ICAO24: {plane.icao24}
                <br />
                Altitude: {plane.altitude_ft ?? "N/A"} ft
                <br />
                Speed: {plane.speed_kt ?? "N/A"} kt
                <br />
                Heading: {plane.heading_deg ?? "N/A"}°
                <br />
                On ground: {plane.on_ground ? "Yes" : "No"}
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
}

export default App;
