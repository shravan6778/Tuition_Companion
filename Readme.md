# Tuition Companion

Tuition Companion is a solution that helps all the tuition teachers to track each student's progress in a unique way, helps to find out weak areas of each student in every student subject and also helps all the students to understand the words, lines, concepts contextually.

Tuition Companion is to be an AI powered solution using Knowledge Graph, Generative AI and Azure AI Services.

## Architecture Decisions

Crucial decisions on the architecture

- **Content vs. Rooms:** Subjects and chapters are uploaded and
  processed once per teacher (OCR + concept extraction via Azure
  Document Intelligence + LLM), then assigned to one or more
  rooms — avoiding redundant processing across batches.
