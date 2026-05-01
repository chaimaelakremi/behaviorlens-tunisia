import { useNavigate } from 'react-router-dom'

export default function Navbar() {
  const navigate = useNavigate()
  const user = JSON.parse(localStorage.getItem('user') || '{}')

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    navigate('/login')
  }

  return (
    <nav className="bg-white border-b border-slate-200 px-6 py-3 flex items-center justify-between shadow-sm">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-red-600 flex items-center justify-center">
          <span className="text-white text-xs font-bold">BL</span>
        </div>
        <span className="font-bold text-slate-800">BehaviorLens Tunisia</span>
      </div>
      <div className="flex items-center gap-4">
        <span className="text-sm text-slate-500">{user.email}</span>
        <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">{user.role}</span>
        <button onClick={logout} className="text-sm text-red-600 hover:text-red-800 font-medium">
          Déconnexion
        </button>
      </div>
    </nav>
  )
}
