import dagre from 'dagre'
import {
  Background,
  Controls,
  MarkerType,
  MiniMap,
  ReactFlow,
  type Edge,
  type Node,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'

import type { ProcessGraph } from '../lib/api'
import ProcessNodeCard from './ProcessNodeCard'

const nodeTypes = {
  processNode: ProcessNodeCard,
}

const nodeWidth = 280
const nodeHeight = 140

function layoutGraph(graph: ProcessGraph) {
  const g = new dagre.graphlib.Graph()
  g.setDefaultEdgeLabel(() => ({}))
  g.setGraph({ rankdir: 'TB', nodesep: 40, ranksep: 80, marginx: 20, marginy: 20 })

  graph.nodes.forEach((node) => g.setNode(node.id, { width: nodeWidth, height: nodeHeight }))
  graph.edges.forEach((edge) => g.setEdge(edge.source, edge.target))
  dagre.layout(g)

  const nodes: Node[] = graph.nodes.map((node) => {
    const position = g.node(node.id)
    return {
      id: node.id,
      type: 'processNode',
      position: {
        x: position.x - nodeWidth / 2,
        y: position.y - nodeHeight / 2,
      },
      data: {
        title: node.title,
        description: node.description,
        type: node.type,
        assigneeName: node.assignee_name,
      },
    }
  })

  const edges: Edge[] = graph.edges.map((edge, index) => ({
    id: edge.id ?? `edge-${index}`,
    source: edge.source,
    target: edge.target,
    label: edge.label ?? undefined,
    markerEnd: { type: MarkerType.ArrowClosed },
    animated: false,
  }))

  return { nodes, edges }
}

interface Props {
  graph: ProcessGraph | null
}

export default function ProcessDiagram({ graph }: Props) {
  if (!graph) {
    return (
      <div className="empty-state">
        <h3>No process yet</h3>
        <p>Describe a workflow in the chat and the diagram will appear here.</p>
      </div>
    )
  }

  const { nodes, edges } = layoutGraph(graph)

  return (
    <div className="diagram-wrapper">
      <div className="diagram-header">
        <div>
          <h2>{graph.title}</h2>
          <p>{graph.summary}</p>
        </div>
        <div className="diagram-stats">
          <span>{graph.nodes.length} steps</span>
          <span>{graph.edges.length} transitions</span>
        </div>
      </div>
      <div className="diagram-canvas">
        <ReactFlow nodes={nodes} edges={edges} fitView nodeTypes={nodeTypes}>
          <MiniMap />
          <Controls />
          <Background />
        </ReactFlow>
      </div>
    </div>
  )
}
