import { useEffect, useState } from 'react'
import { opendata } from '../../services/api'
import StatsCard from '../../components/StatsCard'

const SOURCES = [
  { key: 'ins', label: 'INS — Institut National de la Statistique', icon: '📊' },
  { key: 'anme', label: 'ANME — Agence Nationale pour la Maîtrise de l\'Énergie', icon: '⚡' },
  { key: 'ministere_sante', label: 'Ministère de la Santé', icon: '🏥' },
]

export default function OpenData() {
  const [stats, setStats] = useState(null)
  const [fetching, setFetching] = useState(null)
  const [results, setResults] = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    opendata.stats().then(r => setStats(r.data)).finally(() => setLoading(false))
  }, [])

  const fetchSource = async (key) => {
    setFetching(key)
    try {
      const r = await opendata.fetch(key)
      setResults(prev => ({ ...prev, [key]: r.data.data }))
    } finally {
      setFetching(null)
    }
  }

  if (loading) return <div className="flex items-center justify-center h-64"><p className="text-slate-500">Chargement...</p></div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">🏛️ Open Data Gouvernemental</h1>
        <p className="text-slate-500 text-sm mt-1">Récupération automatique des données publiques tunisiennes</p>
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        <StatsCard title="Datasets Importés" value={stats?.total_datasets} icon="📂" color="blue" />
        <StatsCard title="Sources Disponibles" value={stats?.available_sources?.length} icon="🔗" color="purple" />
        <StatsCard title="Imports Récents" value={stats?.recent_imports?.length} icon="🔄" color="green" />
      </div>
      <div className="bg-white rounded-xl p-5 shadow-sm">
        <h2 className="font-semibold text-slate-700 mb-4">Sources de Données Gouvernementales</h2>
        <div className="space-y-4">
          {SOURCES.map(src => (
            <div key={src.key} className="border border-slate-200 rounded-xl p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{src.icon}</span>
                  <div>
                    <p className="font-medium text-slate-700 text-sm">{src.label}</p>
                    <p className="text-xs text-slate-400">Source: {src.key}</p>
                  </div>
                </div>
                <button
                  onClick={() => fetchSource(src.key)}
                  disabled={fetching === src.key}
                  className="bg-slate-800 text-white px-3 py-1.5 rounded-lg text-xs hover:bg-slate-700 disabled:opacity-50 transition"
                >
                  {fetching === src.key ? 'Récupération...' : 'Récupérer'}
                </button>
              </div>
              {results[src.key] && (
                <div className="mt-3 bg-slate-50 rounded-lg p-3">
                  <pre className="text-xs text-slate-600 overflow-auto">{JSON.stringify(results[src.key], null, 2)}</pre>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
      <div className="bg-white rounded-xl p-5 shadow-sm">
        <h2 className="font-semibold text-slate-700 mb-4">Historique des Imports</h2>
        <table className="w-full text-sm">
          <thead><tr className="border-b border-slate-100">
            <th className="text-left py-2 px-3 text-slate-500 font-medium">Message</th>
            <th className="text-left py-2 px-3 text-slate-500 font-medium">Statut</th>
            <th className="text-left py-2 px-3 text-slate-500 font-medium">Date</th>
          </tr></thead>
          <tbody>
            {(stats?.recent_imports || []).map((r, i) => (
              <tr key={i} className="border-b border-slate-50">
                <td className="py-2 px-3 text-slate-600">{r.message}</td>
                <td className="py-2 px-3"><span className="bg-green-100 text-green-700 text-xs px-2 py-0.5 rounded">{r.status}</span></td>
                <td className="py-2 px-3 text-slate-400 text-xs">{new Date(r.created_at).toLocaleString('fr-TN')}</td>
              </tr>
            ))}
            {!stats?.recent_imports?.length && <tr><td colSpan={3} className="py-8 text-center text-slate-400">Aucun import récent</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  )
}
