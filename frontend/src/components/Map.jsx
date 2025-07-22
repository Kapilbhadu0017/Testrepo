import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { useState } from 'react';

function MapEvents({ onMapClick }) {
  useMapEvents({
    click(e) {
      onMapClick(e.latlng);
    },
  });
  return null;
}

export default function Map({ onLocationSelect, theme }) {
    const [position, setPosition] = useState([28.6139, 77.2090]); // Default to Delhi
    const [markerPosition, setMarkerPosition] = useState(null);
  
    const handleMapClick = (latlng) => {
      setMarkerPosition(latlng);
      onLocationSelect(latlng);
    };

    const isDark = theme === 'dark';
  
    return (
      <div className={`h-96 w-full rounded-lg shadow-lg mt-4 border-2 ${isDark ? 'border-purple-500/50' : 'border-green-300'}`}>
        <MapContainer 
            center={position} 
            zoom={5} 
            scrollWheelZoom={true} 
            style={{ height: '100%', width: '100%', borderRadius: 'inherit' }}
            className={isDark ? 'map-dark' : ''}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {markerPosition && (
            <Marker position={markerPosition}>
              <Popup>
                Selected Location <br /> Lat: {markerPosition.lat.toFixed(4)}, Lon: {markerPosition.lng.toFixed(4)}
              </Popup>
            </Marker>
          )}
          <MapEvents onMapClick={handleMapClick} />
        </MapContainer>
      </div>
    );
  } 