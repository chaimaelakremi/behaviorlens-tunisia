import { useEffect, useState } from 'react'
import { core } from '../services/api'
import StatsCard from '../components/StatsCard'

const CODE_PYTHON = `from behaviorlens_sdk import BehaviorLensClient, BehaviorLensModule

# 1. Connexion au framework
client = BehaviorLensClient("http://localhost:8000")
client.login("admin@behaviorlens.tn", "admin123")

# 2. Créer ton module (une seule fois)
class MonModule(BehaviorLensModule):
    DOMAIN = "mon_module"
    NAME   = "Mon Collecteur"

    def collect(self):
        data = fetch_my_data()            # ta source
        for item in data:
            self.push(
                region_name  = item["region"],
                metric_name  = "ma_metrique",
                metric_value = item["value"],
                age_group    = item.get("age"),
            )

# 3. Enregistrer et lancer
module = MonModule(client)
module.register()
module.run(interval_seconds=60)   # boucle toutes les 60s`

const CODE_JS = `import { BehaviorLensClient } from './behaviorlens-sdk.js'

const client = new BehaviorLensClient('http://localhost:8000')
await client.login('admin@behaviorlens.tn', 'admin123')

// Push direct depuis n'importe quelle app JS/TS
await client.useModule('social_media').push({
  regionName  : 'sfax',
  metricName  : 'mentions',
  metricValue : 1250,
  ageGroup    : '18-25',
  rawData     : JSON.stringify({ hashtag: '#Sfax', platform: 'tiktok' }),
})

// Stats en temps réel
const stats = await client.getStats()
console.log(\`Total: \${stats.total_records} enregistrements\`)`

const CODE_CURL = `# Enregistrer un module
curl -X POST http://localhost:8000/api/modules/register \\
  -H "Authorization: Bearer <token>" \\
  -H "Content-Type: application/json" \\
  -d '{"name":"Mon Module","domain":"mon_module","api_key":"clé-unique"}'

# Pousser une donnée
curl -X POST http://localhost:8000/api/collect \\
  -H "Authorization: Bearer <token>" \\
  -H "Content-Type: application/json" \\
  -d '{
    "module_domain": "mon_module",
    "region_id": 1,
    "metric_name": "evenement",
    "metric_value": 42,
    "age_group": "26-35"
  }'`

const MODULES_BUILTIN = [
  { icon: '📱', name: 'Social Media',      domain: 'social_media', cible: 'Jeunes connectés',         endpoint: '/api/social/collect' },
  { icon: '🗺️', name: 'Terrain',           domain: 'terrain',      cible: 'Zones rurales',             endpoint: '/api/terrain/submit' },
  { icon: '📞', name: 'IVR Téléphone',     domain: 'ivr',          cible: 'Personnes âgées',           endpoint: '/api/ivr/response' },
  { icon: '🛒', name: 'Commerce POS',      domain: 'commerce',     cible: 'Épiceries & souks',         endpoint: '/api/commerce/sale' },
  { icon: '🎮', name: 'Gamification',      domain: 'gamification', cible: 'Tous publics',              endpoint: '/api/game/play' },
  { icon: '🏛️', name: 'Open Data',         domain: 'open_data',    cible: 'Données gouvernementales',  endpoint: '/api/opendata/fetch' },
  { icon: '😊', name: 'Baromètre Humeur',  domain: 'mood',         cible: 'Tous publics',              endpoint: '/api/mood/record' },
  { icon: '📷', name: 'Photo Challenge',   domain: 'photo',        cible: 'Tous publics',              endpoint: '/api/photo/submit' },
]

function CodeBlock({ code, lang }) {
  const [copied, setCopied] = useState(false)
  const copy = () => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }
  return (
    <div className="relative bg-slate-900 rounded-xl overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2 bg-slate-800">
        <span className="text-xs text-slate-400 font-mono">{lang}</span>
        <button onClick={copy} className="text-xs text-slate-400 hover:text-white transition">
          {copied ? '✓ Copié' : 'Copier'}
        </button>
      </div>
      <pre className="p-4 text-xs text-green-300 font-mono overflow-x-auto leading-relaxed whitespace-pre">{code}</pre>
    </div>
  )
}

export default function SDK() {
  const [modules, setModules] = useState([])
  const [stats, setStats] = useState(null)
  const [activeTab, setActiveTab] = useState('python')

  useEffect(() => {
    Promise.all([core.modules(), core.stats()]).then(([m, s]) => {
      setModules(m.data)
      setStats(s.data)
    })
  }, [])

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">SDK &amp; Framework</h1>
        <p className="text-slate-500 text-sm mt-1">
          Intègre n'importe quelle source de données — Python, JavaScript, ou HTTP direct
        </p>
      </div>

      {/* Architecture */}
      <div className="bg-white rounded-xl p-6 shadow-sm">
        <h2 className="font-semibold text-slate-700 mb-5">Architecture du Framework</h2>
        <div className="flex items-start gap-3 overflow-x-auto pb-2">
          {[
            { label: 'Sources', items: ['App mobile', 'Capteur IoT', 'Scraper web', 'Caisse POS', 'SMS / IVR', 'Ton module…'], color: 'bg-blue-50 border-blue-200 text-blue-700' },
            { label: '→', items: [], color: '', arrow: true },
            { label: 'SDK', items: ['Python SDK', 'JavaScript SDK', 'REST API direct'], color: 'bg-purple-50 border-purple-200 text-purple-700' },
            { label: '→', items: [], color: '', arrow: true },
            { label: 'Core API', items: ['POST /api/collect', 'Géolocalisation', 'Horodatage', 'Anonymisation'], color: 'bg-red-50 border-red-200 text-red-700' },
            { label: '→', items: [], color: '', arrow: true },
            { label: 'Dashboard', items: ['Carte Tunisie', 'Stats par module', 'Export CSV', 'API stats'], color: 'bg-green-50 border-green-200 text-green-700' },
          ].map((col, i) =>
            col.arrow ? (
              <div key={i} className="flex items-center pt-6 px-1 text-slate-400 text-xl flex-shrink-0">→</div>
            ) : (
              <div key={i} className={`flex-1 min-w-[140px] border rounded-xl p-4 ${col.color}`}>
                <p className="font-semibold text-sm mb-3">{col.label}</p>
                <ul className="space-y-1">
                  {col.items.map(it => (
                    <li key={it} className="text-xs opacity-80">• {it}</li>
                  ))}
                </ul>
              </div>
            )
          )}
        </div>
      </div>

      {/* Stats framework */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard title="Modules Actifs"     value={modules.length}           icon="🔌" color="blue" />
        <StatsCard title="Enregistrements"    value={stats?.total_records}     icon="📦" color="green" />
        <StatsCard title="Régions Couvertes"  value={stats?.regions_covered}   icon="🗺️" color="purple" />
        <StatsCard title="Couches Sociales"   value={8}                        icon="👥" color="orange" subtitle="toutes couches" />
      </div>

      {/* Modules intégrés */}
      <div className="bg-white rounded-xl p-6 shadow-sm">
        <h2 className="font-semibold text-slate-700 mb-4">8 Modules Intégrés</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {MODULES_BUILTIN.map(m => (
            <div key={m.domain} className="flex items-center gap-3 border border-slate-100 rounded-lg p-3 hover:bg-slate-50 transition">
              <span className="text-2xl">{m.icon}</span>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-slate-700 text-sm">{m.name}</p>
                <p className="text-xs text-slate-400">{m.cible}</p>
              </div>
              <code className="text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded font-mono hidden lg:block">
                {m.endpoint}
              </code>
            </div>
          ))}
        </div>
      </div>

      {/* Code examples */}
      <div className="bg-white rounded-xl p-6 shadow-sm">
        <h2 className="font-semibold text-slate-700 mb-4">Intégration en 3 lignes</h2>
        <div className="flex gap-2 mb-4">
          {['python', 'javascript', 'curl'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-1.5 rounded-lg text-sm font-medium transition ${
                activeTab === tab
                  ? 'bg-slate-900 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {tab === 'python' ? '🐍 Python' : tab === 'javascript' ? '⚡ JavaScript' : '🌐 cURL'}
            </button>
          ))}
        </div>
        {activeTab === 'python'     && <CodeBlock code={CODE_PYTHON} lang="Python — SDK BehaviorLens" />}
        {activeTab === 'javascript' && <CodeBlock code={CODE_JS}     lang="JavaScript — SDK BehaviorLens" />}
        {activeTab === 'curl'       && <CodeBlock code={CODE_CURL}   lang="HTTP — REST API direct" />}
      </div>

      {/* Créer un module */}
      <div className="bg-white rounded-xl p-6 shadow-sm">
        <h2 className="font-semibold text-slate-700 mb-4">Créer un Nouveau Module</h2>
        <ol className="space-y-3">
          {[
            { step: '1', title: 'Copier le template', desc: 'cp -r backend/module_template backend/modules/mon_module', code: true },
            { step: '2', title: 'Implémenter la logique', desc: 'Modifier router.py — endpoints /collect et /stats', code: false },
            { step: '3', title: 'Enregistrer dans main.py', desc: 'from modules.mon_module.router import router as mon_router', code: true },
            { step: '4', title: 'Utiliser le SDK', desc: 'python exemple_scraper.py  # données automatiquement dans le dashboard', code: true },
          ].map(({ step, title, desc, code }) => (
            <li key={step} className="flex gap-4 items-start">
              <div className="w-7 h-7 rounded-full bg-red-600 text-white text-xs font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
                {step}
              </div>
              <div>
                <p className="font-medium text-slate-700 text-sm">{title}</p>
                {code
                  ? <code className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-mono">{desc}</code>
                  : <p className="text-xs text-slate-500">{desc}</p>
                }
              </div>
            </li>
          ))}
        </ol>
      </div>

      {/* Modèle économique contributeurs */}
      <div className="bg-gradient-to-r from-slate-900 to-red-900 rounded-xl p-6 text-white">
        <h2 className="font-semibold mb-4">Modèle Économique — Contributeurs</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { pct: '50%', label: 'Core Framework',     desc: 'Équipe centrale',           color: 'bg-red-500' },
            { pct: '30%', label: 'Créateur du Module', desc: 'Toi, si tu ajoutes un module', color: 'bg-orange-500' },
            { pct: '20%', label: 'Communauté',         desc: 'Testeurs & contributeurs',   color: 'bg-yellow-500' },
          ].map(({ pct, label, desc, color }) => (
            <div key={label} className="bg-white/10 rounded-xl p-4">
              <div className={`w-12 h-12 ${color} rounded-xl flex items-center justify-center text-xl font-black mb-3`}>
                {pct}
              </div>
              <p className="font-semibold">{label}</p>
              <p className="text-xs text-white/60 mt-1">{desc}</p>
            </div>
          ))}
        </div>
        <p className="text-xs text-white/50 mt-4">
          Revenus : vente rapports anonymisés (200–5000 DT) · Abonnements dashboard (100–500 DT/mois) · Consulting · Licence autres pays africains
        </p>
      </div>
    </div>
  )
}
