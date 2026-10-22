# Tuition Companion

Tuition Companion helps local tuition teachers track what each student has **actually understood** (not just what has been "covered"), resolves mid-chapter doubts with explanations grounded in the student's own textbook, and keeps session-to-session continuity so a teacher (or a substitute) always knows where a student stands.

It is an AI-powered platform built on a textbook knowledge graph, retrieval (RAG) and LLM-based agents, with role-based dashboards for **teachers**, **students** and **parents**.

**Stack:** FastAPI · SQLAlchemy/Alembic · PostgreSQL · SuperTokens (self-hosted) · React (Vite) · Memgraph (graph + vector search) · Azure Document Intelligence (OCR) · OpenAI-compatible LLM and embeddings (Azure OpenAI / Foundry or OpenAI).

---

## What it does

| Area                       | What you get                                                                                                                                                                                                                                                                                         |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Auth & roles**           | Sign up / log in as teacher, student or parent (username + password via SuperTokens). Role checks are enforced server-side on every request.                                                                                                                                                         |
| **Rooms**                  | A teacher creates single-class or mixed-class rooms and shares a join code. Students can join several rooms.                                                                                                                                                                                         |
| **Content library**        | Content is organised by real **Book** (board, class, subject, publisher/edition, customised flag, school, `variant_of`) → Chapters → Pages → Concepts. A pre-seeded **Reference Corpus** (NCERT) is available to everyone; every other book is uploaded privately by the teacher.                    |
| **Upload pipeline**        | Front pages first (metadata extraction), then the whole book or chapter by chapter. OCR → page fingerprints → concept extraction → concept dependency graph → embeddings → graph store, in one processing step. Similar pages reuse existing concepts instead of calling the LLM again.              |
| **Doubt resolution**       | Per-assignment Doubt button and a standalone "Ask a Doubt". Word, line or photographed page. Answers are produced only from already-processed pages of the student's linked books, with prerequisite refreshers. If the content isn't in the book, the student is told to ask the teacher to add it. |
| **Assignments & checks**   | Teachers assign at book / chapter / concept / exercise level. Marking an assignment complete triggers a comprehension check sized to its scope (2–10 questions).                                                                                                                                     |
| **Tests & quizzes**        | Teacher-generated chapter/concept tests (10/20/30 questions) and student practice quizzes aimed at weak concepts. Multiple-choice graded in code, short answers graded by the LLM.                                                                                                                   |
| **Weak areas**             | Weakness is derived from check/quiz history and **propagates through the prerequisite graph**; every flag says whether it was tested directly or inherited.                                                                                                                                          |
| **Progress tracking**      | Every mastery update is stored as a dated event. Powers trends, the teacher briefing and the student's "My Progress".                                                                                                                                                                                |
| **Briefing & session log** | Teacher session notes plus an LLM-written pre-session briefing built from mastery and trends.                                                                                                                                                                                                        |
| **Dashboards**             | Teacher (rooms → students → six tools per student), student (today's work, ask a doubt, practice, progress, my books) and parent (link a child with the child's code).                                                                                                                               |

## Architecture

```
React (Vite) ──► FastAPI ──► PostgreSQL        source of truth (data + embeddings)
                    │   └──► Memgraph          knowledge graph + vector search (rebuildable from PostgreSQL)
                    ├──► SuperTokens core      sessions / credentials
                    ├──► Azure Document Intelligence   OCR
                    └──► OpenAI-compatible endpoint    LLM + embeddings
```

- **PostgreSQL is the source of truth.** Memgraph can be wiped and rebuilt without any embedding calls (`python -m app.db.sync_graph --rebuild`).
- **The "agents"** (Tutor, Quiz, Personalization) are prompts plus validation code over chat-completion calls. They are not Azure AI Foundry Agent Service agents.
- **Doubt flow:** embed the doubt → vector search limited to the student's linked books → re-check tenancy in PostgreSQL → Tutor answers from the retrieved pages only and must cite them. Below the similarity cut-off (0.41) the answer is "not in your book".
- **Mastery:** per concept, the average of the 3 most recent measured events (check/quiz). Below 0.6 is weak. Weak concepts flag their dependents up to 2 prerequisite steps away as "at risk".
- **Background work:** upload processing runs through FastAPI `BackgroundTasks` (in-process; a restart interrupts it, and `app.db.reprocess` can re-run a book).

## Repository layout

```
backend/app/
  auth/            SuperTokens setup, role dependencies, admin check
  teacher/ student/ parent/     role-specific routes
  content_library/ book access, search, upload, deletion, link requests
  pipeline/        OCR → fingerprint → concepts → graph → indexing
  doubts/          retrieval, tutor, photo doubts, browse
  assignments/     assignments and scope resolution
  assessment/      checks, quizzes, mastery, trends
  agents/          personalization (briefing)
  graph_store/     Memgraph store (+ fake store for tests)
  embeddings/ llm/ ocr/   provider adapters (real + fake)
  db/              migrations, seed and maintenance scripts
backend/tests/     pytest suite (SQLite, fake providers)
frontend/src/      auth/, teacher/, student/, parent/, shared/, api/
docker-compose.yml PostgreSQL, SuperTokens, Memgraph, Memgraph Lab
```

## Running locally

**Prerequisites:** Docker, Python 3.11+, Node 20+.

```bash
# 1. Infrastructure: PostgreSQL (host port 5434), SuperTokens (3567), Memgraph (7687)
docker compose up -d

# 2. Backend
cd backend
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                    # then edit it (see below)
alembic upgrade head
uvicorn app.main:app --reload                           # http://localhost:8000

# 3. Frontend (second terminal)
cd frontend
cp .env.example .env                                    # VITE_API_URL=http://localhost:8000
npm install
npm run dev                                             # http://localhost:5173
```

### Configuration (`backend/.env`)

| Variable                                                   | Purpose                                                                                  |
| ---------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `DATABASE_URL`                                             | PostgreSQL connection (matches the compose file)                                         |
| `SUPERTOKENS_CONNECTION_URI`, `SUPERTOKENS_API_KEY`        | SuperTokens core                                                                         |
| `API_DOMAIN`, `WEBSITE_DOMAIN`, `CORS_ORIGINS`             | URLs of the API and the frontend                                                         |
| `OCR_PROVIDER`                                             | `azure` or `fake`; with `azure` set `AZURE_DOC_INTEL_ENDPOINT` and `AZURE_DOC_INTEL_KEY` |
| `LLM_PROVIDER`, `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL` | `openai_compat` or `fake`; on Azure the model is your deployment name                    |
| `EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`, `EMBEDDING_DIM`   | `openai_compat`, `fake` or `none` (default `text-embedding-3-small`, 1536)               |
| `GRAPH_STORE_PROVIDER`, `MEMGRAPH_URI`                     | `memgraph`, `fake` or `none`                                                             |
| `ADMIN_USERNAMES`                                          | Teachers allowed to delete official (reference) books/chapters                           |

> Doubts, checks and quizzes need a real LLM, embeddings **and** the graph store. The code defaults for embeddings and the graph store are `none`, so set them in `.env` (the example file already does). The `fake` providers are for tests and local experiments only.

### First-time content

```bash
cd backend
python -m app.db.seed_ncert                       # NCERT Class 9 & 10 Science/Maths reference books
python -m app.db.ingest_reference book.pdf --board CBSE --class "Class 9" \
    --subject Science --publisher NCERT           # or ingest your own official PDF
python -m app.db.sync_graph --status              # embeddings / graph copy status
python -m app.db.sync_graph                       # fill in anything pending or failed
```

### Tests

```bash
cd backend && pytest                              # runs on in-memory SQLite with fake OCR/LLM/graph providers
cd frontend && npm run build
```

### Maintenance and check scripts (`backend/app/db`)

| Script                                        | Use                                                                                        |
| --------------------------------------------- | ------------------------------------------------------------------------------------------ |
| `sync_graph`                                  | Create embeddings and (re)build the Memgraph copy (`--rebuild`, `--prune`, `--status`)     |
| `smoke_memgraph`                              | Verify a running Memgraph with the app's own store code                                    |
| `reprocess <book-id>`                         | Re-run processing from stored files (e.g. after switching from the fake LLM to a real one) |
| `drop_book`, `drop_chapter`, `cleanup_drafts` | Remove content / stale drafts                                                              |
| `phase2_check` … `phase5_6_check`             | End-to-end exit checks against the real database and models (rolled back at the end)       |

## Current status

Backend phases 1–6 are built; the dashboards (phase 7) are mostly built.

- Backend suite: 428 tests passing. Frontend builds.
- Not covered by automated tests: real Azure OCR/LLM output quality, real PostgreSQL + Memgraph runs (use the `phase*_check` and `smoke_memgraph` scripts), and browser UI flows.

## Security notes

- Role and tenancy checks are enforced in the backend; tests cover cross-teacher access.
- The compose file and `.env.example` contain a **development-only** database password. Change it before any shared deployment.
- Rate limits are in-memory per process; use a shared store before running multiple instances.
