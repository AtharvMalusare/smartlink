import { useState } from 'react'
import { createLink } from '../api'
import SlugInput from '../components/SlugInput'

export default function Home() {
  const [url, setUrl] = useState('')
  const [slug, setSlug] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit() {
    if (!url) { setError('Please enter a URL'); return }
    setLoading(true); setError('')
    try {
      const res = await createLink({
        default_url: url,
        custom_slug: slug || undefined,
      })
      setResult(res.data)
    } catch (e) {
      setError(e.response?.data?.detail || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  if (result) return (
    <div className="container">
      <div className="card">
        <h2>Link Created</h2>
        <p style={{ marginBottom: '0.5rem' }}>Your short URL:</p>
        <a href={result.short_url} target="_blank" rel="noreferrer"
          style={{ color: '#6366f1', fontWeight: 600, fontSize: '1.1rem' }}>
          {result.short_url}
        </a>
        <div className="token-box">
          <strong>Manage Token — save this now:</strong><br />
          {result.manage_token}
        </div>
        <div className="warning">
          This token is shown only once. Save it to edit rules, view analytics, or delete this link.
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <button className="btn-primary" onClick={() => navigator.clipboard.writeText(result.manage_token)}>
            Copy Token
          </button>
          <button className="btn-secondary" onClick={() => { setResult(null); setUrl(''); setSlug('') }}>
            Create Another
          </button>
          <button className="btn-secondary" onClick={() => window.location.href = `/manage`}>
            Manage This Link
          </button>
        </div>
      </div>
    </div>
  )

  return (
    <div className="container">
      <h1>SmartLink</h1>
      <p className="subtitle">Context-aware URL shortener — route users by device, country, and more.</p>
      <div className="card">
        <h2>Create a link</h2>
        <input
          placeholder="https://your-long-url.com"
          value={url}
          onChange={e => setUrl(e.target.value)}
        />
        <SlugInput value={slug} onChange={setSlug} />
        {error && <p className="error">{error}</p>}
        <button className="btn-primary" onClick={handleSubmit} disabled={loading}>
          {loading ? 'Creating...' : 'Create Link'}
        </button>
      </div>
    </div>
  )
}