const API_URL = import.meta.env.VITE_API_URL

async function request(path) {
  const response = await fetch(`${API_URL}${path}`)
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail || `Request failed: ${response.status}`)
  }
  return response.json()
}

export const api = {
  root: () => request('/'),
  dbTest: () => request('/db-test'),
  graph: () => request('/graph'),
  search: (q) => request(`/search?q=${encodeURIComponent(q)}`),
  destinations: () => request('/destinations'),
  destination: (id) => request(`/destinations/${encodeURIComponent(id)}`),
  destinationConnections: (id) => request(`/destinations/${encodeURIComponent(id)}/connections`),
  countries: () => request('/countries'),
  cities: () => request('/cities'),
  activities: () => request('/activities'),
  hotels: () => request('/hotels'),
  restaurants: () => request('/restaurants'),
  trips: () => request('/trips'),
  trip: (id) => request(`/trips/${encodeURIComponent(id)}`),
  node: (id) => request(`/nodes/${encodeURIComponent(id)}`),
  stats: () => request('/stats'),
}

export default api
