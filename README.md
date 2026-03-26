# Handbook AI Process Mapper MVP

A full-stack MVP for the final-round project: the user writes a company process in a chat UI, the backend sends that text to OpenAI, and the frontend renders the returned process as a typed node diagram.

## Stack

- **Backend:** FastAPI + SQLAlchemy + SQLite
- **Frontend:** React + Vite + TypeScript + React Flow
- **LLM:** OpenAI Chat Completions with **structured JSON schema output**

## What it does

- Creates chat sessions
- Sends a process description to the backend
- Uses OpenAI to convert the text into:
  - a process title
  - a short summary
  - nodes (steps)
  - edges (transitions between steps)
- Stores the process graph in the database
- Renders the graph in the UI

## Database models

### `chat_sessions`
Represents a single chat thread.

### `chat_messages`
Stores user and assistant messages for a session.

### `processes`
Stores the original text, title, and summary for a generated process.

### `process_nodes`
Stores the generated steps. Each node has:
- `title`
- `description`
- `node_type` (`person`, `automation`, `mixed`, `decision`, `unknown`)
- `assignee_name`
- `position_index`

### `process_edges`
Stores transitions between nodes.

## API endpoints

### `POST /api/v1/chat/sessions`
Create a chat session.

### `GET /api/v1/chat/sessions`
List chat sessions.

### `GET /api/v1/chat/sessions/{session_id}`
Get one session and its messages.

### `POST /api/v1/chat/sessions/{session_id}/messages`
Send a user prompt, generate the process graph, persist it, and return the diagram payload.

### `POST /api/v1/processes/parse`
Stateless parse endpoint that also persists the generated graph.

### `GET /api/v1/processes`
List saved processes.

### `GET /api/v1/processes/{process_id}`
Get one saved process.

## Run locally

### 1) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# add your OPENAI_API_KEY
uvicorn app.main:app --reload --port 8000
```

### 2) Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open the frontend at `http://localhost:5173`.

## Example prompt

```text
When a customer requests a refund, a support agent reviews the request. If the request is valid, finance approves the refund and Stripe automatically sends the money back to the customer. If the request is invalid, the support agent sends a rejection email.
```

## Interview talking points

- I used a **structured-output LLM contract** so the model returns machine-readable graph data instead of free-form text.
- I separated **chat/session persistence** from **process graph persistence** so the product can evolve into multi-turn editing later.
- Node typing supports the core product requirement now while leaving room for richer execution logic later.
- The frontend uses **React Flow** plus **Dagre** so the generated process renders cleanly with automatic top-to-bottom layout.
- SQLite keeps the MVP lightweight, but the models are ready to move to PostgreSQL with minimal changes.

## Good next improvements

- Editable nodes and edges in the UI
- Support follow-up prompts like “make step 3 an automation”
- Add auth and per-user ownership
- Replace `create_all()` with Alembic migrations
- Add retry/fallback logic for malformed LLM outputs
- Stream assistant responses in the chat UI
