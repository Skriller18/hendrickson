# Hendrickson

AI-driven multi-agent QA testing harness that synthesizes PRDs, source code, and ticketing systems into a unified triangulated context graph — then generates, executes, and analyzes full-spectrum test suites.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     HENDRICKSON HARNESS                          │
├──────────────────────────────────────────────────────────────────┤
│  Frontend (Next.js 15)  │  Backend (FastAPI)  │  Services        │
│  ─────────────────────  │  ────────────────   │  ────────        │
│  • AI Chat + Model Pick │  • Triangulation    │  • MongoDB 7     │
│  • PRD Document Drawer  │  • Multi-Agent Gen  │  • Qdrant        │
│  • Test Canvas + Monaco │  • Docker Sandbox   │  • Docker SDK    │
│  • Execution Runner     │  • RAG Vector Store │                  │
│  • Telemetry Dashboard  │  • WebSocket Logs   │                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

| Dependency | Version | Required For |
|---|---|---|
| Python | 3.12+ | Backend |
| Node.js | 22+ | Frontend |
| Docker | 24+ | Sandbox execution + docker-compose |
| MongoDB | 7 | Data persistence |
| Qdrant | latest | Vector embeddings / RAG |

---

## Quick Start (Docker)

```bash
# 1. Clone and configure
git clone https://github.com/Skriller18/hendrickson.git
cd hendrickson
cp .env.example .env
# Edit .env — add at least one LLM API key

# 2. Start everything
docker-compose up --build

# 3. Open
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/api/health
# API Docs: http://localhost:8000/docs
```

---

## Backend

### Setup

```bash
cd backend

# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy env from root
cp ../.env.example ../.env
# Edit ../.env with your API keys
```

### Configuration

All settings are read from `.env` (at the project root). The backend reads it via `pydantic-settings`.

| Variable | Default | Description |
|---|---|---|
| `MONGODB_URI` | `mongodb://localhost:27017` | MongoDB connection string |
| `MONGODB_DB` | `hendrickson` | Database name |
| `QDRANT_URL` | `http://localhost:6333` | Qdrant vector DB URL |
| `QDRANT_API_KEY` | _(empty)_ | Qdrant API key (cloud) |
| `OPENAI_API_KEY` | _(empty)_ | OpenAI API key |
| `ANTHROPIC_API_KEY` | _(empty)_ | Anthropic API key |
| `DEEPSEEK_API_KEY` | _(empty)_ | DeepSeek API key |
| `OPENROUTER_API_KEY` | _(empty)_ | OpenRouter API key |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama local server |
| `DEFAULT_LLM_MODEL` | `gpt-5.6-terra` | Default model for generation |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | OpenAI embedding model |
| `GITHUB_TOKEN` | _(empty)_ | GitHub personal access token |
| `JIRA_URL` | _(empty)_ | JIRA instance URL |
| `JIRA_EMAIL` | _(empty)_ | JIRA account email |
| `JIRA_API_TOKEN` | _(empty)_ | JIRA API token |
| `BACKEND_PORT` | `8000` | Server port |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed CORS origins |

### Run

```bash
cd backend
source .venv/bin/activate
uvicorn src.main:app --reload --port 8000
```

### API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/chat/send` | Send message to AI assistant (with RAG) |
| `POST` | `/api/contexts/triangulate` | Ingest PRD + repo + JIRA → unified context |
| `GET` | `/api/contexts` | List all contexts |
| `GET` | `/api/contexts/{id}` | Get context by ID |
| `POST` | `/api/tests/generate` | Generate test suite from context |
| `GET` | `/api/tests` | List test cases |
| `GET` | `/api/tests/{id}` | Get test case by ID |
| `PUT` | `/api/tests/{id}` | Update test case |
| `POST` | `/api/runs/execute` | Execute test suite in sandbox |
| `GET` | `/api/runs` | List test runs |
| `GET` | `/api/runs/{id}` | Get run results |
| `GET` | `/api/models` | List all available LLM models |
| `GET` | `/api/models/providers` | List LLM providers |
| `WS` | `/ws/runs/{run_id}/logs` | Live execution log stream |

### LLM Providers

The backend supports 5 providers with 35+ models. At least one API key must be configured.

| Provider | Key Required | Models |
|---|---|---|
| **OpenAI** | `OPENAI_API_KEY` | GPT-5.6 Sol/Terra/Luna, GPT-5.5 Pro, GPT-5.4 Mini, o3, o3-pro, o4-mini, o4-mini-high |
| **Anthropic** | `ANTHROPIC_API_KEY` | Claude Fable 5, Opus 5, Sonnet 5, Haiku 4.5 |
| **DeepSeek** | `DEEPSEEK_API_KEY` | V4 Pro, V4 Flash |
| **OpenRouter** | `OPENROUTER_API_KEY` | 12 models across OpenAI, Anthropic, DeepSeek, Google, Meta |
| **Ollama** | None (local) | Llama 3.2, Qwen 2.5, Codestral, DeepSeek R1, Phi-4, Gemma 3 |

The system auto-falls back across configured providers if the selected one is unavailable.

### Project Structure

```
backend/
├── pyproject.toml
├── requirements.txt
├── Dockerfile
└── src/
    ├── main.py              # FastAPI app entry, startup/shutdown
    ├── config.py            # Pydantic settings from .env
    ├── api/
    │   ├── chat.py          # AI chat with RAG context
    │   ├── contexts.py      # Triangulation + CRUD
    │   ├── tests.py         # Test generation + CRUD
    │   ├── runs.py          # Test execution + results
    │   ├── models.py        # Model catalog listing
    │   └── ws.py            # WebSocket live logs
    ├── engines/
    │   ├── prd_parser.py    # Markdown/PDF → requirements
    │   ├── github_indexer.py # Repo clone + AST + diff
    │   ├── jira_connector.py # JIRA REST API
    │   └── triangulator.py  # Merge into unified context
    ├── agents/
    │   ├── models.py        # 35+ model catalog
    │   ├── llm_provider.py  # Multi-provider abstraction
    │   ├── orchestrator.py  # LangGraph orchestration
    │   ├── unit_agent.py    # Unit test generation
    │   ├── integration_agent.py
    │   ├── e2e_agent.py     # Playwright E2E generation
    │   └── uat_agent.py     # Gherkin BDD generation
    ├── services/
    │   ├── sandbox.py       # Docker SDK test execution
    │   ├── vector_store.py  # Qdrant + OpenAI embeddings
    │   └── metrics.py       # Coverage, flakiness, PRD coverage
    └── models/
        ├── context.py       # Triangulated context schema
        ├── test_case.py     # Test case schema
        └── test_run.py      # Test run/result schema
```

---

## Frontend

### Setup

```bash
cd frontend
npm install
```

### Configuration

Create `.env.local` in the frontend directory (or use the root `.env`):

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API URL |
| `NEXT_PUBLIC_WS_URL` | `ws://localhost:8000` | Backend WebSocket URL |

### Run

```bash
cd frontend
npm run dev
# Opens at http://localhost:3000
```

### Dashboard Panels

The dashboard has 4 tabbed panels plus a collapsible PRD drawer:

#### 1. AI Assistant (Chat)
- Conversational interface to the Hendrickson agent
- **Model picker** in the header — select from 35+ models across 5 providers
- RAG-powered: searches Qdrant for relevant requirements and code context
- Example prompts:
  - _"Generate a full test suite for my PRD"_
  - _"Run sanity check on JIRA-402"_
  - _"Show me test coverage metrics"_

#### 2. Test Canvas
- Left sidebar: list of all generated test cases with status badges
- Right panel: **Monaco Editor** for viewing and editing generated test code
- Quick-generate buttons: +Unit, +Integration, +E2E, +UAT
- Requires an active context (ingest a PRD first)

#### 3. Execution Runner
- Environment selector (Sandbox / Staging / Docker)
- **"Run Test Suite"** button executes all tests in the Docker sandbox
- Live terminal output showing stdout/stderr with color-coded pass/fail
- Results stored in MongoDB and reflected in Telemetry

#### 4. Telemetry
- Metric cards: Total Tests, Pass Rate, Last Run Duration, Coverage
- Pie chart: test status distribution (Passed / Failed / Ready / Draft)
- Bar chart: run history with pass/fail breakdown
- Updates automatically after each test run

#### PRD Drawer (left sidebar)
- Collapsible panel for ingesting PRD content
- Paste markdown or plain text requirements
- Click **"Ingest PRD"** to parse, triangulate, and index into Qdrant
- Extracted requirements displayed with tags and descriptions

### Project Structure

```
frontend/
├── package.json
├── next.config.ts
├── tsconfig.json
├── tailwind.config.ts
├── postcss.config.mjs
├── Dockerfile
└── src/
    ├── app/
    │   ├── layout.tsx        # Root layout (dark theme)
    │   ├── page.tsx          # Dashboard with tabbed panels
    │   └── globals.css       # Tailwind + CSS variables
    ├── components/
    │   ├── chat/
    │   │   └── ChatPanel.tsx  # AI chat + model picker
    │   ├── drawer/
    │   │   └── DrawerPanel.tsx # PRD ingestion + requirements
    │   ├── canvas/
    │   │   └── CanvasPanel.tsx # Test list + Monaco editor
    │   ├── runner/
    │   │   └── RunnerPanel.tsx # Execution + live terminal
    │   └── telemetry/
    │       └── TelemetryPanel.tsx # Recharts metrics
    ├── lib/
    │   ├── api.ts            # Typed API client
    │   ├── ws.ts             # WebSocket client
    │   └── utils.ts          # cn(), formatDuration(), statusColor()
    └── stores/
        └── index.ts          # Zustand global state
```

---

## End-to-End Workflow

### Scenario: PRD → Tests → Execute → Metrics

1. **Start services**: `docker-compose up -d mongodb qdrant` then start backend + frontend
2. **Open dashboard**: http://localhost:3000
3. **Ingest PRD**: Open the left drawer, paste PRD content, click "Ingest PRD"
4. **Generate tests**: Go to Test Canvas tab, click +Unit, +Integration, +E2E, +UAT
5. **Inspect code**: Click any test case to view/edit in the Monaco editor
6. **Run tests**: Go to Runner tab, select environment, click "Run Test Suite"
7. **View results**: Watch live terminal output, then switch to Telemetry for metrics
8. **Chat with AI**: Ask the assistant questions about results, coverage, or next steps

### Scenario: JIRA Bug Fix Validation

1. **Triangulate**: `POST /api/contexts/triangulate` with `jira_keys: ["JIRA-402"]` and `repo_url`
2. **Chat**: _"Run a sanity check on JIRA-402 and run regression on affected billing modules"_
3. **Execute**: The system identifies modified functions via git diff, runs targeted tests
4. **Auto-update**: JIRA ticket transitions to "QA Verified" on pass

---

## Development

### Backend

```bash
cd backend
source .venv/bin/activate
uvicorn src.main:app --reload --port 8000
# API docs at http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm run dev
# Hot reload at http://localhost:3000
```

### Lint & Typecheck

```bash
# Backend
cd backend && ruff check src/

# Frontend
cd frontend && npm run lint && npm run typecheck
```

---

## Infrastructure Services

| Service | Port | Purpose |
|---|---|---|
| MongoDB | 27017 | Contexts, test cases, runs, requirements |
| Qdrant | 6333 (REST), 6334 (gRPC) | Vector embeddings for RAG |
| Backend | 8000 | FastAPI REST + WebSocket |
| Frontend | 3000 | Next.js dashboard |
| Ollama | 11434 | Local LLM inference (optional) |
