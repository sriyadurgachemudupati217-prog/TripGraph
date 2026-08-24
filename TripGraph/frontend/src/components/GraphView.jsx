import { useEffect, useMemo, useRef } from 'react'
import ReactFlow, {
  Background,
  Controls,
  Handle,
  Position,
  useNodesState,
  useEdgesState,
  MarkerType,
} from 'reactflow'
import 'reactflow/dist/style.css'

// Deterministic top-to-bottom hierarchy. Row index controls vertical
// placement; nodes within a row are spread horizontally. This is
// calculated ONCE per graph-data/filter change, never on every render.
const TYPE_ROWS = {
  Country: 0,
  City: 1,
  Destination: 2,
  Trip: 2,
  Attraction: 3,
  Activity: 3,
  Hotel: 3,
  Restaurant: 3,
  TravelConcept: 4,
}

const ROW_HEIGHT = 150
const NODE_WIDTH = 190

function layoutNodes(rawNodes, rawEdges) {
  const rows = {}
  rawNodes.forEach((n) => {
    const row = TYPE_ROWS[n.type] ?? 5
    rows[row] = rows[row] || []
    rows[row].push(n)
  })

  const positioned = []
  Object.entries(rows).forEach(([rowKey, nodesInRow]) => {
    const row = Number(rowKey)
    const totalWidth = nodesInRow.length * NODE_WIDTH
    const startX = -totalWidth / 2
    nodesInRow.forEach((n, i) => {
      positioned.push({
        id: n.id,
        type: 'default',
        data: { label: n.label, nodeType: n.type, description: n.description },
        position: { x: startX + i * NODE_WIDTH, y: row * ROW_HEIGHT },
        draggable: true,
      })
    })
  })

  const edges = rawEdges.map((e) => ({
    id: e.id,
    source: e.source,
    target: e.target,
    label: e.label,
    labelStyle: { fill: '#93A0C4', fontSize: 10 },
    labelBgStyle: { fill: '#141F3A', fillOpacity: 0.85 },
    style: { stroke: '#3E5490', strokeWidth: 1.5 },
    markerEnd: { type: MarkerType.ArrowClosed, color: '#3E5490', width: 16, height: 16 },
  }))

  return { nodes: positioned, edges }
}

function TripGraphNode({ data, selected }) {
  return (
    <div className={`tg-node ${selected ? 'selected' : ''}`} data-type={data.nodeType}>
      {/*
        React Flow computes every edge's anchor point from a <Handle>
        element inside the node. Without at least one target + one
        source handle, edges referencing this node cannot be drawn at
        all (they fail silently, only logging a console warning) - this
        is what was causing every edge to be invisible. Two handles
        (top = target, bottom = source) cover the top-to-bottom
        hierarchy used by the layout below.
      */}
      <Handle type="target" position={Position.Top} className="tg-handle" />
      <div className="tg-node-label">{data.label}</div>
      <div className="tg-node-type">{data.nodeType}</div>
      <Handle type="source" position={Position.Bottom} className="tg-handle" />
    </div>
  )
}

const nodeTypes = { default: TripGraphNode }

export default function GraphView({ graphData, filter, selectedId, onSelectNode, focusToken }) {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const reactFlowRef = useRef(null)

  const filteredData = useMemo(() => {
    if (!graphData) return { nodes: [], edges: [] }
    if (filter === 'All') return graphData
    const keep = new Set(
      graphData.nodes.filter((n) => n.type === filter).map((n) => n.id)
    )
    // Also keep directly connected neighbors so the filtered view isn't
    // just a set of floating disconnected nodes.
    const neighbor = new Set(keep)
    graphData.edges.forEach((e) => {
      if (keep.has(e.source)) neighbor.add(e.target)
      if (keep.has(e.target)) neighbor.add(e.source)
    })
    return {
      nodes: graphData.nodes.filter((n) => neighbor.has(n.id)),
      edges: graphData.edges.filter((e) => neighbor.has(e.source) && neighbor.has(e.target)),
    }
  }, [graphData, filter])

  // Recalculate layout ONLY when the underlying data or filter changes.
  useEffect(() => {
    const { nodes: laidOutNodes, edges: laidOutEdges } = layoutNodes(
      filteredData.nodes,
      filteredData.edges
    )
    setNodes(laidOutNodes)
    setEdges(laidOutEdges)
    // Fit view once, after layout settles.
    requestAnimationFrame(() => {
      reactFlowRef.current?.fitView({ padding: 0.25, duration: 300 })
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filteredData])

  // Focus on a specific node (from search) without recalculating layout.
  useEffect(() => {
    if (!focusToken || !selectedId) return
    const target = nodes.find((n) => n.id === selectedId)
    if (target && reactFlowRef.current) {
      reactFlowRef.current.setCenter(target.position.x + 90, target.position.y + 30, {
        zoom: 1.2,
        duration: 400,
      })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [focusToken])

  const styledNodes = useMemo(
    () =>
      nodes.map((n) => ({
        ...n,
        selected: n.id === selectedId,
      })),
    [nodes, selectedId]
  )

  return (
    <div className="graph-canvas">
      <ReactFlow
        nodes={styledNodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        onInit={(instance) => (reactFlowRef.current = instance)}
        onNodeClick={(_, node) => onSelectNode(node.id)}
        onPaneClick={() => onSelectNode(null)}
        minZoom={0.2}
        maxZoom={2}
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#1B2847" gap={28} size={1.5} />
        <Controls showInteractive={false} />
      </ReactFlow>

      <div className="graph-toolbar">
        <button onClick={() => reactFlowRef.current?.fitView({ padding: 0.25, duration: 300 })}>
          Fit view
        </button>
        <button
          onClick={() => {
            const { nodes: laidOutNodes, edges: laidOutEdges } = layoutNodes(
              filteredData.nodes,
              filteredData.edges
            )
            setNodes(laidOutNodes)
            setEdges(laidOutEdges)
            requestAnimationFrame(() => {
              reactFlowRef.current?.fitView({ padding: 0.25, duration: 300 })
            })
          }}
        >
          Reset graph
        </button>
      </div>
    </div>
  )
}
