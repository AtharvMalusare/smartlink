import { useEffect, useState } from 'react'
import { useParams, useLocation } from 'react-router-dom'
import { getAnalytics } from '../api'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line
} from 'recharts'

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#3b82f6']

export default function Analytics() {
  const { shortCode } = useParams()
  const location = useLocation()
  const token = new URLSearchParams(location.search).get('token')
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!token) { setError('No token provided'); return }
    getAnalytics(shortCode, token)
      .then(r => setData(r.data))
      .catch(e => setError(e.response?.data?.detail || 'Failed to load analytics'))
  }, [shortCode, token])

  if (error) return <div className="container"><p className="error">{error}</p></div>
  if (!data) return <div className="container"><p>Loading...</p></div>

  const countryData = Object.entries(data.by_country).map(([k, v]) => ({ name: k, clicks: v }))
  const deviceData = Object.entries(data.by_device).map(([k, v]) => ({ name: k, value: v }))
  const dateData = Object.entries(data.by_date).sort().map(([k, v]) => ({ date: k, clicks: v }))

  return (
    <div className="container">
      <h1>Analytics — {shortCode}</h1>
      <p className="subtitle">Total clicks: <strong>{data.total_clicks}</strong></p>

      <div className="card">
        <h2>Clicks over time</h2>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={dateData}>
            <XAxis dataKey="date" fontSize={12} />
            <YAxis fontSize={12} />
            <Tooltip />
            <Line type="monotone" dataKey="clicks" stroke="#6366f1" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
        <div className="card">
          <h2>By country</h2>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={countryData}>
              <XAxis dataKey="name" fontSize={12} />
              <YAxis fontSize={12} />
              <Tooltip />
              <Bar dataKey="clicks" fill="#6366f1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h2>By device</h2>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={deviceData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} label>
                {deviceData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {(data.ab_variants.A > 0 || data.ab_variants.B > 0) && (
        <div className="card">
          <h2>A/B variants</h2>
          <ResponsiveContainer width="100%" height={150}>
            <BarChart data={[
              { name: 'Variant A', clicks: data.ab_variants.A },
              { name: 'Variant B', clicks: data.ab_variants.B },
            ]}>
              <XAxis dataKey="name" fontSize={12} />
              <YAxis fontSize={12} />
              <Tooltip />
              <Bar dataKey="clicks" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}