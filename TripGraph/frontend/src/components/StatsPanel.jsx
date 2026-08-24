const LABELS = {
  countries: 'Countries',
  cities: 'Cities',
  destinations: 'Destinations',
  activities: 'Activities',
  hotels: 'Hotels',
  restaurants: 'Restaurants',
  trips: 'Trips',
}

export default function StatsPanel({ stats }) {
  if (!stats) return null
  return (
    <div className="stats-grid">
      {Object.entries(LABELS).map(([key, label]) => (
        <div className="stat-card" key={key}>
          <div className="stat-number">{stats[key] ?? 0}</div>
          <div className="stat-label">{label}</div>
        </div>
      ))}
    </div>
  )
}
