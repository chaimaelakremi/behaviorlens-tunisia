import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { terrain } from '../../services/api'
import StatsCard from '../../components/StatsCard'

export default function Terrain() {
  const [stats, setStats] = useState(null)
  const [agents, setAgents] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([terrain.stats(), terrain.agents()]).then(([s, a]) => {
      setStats(s.data)
      setAgents(a.data)
    }).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="flex items-center justify-center h-64"><p className="text-slate-500">Chargement...</p></div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">🗺️ Terrain</h1>
        <p className="text-slate-500 text-sm mt-1">Agents mobiles avec tablette — mode offline</p>
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard title="Total Soumissions" value={stats?.total_submissions} icon="📋" color="blue" />
        <StatsCard title="Agents Actifs" value={stats?.active_agents} icon="👤" color="green" />
        <StatsCard title="Régions Terrain" value={stats?.by_region?.length} icon="📍" color="purple" />
        <StatsCard title="Groupes d'âge" value={stats?.by_age_group?.length} icon="👥" color="orange" />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-5 shadow-sm">
          <h2 className="font-semibold text-slate-700 mb-4">Collecte par Région</h2>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={stats?.by_region || []} margin={{ bottom: 50 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="region" angle={-30} textAnchor="end" tick={{ fontSize: 10 }} interval={0} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#457B9D" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="bg-white rounded-xl p-5 shadow-sm">
          <h2 className="font-semibold text-slate-700 mb-4">Collecte par Tranche d'Âge</h2>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={stats?.by_age_group || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="age_group" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#2A9D8F" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div className="bg-white rounded-xl p-5 shadow-sm">
        <h2 className="font-semibold text-slate-700 mb-4">Agents Terrain Actifs</h2>
        <table className="w-full text-sm">
          <thead><tr className="border-b border-slate-100">
            <th className="text-left py-2 px-3 text-slate-500 font-medium">ID</th>
            <th className="text-left py-2 px-3 text-slate-500 font-medium">Zone</th>
            <th className="text-left py-2 px-3 text-slate-500 font-medium">Agent</th>
            <th className="text-left py-2 px-3 text-slate-500 font-medium">Région</th>
          </tr></thead>
          <tbody>
            {agents.map(a => (
              <tr key={a.id} className="border-b border-slate-50 hover:bg-slate-50">
                <td className="py-2 px-3 text-slate-400">#{a.id}</td>
                <td className="py-2 px-3 text-slate-700 font-medium">{a.zone || '—'}</td>
                <td className="py-2 px-3 text-slate-500">Utilisateur #{a.user_id}</td>
                <td className="py-2 px-3"><span className="bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded">{a.region || '—'}</span></td>
              </tr>
            ))}
            {!agents.length && <tr><td colSpan={4} className="py-8 text-center text-slate-400">Aucun agent enregistré</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  )
}
