import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { commerce } from '../../services/api'
import StatsCard from '../../components/StatsCard'

export default function Commerce() {
  const [stats, setStats] = useState(null)
  const [topProducts, setTopProducts] = useState([])
  const [byRegion, setByRegion] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([commerce.stats(), commerce.topProducts(), commerce.byRegion()]).then(([s, p, r]) => {
      setStats(s.data); setTopProducts(p.data); setByRegion(r.data)
    }).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="flex items-center justify-center h-64"><p className="text-slate-500">Chargement...</p></div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">🛒 Commerce POS</h1>
        <p className="text-slate-500 text-sm mt-1">Données de ventes épiceries, supermarchés, souks</p>
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard title="Commerces" value={stats?.total_stores} icon="🏪" color="blue" />
        <StatsCard title="Transactions" value={stats?.total_sales} icon="🧾" color="green" />
        <StatsCard title="Chiffre d'Affaires" value={`${(stats?.total_revenue || 0).toFixed(0)} TND`} icon="💰" color="purple" />
        <StatsCard title="Types de Commerce" value={stats?.by_store_type?.length} icon="🏬" color="orange" />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-5 shadow-sm">
          <h2 className="font-semibold text-slate-700 mb-4">Top Produits Vendus</h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={topProducts.slice(0, 8)} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis type="number" />
              <YAxis dataKey="product" type="category" width={100} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="quantity" fill="#F4A261" radius={[0,4,4,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="bg-white rounded-xl p-5 shadow-sm">
          <h2 className="font-semibold text-slate-700 mb-4">Ventes par Région</h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={byRegion} margin={{ bottom: 50 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="region" angle={-30} textAnchor="end" tick={{ fontSize: 10 }} interval={0} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="revenue" fill="#2A9D8F" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div className="bg-white rounded-xl p-5 shadow-sm">
        <h2 className="font-semibold text-slate-700 mb-4">Ventes Récentes</h2>
        <table className="w-full text-sm">
          <thead><tr className="border-b border-slate-100">
            <th className="text-left py-2 px-3 text-slate-500 font-medium">ID</th>
            <th className="text-left py-2 px-3 text-slate-500 font-medium">Produit</th>
            <th className="text-left py-2 px-3 text-slate-500 font-medium">Quantité</th>
            <th className="text-left py-2 px-3 text-slate-500 font-medium">Total</th>
            <th className="text-left py-2 px-3 text-slate-500 font-medium">Date</th>
          </tr></thead>
          <tbody>
            {(stats?.recent || []).map(r => (
              <tr key={r.id} className="border-b border-slate-50 hover:bg-slate-50">
                <td className="py-2 px-3 text-slate-400">#{r.id}</td>
                <td className="py-2 px-3 text-slate-700">{r.product}</td>
                <td className="py-2 px-3 text-slate-600">{r.quantity}</td>
                <td className="py-2 px-3 font-medium text-green-600">{r.total?.toFixed(2)} TND</td>
                <td className="py-2 px-3 text-slate-400 text-xs">{new Date(r.created_at).toLocaleString('fr-TN')}</td>
              </tr>
            ))}
            {!stats?.recent?.length && <tr><td colSpan={5} className="py-8 text-center text-slate-400">Aucune vente enregistrée</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  )
}
