# Hendrickson

AI-driven multi-agent QA testing harness that synthesizes PRDs, source code, and ticketing systems (JIRA, Linear, GitHub) into a unified triangulated context graph — then generates, executes, and analyzes full-spectrum test suites.

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
│  • Settings Panel       │  • Connectors API   │                  │
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

## Service Setup

Before starting the backend, you must have MongoDB, Qdrant, and Docker installed and running. Choose one of the methods below for each service.

### 1. Docker

Docker is required for sandboxed test execution and for running MongoDB/Qdrant via docker-compose.

**macOS**
```bash
# Download and install Docker Desktop
# https://www.docker.com/products/docker-desktop/

# Or via Homebrew
brew install --cask docker
# Launch Docker Desktop from Applications, then verify:
docker --version
docker ps
```

**Linux (Ubuntu/Debian)**
```bash
sudo apt update
sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
# Log out and back in, then verify:
docker --version
docker ps
```

**Windows**
```powershell
# Download and install Docker Desktop from:
# https://www.docker.com/products/docker-desktop/
# After installation, verify in PowerShell:
docker --version
docker ps
```

### 2. MongoDB 7

**Option A: Docker (recommended)**
```bash
docker run -d --name mongodb \
  -p 27017:27017 \
  -v mongo_data:/data/db \
  -e MONGO_INITDB_DATABASE=hendrickson \
  mongo:7

# Verify
docker ps | grep mongodb
```

**Option B: Homebrew (macOS)**
```bash
brew tap mongodb/brew
brew install mongodb-community@7.0
brew services start mongodb-community@7.0

# Verify
mongosh --eval "db.version()"
```

**Option C: Direct install (Linux)**
```bash
# Ubuntu/Debian
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | sudo gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg
echo "deb [signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt update
sudo apt install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify
mongosh --eval "db.version()"
```

### 3. Qdrant

**Option A: Docker (recommended)**
```bash
docker run -d --name qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -v qdrant_data:/qdrant/storage \
  qdrant/qdrant:latest

# Verify
curl http://localhost:6333/health
```

**Option B: Quick install (macOS/Linux)**
```bash
# Download and run the latest binary
curl -fsSL https://qdrant.tech/install.sh | bash

# Or via Homebrew (macOS)
brew install qdrant
qdrant

# Verify
curl http://localhost:6333/health
```

### 4. Start All Services Together

Once Docker is installed, the simplest way to start MongoDB and Qdrant together:

```bash
docker-compose up -d mongodb qdrant
```

Verify all services are healthy:
```bash
# MongoDB
docker exec mongodb mongosh --eval "db.version()"

# Qdrant
curl -s http://localhost:6333/health

# Docker
docker ps
```

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
| `GEMINI_API_KEY` | _(empty)_ | Google Gemini API key (AI Studio) |
| `VERTEX_PROJECT` | _(empty)_ | GCP project ID for Vertex AI |
| `VERTEX_LOCATION` | `us-central1` | Vertex AI region |
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
| `POST` | `/api/contexts/triangulate` | Ingest PRD + repo + JIRA + Linear → unified context |
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
| `GET` | `/api/settings` | Get user settings (provider keys, connectors) |
| `POST` | `/api/settings/provider-keys` | Add a user-provided LLM API key |
| `DELETE` | `/api/settings/provider-keys/{provider}` | Remove a user-provided LLM API key |
| `POST` | `/api/settings/jira` | Configure JIRA connector |
| `POST` | `/api/settings/linear` | Configure Linear connector |
| `POST` | `/api/settings/github` | Configure GitHub connector |
| `DELETE` | `/api/settings/github` | Disconnect GitHub |
| `GET` | `/api/connectors/github/repos` | List GitHub repos |
| `GET` | `/api/connectors/github/repos/{owner}/{repo}/branches` | List repo branches |
| `POST` | `/api/connectors/jira/issue` | Get JIRA issue by key |
| `POST` | `/api/connectors/jira/search` | Search JIRA issues (JQL) |
| `POST` | `/api/connectors/linear/issue` | Get Linear issue by ID |
| `GET` | `/api/connectors/linear/teams` | List Linear teams |
| `POST` | `/api/connectors/linear/search` | Search Linear issues |
| `POST` | `/api/prd/upload` | Upload PRD file (.md, .txt, .pdf) |
| `POST` | `/api/prd/google-doc` | Fetch PRD from Google Doc URL |
| `WS` | `/ws/runs/{run_id}/logs` | Live execution log stream |

### LLM Providers

The backend supports 6 providers with 40+ models. At least one API key must be configured.

| Provider | Key Required | Models |
|---|---|---|
| **OpenAI** | `OPENAI_API_KEY` | GPT-5.6 Sol/Terra/Luna, GPT-5.5 Pro, GPT-5.4 Mini, o3, o3-pro, o4-mini, o4-mini-high |
| **Anthropic** | `ANTHROPIC_API_KEY` | Claude Fable 5, Opus 5, Sonnet 5, Haiku 4.5 |
| **DeepSeek** | `DEEPSEEK_API_KEY` | V4 Pro, V4 Flash |
| **Google Gemini** | `GEMINI_API_KEY` or Vertex AI | Gemini 2.5 Pro, Gemini 2.5 Flash, Gemini 2.5 Flash Lite |
| **OpenRouter** | `OPENROUTER_API_KEY` | 12 models across OpenAI, Anthropic, DeepSeek, Google, Meta |
| **Ollama** | None (local) | Llama 3.2, Qwen 2.5, Codestral, DeepSeek R1, Phi-4, Gemma 3 |

Gemini supports two authentication modes:
- **AI Studio**: Set `GEMINI_API_KEY` in `.env` or add it in the Settings panel
- **Vertex AI**: Set `VERTEX_PROJECT` and `VERTEX_LOCATION` in `.env`, or configure in the Settings panel (requires `gcloud auth application-default login`)

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
    │   ├── settings.py      # User settings (keys, connectors)
    │   ├── connectors.py    # GitHub/JIRA/Linear connector API
    │   ├── prd.py           # PRD file upload + Google Doc fetch
    │   └── ws.py            # WebSocket live logs
    ├── engines/
    │   ├── prd_parser.py    # Markdown/PDF → requirements
    │   ├── github_indexer.py # Repo clone + AST + diff
    │   ├── jira_connector.py # JIRA REST API
    │   ├── linear_connector.py # Linear GraphQL API
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

The dashboard has 5 tabbed panels plus a collapsible PRD drawer:

#### 1. AI Assistant (Chat)
- Conversational interface to the Hendrickson agent
- **Model picker** in the header — select from 35+ models across 5 providers
- RAG-powered: searches Qdrant for relevant requirements and code context
- Supports user-provided API keys configured in Settings
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

#### 5. Settings
- **LLM Provider Keys**: Add/remove per-user API keys for OpenAI, Anthropic, DeepSeek, OpenRouter
- **Gemini**: Configure via AI Studio API key or Vertex AI (GCP project + location)
- **GitHub**: Connect a GitHub account, browse repos, select repo + branch for triangulation
- **JIRA**: Configure JIRA instance URL, email, and API token; search and select issues
- **Linear**: Configure Linear API key; browse teams and select issues
- All settings are persisted in MongoDB and override environment-level defaults

#### PRD Drawer (left sidebar)
- Collapsible panel for ingesting PRD content
- Paste markdown or plain text requirements
- **Upload** .md, .txt, or .pdf files
- **Fetch** from a Google Doc URL
- Shows linked context: selected repo, branch, JIRA keys, Linear issue IDs
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
    │   ├── telemetry/
    │   │   └── TelemetryPanel.tsx # Recharts metrics
    │   └── settings/
    │       └── SettingsPanel.tsx # Provider keys + connectors
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
2. **Configure connectors**: Go to Settings tab, connect GitHub, JIRA, and/or Linear
3. **Open dashboard**: http://localhost:3000
4. **Ingest PRD**: Open the left drawer, paste PRD content (or upload a file, or fetch from Google Doc), click "Ingest PRD"
5. **Generate tests**: Go to Test Canvas tab, click +Unit, +Integration, +E2E, +UAT
6. **Inspect code**: Click any test case to view/edit in the Monaco editor
7. **Run tests**: Go to Runner tab, select environment, click "Run Test Suite"
8. **View results**: Watch live terminal output, then switch to Telemetry for metrics
9. **Chat with AI**: Ask the assistant questions about results, coverage, or next steps

### Scenario: JIRA Bug Fix Validation

1. **Configure JIRA**: In Settings, add your JIRA URL, email, and API token
2. **Triangulate**: `POST /api/contexts/triangulate` with `jira_keys: ["JIRA-402"]` and `repo_url`
3. **Chat**: _"Run a sanity check on JIRA-402 and run regression on affected billing modules"_
4. **Execute**: The system identifies modified functions via git diff, runs targeted tests
5. **Auto-update**: JIRA ticket transitions to "QA Verified" on pass

### Scenario: Linear Issue Validation

1. **Configure Linear**: In Settings, add your Linear API key
2. **Select issues**: Browse Linear teams and issues from the Settings panel
3. **Triangulate**: Ingest PRD with linked Linear issue IDs
4. **Generate + Execute**: The system generates tests scoped to the Linear issues and runs them

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
