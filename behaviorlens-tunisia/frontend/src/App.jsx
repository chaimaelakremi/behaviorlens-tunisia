import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import SocialMedia from './pages/modules/SocialMedia'
import Terrain from './pages/modules/Terrain'
import IVR from './pages/modules/IVR'
import Commerce from './pages/modules/Commerce'
import Gamification from './pages/modules/Gamification'
import OpenData from './pages/modules/OpenData'
import Mood from './pages/modules/Mood'
import Photo from './pages/modules/Photo'
import SDK from './pages/SDK'
import Layout from './components/Layout'

function PrivateRoute({ children }) {
  return localStorage.getItem('token') ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<PrivateRoute><Layout /></PrivateRoute>}>
          <Route index element={<Dashboard />} />
          <Route path="social" element={<SocialMedia />} />
          <Route path="terrain" element={<Terrain />} />
          <Route path="ivr" element={<IVR />} />
          <Route path="commerce" element={<Commerce />} />
          <Route path="gamification" element={<Gamification />} />
          <Route path="opendata" element={<OpenData />} />
          <Route path="mood" element={<Mood />} />
          <Route path="photo" element={<Photo />} />
          <Route path="sdk" element={<SDK />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
