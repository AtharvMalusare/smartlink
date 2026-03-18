import { useState, useEffect } from 'react'
import { checkSlug } from '../api'

export default function SlugInput({ value, onChange }) {
  const [status, setStatus] = useState(null)

  useEffect(() => {
    if (!value) { setStatus(null); return }
    const timer = setTimeout(async () => {
      try {
        const res = await checkSlug(value)
        setStatus(res.data)
      } catch {
        setStatus(null)
      }
    }, 400)
    return () => clearTimeout(timer)
  }, [value])

  return (
    <div>
      <div className="slug-row">
        <span style={{ padding: '0.6rem 0', whiteSpace: 'nowrap', color: '#6b7280', fontSize: '0.9rem' }}>
          localhost:8000/
        </span>
        <input
          placeholder="my-custom-slug (optional)"
          value={value}
          onChange={e => onChange(e.target.value)}
        />
      </div>
      {status && (
        <p className={status.available ? 'success' : 'error'} style={{ marginTop: '-0.25rem', marginBottom: '0.75rem' }}>
          {status.available ? 'Available' : status.reason}
        </p>
      )}
    </div>
  )
}