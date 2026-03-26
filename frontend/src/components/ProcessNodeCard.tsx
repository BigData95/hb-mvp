import { Handle, Position, type NodeProps } from '@xyflow/react'

type NodeData = {
  title: string
  description?: string | null
  type: string
  assigneeName?: string | null
}

export default function ProcessNodeCard({ data }: NodeProps) {
  const typedData = data as NodeData

  return (
    <div className={`node-card node-${typedData.type}`}>
      <Handle type="target" position={Position.Top} />
      <div className="node-chip">{typedData.type}</div>
      <h4>{typedData.title}</h4>
      {typedData.assigneeName ? <p><strong>Owner:</strong> {typedData.assigneeName}</p> : null}
      {typedData.description ? <p>{typedData.description}</p> : null}
      <Handle type="source" position={Position.Bottom} />
    </div>
  )
}
