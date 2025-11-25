import React from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, Tooltip } from 'react-leaflet';
import { CountryIncident, getCategoryColor } from '@/types/feed';
import 'leaflet/dist/leaflet.css';

interface CrisisMapProps {
  countries: CountryIncident[];
  onCountrySelect?: (country: CountryIncident) => void;
}

const CrisisMap: React.FC<CrisisMapProps> = ({ countries, onCountrySelect }) => {
  // Center roughly on the world or a default location
  const center: [number, number] = [20, 0];
  const zoom = 2;

  return (
    <div className="h-[500px] w-full rounded-lg overflow-hidden border border-border shadow-sm bg-slate-50 relative z-0">
      <MapContainer 
        center={center} 
        zoom={zoom} 
        scrollWheelZoom={false} 
        style={{ height: '100%', width: '100%' }}
        className="z-0"
      >
        {/* CartoDB Positron - Clean, minimal, professional */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
        />

        {countries.map((country) => (
          <CircleMarker
            key={country.iso2}
            center={[country.lat, country.lon]}
            pathOptions={{
              color: getCategoryColor(country.top_category),
              fillColor: getCategoryColor(country.top_category),
              fillOpacity: 0.6,
              weight: 1,
            }}
            radius={Math.max(4, Math.sqrt(country.incidents) * 3)} // Scale radius by incidents
            eventHandlers={{
              click: () => onCountrySelect && onCountrySelect(country),
            }}
          >
            <Tooltip direction="top" offset={[0, -10]} opacity={1}>
              <div className="text-xs font-semibold">
                {country.country}: {country.incidents}
              </div>
            </Tooltip>
            <Popup>
              <div className="p-1 min-w-[200px]">
                <h3 className="font-bold text-sm mb-1">{country.country}</h3>
                <div className="text-xs text-slate-600 mb-2">
                  {country.incidents} incidents
                </div>
                <div className="text-xs font-medium mb-2" style={{ color: getCategoryColor(country.top_category) }}>
                  Top: {country.top_category}
                </div>
                <div className="text-xs text-slate-500">
                  Click for details
                </div>
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
      
      {/* Legend Overlay */}
      <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur-sm p-3 rounded shadow-sm border border-slate-200 text-xs z-[1000]">
        <div className="font-semibold mb-2 text-slate-700">Incident Severity</div>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#0f172a]"></div>
            <span>Human Rights Violations</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#1d4ed8]"></div>
            <span>Political Conflicts</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#0ea5e9]"></div>
            <span>Humanitarian Crises</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CrisisMap;
