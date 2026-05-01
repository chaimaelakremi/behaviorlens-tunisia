import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { social } from '../../services/api'
import StatsCard from '../../components/StatsCard'

const SENTIMENT_COLORS = { positive: '#2A9D8F', negative: '#E63946', neutral: '#457B9D', mixed: '#F4A261' }

export default function SocialMedia() {
  const [stats, setStats] = useState(null)
  const [trends, setTrends] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([social.stats(), social.trends()]).then(([s, t]) => {
      setStats(s.data)
      setTrends(t.data)
    }).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="flex items-center justify-center h-64"><p className="text-slate-500">Chargement...</p></div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">📱 Social Media</h1>
        <p className="text-slate-500 text-sm mt-1">Scraping Facebook, TikTok, Twitter tunisien</p>
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard title="Total Posts" value={stats?.total_posts} icon="📝" color="blue" />
        <StatsCard title="Plateformes" value={stats?.by_platform?.length} icon="📱" color="purple" />
        <StatsCard title="Sentiments" value={stats?.by_sentiment?.length} icon="💬" color="green" />
        <StatsCard title="Récents (10)" value={stats?.recent?.length} icon="🔔" color="orange" />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-5 shadow-sm">
          <h2 className="font-semibold text-slate-700 mb-4">Posts par Plateforme</h2>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={stats?.by_platform || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="platform" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#457B9D" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="bg-white rounded-xl p-5 shadow-sm">
          <h2 className="font-semibold text-slate-700 mb-4">Analyse Sentiment</h2>
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie data={stats?.by_sentiment || []} dataKey="count" nameKey="sentiment" cx="50%" cy="50%" outerRadius={90} label={({sentiment, percent}) => `${sentiment} ${(percent*100).toFixed(0)}%`}>
                {(stats?.by_sentiment || []).map((entry, i) => (
                  <Cell key={i} fill={SENTIMENT_COLORS[entry.sentiment] || '#8884d8'} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div className="bg-white rounded-xl p-5 shadow-sm">
        <h2 className="font-semibold text-slate-700 mb-4">Top Hashtags Tendances</h2>
        <div className="flex flex-wrap gap-2">
          {trends.map((t, i) => (
            <span key={i} className="bg-slate-100 text-slate-700 px-3 py-1.5 rounded-full text-sm font-medium">
              #{t.hashtag} <span className="text-slate-400 ml-1">{t.count}</span>
            </span>
          ))}
          {!trends.length && <p className="text-slate-400 text-sm">Aucun hashtag enregistré</p>}
        </div>
      </div>
      <div className="bg-white rounded-xl p-5 shadow-sm">
        <h2 className="font-semibold text-slate-700 mb-4">Derniers Posts Collectés</h2>
        <table className="w-full text-sm">
          <thead><tr className="border-b border-slate-100">
            <th className="text-left py-2 px-3 text-slate-500 font-medium">ID</th>
            <th className="text-left py-2 px-3 text-slate-500 font-medium">Plateforme</th>
            <th className="text-left py-2 px-3 text-slate-500 font-medium">Hashtag</th>
            <th className="text-left py-2 px-3 text-slate-500 font-medium">Sentiment</th>
            <th className="text-left py-2 px-3 text-slate-500 font-medium">Date</th>
          </tr></thead>
          <tbody>
            {(stats?.recent || []).map(r => (
              <tr key={r.id} className="border-b border-slate-50 hover:bg-slate-50">
                <td className="py-2 px-3 text-slate-400">#{r.id}</td>
                <td className="py-2 px-3"><span className="bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded">{r.platform}</span></td>
                <td className="py-2 px-3 text-slate-600">{r.hashtag || '—'}</td>
                <td className="py-2 px-3"><span style={{color: SENTIMENT_COLORS[r.sentiment]}} className="font-medium text-xs">{r.sentiment || '—'}</span></td>
                <td className="py-2 px-3 text-slate-400 text-xs">{new Date(r.created_at).toLocaleString('fr-TN')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
