import { useState, useRef, useEffect } from 'react'
import api from '../services/api'

export default function SearchBar({ onSelect }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState(null)
  const [open, setOpen] = useState(false)
  const wrapRef = useRef(null)

  useEffect(() => {
    function handleClickOutside(e) {
      if (wrapRef.current && !wrapRef.current.contains(e.target)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  useEffect(() => {
    if (!query.trim()) {
      setResults(null)
      return
    }
    const timeout = setTimeout(async () => {
      try {
        const data = await api.search(query.trim())
        setResults(data.results || [])
        setOpen(true)
      } catch (e) {
        setResults([])
        setOpen(true)
      }
    }, 250)
    return () => clearTimeout(timeout)
  }, [query])

  const grouped = (results || []).reduce((acc, item) => {
    acc[item.type] = acc[item.type] || []
    acc[item.type].push(item)
    return acc
  }, {})

  return (
    <div className="search-input-wrap" ref={wrapRef}>
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="11" cy="11" r="8" />
        <path d="m21 21-4.35-4.35" />
      </svg>
      <input
        className="search-input"
        placeholder="Search destinations, cities, countries..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onFocus={() => query && setOpen(true)}
      />

      {open && results !== null && (
        <div className="search-results">
          {results.length === 0 ? (
            <div className="search-results-empty">
              No destinations found.
              <div className="suggestion-list">
                {['Paris', 'Tokyo', 'Japan', 'Beach', 'Adventure'].map((s) => (
                  <span
                    key={s}
                    className="chip"
                    style={{ cursor: 'pointer' }}
                    onClick={() => setQuery(s)}
                  >
                    {s}
                  </span>
                ))}
              </div>
            </div>
          ) : (
            Object.entries(grouped).map(([type, items]) => (
              <div className="search-results-group" key={type}>
                <h4>{type}</h4>
                {items.map((item) => (
                  <div
                    key={item.id}
                    className="search-result-item"
                    onClick={() => {
                      onSelect(item)
                      setOpen(false)
                      setQuery(item.label)
                    }}
                  >
                    <span>{item.label}</span>
                  </div>
                ))}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  )
}
