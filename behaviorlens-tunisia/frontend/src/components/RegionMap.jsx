import { MapContainer, TileLayer, CircleMarker, Tooltip } from 'react-leaflet'

export default function RegionMap({ data = [] }) {
  const maxCount = Math.max(...data.map(d => d.count), 1)

  return (
    <MapContainer center={[34.5, 9.0]} zoom={6} className="w-full" style={{ height: '400px', borderRadius: '12px' }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; OpenStreetMap'
      />
      {data.filter(d => d.latitude && d.longitude).map((d, i) => (
        <CircleMarker
          key={i}
          center={[d.latitude, d.longitude]}
          radius={Math.max(6, (d.count / maxCount) * 30)}
          fillColor="#E63946"
          color="#fff"
          weight={2}
          fillOpacity={0.75}
        >
          <Tooltip>
            <strong>{d.region}</strong><br />
            {d.count} enregistrements
          </Tooltip>
        </CircleMarker>
      ))}
    </MapContainer>
  )
}
