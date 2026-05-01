import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { photo } from '../../services/api'
import StatsCard from '../../components/StatsCard'

export default function Photo() {
  const [stats, setStats] = useState(null)
  const [challenges, setChallenges] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([photo.stats(), photo.challenges()]).then(([s, c]) => {
      setStats(s.data); setChallenges(c.data)
    }).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="flex items-center justify-center h-64"><p className="text-slate-500">Chargement...</p></div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">📷 Photo Challenge</h1>
        <p className="text-slate-500 text-sm mt-1">Collecte visuelle via photos par région</p>
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard title="Défis Actifs" value={stats?.total_challenges} icon="🏆" color="blue" />
        <StatsCard title="Photos Soumises" value={stats?.total_submissions} icon="📸" color="green" />
        <StatsCard title="Régions Participantes" value={stats?.by_region?.length} icon="📍" color="purple" />
        <StatsCard title="Défis Couverts" value={stats?.by_challenge?.length} icon="🎯" color="orange" />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-5 shadow-sm">
          <h2 className="font-semibold text-slate-700 mb-4">Photos par Région</h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={stats?.by_region || []} margin={{ bottom: 50 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="region" angle={-30} textAnchor="end" tick={{ fontSize: 10 }} interval={0} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#FB8500" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="bg-white rounded-xl p-5 shadow-sm">
          <h2 className="font-semibold text-slate-700 mb-4">Photos par Défi</h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={stats?.by_challenge || []} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis type="number" />
              <YAxis dataKey="challenge" type="category" width={120} tick={{ fontSize: 10 }} />
              <Tooltip />
              <Bar dataKey="count" fill="#E63946" radius={[0,4,4,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div className="bg-white rounded-xl p-5 shadow-sm">
        <h2 className="font-semibold text-slate-700 mb-4">Défis Photo Actifs</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {challenges.map(c => (
            <div key={c.id} className="border border-slate-200 rounded-xl p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-2">
                <span className="bg-orange-100 text-orange-700 text-xs px-2 py-0.5 rounded-full">{c.theme}</span>
                <span className="text-xs text-slate-400">{c.submissions} photos</span>
              </div>
              <h3 className="font-semibold text-slate-700">{c.title}</h3>
              <p className="text-xs text-slate-500 mt-1 line-clamp-2">{c.description}</p>
              {c.region && (
                <div className="mt-3 flex items-center gap-1">
                  <span className="text-xs">📍</span>
                  <span className="text-xs text-slate-500">{c.region}</span>
                </div>
              )}
            </div>
          ))}
          {!challenges.length && (
            <div className="col-span-3 py-12 text-center text-slate-400">
              <p className="text-4xl mb-2">📷</p>
              <p>Aucun défi photo actif</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
