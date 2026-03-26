import { FormEvent, useEffect, useMemo, useState } from 'react'

import ProcessDiagram from './components/ProcessDiagram'
import { createSession, getSession, sendMessage, type ChatMessage, type ProcessGraph, type Session } from './lib/api'

const samplePrompt = `When a new lead requests a demo, an SDR qualifies the lead. If the lead is qualified, an AE schedules the demo. After the demo, the AE sends a proposal. If the proposal is signed, finance creates the invoice and an onboarding automation sends the welcome email.`

export default function App() {
  const [session, setSession] = useState<Session | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [graph, setGraph] = useState<ProcessGraph | null>(null)
  const [input, setInput] = useState(samplePrompt)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const bootstrap = async () => {
      try {
        const created = await createSession()
        setSession(created)
        const loaded = await getSession(created.id)
        setMessages(loaded.messages)
      } catch (err) {
        setError('Could not initialize the chat session.')
      }
    }
    bootstrap()
  }, [])

  const canSubmit = useMemo(() => input.trim().length > 0 && !loading && !!session, [input, loading, session])

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    if (!session || !input.trim()) return

    const content = input.trim()
    const optimisticUserMessage: ChatMessage = {
      id: `local-${Date.now()}`,
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, optimisticUserMessage])
    setInput('')
    setLoading(true)
    setError(null)

    try {
      const response = await sendMessage(session.id, content)
      const refreshed = await getSession(session.id)
      setMessages(refreshed.messages)
      setGraph(response.graph)
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Something went wrong while mapping the process.')
      setMessages((prev) => prev.filter((message) => message.id !== optimisticUserMessage.id))
      setInput(content)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-shell">
      <aside className="chat-panel">
        <div className="app-header">
          <p className="eyebrow">Handbook AI MVP</p>
          <h1>Process Mapper</h1>
          <p>
            Paste a company workflow in plain English. The assistant converts it into typed process steps and renders a node diagram.
          </p>
        </div>

        <div className="messages">
          {messages.length === 0 ? (
            <div className="hint-card">
              <strong>Try something like:</strong>
              <p>{samplePrompt}</p>
            </div>
          ) : null}

          {messages.map((message) => (
            <div key={message.id} className={`message-bubble ${message.role}`}>
              <span className="message-role">{message.role === 'user' ? 'You' : 'Assistant'}</span>
              <p>{message.content}</p>
            </div>
          ))}
        </div>

        <form className="composer" onSubmit={handleSubmit}>
          <textarea
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Describe a process, for example: HR receives a vacation request, a manager approves it, payroll updates balances..."
            rows={8}
          />
          {error ? <div className="error-banner">{error}</div> : null}
          <button type="submit" disabled={!canSubmit}>
            {loading ? 'Mapping process...' : 'Generate process map'}
          </button>
        </form>
      </aside>

      <main className="diagram-panel">
        <ProcessDiagram graph={graph} />
      </main>
    </div>
  )
}
