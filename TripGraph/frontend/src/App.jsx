import { useCallback, useEffect, useState } from 'react'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import GraphView from './components/GraphView'
import NodeDetails from './components/NodeDetails'
import StatsPanel from './components/StatsPanel'
import EmptyState from './components/EmptyState'
import api from './services/api'

const API_URL = import.meta.env.VITE_API_URL

export default function App() {
  const [status, setStatus] = useState('checking')
  const [graphData, setGraphData] = useState(null)
  const [stats, setStats] = useState(null)
  const [filter, setFilter] = useState('All')
  const [selectedId, setSelectedId] = useState(null)
  const [focusToken, setFocusToken] = useState(0)
  const [loadError, setLoadError] = useState(null)

  const loadAll = useCallback(async () => {
    setStatus('checking')
    setLoadError(null)

    // 1. Is the API reachable at all?
    try {
      await api.root()
    } catch (e) {
      setStatus('api-offline')
      return
    }

    // 2. Is the database reachable?
    let dbStatus
    try {
      dbStatus = await api.dbTest()
    } catch (e) {
      setStatus('db-offline')
      return
    }
    if (!dbStatus.connected) {
      setStatus('db-offline')
      return
    }

    setStatus('connected')

    // 3. Load graph + stats
    try {
      const [graph, statsData] = await Promise.all([api.graph(), api.stats()])
      setGraphData(graph)
      setStats(statsData)
    } catch (e) {
      setLoadError(e.message)
    }
  }, [])

  useEffect(() => {
    loadAll()
  }, [loadAll])

  const selectedNode = graphData?.nodes.find((n) => n.id === selectedId) || null

  const handleSearchSelect = (item) => {
    setSelectedId(item.id)
    setFilter('All')
    setFocusToken((t) => t + 1)
  }

  const renderCanvasState = () => {
    // Only ever shown when GET / itself could not be reached.
    if (status === 'checking') return <EmptyState type="loading" />
    if (status === 'api-offline') return <EmptyState type="api-offline" apiUrl={API_URL} onRetry={loadAll} />
    if (status === 'db-offline') return <EmptyState type="db-offline" onRetry={loadAll} />
    // Backend + database were both reachable, but /graph or /stats itself
    // failed (e.g. a 500 from a query bug) - this is NOT the same as the
    // API being offline, so it gets its own message with the real error.
    if (loadError) return <EmptyState type="graph-error" errorMessage={loadError} onRetry={loadAll} />
    if (graphData && graphData.nodes.length === 0) return <EmptyState type="empty-graph" onRetry={loadAll} />
    return null
  }

  const canvasState = renderCanvasState()

  return (
    <div className="app-shell">
      <Header status={status} onRefresh={loadAll} onSearchSelect={handleSearchSelect} />

      <div className="app-body">
        <Sidebar active={filter} onChange={setFilter} />

        <main className="app-main">
          <div className="graph-panel">
            {canvasState ? (
              canvasState
            ) : (
              <GraphView
                graphData={graphData}
                filter={filter}
                selectedId={selectedId}
                onSelectNode={setSelectedId}
                focusToken={focusToken}
              />
            )}
          </div>

          <div className="bottom-panel">
            {selectedNode ? (
              <NodeDetails node={selectedNode} onClose={() => setSelectedId(null)} />
            ) : (
              <StatsPanel stats={stats} />
            )}
          </div>
        </main>
      </div>
    </div>
  )
}
