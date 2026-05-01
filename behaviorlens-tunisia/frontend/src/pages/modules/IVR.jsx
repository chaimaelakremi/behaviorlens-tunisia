import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { ivr } from '../../services/api'
import StatsCard from '../../components/StatsCard'

export default function IVR() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    ivr.stats().then(r => setStats(r.data)).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="flex items-center justify-center h-64"><p className="text-slate-500">Chargement...</p></div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">📞 IVR Téléphone</h1>
        <p className="text-slate-500 text-sm mt-1">Sondages automatisés par téléphone pour personnes âgées</p>
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard title="Campagnes" value={stats?.total_campaigns} icon="📣" color="blue" />
        <StatsCard title="Réponses" value={stats?.total_responses} icon="🎙️" color="green" />
        <StatsCard title="Durée Moyenne" value={`${Math.round(stats?.avg_duration_seconds || 0)}s`} icon="⏱️" color="purple" subtitle="par appel" />
        <StatsCard title="Régions" value={stats?.by_region?.length} icon="📍" color="orange" />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-5 shadow-sm">
          <h2 className="font-semibold text-slate-700 mb-4">Réponses par Région</h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={stats?.by_region || []} margin={{ bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="region" angle={-30} textAnchor="end" tick={{ fontSize: 10 }} interval={0} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#A8DADC" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="bg-white rounded-xl p-5 shadow-sm">
          <h2 className="font-semibold text-slate-700 mb-4">Réponses par Tranche d'Âge</h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={stats?.by_age_group || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="age_group" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#E63946" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div className="bg-white rounded-xl p-5 shadow-sm">
        <h2 className="font-semibold text-slate-700 mb-3">À propos du module IVR</h2>
        <p className="text-slate-600 text-sm leading-relaxed">
          Le module IVR (Interactive Voice Response) permet de conduire des sondages téléphoniques automatisés ciblant particulièrement les
          personnes âgées et les zones rurales avec une faible pénétration du smartphone. Les réponses sont collectées via les touches du
          téléphone et géolocalisées par gouvernorat.
        </p>
      </div>
    </div>
  )
}
