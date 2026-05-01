import { NavLink } from 'react-router-dom'

const MODULES = [
  { path: '/', label: 'Dashboard', icon: '📊', exact: true },
  { path: '/social', label: 'Social Media', icon: '📱' },
  { path: '/terrain', label: 'Terrain', icon: '🗺️' },
  { path: '/ivr', label: 'IVR Téléphone', icon: '📞' },
  { path: '/commerce', label: 'Commerce POS', icon: '🛒' },
  { path: '/gamification', label: 'Gamification', icon: '🎮' },
  { path: '/opendata', label: 'Open Data', icon: '🏛️' },
  { path: '/mood', label: 'Baromètre Humeur', icon: '😊' },
  { path: '/photo', label: 'Photo Challenge', icon: '📷' },
]

const FRAMEWORK = [
  { path: '/sdk', label: 'SDK & Framework', icon: '🔌' },
]

export default function Sidebar() {
  return (
    <aside className="w-60 bg-slate-900 text-white flex flex-col">
      <div className="p-5 border-b border-slate-700">
        <div className="flex items-center gap-3 mb-1">
          <div className="w-9 h-9 bg-red-600 rounded-xl flex items-center justify-center shadow-lg flex-shrink-0">
            <span className="text-white text-xs font-black">BL</span>
          </div>
          <div>
            <p className="font-bold text-white text-sm leading-tight">BehaviorLens</p>
            <p className="text-xs text-red-400 font-medium">Tunisia</p>
          </div>
        </div>
        <p className="text-xs text-slate-500 mt-2 uppercase tracking-wider">Navigation</p>
      </div>
      <nav className="flex-1 py-2 overflow-y-auto">
        <p className="px-4 pt-2 pb-1 text-xs text-slate-500 uppercase tracking-wider">Modules</p>
        {MODULES.map(({ path, label, icon, exact }) => (
          <NavLink
            key={path}
            to={path}
            end={exact}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2.5 text-sm transition-colors ${
                isActive
                  ? 'bg-red-600 text-white'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`
            }
          >
            <span className="text-base">{icon}</span>
            <span>{label}</span>
          </NavLink>
        ))}
        <p className="px-4 pt-4 pb-1 text-xs text-slate-500 uppercase tracking-wider">Framework</p>
        {FRAMEWORK.map(({ path, label, icon }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2.5 text-sm transition-colors ${
                isActive
                  ? 'bg-purple-600 text-white'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`
            }
          >
            <span className="text-base">{icon}</span>
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="p-4 border-t border-slate-700">
        <p className="text-xs text-slate-500">v1.0.0 — Tunisie 2026</p>
      </div>
    </aside>
  )
}
