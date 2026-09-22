# Tuition Companion

Tuition Companion is a solution that helps all the tuition teachers to track each student's progress in a unique way, helps to find out weak areas of each student in every student subject and also helps all the students to understand the words, lines, concepts contextually.

Tuition Companion is to be an AI powered solution using Knowledge Graph, Generative AI and Azure AI Services.

Stack: FastAPI · React · PostgreSQL · SuperTokens (self-hosted) · Azure AI (later phases).

## Current status

Auth, roles, and room/parent linking are working end to end.

- Sign up and log in as a teacher, student, or parent (phone + password, via a self-hosted SuperTokens core)
- Teachers create rooms and get a join code
- Students join a room with that code
- Parents link to a student with the student's link code and get a read-only view
- Role checks are enforced server-side on every request, not just in the UI
- Backend test suite passing (auth guards + the full room/join/link flow)

Not built yet: the content pipeline, concept graph, retrieval, and the tutor/quiz/personalization agents — that's next phase .

## Running locally

```bash
docker compose up -d          # Postgres + SuperTokens core
cd backend && uvicorn app.main:app --reload
cd frontend && npm run dev
```
