import { useState } from 'react'
import { addRule, deleteRule } from '../api'

const CONDITION_TYPES = ['device', 'country', 'referrer', 'time_range']
const DEVICES = ['mobile', 'desktop', 'tablet']

export default function RuleBuilder({ shortCode, token, rules, onUpdate }) {
  const [type, setType] = useState('device')
  const [value, setValue] = useState('mobile')
  const [targetUrl, setTargetUrl] = useState('')
  const [priority, setPriority] = useState(0)
  const [error, setError] = useState('')

  async function handleAdd() {
    if (!targetUrl) { setError('Target URL is required'); return }
    setError('')
    try {
      await addRule(shortCode, token, {
        condition_type: type,
        condition_value: value,
        target_url: targetUrl,
        priority,
      })
      setTargetUrl('')
      onUpdate()
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to add rule')
    }
  }

  async function handleDelete(ruleId) {
    await deleteRule(ruleId, token)
    onUpdate()
  }

  return (
    <div>
      <h2>Routing Rules</h2>
      {rules.length === 0 && (
        <p style={{ color: '#6b7280', fontSize: '0.875rem', marginBottom: '1rem' }}>
          No rules yet — all users go to the default URL.
        </p>
      )}
      {rules.map(r => (
        <div className="rule-item" key={r.id}>
          <span>
            If <strong>{r.condition_type}</strong> = <strong>{r.condition_value}</strong>
            {' → '}<a href={r.target_url} target="_blank" rel="noreferrer"
              style={{ color: '#6366f1' }}>{r.target_url}</a>
            {' '}(priority {r.priority})
          </span>
          <button className="btn-danger" style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem' }}
            onClick={() => handleDelete(r.id)}>Remove</button>
        </div>
      ))}

      <div className="card" style={{ marginTop: '1rem' }}>
        <h2>Add Rule</h2>
        <select value={type} onChange={e => { setType(e.target.value); setValue('') }}>
          {CONDITION_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        {type === 'device'
          ? <select value={value} onChange={e => setValue(e.target.value)}>
              {DEVICES.map(d => <option key={d} value={d}>{d}</option>)}
            </select>
          : <input placeholder={
              type === 'country' ? 'e.g. IN, US, GB' :
              type === 'time_range' ? 'e.g. 09:00-17:00' : 'e.g. twitter.com'
            } value={value} onChange={e => setValue(e.target.value)} />
        }
        <input placeholder="Target URL" value={targetUrl} onChange={e => setTargetUrl(e.target.value)} />
        <input type="number" placeholder="Priority (0 = highest)" value={priority}
          onChange={e => setPriority(Number(e.target.value))} />
        {error && <p className="error">{error}</p>}
        <button className="btn-primary" onClick={handleAdd}>Add Rule</button>
      </div>
    </div>
  )
}