import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, Legend } from 'recharts'
import { core } from '../services/api'
import StatsCard from '../components/StatsCard'
import RegionMap from '../components/RegionMap'

const MODULE_COLORS = {
  social_media: '#E63946', terrain: '#457B9D', ivr: '#A8DADC',
  commerce: '#F4A261', gamification: '#2A9D8F', open_data: '#8338EC',
  mood: '#FFB703', photo: '#FB8500'
}

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [byModule, setByModule] = useState([])
  const [byRegion, setByRegion] = useState([])
  const [timeline, setTimeline] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      core.stats(), core.statsByModule(), core.statsByRegion(), core.timeline()
    ]).then(([s, m, r, t]) => {
      setStats(s.data)
      setByModule(m.data)
      setByRegion(r.data)
      setTimeline(t.data)
    }).finally(() => setLoading(false))
  }, [])

  const exportCSV = () => {
    const rows = [['Module', 'Enregistrements'], ...byModule.map(m => [m.label || m.module, m.count])]
    const csv = rows.map(r => r.join(',')).join('\n')
    const a = document.createElement('a')
    a.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv)
    a.download = 'behaviorlens_stats.csv'
    a.click()
  }

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="text-slate-500">Chargement des données...</div>
    </div>
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Dashboard Principal</h1>
          <p className="text-slate-500 text-sm mt-1">Vue globale de tous les modules de collecte</p>
        </div>
        <button onClick={exportCSV} className="bg-slate-800 text-white px-4 py-2 rounded-lg text-sm hover:bg-slate-700 transition">
          Exporter CSV
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard title="Données Collectées" value={stats?.total_records} icon="📦" color="blue" />
        <StatsCard title="Modules Actifs" value={stats?.active_modules} icon="⚙️" color="green" />
        <StatsCard title="Régions Couvertes" value={stats?.regions_covered} icon="🗺️" color="purple" />
        <StatsCard title="Joueurs Actifs" value={stats?.active_players} icon="🎮" color="orange" />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-5 shadow-sm">
          <h2 className="font-semibold text-slate-700 mb-4">Données par Module</h2>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={byModule} margin={{ top: 5, right: 10, left: 0, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="label" angle={-35} textAnchor="end" tick={{ fontSize: 11 }} interval={0} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="count" fill="#E63946" radius={[4, 4, 0, 0]}>
                {byModule.map((entry, i) => (
                  <rect key={i} fill={MODULE_COLORS[entry.module] || '#E63946'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm">
          <h2 className="font-semibold text-slate-700 mb-4">Évolution Temporelle (30 jours)</h2>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={timeline}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="date" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Line type="monotone" dataKey="count" stroke="#E63946" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Map */}
      <div className="bg-white rounded-xl p-5 shadow-sm">
        <h2 className="font-semibold text-slate-700 mb-4">Carte Tunisie — Données par Gouvernorat</h2>
        <RegionMap data={byRegion} />
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-xl p-5 shadow-sm">
        <h2 className="font-semibold text-slate-700 mb-4">Activité Récente</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-100">
                <th className="text-left py-2 px-3 text-slate-500 font-medium">ID</th>
                <th className="text-left py-2 px-3 text-slate-500 font-medium">Module</th>
                <th className="text-left py-2 px-3 text-slate-500 font-medium">Type</th>
                <th className="text-left py-2 px-3 text-slate-500 font-medium">Région</th>
                <th className="text-left py-2 px-3 text-slate-500 font-medium">Date</th>
              </tr>
            </thead>
            <tbody>
              {(stats?.recent_activity || []).map(row => (
                <tr key={row.id} className="border-b border-slate-50 hover:bg-slate-50">
                  <td className="py-2 px-3 text-slate-400">#{row.id}</td>
                  <td className="py-2 px-3">
                    <span className="bg-red-100 text-red-700 text-xs px-2 py-0.5 rounded-full">{row.module}</span>
                  </td>
                  <td className="py-2 px-3 text-slate-600">{row.type}</td>
                  <td className="py-2 px-3 text-slate-500">{row.region_id || '—'}</td>
                  <td className="py-2 px-3 text-slate-400 text-xs">{new Date(row.created_at).toLocaleString('fr-TN')}</td>
                </tr>
              ))}
              {(!stats?.recent_activity?.length) && (
                <tr><td colSpan={5} className="py-8 text-center text-slate-400">Aucune activité récente</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
