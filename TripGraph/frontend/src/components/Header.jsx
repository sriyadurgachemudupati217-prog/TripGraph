import SearchBar from './SearchBar'

function StatusPill({ status }) {
  const labelMap = {
    checking: 'Checking...',
    connected: 'Connected',
    'db-offline': 'Database Offline',
    'api-offline': 'API Offline',
  }
  return (
    <div className={`status-pill ${status}`}>
      <span className="status-dot" />
      {labelMap[status] || 'Unknown'}
    </div>
  )
}

export default function Header({ status, onRefresh, onSearchSelect }) {
  return (
    <header className="header">
      <div className="header-brand">
        <div className="brand-mark">
          <h1>TripGraph</h1>
          <span className="brand-dot" />
        </div>
        <p>Explore the world through connections.</p>
      </div>

      <div className="header-search">
        <SearchBar onSelect={onSearchSelect} />
      </div>

      <div className="header-actions">
        <StatusPill status={status} />
        <button className="icon-button" onClick={onRefresh} title="Refresh">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M23 4v6h-6" />
            <path d="M1 20v-6h6" />
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
          </svg>
        </button>
      </div>
    </header>
  )
}
