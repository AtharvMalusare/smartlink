import { Routes, Route, Link } from 'react-router-dom'
import Home from './pages/Home'
import Manage from './pages/Manage'
import Analytics from './pages/Analytics'

export default function App() {
  return (
    <>
      <nav>
        <span className="brand">SmartLink</span>
        <Link to="/">Create</Link>
        <Link to="/manage">Manage</Link>
      </nav>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/manage" element={<Manage />} />
        <Route path="/analytics/:shortCode" element={<Analytics />} />
      </Routes>
    </>
  )
}