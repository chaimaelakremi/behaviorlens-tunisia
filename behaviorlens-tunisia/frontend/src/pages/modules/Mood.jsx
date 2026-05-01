import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'
import { mood } from '../../services/api'
import StatsCard from '../../components/StatsCard'
import { MapContainer, TileLayer, CircleMarker, Tooltip as LeafTooltip } from 'react-leaflet'

const MOOD_COLORS = { 'très heureux': '#2A9D8F', 'heureux': '#57CC99', 'neutre': '#FFB703', 'triste': '#F4A261', 'très triste': '#E63946' }

export default function Mood() {
  const [stats, setStats] = useState(null)
  const [trends, setTrends] = useState([])
  const [moodMap, setMoodMap] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([mood.stats(), mood.trends(), mood.map()]).then(([s, t, m]) => {
      setStats(s.data); setTrends(t.data); setMoodMap(m.data)
    }).finally(() => setLoading(false))
  }, [])

  const moodEmoji = score => score >= 4 ? '😄' : score >= 3 ? '🙂' : score >= 2 ? '😐' : '😔'

  if (loading) return <div className="flex items-center justify-center h-64"><p className="text-slate-500">Chargement...</p></div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">😊 Baromètre d'Humeur</h1>
        <p className="text-slate-500 text-sm mt-1">Comment les Tunisiens se sentent chaque jour par région</p>
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard title="Enregistrements" value={stats?.total_records} icon="📊" color="blue" />
        <StatsCard title="Humeur Moyenne" value={`${(stats?.global_avg_mood || 0).toFixed(1)}/5`} icon="😊" color="green" />
        <StatsCard title="Humeurs" value={stats?.by_mood_label?.length} icon="🎭" color="purple" />
        <StatsCard title="Récents (10)" value={stats?.recent?.length} icon="🔔" color="orange" />
      </div>
      <div className="bg-white rounded-xl p-5 shadow-sm">
        <h2 className="font-semibold text-slate-700 mb-4">Carte Humeur Tunisie</h2>
        <MapContainer center={[34.5, 9.0]} zoom={6} style={{ height: '380px', borderRadius: '12px' }}>
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution='&copy; OpenStreetMap' />
          {moodMap.filter(d => d.latitude && d.longitude).map((d, i) => {
            const color = d.avg_mood >= 4 ? '#2A9D8F' : d.avg_mood >= 3 ? '#FFB703' : '#E63946'
            return (
              <CircleMarker key={i} center={[d.latitude, d.longitude]} radius={Math.max(8, d.count * 2)} fillColor={color} color="#fff" weight={2} fillOpacity={0.8}>
                <LeafTooltip><strong>{d.region}</strong><br/>Humeur: {d.avg_mood.toFixed(1)}/5 ({d.count} votes)</LeafTooltip>
              </CircleMarker>
            )
          })}
        </MapContainer>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-5 shadow-sm">
          <h2 className="font-semibold text-slate-700 mb-4">Évolution de l'Humeur (30 jours)</h2>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={trends}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="date" tick={{ fontSize: 10 }} />
              <YAxis domain={[0, 5]} />
              <Tooltip />
              <Line type="monotone" dataKey="avg_mood" stroke="#FFB703" strokeWidth={2.5} dot={false} name="Humeur Moy." />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="bg-white rounded-xl p-5 shadow-sm">
          <h2 className="font-semibold text-slate-700 mb-4">Distribution des Humeurs</h2>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={stats?.by_mood_label || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="label" tick={{ fontSize: 10 }} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#FFB703" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div className="bg-white rounded-xl p-5 shadow-sm">
        <h2 className="font-semibold text-slate-700 mb-4">Dernières Humeurs Enregistrées</h2>
        <table className="w-full text-sm">
          <thead><tr className="border-b border-slate-100">
            <th className="text-left py-2 px-3 text-slate-500 font-medium">ID</th>
            <th className="text-left py-2 px-3 text-slate-500 font-medium">Score</th>
            <th className="text-left py-2 px-3 text-slate-500 font-medium">Humeur</th>
            <th className="text-left py-2 px-3 text-slate-500 font-medium">Région</th>
            <th className="text-left py-2 px-3 text-slate-500 font-medium">Date</th>
          </tr></thead>
          <tbody>
            {(stats?.recent || []).map(r => (
              <tr key={r.id} className="border-b border-slate-50">
                <td className="py-2 px-3 text-slate-400">#{r.id}</td>
                <td className="py-2 px-3 text-xl">{moodEmoji(r.mood_score)} {r.mood_score}/5</td>
                <td className="py-2 px-3" style={{color: MOOD_COLORS[r.mood_label]}}>{r.mood_label}</td>
                <td className="py-2 px-3 text-slate-500">Région #{r.region_id}</td>
                <td className="py-2 px-3 text-slate-400 text-xs">{new Date(r.created_at).toLocaleString('fr-TN')}</td>
              </tr>
            ))}
            {!stats?.recent?.length && <tr><td colSpan={5} className="py-8 text-center text-slate-400">Aucune humeur enregistrée</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  )
}
