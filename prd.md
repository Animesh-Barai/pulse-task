# Product Requirements Document — **PulseTasks**

*(Realtime collaborative todo with CRDT sync, AI-powered SMART-task rewriting, blocker inference, and time-aware prioritization — built with Antigravity agentic development workflow)*

> Note: you said you’ll build this using **Antigravity** (agent-first IDE). Antigravity is an agentic, AI-powered development platform/IDE designed to let autonomous agents plan, execute, and verify engineering tasks. I’ll assume you’ll use Antigravity for code generation, tests, infra tasks, and creating “Skills”/agents that run LLM workflows. (If you meant a different “antigravity,” tell me and I’ll adapt.) ([Google Antigravity][1])

---

# 1 — Executive summary

PulseTasks is a production-grade, real-time collaborative task management platform targeted at knowledge teams and SMEs that need low-friction async collaboration plus operational intelligence. It offers:

* CRDT-based concurrent editing (Yjs/ypy) for conflict-free real-time lists and offline merges.
* AI SMART-task rewriting: turn ambiguous tasks into actionable work (title, checklist, acceptance criteria, priority, suggested due-date).
* Blocker inference: automatically detect implicit blockers and notify stakeholders.
* Time-aware auto-prioritization & rescheduling: considers calendar availability, historical velocity, and team load.
* Edge-first lightweight AI with cloud LLM fallback, telemetry-driven personalization, and enterprise privacy controls.

Primary stakeholders: Product managers, engineering teams, marketing teams, support ops, freelancers/agencies, platform/infra & security.

Success metrics (KPIs):

* AI suggestion acceptance rate ≥ 50% within first 6 weeks (baseline: 0%).
* Reduction in task clarification comments per task ≥ 30%.
* Median time-to-first-action on new task reduced by 25%.
* CRDT sync consistency: zero data-loss incidents in acceptance testing; recoverable merges in >99.9% reconnection scenarios.

---

# 2 — Goals & constraints

Primary goals

* Deliver a robust realtime collaborative UX that supports concurrent editors and offline merges.
* Provide high-precision AI suggestions that improve task clarity and measurably improve throughput.
* Ensure enterprise-grade privacy, auditability, and resilience for regulated customers.

Constraints & assumptions

* Backend implementation will be in **Python** (FastAPI ASGI + python-socketio / ypy-websocket).
* Frontend will be React + Yjs for CRDT docs.
* You will build using Antigravity agents to scaffold code, generate tests, and automate infra tasks where applicable. ([Google Antigravity][1])
* Initial deployment target: cloud-managed infra (Render/Fly/AWS) with managed Redis & MongoDB Atlas.
* Compliance: GDPR / SOC2 readiness required for enterprise adoption.

Success criteria (release v1)

* Fully functional MVP: real-time lists, AI rewrite suggestions (local classifier + opt-in cloud LLM), blocker detection, presence indicators, basic auth and SSO.
* Automated CI/CD with tests, infra as code, and observability dashboards.

---

# 3 — Personas & user stories

Primary personas

1. Product Manager (PM) — creates vague tasks and needs actionable checklists and acceptance criteria. Wants sprint-ready tasks.
2. Individual Contributor (IC/Developer/Designer) — wants clear work, minimal context switching, and fair workload.
3. Team Lead — wants team-level workload balancing, blocker visibility, and SLA dashboards.
4. Support Agent — wants high-priority conversion from incoming threads, automated triage, and clear ownership.
5. Admin (IT/Compliance) — needs audit trails, data export, SSO, and privacy controls.

Key user stories (ranked)

* As a PM, when I create a vague task, I want AI to propose a SMART rewrite so I can accept and move on.
* As an IC, when I go offline and edit a list, I want my edits to merge without conflicts on reconnect.
* As a Team Lead, I want the system to auto-detect blocked tasks and surface whom to nudge.
* As an Admin, I want an append-only cryptographically verifiable edit trail for compliance.

Acceptance criteria attached per feature in section 6.

---

# 4 — Feature list (priority & details)

## Core (MVP)

1. Auth & onboarding

   * Email/password & OAuth2 (Google). JWT + refresh tokens.
   * Workspace creation + member invites.
2. Realtime collaboration

   * Yjs (client) + ypy-websocket/python-socketio bridge for CRDT sync.
   * Presence, cursors, typing indicators.
   * Snapshot persistence and delta persistence to MongoDB.
3. Tasks & lists

   * Task fields: title, description, assignee, priority, due_date, tags, status, attachments.
   * CRUD REST API (FastAPI) + socket events.
4. AI SMART-task rewriting

   * Async pipeline: heuristic rules -> local classifier -> optional cloud LLM enrichment.
   * Confidence score and explanation text; accept/reject telemetry.
5. Blocker inference

   * Background pipeline combining NLP on comments, attachment checks, and status-duration heuristics.
   * Socket notifications & suggested next actions.
6. Time-aware prioritization

   * API to compute effective priority from deadlines, calendar availability (via OAuth calendar integrate), historical velocity, and team load.

## Secondary / Stretch

* Low-code playbooks/triggers.
* Signed CRDT ops for verifiable audit trail.
* Edge/On-prem AI runtime (for enterprise).
* Offline-first mobile SDK.
* Large org sharding & multi-region replication.

---

# 5 — Non-functional requirements (NFRs)

Performance

* 95th percentile roundtrip socket latency < 250ms (in-region).
* Task CRUD API median latency < 150ms.

Scalability

* Support 10k concurrent connected users across instances (initial target).
* Shard by workspace_id when total documents grow >100k workspaces.

Availability & reliability

* Target 99.9% API uptime.
* Automatic failover for Redis and MongoDB.

Security

* TLS everywhere; encryption at rest for attachments.
* Enterprise SSO (SAML) + field-level ACLs.
* Rate limits: per-user and per-workspace.

Privacy

* Allow workspace-level toggle: "Cloud LLM Off" (local model only).
* Retention & data export tools for GDPR.

Observability

* Metrics: requests/sec, socket msgs/sec, AI calls, job queue depth.
* Logging: structured JSON, Sentry for exceptions.

---

# 6 — Functional requirements (detailed)

### 6.1 REST API endpoints (representative)

* `POST /api/v1/auth/login` — returns JWT + refresh token.
* `POST /api/v1/auth/signup`
* `GET /api/v1/workspaces` — list workspaces.
* `POST /api/v1/workspaces` — create workspace.
* `POST /api/v1/lists` — create list (returns y_doc_key).
* `GET /api/v1/lists/{id}` — read list metadata.
* `GET /api/v1/tasks?list_id=...` — query tasks.
* `GET /api/v1/tasks/{id}`
* `POST /api/v1/tasks` — create task (triggers AI suggestion job).
* `PATCH /api/v1/tasks/{id}` — update (also accepted from CRDT persist hooks).
* `POST /api/v1/ai/suggestions/{task_id}/accept` — accept suggestion.
* `GET /api/v1/ai/suggestions/{task_id}` — fetch suggestions.

(Full OpenAPI spec attached in Appendix A.)

### 6.2 Socket contract (events)

Client → Server:

* `join_workspace` { workspace_id, auth_token }
* `ydoc_sync` (binary CRDT ops)
* `task_update` { task_id, delta } — optional if using CRDT to persist denormalized fields.
* `ai:suggestion_ack` { suggestion_id, action }

Server → Client:

* `presence_update` { user_id, status }
* `ydoc_update` (binary)
* `task_broadcast` { task payload }
* `ai:suggestion` { suggestion payload }
* `task_blocked` { task_id, reason, confidence }

### 6.3 AI microservice interface (FastAPI)

* `POST /ai/suggest/task`
  Input: `{ raw_title, raw_description, context }`
  Output: `{ rewritten_title, checklist[], suggested_priority, suggested_due_date, confidence, explanation }`

* `POST /ai/prioritize` — compute effective priority for tasks given context.

* `POST /ai/train/feedback` — accept accept/reject telemetry.

---

# 7 — Data model (core collections, examples)

**users**

```json
{ "_id":"ObjectId", "email":"", "name":"", "password_hash":"", "created_at": "ISODate" }
```

**workspaces**

```json
{ "_id":"ObjectId","name":"", "owner_id":"", "member_ids":[], "region":"", "created_at":"" }
```

**lists**

```json
{ "_id":"ObjectId", "workspace_id":"", "title":"", "y_doc_key":"", "created_at":"" }
```

**tasks**

```json
{
  "_id":"ObjectId",
  "list_id":"ObjectId",
  "title":"string",
  "description":"string",
  "assignee_id":"ObjectId|null",
  "priority":1,
  "status":"OPEN|IN_PROGRESS|DONE",
  "due_date": "ISODate|null",
  "tags":["string"],
  "created_at":"ISODate",
  "updated_at":"ISODate",
  "last_edit_meta": {"user_id":"", "op_id":""}
}
```

**ai_suggestions**

```json
{
  "_id":"ObjectId",
  "task_id":"ObjectId",
  "workspace_id":"ObjectId",
  "rewritten_title":"string",
  "checklist":["string"],
  "priority":2,
  "due_date":"ISODate",
  "explanation":"string",
  "confidence":0.86,
  "created_at":"ISODate",
  "accepted": false
}
```

Indexes: compound indexes on `(workspace_id, list_id, status)`, text index on `title + description`, TTL for ephemeral presence keys via Redis.

---

# 8 — AI & ML architecture (very detailed — essential for LLM-driven Antigravity workflow)

## 8.1 Overview

AI flow must prioritize latency, privacy, and reliability:

1. **Heuristics & rules** (fast): regex and rule-based parsers (e.g., detect "by Friday", "ASAP", "urgent").
2. **Local classifier** (fast, small): scikit-learn or distilled transformer running on infra edge container for immediate suggestions (<50ms).
3. **Cloud LLM fallback** (optional, async): long-form rewrite and explanation using a high-quality model (OpenAI/GPT or Google Gemini). Only invoked when local model confidence < threshold OR user explicitly requests richer suggestion.
4. **Feedback loop**: accept/reject events sent to `POST /ai/train/feedback`. Periodic retrain using aggregated, anonymized data.

## 8.2 Data needs & labeling

* Seed dataset:

  * 5k–10k annotated (raw_task -> rewritten_task + checklist + labels) examples. Source: internal team, public task corpora, synthetic augmentation.
  * Additional data: comments + outcome labels (whether suggestion accepted & task completed).
* Label schema:

  * `rewritten_title`, array `checklist`, `priority` (1-5), `due_date` (ISO or null), `explanation`, `confidence`.
* Privacy: store only hashed user IDs; allow opt-out for dataset inclusion.

## 8.3 Model & infra choices

* Local classifier: DistilBERT or small transformer distilled & quantized; containerized with CPU inference. Optionally use ONNX for faster CPU inference.
* Cloud LLM: high-quality model (Gemini / GPT / local private LLM) used for complex rewrites.
* Caching: Redis for suggestion results keyed by `hash(raw_title + workspace_context)`.

## 8.4 Prompting & guardrails (CRITICAL — avoid hallucination)

Use explicit system message and structured response schema. Example system message for LLM:

```
You are an assistant that rewrites short task titles into actionable software/product tasks. Output must be strictly JSON with keys:
{
  "rewritten_title": "...",
  "checklist": ["...","..."],
  "suggested_priority": integer 1-5,
  "suggested_due_date": "YYYY-MM-DD or null",
  "confidence": 0.0-1.0,
  "explanation": "short text"
}
Do NOT include any other keys or free-form commentary. If you cannot infer a due date, return null. If uncertain about a due date, set confidence low and ask for clarification in explanation.
If user provided calendar context, prefer that for due_date suggestions.
Always include a confidence score and a short explanation of why suggestion is made. Do not hallucinate facts.
```

(You’ll use Antigravity to generate and version prompts/skills; include these system messages as immutable artifacts in the repo.)

## 8.5 Suggestion acceptance policy

* If `confidence >= 0.8` → show inline suggestion as “high confidence”.
* If `0.5 <= confidence < 0.8` → show suggestion with “needs review”.
* If `<0.5` → only store suggestion in background and optionally surface to power users.

## 8.6 Feedback & online learning

* Capture: `user_id`, `workspace_id`, `suggestion_id`, `accepted: bool`, `edit_distance` between suggested and final accepted version.
* Retrain cadence: weekly mini-batches or continuous learning using safe human-in-the-loop validation.

---

# 9 — UX & UI flows (wireframe-level descriptions)

## 9.1 Create task flow (with AI rewrite)

1. User clicks "New Task".
2. Inline composer appears; user types short title.
3. On blur or after 800ms idle, frontend fires `POST /api/v1/tasks` with raw title.
4. UI shows ghost suggestion below input: rewritten title (editable), checklist collapsed, suggested priority, and a small confidence badge.
5. User actions: Accept all (one click), Edit suggestions inline, or Dismiss.
6. Accepting fires `POST /api/v1/ai/suggestions/{task_id}/accept`.

Notes:

* No modal popups; non-blocking assistant.
* Accessibility: keyboard-first acceptance and rejection.

## 9.2 Blocker detection flow

* Background worker runs inference every X minutes or on relevant triggers (comment added, attachment state change).
* If blocked: show red badge on task and push `task_blocked` socket event to workspace.
* Actionable CTA: “Suggest next action” / “Auto-message assignee”.

## 9.3 Time-aware reprioritization

* On dashboard, hover on task shows “Why prioritized” tooltip with rule breakdown (deadline weight 40%, calendar 30%, velocity 30%).
* When rescheduling suggested, show one-click accept.

---

# 10 — System architecture & infra (ops-ready)

## Components

* Frontend: React + Yjs (client CRDT).
* API: FastAPI (ASGI), python-socketio or ypy-websocket adapter.
* Real-time broker: Redis (pub/sub) + Redis Streams for durability.
* DB: MongoDB Atlas (replica set) — store denormalized task fields and YDoc snapshots.
* AI microservice: FastAPI Python service, local classifier + async LLM client.
* Background jobs: Celery (with Redis broker) or RQ.
* Storage: S3-compatible for attachments + CDN for media serving.
* Observability: Prometheus, Grafana, Sentry, Loki/ELK for logs.
* CI/CD: GitHub Actions -> build/test -> push Docker -> deploy to staging/production.
* Secrets: Vault / AWS Secrets Manager.

## Scaling patterns

* Horizontal app autoscaling; Redis pub/sub ensures message delivery across nodes.
* Sticky sessions NOT required (using Redis adapter), but preserved for ease in some PaaS.
* Sharding: shard MongoDB by `workspace_id` if >X TB or heavy load.

---

# 11 — Security, compliance & governance

Key items

* RBAC: workspace roles — owner, admin, member, guest.
* Data governance: workspace-level LLM toggle (Off/Local/Cloud). If Off, LLM calls are not made and all suggestions come from local models.
* Audit trail: store CRDT op metadata (user_id, timestamp, op_hash). Option: sign ops using a signing key to produce verifiable chain for regulated customers.
* SAML/SSO & SCIM for enterprise provisioning.
* DLP & content scanning for attachments.

---

# 12 — Testing & QA

Automated tiers

* Unit tests (pytest) for all services.
* Integration tests:

  * REST endpoints against a test DB (docker-compose).
  * Socket flows using `python-socketio` test client and a test Redis.
* E2E: Playwright for UX flows (task create, accept AI suggestion, block detection).
* Load testing: Locust / k6 to simulate N concurrent sockets & validate CRDT merges under network partitions.
* Security: SAST (Bandit), dependency scanning (pip-audit), container image scanning.

Regression & safety tests for LLM flows

* Prompt-safety tests: ensure LLM output conforms to JSON schema; reject non-conforming responses.
* Hallucination tests: test cases that could trigger hallucinations and verify model returns null or asks for clarification.

---

# 13 — Observability & KPIs (dashboards)

Suggested dashboards:

1. System health: API latency, socket messages/sec, CPU/memory by service.
2. AI Dashboard:

   * Suggestions generated / accepted / rejected per day.
   * Average confidence & distribution.
   * LLM calls per hour and cost.
3. User productivity:

   * Avg tasks created per user/day.
   * Avg time from creation → start.
   * Blocked task count & mean time-to-unblock.
4. Ops:

   * Redis queue depth, Celery job failures, DB replication lag.

---

# 14 — Rollout plan & roadmap (6–8 week example)

**Week 0 — Planning**

* Finalize requirements, seed dataset collection & annotation plan.

**Week 1 — Core backend & auth**

* Implement FastAPI skeleton + DB models, basic REST APIs, React skeleton front-end.

**Week 2 — Realtime & CRDT**

* Integrate Yjs + ypy-websocket (or python-socketio CRDT bridge), presence, and persistence.

**Week 3 — AI microservice (MVP)**

* Implement heuristics + small classifier, Redis caching, HTTP contract, background worker hooking.

**Week 4 — Blocker detection + prioritization**

* Implement blocker inference worker + prioritize API; start collecting telemetry.

**Week 5 — Testing & Infra**

* CI/CD, unit/integration tests, docker-compose, staging deploy.

**Week 6 — Performance & polish**

* Load testing, optimize, analytics dashboard, business metrics, demo polish.

**Post-MVP**

* Signed ops, SSO, on-prem model, playbooks.

---

# 15 — Acceptance criteria / definition of done (per major feature)

AI SMART rewrite

* Given a raw title, the system returns a JSON suggestion in <1s (local classifier) with confidence.
* If cloud LLM is used, it must return structured JSON conforming to schema; invalid responses rejected and logged.
* Acceptance telemetry recorded and visible in dashboard.

Real-time CRDT

* Two users editing the same list (text and task fields) while one goes offline must see consistent merged state upon reconnect in >99.5% of tests.
* No lost updates in integration suite.

Blocker detection

* In 90% of seeded test cases (synthetic blocked scenarios), the system marks a task blocked and suggests an action.

Time-aware prioritization

* Reprioritization API returns a stable ranking given same input context; tooltips explain weight contributions.

---

# 16 — Work items for Antigravity agents / Skills (how to use Antigravity effectively)

Use Antigravity to:

* Generate initial code scaffolding for services (FastAPI endpoints, dockerfiles).
* Create test scaffolding (pytest + socketio integration).
* Auto-generate OpenAPI spec from routes and keep docs synced.
* Create “Skills” for:

  * Prompt/version management — store system messages as artifacts.
  * Test generation — produce unit/integration tests for AI flows.
  * Infra tasks — generate IaC snippets for Terraform or Cloud Run.
* Use Antigravity artifacts for verifiable agent outputs (prompts, test logs, infra diffs). ([Google Codelabs][2])

**Important agent governance rules** (avoid accidents like file deletion incidents):

* Restrict agent permissions: never grant file-system destructive rights to agents in production mode.
* Use review gates: all destructive changes require human approval.
* Log all agent actions and provide an option to “replay” actions in dry-run mode.

---

# 17 — Safety & anti-hallucination guardrails (for LLMs)

Hard rules for LLM outputs:

* Always output structured JSON only for API consumption.
* Include `confidence` numeric field.
* If LLM cannot infer due date, return `null` not a guess.
* Never fabricate external facts (e.g., “due date based on calendar” must be computed from real calendar data or returned as `null`).
* Add schema validations on server: reject malformed LLM output and fallback to heuristic/local suggestion.
* Rate-limit LLM calls; have quotas and alerts.

Prompt engineering guidelines (short)

* Use system-level instruction that demands JSON-only outputs.
* Provide constrained examples (few-shot) inside Antigravity Skill artifacts.
* Add guardrail layer that validates and sanitizes date/time strings, numeric ranges, and checklist lengths (max 10 items).

Sample **high-quality** LLM prompt (system + user) — put as an artifact in repo:

```
SYSTEM: You are an assistant that rewrites short task titles into structured actionable tasks. Respond with JSON only in this schema:
{ "rewritten_title":string, "checklist": [string], "suggested_priority": int(1-5), "suggested_due_date": "YYYY-MM-DD|null", "confidence": 0.0-1.0, "explanation": string }
USER: Title: "Fix landing page"
CONSTRAINTS: - Do not invent dates; if not available, return null. - Checklist max 6 items. - Prioritize clarity.
```

---

# 18 — Edge cases & failure modes (with mitigations)

1. **LLM returns free text / hallucination**

   * Mitigation: strict JSON schema validation; fallback to local classifier and show “needs review”.

2. **User offline edits huge doc causing huge CRDT**

   * Mitigation: implement doc compaction and periodic snapshots; limit client-side CRDT size and show warning.

3. **Redis outage**

   * Mitigation: local in-memory fallback for small team (degraded mode), alert ops, auto-failover via managed Redis.

4. **Agent in Antigravity runs destructive command**

   * Mitigation: disallow destructive ops in agent config; require approval gates.

5. **Privacy concerns with cloud LLM**

   * Mitigation: workspace toggle to disable cloud LLM and use local classifiers; explicit user consent screens.

---

# 19 — Deliverables & repo layout (what to include in GitHub repo)

```
/frontend/            (React + Yjs + Storybook)
  /src/
  /components/
  /pages/
  /public/
/backend/             (FastAPI)
  /app/
    main.py
    routes/
    models/
    ai_client/
  Dockerfile
/ai-service/          (FastAPI classifier + LLM client)
  /models/
  /prompts/
infra/
  docker-compose.yml  (dev)
  terraform/           (prod)
tests/
  unit/
  integration/
  e2e/
ci/
  workflows/
docs/
  PRD.md
  OpenAPI.yaml
  UX-wireframes/
```

---

# 20 — Appendix A — Sample API contract (OpenAPI-style snippet)

*(Already included in section 6.1; full OpenAPI file should be generated in repo.)*

---

# 21 — Appendix B — Sample LLM input/output examples

**Input**

```json
{
  "raw_title": "Fix landing page",
  "context": {"workspace_type":"marketing", "user_role":"pm"}
}
```

**Desired LLM JSON output**

```json
{
  "rewritten_title":"Improve landing page conversion rate (A/B test hero)",
  "checklist":[
    "Analyze funnel analytics to identify drop-off points",
    "Design hero section A & B variants",
    "Implement AB test and run for 2 weeks",
    "Collect metrics and decide winner"
  ],
  "suggested_priority": 2,
  "suggested_due_date": "2026-02-01",
  "confidence": 0.86,
  "explanation": "Detected marketing conversion intent + default 2-week testing cadence"
}
```

If `confidence < 0.5`:

```json
{
  "rewritten_title": null,
  "checklist": [],
  "suggested_priority": null,
  "suggested_due_date": null,
  "confidence": 0.23,
  "explanation": "Insufficient context: no workspace context or related historical tasks."
}
```

---

# 22 — Appendix C — Glossary & terms

* CRDT — Conflict-free replicated data type.
* Yjs / ypy — CRDT library & Python bindings.
* LLM — large language model.
* Antigravity — agent-first IDE / platform for agentic development. ([Google Antigravity][1])

---

# 23 — Next steps (practical checklist for you to hand to Antigravity agents)

1. Create repo skeleton (use Antigravity agent to scaffold FastAPI + React + docker-compose).
2. Produce seed dataset for SMART-task training (collect internal examples; augment with synthetic rewrites).
3. Implement local classifier (baseline) and a robust input/output schema validator.
4. Implement CRDT pipeline and persist snapshots to MongoDB.
5. Wire AI microservice & background workers; add telemetry.
6. Create CI pipelines and unit/integration tests (Antigravity agent can auto-generate tests).
7. Run load tests and tune infra.
