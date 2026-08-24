import { useEffect, useState } from 'react'
import api from '../services/api'

function Chips({ items }) {
  if (!items || items.length === 0) {
    return <span style={{ color: 'var(--color-text-faint)', fontSize: 13 }}>None yet</span>
  }
  return (
    <div className="chip-row">
      {items.map((item) => (
        <span className="chip" key={item}>{item}</span>
      ))}
    </div>
  )
}

export default function NodeDetails({ node, onClose }) {
  const [details, setDetails] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!node) {
      setDetails(null)
      return
    }
    let cancelled = false
    setLoading(true)
    api
      .node(node.id)
      .then((data) => {
        if (!cancelled) setDetails(data)
      })
      .catch(() => {
        if (!cancelled) setDetails(null)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [node])

  if (!node) {
    return (
      <div className="details-empty">
        <p style={{ color: 'var(--color-text-muted)', fontSize: 13.5, margin: 0 }}>
          Select a node in the graph, or search above, to see full travel details here.
        </p>
      </div>
    )
  }

  const outgoing = details?.outgoing?.filter((o) => o.name) || []
  const incoming = details?.incoming?.filter((i) => i.name) || []

  const byRelation = (list, relType) =>
    list.filter((r) => r.type === relType).map((r) => r.name)

  return (
    <div>
      <div className="details-header">
        <h2>{node.label}</h2>
        <span className="type-badge">{node.type}</span>
        <button className="close-button" onClick={onClose}>×</button>
      </div>

      {node.description && <p className="details-description">{node.description}</p>}

      {loading ? (
        <p style={{ color: 'var(--color-text-muted)', fontSize: 13 }}>Loading connections...</p>
      ) : (
        <>
          {byRelation(outgoing, 'HAS_ATTRACTION').length > 0 && (
            <div className="details-section">
              <h4>Attractions</h4>
              <Chips items={byRelation(outgoing, 'HAS_ATTRACTION')} />
            </div>
          )}
          {byRelation(outgoing, 'OFFERS').length > 0 && (
            <div className="details-section">
              <h4>Activities</h4>
              <Chips items={byRelation(outgoing, 'OFFERS')} />
            </div>
          )}
          {byRelation(outgoing, 'HAS_HOTEL').length > 0 && (
            <div className="details-section">
              <h4>Nearby hotels</h4>
              <Chips items={byRelation(outgoing, 'HAS_HOTEL')} />
            </div>
          )}
          {byRelation(outgoing, 'HAS_RESTAURANT').length > 0 && (
            <div className="details-section">
              <h4>Nearby restaurants</h4>
              <Chips items={byRelation(outgoing, 'HAS_RESTAURANT')} />
            </div>
          )}
          {byRelation(outgoing, 'SUITABLE_FOR').length > 0 && (
            <div className="details-section">
              <h4>Travel concepts</h4>
              <Chips items={byRelation(outgoing, 'SUITABLE_FOR')} />
            </div>
          )}
          {byRelation(outgoing, 'RELATED_TO').length > 0 && (
            <div className="details-section">
              <h4>Related</h4>
              <Chips items={byRelation(outgoing, 'RELATED_TO')} />
            </div>
          )}
          {byRelation(outgoing, 'HAS_DESTINATION').length > 0 && (
            <div className="details-section">
              <h4>Destinations</h4>
              <Chips items={byRelation(outgoing, 'HAS_DESTINATION')} />
            </div>
          )}
          {byRelation(outgoing, 'CONTAINS').length > 0 && (
            <div className="details-section">
              <h4>Cities</h4>
              <Chips items={byRelation(outgoing, 'CONTAINS')} />
            </div>
          )}
          {byRelation(outgoing, 'VISITS').length > 0 && (
            <div className="details-section">
              <h4>Trip visits</h4>
              <Chips items={byRelation(outgoing, 'VISITS')} />
            </div>
          )}
          {incoming.length > 0 && (
            <div className="details-section">
              <h4>Connected from</h4>
              <Chips items={incoming.map((i) => `${i.name} (${i.label})`)} />
            </div>
          )}
        </>
      )}
    </div>
  )
}
