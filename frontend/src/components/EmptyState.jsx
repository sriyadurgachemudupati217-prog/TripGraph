export default function EmptyState({ type, apiUrl, errorMessage, onRetry }) {
  if (type === 'loading') {
    return (
      <div className="state-panel">
        <div className="spinner" />
        <p>Loading travel graph...</p>
      </div>
    )
  }

  if (type === 'api-offline') {
    return (
      <div className="state-panel">
        <h3>TripGraph API unavailable</h3>
        <p>
          Make sure the FastAPI backend is running on <code>{apiUrl}</code>
        </p>
        <button className="retry-button" onClick={onRetry}>Retry</button>
      </div>
    )
  }

  if (type === 'db-offline') {
    return (
      <div className="state-panel">
        <h3>CognoDB unavailable</h3>
        <p>The TripGraph API is running, but the graph database could not be reached.</p>
        <button className="retry-button" onClick={onRetry}>Retry</button>
      </div>
    )
  }

  if (type === 'graph-error') {
    return (
      <div className="state-panel">
        <h3>Couldn't load the travel graph</h3>
        <p>
          The TripGraph API and database are both reachable, but loading the
          graph data failed.
        </p>
        {errorMessage && <code>{errorMessage}</code>}
        <button className="retry-button" onClick={onRetry}>Retry</button>
      </div>
    )
  }

  if (type === 'empty-graph') {
    return (
      <div className="state-panel">
        <h3>No graph data yet</h3>
        <p>Run the seed script to populate CognoDB with the TripGraph demo dataset.</p>
        <code>python -m app.seed_data</code>
        <button className="retry-button" onClick={onRetry}>Retry</button>
      </div>
    )
  }

  return null
}
