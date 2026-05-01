import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { gamification } from '../../services/api'
import StatsCard from '../../components/StatsCard'

export default function Gamification() {
  const [stats, setStats] = useState(null)
  const [leaderboard, setLeaderboard] = useState([])
  const [games, setGames] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([gamification.stats(), gamification.leaderboard(), gamification.games()]).then(([s, l, g]) => {
      setStats(s.data); setLeaderboard(l.data); setGames(g.data)
    }).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="flex items-center justify-center h-64"><p className="text-slate-500">Chargement...</p></div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">🎮 Gamification</h1>
        <p className="text-slate-500 text-sm mt-1">Mini-jeux et rewards pour collecter les données de façon ludique</p>
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard title="Joueurs" value={stats?.total_players} icon="👤" color="blue" />
        <StatsCard title="Sessions de Jeu" value={stats?.total_sessions} icon="🎯" color="green" />
        <StatsCard title="Points Distribués" value={stats?.total_points_distributed} icon="⭐" color="orange" />
        <StatsCard title="Jeux Disponibles" value={games.length} icon="🕹️" color="purple" />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-5 shadow-sm">
          <h2 className="font-semibold text-slate-700 mb-4">Parties par Jeu</h2>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={stats?.by_game || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="game" tick={{ fontSize: 11 }} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="plays" fill="#2A9D8F" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="bg-white rounded-xl p-5 shadow-sm">
          <h2 className="font-semibold text-slate-700 mb-4">Joueurs par Région</h2>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={stats?.by_region || []} margin={{ bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="region" angle={-30} textAnchor="end" tick={{ fontSize: 10 }} interval={0} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="players" fill="#8338EC" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-5 shadow-sm">
          <h2 className="font-semibold text-slate-700 mb-4">🏆 Classement Joueurs</h2>
          <table className="w-full text-sm">
            <thead><tr className="border-b border-slate-100">
              <th className="text-left py-2 px-3 text-slate-500 font-medium">Rang</th>
              <th className="text-left py-2 px-3 text-slate-500 font-medium">Pseudo</th>
              <th className="text-left py-2 px-3 text-slate-500 font-medium">Région</th>
              <th className="text-right py-2 px-3 text-slate-500 font-medium">Points</th>
            </tr></thead>
            <tbody>
              {leaderboard.map(p => (
                <tr key={p.rank} className="border-b border-slate-50">
                  <td className="py-2 px-3">
                    <span className={`font-bold ${p.rank === 1 ? 'text-yellow-500' : p.rank === 2 ? 'text-slate-400' : p.rank === 3 ? 'text-orange-400' : 'text-slate-600'}`}>
                      #{p.rank}
                    </span>
                  </td>
                  <td className="py-2 px-3 font-medium text-slate-700">{p.nickname}</td>
                  <td className="py-2 px-3 text-slate-500">{p.region}</td>
                  <td className="py-2 px-3 text-right font-bold text-amber-600">{p.points} pts</td>
                </tr>
              ))}
              {!leaderboard.length && <tr><td colSpan={4} className="py-8 text-center text-slate-400">Aucun joueur</td></tr>}
            </tbody>
          </table>
        </div>
        <div className="bg-white rounded-xl p-5 shadow-sm">
          <h2 className="font-semibold text-slate-700 mb-4">Jeux Disponibles</h2>
          <div className="space-y-3">
            {games.map(g => (
              <div key={g.id} className="border border-slate-100 rounded-lg p-3 flex items-center justify-between">
                <div>
                  <p className="font-medium text-slate-700">{g.name}</p>
                  <p className="text-xs text-slate-400">{g.description}</p>
                </div>
                <span className="bg-amber-100 text-amber-700 text-xs px-2 py-1 rounded-full font-medium">+{g.points} pts</span>
              </div>
            ))}
            {!games.length && <p className="text-slate-400 text-sm text-center py-8">Aucun jeu disponible</p>}
          </div>
        </div>
      </div>
    </div>
  )
}
