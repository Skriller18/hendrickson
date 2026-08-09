# PRODUCT.MD — HENDRICKSON: AI-DRIVEN QA AGENT HARNESS & TRIPLE-ENGINE TESTING PLATFORM

---

## 1. EXECUTIVE SUMMARY & VISION

### 1.1 Overview
**Hendrickson** is an autonomous, multi-agent QA and Testing Harness designed to bridge the structural disconnect in modern software engineering teams. Every active software project is built upon three foundational artifacts:
1. **Product Requirement Documents (PRDs)**: Defining human intent, functional logic, edge cases, and business rules.
2. **Source Code Repositories (GitHub / GitLab)**: Containing the actual implementation, ASTs, API definitions, schemas, and PR diffs.
3. **Ticketing & Work Tracking Systems (JIRA / Linear)**: Recording software bugs, failed test runs, patch histories, and workflow states.

Hendrickson synthesizes these three data sources into a unified **Triangulated QA Context Graph**. Through an interactive, developer-centric Frontend Dashboard, engineering and product teams can interrogate their codebase, generate full-spectrum automated test suites (Functional, Operational, and Non-Functional), inspect generated test code, execute tests within secure isolated sandboxes, and analyze real-time multi-dimensional quality metrics.

```
+-----------------------------------------------------------------------------------+
|                                HENDRICKSON HARNESS                                |
+-----------------------------------------------------------------------------------+
                                          |
         +--------------------------------+--------------------------------+
         |                                |                                |
         v                                v                                v
+------------------+             +------------------+             +------------------+
|    PRD ENGINE    |             |  CODEBASE ENGINE |             | TICKETING ENGINE |
| (Notion/Doc/MD)  |             |  (GitHub Repos)  |             |  (JIRA / Linear) |
+--------+---------+             +--------+---------+             +--------+---------+
         |                                |                                |
         +--------------------------------+--------------------------------+
                                          |
                                          v
                              +-----------------------+
                              |   Unified QA Graph    |
                              |   & Context Engine    |
                              +-----------+-----------+
                                          |
                                          v
                              +-----------------------+
                              | Multi-Agent AI Harness|
                              +-----------+-----------+
                                          |
           +------------------------------+------------------------------+
           |                              |                              |
           v                              v                              v
+--------------------+         +--------------------+         +--------------------+
| Functional Testing |         |Operational Testing |         |  Non-Functional    |
| (Unit/Int/E2E/UAT) |         |(Smoke/Sanity/Regr) |         |(Perf/Stress/Sec)   |
+--------------------+         +--------------------+         +--------------------+
```

---

## 2. THE THREE PILLARS OF CONTEXT INTEGRATION

### 2.1 PRD Ingestion & Spec Parser Engine
* **Source Support**: Markdown (`.md`), Confluence, Notion, Google Docs, PDF specs.
* **Extraction Logic**: Parses documents into atomic business rules, acceptance criteria, user stories, boundary conditions, and flow diagrams.
* **Tagging & Requirement Indexing**: Assigns unique identifiers (e.g., `@req-auth-01`, `@req-billing-04`) to establish 1:1 traceability matrices with generated tests.

### 2.2 GitHub Codebase & AST Graph Engine
* **Source Support**: GitHub Repositories (Public/Private), GitLab, Bitbucket.
* **Analysis**: Performs deep AST (Abstract Syntax Tree) indexing, symbol resolution, API route extraction, database ORM mapping, and dependency tree generation.
* **Impact Tracking**: Analyzes `git diff` and pull request modifications to determine exactly which code paths have changed relative to uploaded PRDs.

### 2.3 Ticketing Software Sync Engine (JIRA / Linear)
* **Source Support**: JIRA Cloud/Server REST API, Linear GraphQL API, GitHub Issues.
* **Data Harvested**: Bug reports, stack traces, regression tickets, failed test logs, and assigned feature tickets.
* **Bi-directional Sync**: Creates tickets automatically when tests fail during execution; updates/resolves tickets when sanity/regression test suites pass.

---

## 3. COMPREHENSIVE MULTI-TIER TESTING CAPABILITIES

Hendrickson generates, inspects, executes, and analyzes test suites across three primary QA pillars:

### 3.1 Functional Testing (The Core Pyramid)
Functional testing verifies system correctness by validating software outputs against explicit business logic and technical specifications extracted from PRDs.

| Test Category | Target Scope & Granularity | Execution Method & Frameworks | Hendrickson AI Generation Strategy |
| :--- | :--- | :--- | :--- |
| **Unit Testing** | Evaluates individual methods, functions, or classes in complete isolation. Bypasses external dependencies (DBs, APIs) via mocking. | `Pytest` (Python), `JUnit 5` (Java), `Jest/Vitest` (JS/TS), `Go Test` | Generates 100% branch/line coverage unit scripts; auto-creates mock objects and synthetic fixtures for all external calls. |
| **Integration Testing** | Validates inter-module communication, database transactions, API endpoints, and third-party webhooks. | `Postman / Newman`, `Testcontainers`, `REST Assured`, `HTTPX` | Spins up ephemeral containers (PostgreSQL, Redis, RabbitMQ); generates API payload assertions and contract verification tests. |
| **System Testing** | Evaluates the complete, integrated software package as a unified black box against high-level specs. | `Custom HTTP Drivers`, `Docker Compose Harness`, `CLI Runners` | Executes end-to-end black-box request chains verifying system-level state transitions and multi-service workflows. |
| **End-to-End (E2E) Testing** | Simulates complete user journeys through the frontend UI down to backend databases, payment processors, and auth. | `Playwright`, `Cypress`, `Selenium` | Generates resilient browser automation scripts with DOM auto-healing, visual state assertions, network interceptors, and video/screenshot captures. |
| **Acceptance Testing (UAT)** | Verifies that the feature delivers exact business value promised in the PRD prior to public release. | `Cucumber / Gherkin`, `Behave`, `BDD Frameworks` | Translates PRD user acceptance criteria directly into Gherkin BDD specs (`Given / When / Then`) with underlying code bindings. |

### 3.2 Operational & Stability Testing
Automated verification checkpoints executed at strategic CI/CD deployment stages to protect codebase integrity and prevent regressions.

| Test Category | Execution Timing & Purpose | Scope & Strategy | Key Success Criteria & Action |
| :--- | :--- | :--- | :--- |
| **Smoke Testing** | Post-deployment / Post-build verification. | Minimal fast-path suite (< 60 sec) testing core vital paths (Healthchecks, Auth, Database Ping, Main Navigation). | **Go/No-Go Gate**: Immediately aborts deployment pipeline if smoke suite fails. |
| **Sanity Testing** | Post-patch / Bugfix verification. | Highly targeted check verifying specific code components modified in a JIRA/Linear bug ticket and immediate downstream modules. | **Ticket Verification**: Confirms fix validity before moving JIRA/Linear ticket to 'Resolved'. |
| **Regression Testing** | Pre-merge / CI Pipeline trigger. | Runs full or smart-subset functional suites following code changes or refactoring. | **Side-Effect Detection**: Prevents legacy feature breakage by matching diff impact trees against existing test suites. |

### 3.3 Non-Functional Testing
Evaluates system operational traits, performance thresholds, scaling limits, and security vulnerabilities under load.

| Test Category | Primary Objectives | Tools & Harnesses | Metrics Captured & Analyzed |
| :--- | :--- | :--- | :--- |
| **Performance Testing** | Measures processing latency, execution speeds, TTFB, and API response times under standard conditions. | `k6`, `Locust`, `Apache JMeter` | Response time distributions (p50, p90, p95, p99), Requests/Sec (RPS), Resource utilization (CPU/RAM). |
| **Load & Stress Testing** | Pushes application to extreme traffic spikes to determine breaking points and capacity limits. | `k6 Distributed`, `Vegeta` | Maximum concurrent users, breaking point thresholds, DB connection pool bottlenecks, memory leak curves. |
| **Security Testing** | Proactively scans code, modules, and API endpoints for exploitable flaws, data leaks, and OWASP vulnerabilities. | `Bandit`, `OWASP ZAP`, `Trivy`, `Semgrep` | OWASP Top 10 risks, SAST static code vulnerabilities, CVE dependency flaws, exposed secret detection, CVSS scores. |

---

## 4. FRONTEND DASHBOARD & USER EXPERIENCE

### 4.1 Dashboard Layout & Core Modules
1. **Interactive AI QA Assistant (Command Center)**:
   - Conversational prompt interface allowing users to ask natural language questions (e.g., *"Show me all test cases generated for PRD-Payment-v2 and run a sanity check against JIRA-402"*).
   - Multi-modal selector for switching active PRD versions, GitHub repository branches, and JIRA sprints.
2. **PRD & Requirement Reference Drawer**:
   - Split-screen document viewer highlighting parsed functional requirements and acceptance tags.
   - Interactive cross-linking showing exactly which test cases map to each PRD paragraph.
3. **Test Suite Canvas & Code Inspector**:
   - Organized matrix of all generated test cases categorized by Functional, Operational, and Non-Functional tiers.
   - Full code editor view (Monaco) enabling engineers to inspect, edit, or customize generated Python/TypeScript/SQL/k6 test scripts before execution.
4. **Execution Runner & Real-Time Terminal**:
   - Single-click **"Run Test Suite"** button with target environment selection (Staging, Docker Sandbox, Ephemeral Cloud Cluster).
   - Live streaming execution log (stdout/stderr), real-time progress bars, step-by-step E2E DOM previews, and video replay controls.
5. **Telemetry & QA Metrics Dashboard**:
   - Comprehensive analytical visualizers detailing Pass/Fail ratios, Flakiness Index, Line/Branch Coverage %, PRD Requirement Coverage %, Performance Latency Histograms, and Security Risk Vulnerability Matrices.

---

## 5. TECHNICAL ARCHITECTURE & DATA SCHEMAS

### 5.1 System Stack
* **Frontend UI**: Next.js 15, React 19, TypeScript, Tailwind CSS, Shadcn UI, Monaco Editor, Recharts.
* **Backend API & Orchestration**: Python 3.12, FastAPI, Celery, Redis, Temporal.io.
* **AI & Multi-Agent Framework**: Orchestrated Multi-Agent Harness (LangGraph / LlamaIndex), OpenAI GPT-4o / Claude 3.5 Sonnet / DeepSeek-R1, Qdrant Vector Engine.
* **Execution Engine**: Containerized Docker SDK, Firecracker MicroVMs, Playwright Node Service, k6 CLI Runner, Bandit / OWASP ZAP Containers.
* **Integrations**: GitHub GraphQL API & Webhooks, JIRA REST API, Linear GraphQL API, Notion API.

### 5.2 Key Data Models

#### 5.2.1 Triangulated Context Schema
```json
{
  "context_id": "CTX-PAY-2026-08",
  "prd": {
    "id": "PRD-PAYMENT-004",
    "version": "2.1",
    "title": "Automated Retry Strategy for Failed Payment Webhooks"
  },
  "codebase": {
    "repository": "github.com/fintech/payment-gateway",
    "branch": "feature/webhook-retry",
    "commit_hash": "a1b2c3d4e5f6",
    "affected_files": [
      "services/payment/webhook_handler.py",
      "services/payment/retry_queue.py"
    ]
  },
  "ticketing": {
    "jira_issue_keys": ["JIRA-892", "JIRA-910"],
    "status": "In QA Verification"
  }
}
```

#### 5.2.2 Test Case Definition Schema
```json
{
  "test_id": "TC-FUNC-INT-042",
  "title": "Verify Payment Gateway Timeout Triggers Exponential Backoff",
  "category": "Functional",
  "sub_category": "Integration",
  "prd_reference": "PRD-PAYMENT-004@req-03",
  "jira_reference": "JIRA-892",
  "target_framework": "Pytest + Testcontainers",
  "script_path": "tests/integration/test_webhook_retry.py",
  "code_body": "def test_webhook_retry_backoff(mock_gateway, db_session):
    # Test logic auto-generated by Hendrickson
    ...",
  "status": "Ready",
  "metrics": {
    "last_execution": "2026-08-09T13:25:00Z",
    "status": "PASSED",
    "duration_ms": 1420,
    "memory_mb": 48.6,
    "flakiness_score": 0.02
  }
}
```

---

## 6. END-TO-END WORKFLOW SCENARIOS

### Scenario A: New Feature PRD Upload -> Test Suite Synthesis -> Execution -> Metrics
1. **Ingestion**: PM uploads `PRD_Subscriptions_v2.md` to Hendrickson.
2. **Context Triangulation**: Hendrickson links PRD requirements to `subscription_service` in GitHub and references relevant sprint tickets in JIRA.
3. **User Prompt on Dashboard**: *"Generate a full-spectrum QA suite for the tier upgrade feature in PRD_Subscriptions_v2."*
4. **Test Authoring**: Hendrickson generates:
   - 12 Unit tests (Pytest)
   - 4 Integration tests (Testcontainers PostgreSQL + Stripe API mock)
   - 2 E2E Playwright tests (UI subscription flow)
   - 1 Smoke test & 1 Regression test script
   - 1 k6 Load test script (1,000 concurrent upgrades)
5. **Display & Inspection**: Generated test scripts appear in the Dashboard Code Inspector for engineering review.
6. **Execution**: User clicks **"Run Test Suite"**. Hendrickson spawns Docker sandbox, runs all suites, and streams logs live.
7. **Telemetry & Metrics**: Dashboard updates with **100% PRD Coverage**, **18/19 Tests Passed**, **1 Integration Test Failed** (API payload key mismatch).
8. **Automated Ticket Action**: Hendrickson opens a JIRA ticket pre-populated with failure traces, code location, and PRD requirement link.

### Scenario B: Patch Fix Validation (Sanity & Regression)
1. Developer fixes a bug reported in `JIRA-402` and pushes a commit to GitHub.
2. User asks Hendrickson: *"Run a Sanity check on JIRA-402 and run Regression suite on affected billing modules."*
3. Hendrickson identifies modified functions via `git diff`, extracts target sanity tests, executes them, and reports zero regressions.
4. Hendrickson automatically updates `JIRA-402` ticket status to "QA Verified".

---

## 7. PROJECT ROADMAP

* **Phase 1 (MVP Foundation)**:
  * Triangulation Engine (PRD Parser + GitHub Indexer + JIRA Connector).
  * Frontend Dashboard Chat, Document Drawer, and Code Canvas.
  * Functional Testing Suite Generation (Unit, Integration, E2E, UAT).
  * Docker Execution Sandbox & Core Coverage Metrics.
* **Phase 2 (Operational & Non-Functional Expansion)**:
  * Smoke, Sanity, and Automated Regression Test Engines.
  * k6 Load/Stress Testing & Bandit/OWASP Security Vulnerability Scanners.
  * Bi-directional JIRA / Linear ticket automated lifecycle management.
* **Phase 3 (Self-Healing & Continuous QA Autonomous Agent)**:
  * Self-healing E2E tests (automatic selector updating upon UI DOM shifts).
  * GitHub Actions / CI/CD pipeline blocking gates based on quality metrics.
  * Continuous load & security benchmarking against production PRDs.
