const FILTERS = [
  { key: 'All', label: 'All' },
  { key: 'Country', label: 'Countries' },
  { key: 'City', label: 'Cities' },
  { key: 'Destination', label: 'Destinations' },
  { key: 'Activity', label: 'Activities' },
  { key: 'Hotel', label: 'Hotels' },
  { key: 'Restaurant', label: 'Restaurants' },
  { key: 'Trip', label: 'Trips' },
]

export default function Sidebar({ active, onChange }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-label">Explore</div>
      {FILTERS.map((f) => (
        <div
          key={f.key}
          className={`sidebar-item ${active === f.key ? 'active' : ''}`}
          onClick={() => onChange(f.key)}
        >
          <span className="dot" />
          {f.label}
        </div>
      ))}
    </aside>
  )
}
