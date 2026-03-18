import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getRules, deleteLink } from '../api'
import RuleBuilder from '../components/RuleBuilder'

export default function Manage() {
  const [shortCode, setShortCode] = useState('')
  const [token, setToken] = useState('')
  const [rules, setRules] = useState(null)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  async function handleLoad() {
    if (!shortCode || !token) { setError('Both fields required'); return }
    setError('')
    try {
      const res = await getRules(shortCode, token)
      setRules(res.data)
    } catch (e) {
      setError(e.response?.data?.detail || 'Could not load link')
    }
  }

  async function handleDelete() {
    if (!confirm('Delete this link permanently?')) return
    await deleteLink(shortCode, token)
    navigate('/')
  }

  async function refreshRules() {
    const res = await getRules(shortCode, token)
    setRules(res.data)
  }

  return (
    <div className="container">
      <h1>Manage Link</h1>
      <p className="subtitle">Enter your short code and manage token to edit your link.</p>

      {rules === null ? (
        <div className="card">
          <input placeholder="Short code (e.g. atharv-github)"
            value={shortCode} onChange={e => setShortCode(e.target.value)} />
          <input placeholder="Manage token"
            value={token} onChange={e => setToken(e.target.value)} />
          {error && <p className="error">{error}</p>}
          <button className="btn-primary" onClick={handleLoad}>Load Link</button>
        </div>
      ) : (
        <>
          <div className="card">
            <p style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '0.75rem' }}>
              Managing: <strong>localhost:8000/{shortCode}</strong>
            </p>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button className="btn-secondary"
                onClick={() => navigate(`/analytics/${shortCode}?token=${token}`)}>
                View Analytics
              </button>
              <button className="btn-danger" onClick={handleDelete}>Delete Link</button>
            </div>
          </div>
          <RuleBuilder
            shortCode={shortCode}
            token={token}
            rules={rules}
            onUpdate={refreshRules}
          />
        </>
      )}
    </div>
  )
}