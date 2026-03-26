import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1',
})

export type MessageRole = 'user' | 'assistant'

export interface Session {
  id: string
  title: string
  created_at: string
  updated_at?: string | null
  messages: ChatMessage[]
}

export interface ChatMessage {
  id: string
  role: MessageRole
  content: string
  process_id?: string | null
  created_at: string
}

export interface GraphNode {
  id: string
  node_key?: string
  title: string
  description?: string | null
  type: 'person' | 'automation' | 'mixed' | 'decision' | 'unknown'
  assignee_name?: string | null
  position_index?: number
}

export interface GraphEdge {
  id?: string
  source: string
  target: string
  label?: string | null
  position_index?: number
}

export interface ProcessGraph {
  process_id: string
  title: string
  summary: string
  nodes: GraphNode[]
  edges: GraphEdge[]
}

export interface SendMessageResponse {
  user_message_id: string
  assistant_message_id: string
  assistant_text: string
  graph: ProcessGraph
}

export async function createSession() {
  const { data } = await api.post<Session>('/chat/sessions', { title: 'New process chat' })
  return data
}

export async function getSession(sessionId: string) {
  const { data } = await api.get<Session>(`/chat/sessions/${sessionId}`)
  return data
}

export async function sendMessage(sessionId: string, content: string) {
  const { data } = await api.post<SendMessageResponse>(`/chat/sessions/${sessionId}/messages`, {
    content,
    persist_process: true,
  })
  return data
}
