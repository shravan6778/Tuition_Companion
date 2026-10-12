This file is a merged representation of the entire codebase, combined into a single document by Repomix.

<file_summary>
This section contains a summary of this file.

<purpose>
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.
</purpose>

<file_format>
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  - File path as an attribute
  - Full contents of the file
</file_format>

<usage_guidelines>
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.
</usage_guidelines>

<notes>
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)
</notes>

</file_summary>

<directory_structure>
backend/
  app/
    admin/
      __init__.py
      routes.py
    agents/
      __init__.py
    assessment/
      __init__.py
      checks.py
    assignments/
      __init__.py
      scope.py
    auth/
      __init__.py
      admin.py
      dependencies.py
      identity.py
      routes.py
      supertokens_config.py
    content_library/
      __init__.py
      access.py
      deletion.py
      feedback.py
      graph_view.py
      link_requests.py
      publishers.py
      search.py
      upload.py
    core/
      __init__.py
      codes.py
      config.py
      errors.py
      logging.py
      ratelimit.py
      storage.py
    db/
      migrations/
        versions/
          0aa84017b2de_create_book_content_model_uuid.py
          182f276a6fc0_add_username_and_make_phone_non_unique.py
          378cd2f34a69_initial_schema.py
          483e86509e12_add_chapter_extractions_cache.py
          529cab5476db_username_replaces_phone_as_unique_login_.py
          7a30a692ec87_small_changes_in_making_username_.py
          7efe47816699_rename_firebase_uid_to_supertokens_user_.py
          9c1d4e7a2b38_book_ownership_and_reference_flag.py
          a8e2c5d7f419_page_concepts_model.py
          b27e5f1c8d04_chapter_processing_status.py
          b3d7f1a9c562_embeddings_and_graph_sync.py
          c4a91d6e3f72_concept_graph.py
          c8f2a4b6d913_cross_chapter_edges.py
          d5b3e8f2a916_page_fingerprint_index.py
          d9a3b5c7e124_match_feedback.py
          e1b4c7d9a203_page_kind.py
          e6c4f9a3b027_upload_drafts_and_chapter_requests.py
          f7d5a0b4c138_page_needs_review.py
          fc42ab2fc59f_add_subjects_chapters_room_subjects.py
        env.py
        README
        script.py.mako
      __init__.py
      backfill_page_kind.py
      check_probe.py
      cleanup_drafts.py
      crosslink.py
      drop_book.py
      drop_chapter.py
      embedmatch.py
      exercise_map.py
      ingest_reference.py
      match_feedback.py
      phase2_check.py
      rebuild_fingerprints.py
      relink_chapters.py
      reprocess.py
      retrieval_probe.py
      seed_ncert.py
      session.py
      show_graph.py
      smoke_memgraph.py
      sync_graph.py
      try_doubt_photo.py
      try_front_pages.py
    doubts/
      __init__.py
      calibration.py
      query.py
      retrieval.py
    embeddings/
      __init__.py
      base.py
      fake_provider.py
      openai_compat_provider.py
      vectors.py
    graph_store/
      __init__.py
      base.py
      fake_store.py
      memgraph_store.py
    llm/
      __init__.py
      base.py
      check.py
      fake_provider.py
      openai_compat_provider.py
    models/
      __init__.py
      base.py
      content.py
      links.py
      room.py
      user.py
    ocr/
      __init__.py
      azure_provider.py
      base.py
      fake_provider.py
    parent/
      __init__.py
      routes.py
    pipeline/
      __init__.py
      concepts.py
      crosslink.py
      embedmatch.py
      embedprobe.py
      fingerprint.py
      front_matter.py
      graph.py
      indexing.py
      jobs.py
      linking.py
      matching.py
      orchestrator.py
      structure.py
    student/
      __init__.py
      request_routes.py
      routes.py
    teacher/
      __init__.py
      request_routes.py
      rooms.py
      routes.py
      upload_routes.py
    __init__.py
    main.py
    schemas.py
  tests/
    __init__.py
    conftest.py
    test_book_access.py
    test_chapter_jobs.py
    test_concept_graph.py
    test_concepts.py
    test_library.py
    test_matching.py
    test_phase1_flow.py
    test_phase3_settle.py
    test_pipeline.py
    test_processing.py
    test_roles.py
    test_step10.py
    test_step11.py
    test_step12.py
    test_step13.py
    test_step14.py
    test_step15.py
    test_step16.py
    test_step6.py
    test_step7.py
    test_step9.py
  .env.example
  alembic.ini
  pytest.ini
  requirements.txt
db-init/
  init-supertokens-db.sql
frontend/
  src/
    api/
      content.js
    auth/
      AuthContext.jsx
      identity.js
      LoginPage.jsx
      SignupPage.jsx
      supertokensInit.js
    parent/
      ParentDashboard.jsx
    shared/
      api.js
      Header.jsx
      Landing.jsx
      ProtectedRoute.jsx
      theme.css
    student/
      ChapterRequestPanel.jsx
      StudentDashboard.jsx
    teacher/
      ChapterRequests.jsx
      NewBookWizard.jsx
      RoomDetail.jsx
      TeacherDashboard.jsx
      TeacherLibrary.jsx
      WholeBookUpload.jsx
    App.jsx
    main.jsx
  .env.example
  .gitignore
  eslint.config.js
  index.html
  package.json
  vite.config.js
.gitignore
docker-compose.yml
</directory_structure>

<files>
This section contains the contents of the repository's files.

<file path="backend/app/admin/__init__.py">

</file>

<file path="backend/app/admin/routes.py">
"""Administrator actions on OFFICIAL books (who is an administrator: ADMIN_USERNAMES). Teachers delete their own
books through /teacher/books/...; these routes exist only for the official library."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.auth.admin import require_admin
from app.content_library import deletion
from app.db.session import get_db
from app.models import Book, Chapter

router = APIRouter(prefix="/admin", tags=["admin"])


def _official_book(db: Session, book_id: uuid.UUID) -> Book:
    book = db.get(Book, book_id)
    if book is None or not book.is_reference:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Official book not found")
    return book


@router.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_official_book(book_id: uuid.UUID, admin=Depends(require_admin), db: Session = Depends(get_db)):
    deletion.delete_book(db, _official_book(db, book_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/books/{book_id}/chapters/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_official_chapter(book_id: uuid.UUID, chapter_id: uuid.UUID, admin=Depends(require_admin), db: Session = Depends(get_db)):
    book = _official_book(db, book_id)
    chapter = db.get(Chapter, chapter_id)
    if chapter is None or chapter.book_id != book.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chapter not found")
    deletion.delete_chapter(db, chapter)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
</file>

<file path="backend/app/agents/__init__.py">

</file>

<file path="backend/app/assessment/__init__.py">

</file>

<file path="backend/app/assessment/checks.py">
"""The comprehension check that follows "mark complete". Pure functions plus one validated model call per question.

Decided in Phase 3 (Phases.md "Settled before building"):
  * size    : one question per concept, never fewer than CHECK_MIN_QUESTIONS and never more than CHECK_MAX_QUESTIONS.
              Fewer concepts than the floor -> several questions on the same concept; more than the ceiling -> concepts
              the student asked doubts about or scored weak on come first, then the rest in book order.
  * type    : multiple choice only (exactly 4 options, one correct), so grading is plain code (Rules.md §1), never a model.
  * source  : the question is written from the concept's description and the text of ITS OWN page (grounded), checked
              against a schema, retried twice with a correction prompt like concept extraction.
  * no leak : `student_view` has no key and no explanation; those are only revealed by `grade` after submission.
  * order   : the model tends to put the right answer first, so options are shuffled in code (seeded per question id)."""
import json
import random
import re
from dataclasses import dataclass
from typing import Optional, Sequence

from pydantic import BaseModel, Field, ValidationError, field_validator

from app.core.config import settings
from app.core.errors import ProcessingError

MAX_RETRIES = 2

SYSTEM = (
    "You write ONE multiple-choice comprehension question for a school student, about ONE concept, using only the "
    "textbook page given. Reply with JSON only: "
    '{"question":str,"options":[str,str,str,str],"correct_index":int,"explanation":str}. '
    "Exactly 4 options, exactly one correct, the others plausible but clearly wrong according to the page. Test "
    "understanding, not copying: do not quote the page's own sentence as the question. Do not use 'all of the above', "
    "'none of the above' or 'both A and B'. The explanation is one or two sentences saying why the answer is right. "
    "Add no outside knowledge. If a list of questions already asked is given, ask about a different aspect."
)


class CheckQuestionError(ProcessingError):
    pass


class McqSchema(BaseModel):
    question: str = Field(min_length=8, max_length=400)
    options: list[str] = Field(min_length=4, max_length=4)
    correct_index: int = Field(ge=0, le=3)
    explanation: str = Field(default="", max_length=500)

    @field_validator("options")
    @classmethod
    def _distinct(cls, options: list[str]) -> list[str]:
        cleaned = [o.strip() for o in options]
        if any(not o or len(o) > 250 for o in cleaned):
            raise ValueError("every option must be 1-250 characters")
        if len({o.lower() for o in cleaned}) != 4:
            raise ValueError("options must be different from each other")
        if any(re.search(r"\b(all|none) of the above\b|\bboth [a-d] and [a-d]\b", o, re.I) for o in cleaned):
            raise ValueError("no 'all/none of the above' options")
        return cleaned


@dataclass
class Question:
    """The server-side record: includes the key. Never send this to a student before submission."""
    concept_id: str
    question: str
    options: list[str]
    correct_index: int
    explanation: str


def question_count(n_concepts: int) -> int:
    return max(settings.check_min_questions, min(settings.check_max_questions, n_concepts))


def plan_check(concept_ids: Sequence[str], priority_ids: Sequence[str] = ()) -> list[str]:
    """The concept each question is about, in order. Repeats a concept only to reach the floor."""
    unique = list(dict.fromkeys(concept_ids))
    if not unique:
        return []
    n = question_count(len(unique))
    if len(unique) > n:
        first = [c for c in dict.fromkeys(priority_ids) if c in set(unique)]
        chosen = (first + [c for c in unique if c not in set(first)])[:n]
        chosen_set = set(chosen)
        return [c for c in unique if c in chosen_set]  # back into book order
    return [unique[i % len(unique)] for i in range(n)]


def _strip_fences(raw: str) -> str:
    return re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())


def generate_question(provider, concept_id: str, name: str, description: str, page_text: str,
                      already_asked: Sequence[str] = (), seed: Optional[str] = None) -> Question:
    """Raises CheckQuestionError after MAX_RETRIES failed corrections (the caller shows "couldn't generate this right
    now", never a blank question or a stale one)."""
    user = f"CHECK QUESTION\nCONCEPT: {name}\nDESCRIPTION: {description or ''}\nPAGE:\n{(page_text or '')[: settings.concept_max_chars]}"
    if already_asked:
        user += "\nQUESTIONS ALREADY ASKED:\n" + "\n".join(f"- {q}" for q in already_asked)
    last_error = ""
    for attempt in range(MAX_RETRIES + 1):
        prompt = user + (f"\n\nYour previous reply was invalid: {last_error}\nReturn valid JSON only, matching the schema exactly." if attempt else "")
        raw = provider.complete_json(SYSTEM, prompt)
        try:
            parsed = McqSchema.model_validate_json(_strip_fences(raw))
        except ValidationError as exc:
            last_error = "; ".join(e["msg"] for e in exc.errors())[:300]
            continue
        return shuffle_options(Question(concept_id, parsed.question.strip(), parsed.options, parsed.correct_index, parsed.explanation.strip()), seed)
    raise CheckQuestionError("Couldn't generate this check right now. Please try again in a moment.")


def shuffle_options(q: Question, seed: Optional[str]) -> Question:
    order = list(range(len(q.options)))
    random.Random(seed if seed is not None else json.dumps([q.concept_id, q.question])).shuffle(order)
    return Question(q.concept_id, q.question, [q.options[i] for i in order], order.index(q.correct_index), q.explanation)


def student_view(q: Question) -> dict:
    """Everything a student may see BEFORE submitting: no key, no explanation."""
    return {"concept_id": q.concept_id, "question": q.question, "options": list(q.options)}


@dataclass
class Graded:
    concept_id: str
    correct: bool
    correct_index: int
    explanation: str


def grade(q: Question, chosen_index: Optional[int]) -> Graded:
    """Deterministic. An unanswered or out-of-range choice is simply wrong."""
    ok = isinstance(chosen_index, int) and not isinstance(chosen_index, bool) and chosen_index == q.correct_index
    return Graded(q.concept_id, ok, q.correct_index, q.explanation)


def concept_scores(graded: Sequence[Graded]) -> dict[str, float]:
    """Share correct per concept (0..1). One concept asked twice and answered once right scores 0.5."""
    totals: dict[str, list[int]] = {}
    for g in graded:
        t = totals.setdefault(g.concept_id, [0, 0])
        t[0] += 1 if g.correct else 0
        t[1] += 1
    return {cid: right / asked for cid, (right, asked) in totals.items()}
</file>

<file path="backend/app/assignments/__init__.py">

</file>

<file path="backend/app/assignments/scope.py">
"""Which concepts does an assignment cover? Everything in Phase 3 (the Doubt button's search scope, the size of
the comprehension check, the weak-area flags) starts from this list, so it is decided here, once, deterministically.

  concept  -> that concept
  chapter  -> the chapter's canonical concepts
  subject  -> canonical concepts of every READY chapter of the student's linked books for that subject
  exercise -> exercise pages carry no concepts of their own (Phase 2 drops them on purpose), so the concepts whose
              stored vectors are closest to the exercise pages' vectors are PROPOSED. No model or embedding call:
              both vectors already sit in `content_embeddings`. The teacher sees and edits the list when assigning.
"""
import uuid
from dataclasses import dataclass, field

import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.embeddings.vectors import from_bytes
from app.models.content import Book, Chapter, ChapterStatus, Concept, ContentEmbedding, Page, PageKind


def chapter_concepts(db: Session, chapter_id: uuid.UUID) -> list[Concept]:
    return list(db.scalars(
        select(Concept).join(Page, Page.id == Concept.page_id)
        .where(Page.chapter_id == chapter_id, Concept.is_canonical.is_(True))
        .order_by(Page.page_number, Concept.position)
    ))


def subject_concepts(db: Session, book_ids: list[uuid.UUID], subject: str) -> list[Concept]:
    """`book_ids` = the books the student has linked (the caller decides who may see what)."""
    if not book_ids:
        return []
    return list(db.scalars(
        select(Concept).join(Page, Page.id == Concept.page_id).join(Chapter, Chapter.id == Page.chapter_id)
        .join(Book, Book.id == Chapter.book_id)
        .where(Book.id.in_(book_ids), Book.subject.ilike(subject), Chapter.status == ChapterStatus.READY,
               Concept.is_canonical.is_(True))
        .order_by(Book.id, Chapter.sequence_num, Page.page_number, Concept.position)
    ))


@dataclass
class ProposedConcept:
    concept_id: uuid.UUID
    name: str
    similarity: float  # best cosine over the exercise pages
    pages: list[int] = field(default_factory=list)  # exercise page numbers that pointed at it


@dataclass
class ExerciseMapping:
    status: str  # "ok" | "no_exercise_pages" | "no_vectors"
    exercise_pages: list[int] = field(default_factory=list)
    per_page: dict[int, list[tuple[str, float]]] = field(default_factory=dict)  # page number -> [(concept name, similarity)] top candidates, whether kept or not
    proposed: list[ProposedConcept] = field(default_factory=list)


def propose_exercise_concepts(db: Session, chapter: Chapter, page_numbers: list[int] | None = None,
                              top_k: int | None = None, min_similarity: float | None = None,
                              max_concepts: int | None = None) -> ExerciseMapping:
    """Concepts an exercise practises. `page_numbers` = the pages the teacher picked (e.g. the pages of Ex.9.5);
    omitted = every page of the chapter labelled `exercise`. Only vectors from ONE embedding model are compared."""
    top_k = top_k or settings.exercise_map_top_k
    floor = settings.exercise_map_min_similarity if min_similarity is None else min_similarity
    cap = max_concepts or settings.exercise_map_max_concepts

    query = select(Page).where(Page.chapter_id == chapter.id)
    query = query.where(Page.page_number.in_(page_numbers)) if page_numbers else query.where(Page.page_kind == PageKind.EXERCISE)
    pages = list(db.scalars(query.order_by(Page.page_number)))
    if not pages:
        return ExerciseMapping("no_exercise_pages")

    page_vectors = {e.page_id: e for e in db.scalars(select(ContentEmbedding).where(
        ContentEmbedding.chapter_id == chapter.id, ContentEmbedding.page_id.in_([p.id for p in pages])))}
    concepts = chapter_concepts(db, chapter.id)
    concept_vectors = {e.concept_id: e for e in db.scalars(select(ContentEmbedding).where(
        ContentEmbedding.chapter_id == chapter.id, ContentEmbedding.concept_id.is_not(None)))}
    if not page_vectors or not concept_vectors:
        return ExerciseMapping("no_vectors", [p.page_number for p in pages])

    model = next(iter(page_vectors.values())).model
    usable = [c for c in concepts if c.id in concept_vectors and concept_vectors[c.id].model == model]
    if not usable:
        return ExerciseMapping("no_vectors", [p.page_number for p in pages])
    matrix = np.vstack([_unit(from_bytes(concept_vectors[c.id].vector)) for c in usable])

    result = ExerciseMapping("ok", [p.page_number for p in pages])
    best: dict[uuid.UUID, ProposedConcept] = {}
    for page in pages:
        embedding = page_vectors.get(page.id)
        if embedding is None or embedding.model != model:
            continue  # a page too short to be embedded (a stray heading) says nothing
        sims = matrix @ _unit(from_bytes(embedding.vector))
        order = np.argsort(-sims)[:top_k]
        result.per_page[page.page_number] = [(usable[i].name, round(float(sims[i]), 3)) for i in order]
        for i in order:
            if sims[i] < floor:
                continue
            concept = usable[i]
            entry = best.setdefault(concept.id, ProposedConcept(concept.id, concept.name, float(sims[i])))
            entry.similarity = max(entry.similarity, float(sims[i]))
            entry.pages.append(page.page_number)
    result.proposed = sorted(best.values(), key=lambda c: -c.similarity)[:cap]
    return result


def _unit(vector) -> np.ndarray:
    v = np.asarray(vector, dtype=float)
    return v / (np.linalg.norm(v) or 1.0)
</file>

<file path="backend/app/auth/__init__.py">

</file>

<file path="backend/app/auth/admin.py">
"""Who may delete OFFICIAL books and chapters: teachers whose username is listed in ADMIN_USERNAMES (empty = nobody)."""
from fastapi import Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.core.config import settings
from app.models import Role, User


def admin_usernames() -> set[str]:
    return {u.strip().lower() for u in settings.admin_usernames.split(",") if u.strip()}


def is_admin(user: User) -> bool:
    return user.role == Role.teacher and (user.username or "").lower() in admin_usernames()


def require_admin(user: User = Depends(get_current_user)) -> User:
    if not is_admin(user):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only an administrator can change official books")
    return user
</file>

<file path="backend/app/auth/dependencies.py">
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session

from app.db.session import get_db
from app.models import Role, User

# Defined once at module level so tests can override this exact dependency object.
session_dependency = verify_session()


def get_current_user(
    s: SessionContainer = Depends(session_dependency),
    db: Session = Depends(get_db),
) -> User:
    # Role comes from OUR database on every request, never from the session payload.
    user = db.scalar(select(User).where(User.supertokens_user_id == s.get_user_id()))
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    return user


def require_roles(*roles: Role):
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Forbidden")
        return user

    return checker


require_teacher = require_roles(Role.teacher)
require_student = require_roles(Role.student)
require_parent = require_roles(Role.parent)
</file>

<file path="backend/app/auth/identity.py">
import re

USERNAME_RE = re.compile(r"^[a-z0-9_]{3,30}$")
PHONE_RE = re.compile(r"^\+?[0-9]{10,15}$")


def normalize_username(value: str) -> str:
    value = value.strip().lower()
    if not USERNAME_RE.match(value):
        raise ValueError("Username must be 3-30 characters: lowercase letters, numbers, underscore only")
    return value


def username_to_email(username: str) -> str:
    """SuperTokens' EmailPassword recipe is email-based, so map the username to a
    hidden email. Must match usernameToEmail() in the frontend."""
    return f"{username}@user.tuition-companion.app"


def normalize_phone(value: str) -> str:
    value = re.sub(r"[\s\-()]", "", value)
    if not PHONE_RE.match(value):
        raise ValueError("Enter a valid phone number")
    return value
</file>

<file path="backend/app/auth/routes.py">
from fastapi import APIRouter, Depends

from app.auth.admin import is_admin
from app.auth.dependencies import get_current_user
from app.models import User
from app.schemas import UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    out = UserOut.model_validate(user)
    out.is_admin = is_admin(user)
    return out
</file>

<file path="backend/app/auth/supertokens_config.py">
from typing import Any, Dict, List, Union

from sqlalchemy import select
from supertokens_python import InputAppInfo, SupertokensConfig, init
from supertokens_python.asyncio import delete_user
from supertokens_python.recipe import emailpassword, session
from supertokens_python.recipe.emailpassword import InputFormField, InputSignUpFeature
from supertokens_python.recipe.emailpassword.interfaces import (
    APIInterface,
    APIOptions,
    SignUpPostOkResult,
)
from supertokens_python.recipe.emailpassword.types import FormField
from supertokens_python.recipe.session.interfaces import SessionContainer
from supertokens_python.types import GeneralErrorResponse

from app.auth.identity import PHONE_RE, USERNAME_RE
from app.core.codes import generate_unique_code
from app.core.config import settings
from app.db.session import SessionLocal
from app.models import Role, User

GENERIC_ERROR = "Could not create account with these details"


def _field(form_fields: List[FormField], field_id: str) -> str:
    return next(f.value for f in form_fields if f.id == field_id)


async def validate_username(value: str, tenant_id: str):
    if not USERNAME_RE.match(value):
        return "Username must be 3-30 characters: lowercase letters, numbers, underscore only"
    return None


async def validate_phone(value: str, sign_up_posttenant_id: str):
    if not PHONE_RE.match(value.replace(" ", "").replace("-", "")):
        return "Enter a valid phone number"
    return None


def override_email_password_apis(original_implementation: APIInterface) -> APIInterface:
    original_sign_up_post = original_implementation.sign_up_post

    async def sign_up_post(
        form_fields: List[FormField],
        tenant_id: str,
        session: Union[SessionContainer, None],
        should_try_linking_with_session_user: Union[bool, None],
        api_options: APIOptions,
        user_context: Dict[str, Any],
    ):
        name = _field(form_fields, "name")
        username = _field(form_fields, "username")
        phone = _field(form_fields, "phone")
        role = _field(form_fields, "role")

        if role not in (
            Role.teacher.value,
            Role.student.value,
            Role.parent.value,
        ):
            return GeneralErrorResponse(GENERIC_ERROR)

        # SuperTokens creates the identity here.
        # The frontend maps username to a hidden synthetic email,
        # so duplicate usernames are rejected by SuperTokens.
        response = await original_sign_up_post(
            form_fields,
            tenant_id,
            session,
            should_try_linking_with_session_user,
            api_options,
            user_context,
        )

        if isinstance(response, SignUpPostOkResult):
            db = SessionLocal()

            try:
                link_code = None

                if role == Role.student.value:
                    link_code = generate_unique_code(
                        lambda c: db.scalar(
                            select(User.id).where(User.link_code == c)
                        )
                        is not None,
                        length=8,
                    )
                #username replaces phone as the unique login identifier
                db.add(
                    User(
                        supertokens_user_id=response.user.id,
                        name=name,
                        username=username,
                        phone=phone,
                        role=Role(role),
                        link_code=link_code,
                    )
                )

                db.commit()

            except Exception as exc:
                print("========== SIGNUP DATABASE ERROR ==========")
                print(repr(exc))
                print("============================================")

                db.rollback()
                db.close()
                await delete_user(response.user.id)
                return GeneralErrorResponse(GENERIC_ERROR)

            else:
                db.close()

        return response

    original_implementation.sign_up_post = sign_up_post
    return original_implementation


def init_supertokens() -> None:
    init(
        app_info=InputAppInfo(
            app_name=settings.app_name,
            api_domain=settings.api_domain,
            website_domain=settings.website_domain,
            api_base_path="/auth",
        ),
        supertokens_config=SupertokensConfig(
            connection_uri=settings.supertokens_connection_uri,
            api_key=settings.supertokens_api_key,
        ),
        framework="fastapi",
        mode="asgi",
        recipe_list=[
            session.init(),
            emailpassword.init(
                #username replaces phone as the unique login identifier
                sign_up_feature=InputSignUpFeature(
                    form_fields=[
                        InputFormField(id="name"),
                        InputFormField(id="username", validate=validate_username),
                        InputFormField(id="phone", validate=validate_phone),
                        InputFormField(id="role"),
                    ]
                ),
                override=emailpassword.InputOverrideConfig(
                    apis=override_email_password_apis
                ),
            ),
        ],
    )
</file>

<file path="backend/app/content_library/__init__.py">

</file>

<file path="backend/app/content_library/access.py">
"""Who may see / change which Book. Single source of truth for content tenancy (Rules.md §2, §4).

- Reference books (NCERT etc.): readable by everyone, writable by no one through the API.
- Private books: owned by exactly one teacher. A student can only see/link them if the student has
  joined a room of that teacher. Nobody else ever sees them. Not-visible looks like "doesn't exist" (404).
"""
import uuid

from fastapi import HTTPException, status
from sqlalchemy import Select, or_, select
from sqlalchemy.orm import Session

from app.models import Book, Room, RoomMember, User, student_book


def _not_found() -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, "Book not found")


# ---- teacher ---------------------------------------------------------------

def teacher_visible_books(teacher: User) -> Select:
    return select(Book).where(or_(Book.is_reference.is_(True), Book.owner_teacher_id == teacher.id))


def get_book_visible_to_teacher(db: Session, teacher: User, book_id: uuid.UUID) -> Book:
    book = db.scalar(teacher_visible_books(teacher).where(Book.id == book_id))
    if book is None:
        raise _not_found()
    return book


def get_owned_book(db: Session, teacher: User, book_id: uuid.UUID) -> Book:
    """For anything that changes a book (add chapter, upload pages)."""
    book = db.get(Book, book_id)
    if book is None:
        raise _not_found()
    if book.is_reference:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Reference books are read-only")
    if book.owner_teacher_id != teacher.id:
        raise _not_found()
    return book


# ---- student ---------------------------------------------------------------

def student_visible_books(student: User) -> Select:
    """Reference books + private books of any teacher whose room this student has joined."""
    my_teachers = (
        select(Room.teacher_id)
        .join(RoomMember, RoomMember.room_id == Room.id)
        .where(RoomMember.user_id == student.id)
    )
    return select(Book).where(or_(Book.is_reference.is_(True), Book.owner_teacher_id.in_(my_teachers)))


def get_book_visible_to_student(db: Session, student: User, book_id: uuid.UUID) -> Book:
    book = db.scalar(student_visible_books(student).where(Book.id == book_id))
    if book is None:
        raise _not_found()
    return book


def get_linked_book(db: Session, student: User, book_id: uuid.UUID) -> Book:
    """Page content is only readable for books the student has linked."""
    book = db.scalar(
        select(Book)
        .join(student_book, student_book.c.book_id == Book.id)
        .where(Book.id == book_id, student_book.c.student_id == student.id)
    )
    if book is None:
        raise _not_found()
    return book
</file>

<file path="backend/app/content_library/deletion.py">
"""Deleting a chapter or a whole book, with everything under it (pages, concepts, edges, embeddings, teacher decisions)
and its copy in the graph store. Shared by the teacher routes (own books), the admin routes (official books) and the
operator tools (`app.db.drop_book`). The graph store is a rebuildable copy: if it cannot be cleaned right now, the
database deletion still goes ahead and `python -m app.db.sync_graph --prune` removes the leftovers later."""
import logging

from fastapi import HTTPException, status
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.graph_store import get_graph_store
from app.models import Book, Chapter
from app.pipeline.jobs import is_actively_processing

logger = logging.getLogger(__name__)


def _clean_graph_store(chapter_ids) -> None:
    try:
        store = get_graph_store()
        if store is not None:
            for cid in chapter_ids:
                store.delete_chapter(str(cid))
    except Exception:
        logger.exception("Could not remove chapters from the graph store; run `python -m app.db.sync_graph --prune`")


def delete_chapter(db: Session, chapter: Chapter) -> None:
    if is_actively_processing(chapter):
        raise HTTPException(status.HTTP_409_CONFLICT, "This chapter is still being processed. Wait for it to finish, then delete it.")
    cid = chapter.id
    db.delete(chapter)
    db.commit()
    _clean_graph_store([cid])


def delete_book(db: Session, book: Book) -> None:
    chapters = list(book.chapters)
    if any(is_actively_processing(c) for c in chapters):
        raise HTTPException(status.HTTP_409_CONFLICT, "A chapter of this book is still being processed. Wait for it to finish, then delete the book.")
    ids = [c.id for c in chapters]
    # books marked as a variant of this one simply stop being marked (the column has no delete rule of its own)
    db.execute(update(Book).where(Book.variant_of_id == book.id).values(variant_of_id=None))
    db.delete(book)
    db.commit()
    _clean_graph_store(ids)
</file>

<file path="backend/app/content_library/feedback.py">
"""Layer 5: remembering what teachers decided about variant suggestions (table `match_feedback`)."""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import MatchFeedback


def record(db: Session, book_id: uuid.UUID, base_book_id: uuid.UUID, decision: str, evidence: dict | None = None) -> MatchFeedback:
    """One row per (book, base). A later decision replaces the earlier one; evidence is kept unless new evidence is given
    (so clearing a variant keeps what the suggestion had shown when it was confirmed). Commits nothing."""
    row = db.scalar(select(MatchFeedback).where(MatchFeedback.book_id == book_id, MatchFeedback.base_book_id == base_book_id))
    if row is None:
        row = MatchFeedback(book_id=book_id, base_book_id=base_book_id, decision=decision, evidence=evidence)
        db.add(row)
    else:
        row.decision = decision
        if evidence is not None:
            row.evidence = evidence
    db.flush()
    return row


def dismissed_ids(db: Session, book_id: uuid.UUID) -> set[uuid.UUID]:
    return set(db.scalars(select(MatchFeedback.base_book_id).where(
        MatchFeedback.book_id == book_id, MatchFeedback.decision == "dismissed")))
</file>

<file path="backend/app/content_library/graph_view.py">
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.content import Chapter, ChapterStatus, Concept, ConceptEdge, CrossChapterEdge, Page
from app.schemas import ChapterGraphOut, CrossChapterEdgeOut, GraphEdgeOut, GraphNodeOut


def chapter_graph(db: Session, chapter: Chapter) -> ChapterGraphOut:
    """The chapter's deduplicated concept graph: one node per distinct concept, edges prerequisite -> concept."""
    rows = db.execute(
        select(Concept, Page.page_number)
        .join(Page, Page.id == Concept.page_id)
        .where(Page.chapter_id == chapter.id)
        .order_by(Page.page_number, Concept.position)
    ).all()
    pages_by_key: dict[str, set[int]] = defaultdict(set)
    for concept, page_number in rows:
        pages_by_key[concept.name_key].add(page_number)

    nodes = [
        GraphNodeOut(id=c.id, name=c.name, description=c.description, pages=sorted(pages_by_key[c.name_key]))
        for c, _ in rows if c.is_canonical
    ]
    edges = db.scalars(select(ConceptEdge).where(ConceptEdge.chapter_id == chapter.id)).all()
    cross = db.execute(
        select(CrossChapterEdge, Concept, Chapter)
        .join(Concept, Concept.id == CrossChapterEdge.prerequisite_id)
        .join(Page, Page.id == Concept.page_id).join(Chapter, Chapter.id == Page.chapter_id)
        .where(CrossChapterEdge.chapter_id == chapter.id, Chapter.status == ChapterStatus.READY)  # same book by construction
        .order_by(Chapter.sequence_num, Concept.name)
    ).all()
    return ChapterGraphOut(
        chapter_id=chapter.id,
        cross_chapter=[
            CrossChapterEdgeOut(
                concept_id=e.concept_id, prerequisite_id=e.prerequisite_id, prerequisite_name=c.name,
                prerequisite_chapter_id=ch.id, prerequisite_chapter_title=ch.title, similarity=e.similarity,
            ) for e, c, ch in cross
        ],
        status=chapter.status,
        nodes=nodes,
        edges=[GraphEdgeOut(prerequisite_id=e.prerequisite_id, concept_id=e.concept_id, source=e.source) for e in edges],
        report=chapter.graph_report,
    )
</file>

<file path="backend/app/content_library/link_requests.py">
"""Student -> teacher chapter requests: 'this chapter isn't in my teacher's book yet, please add it'."""
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Book, Chapter, ChapterRequest, ChapterStatus, User
from app.pipeline.graph import normalize_name


def clean_hint(hint: str) -> str:
    return " ".join(hint.split())


def create_request(
    db: Session, student: User, book: Book, hint: str, chapter_id: uuid.UUID | None
) -> tuple[ChapterRequest, bool]:
    """Returns (request, created). Asking twice for the same thing returns the existing open request."""
    if book.owner_teacher_id is None:
        raise HTTPException(409, "Official books are maintained by us. If a chapter is missing, tell your teacher.")
    hint = clean_hint(hint)
    if len(normalize_name(hint)) < 3:
        raise HTTPException(422, "Please say which chapter you need (name or number)")

    if chapter_id is not None:
        chapter = db.scalar(select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book.id))
        if chapter is None:
            raise HTTPException(404, "Chapter not found in this book")
        if chapter.status == ChapterStatus.READY:
            raise HTTPException(409, "That chapter is already available")

    open_requests = db.scalars(
        select(ChapterRequest).where(ChapterRequest.student_id == student.id, ChapterRequest.status == "open")
    ).all()
    key = normalize_name(hint)
    for existing in open_requests:
        if existing.book_id == book.id and (
            normalize_name(existing.chapter_hint) == key or (chapter_id and existing.chapter_id == chapter_id)
        ):
            return existing, False
    if len(open_requests) >= settings.open_requests_per_student:
        raise HTTPException(429, "You have too many open requests. Wait for your teacher to respond to some first.")

    request = ChapterRequest(
        student_id=student.id, teacher_id=book.owner_teacher_id, book_id=book.id,
        chapter_id=chapter_id, chapter_hint=hint,
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request, True


def resolve(db: Session, request: ChapterRequest, new_status: str) -> ChapterRequest:
    request.status = new_status
    request.resolved_at = datetime.now(timezone.utc)
    return request


def fulfill_requests_for_chapter(db: Session, chapter: Chapter) -> int:
    """Called when a chapter becomes ready: closes open requests that asked for exactly this chapter, or whose
    wording (>= 4 characters) appears in its title. Does not commit; the caller does."""
    title_key = normalize_name(chapter.title)
    count = 0
    for request in db.scalars(
        select(ChapterRequest).where(ChapterRequest.book_id == chapter.book_id, ChapterRequest.status == "open")
    ).all():
        hint_key = normalize_name(request.chapter_hint)
        if request.chapter_id == chapter.id or (len(hint_key) >= 4 and hint_key in title_key):
            resolve(db, request, "fulfilled")
            count += 1
    return count
</file>

<file path="backend/app/content_library/publishers.py">
"""Publisher names written differently are still the same publisher: 'NCERT', 'N.C.E.R.T.' and 'National Council of
Educational Research and Training' (the last one's initials spell the first)."""
from app.pipeline.graph import normalize_name

_SKIP = {"of", "and", "for", "the", "in", "&"}
NOT_BOARDS = {"ncert", "scert", "national council of educational research and training"}  # publishers, never an exam board


def acronym(name: str) -> str:
    """Initials of the significant words of a long name ('' for short names): the National Council of ... Training -> 'ncert'."""
    words = [w for w in normalize_name(name).split() if w not in _SKIP]
    return "".join(w[0] for w in words) if len(words) >= 3 else ""


def same_publisher(a: str | None, b: str | None) -> bool:
    na, nb = normalize_name(a or ""), normalize_name(b or "")
    if not na or not nb:
        return False
    if na == nb:
        return True
    ja, jb = na.replace(" ", ""), nb.replace(" ", "")  # 'N C E R T' and 'NCERT'
    return ja == jb or (acronym(na) != "" and acronym(na) == jb) or (acronym(nb) != "" and acronym(nb) == ja)


def board_is_really_a_publisher(board: str | None, publisher: str | None = None) -> bool:
    nb = normalize_name(board or "")
    return bool(nb) and (nb in NOT_BOARDS or nb.replace(" ", "") in NOT_BOARDS or same_publisher(board, publisher))
</file>

<file path="backend/app/content_library/search.py">
"""Searching the library (official books + the teacher's own), and matching extracted metadata to known books."""
import re
from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.content_library import access
from app.models import Book, User
from app.content_library.publishers import board_is_really_a_publisher, same_publisher
from app.pipeline.graph import normalize_name

_ROMAN = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7, "viii": 8, "ix": 9, "x": 10, "xi": 11, "xii": 12}


def normalize_class(value: Optional[str]) -> str:
    """'Class 9', 'IX', '9th', 'Grade 9' -> '9'."""
    s = normalize_name(value or "")
    digits = re.search(r"\d+", s)
    if digits:
        return digits.group()
    for token in s.split():
        if token in _ROMAN:
            return str(_ROMAN[token])
    return s


def search_books(
    db: Session, teacher: User, *, q: Optional[str] = None, board: Optional[str] = None,
    class_name: Optional[str] = None, subject: Optional[str] = None, publisher: Optional[str] = None,
    scope: str = "all",
):
    """Books visible to this teacher, case-insensitive 'contains' on each filter; q searches all text fields."""
    query = access.teacher_visible_books(teacher)
    if scope == "mine":
        query = query.where(Book.owner_teacher_id == teacher.id)
    elif scope == "reference":
        query = query.where(Book.is_reference.is_(True))
    for column, value in ((Book.board, board), (Book.subject, subject), (Book.publisher, publisher)):
        if value and value.strip():
            query = query.where(func.lower(column).contains(value.strip().lower(), autoescape=True))
    if class_name and class_name.strip():
        wanted = normalize_class(class_name)
        query = query.where(or_(
            func.lower(Book.class_name).contains(class_name.strip().lower(), autoescape=True),
            func.lower(Book.class_name).contains(wanted.lower(), autoescape=True),
        ))
    if q and q.strip():
        for word in q.lower().split():
            query = query.where(or_(*(
                func.lower(c).contains(word, autoescape=True)
                for c in (Book.board, Book.class_name, Book.subject, Book.publisher, Book.edition, Book.school)
            )))
    return query.order_by(Book.is_reference.desc(), Book.board, Book.class_name, Book.subject)


def match_metadata(db: Session, teacher: User, metadata) -> list[Book]:
    """Visible books that agree with what the front pages say: same class and subject (when stated), and
    >= 2 stated fields / >= 75% of them match overall. Official ones first. Class is compared as a number,
    so 'IX' equals 'Class 9'."""
    stated = {
        "board": normalize_name(metadata.board or ""),
        "class": normalize_class(metadata.class_name),
        "subject": normalize_name(metadata.subject or ""),
        "publisher": normalize_name(metadata.publisher or ""),
    }
    if board_is_really_a_publisher(metadata.board, metadata.publisher):
        stated["board"] = ""  # 'NCERT' read as the board: a publisher, so it says nothing about the board
    stated = {k: v for k, v in stated.items() if v}
    if len(stated) < 2:
        return []
    scored = []
    for book in db.scalars(access.teacher_visible_books(teacher)).all():
        have = {
            "board": normalize_name(book.board), "class": normalize_class(book.class_name),
            "subject": normalize_name(book.subject), "publisher": normalize_name(book.publisher),
        }
        if any(k in stated and have[k] != stated[k] for k in ("class", "subject")):
            continue  # a different class or subject is a different book, however well the rest matches
        hits = sum(1 for k, v in stated.items()
                   if (same_publisher(book.publisher, metadata.publisher) if k == "publisher" else have[k] == v))
        if hits >= 2 and hits / len(stated) >= 0.75:
            scored.append((hits / len(stated), book.is_reference, book))
    scored.sort(key=lambda t: (t[0], t[1]), reverse=True)
    return [b for _, _, b in scored[:5]]
</file>

<file path="backend/app/content_library/upload.py">
"""Front-pages-first upload orchestration (Rules.md §3 / md 'Step 2').

1. Front pages (cover + publisher/edition page): OCR + one small LLM call -> proposed metadata + known
   books that already match it. Nothing is created until the teacher confirms (POST /teacher/books with draft_id).
2. Then the content itself: chapter-by-chapter (teacher/routes.py) or the whole textbook at once, which is
   split into chapters from the PDF's bookmarks or the teacher's page ranges and processed per chapter."""
import io
import logging
import uuid
from dataclasses import dataclass
from typing import Optional

import pypdf
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import ProcessingError
from app.core.storage import detect_extension, save_by_hash, sha256_hex
from app.llm import get_llm_provider
from app.models import Book, Chapter, UploadDraft, User
from app.ocr import get_ocr_provider
from app.pipeline.front_matter import extract_book_metadata
from app.schemas import ChapterRange
from app.content_library.search import match_metadata

logger = logging.getLogger(__name__)


@dataclass
class ValidatedUpload:
    data: bytes
    ext: str
    sha256: str


def read_validated_upload(file: UploadFile, max_mb: int, pdf_only: bool = False) -> ValidatedUpload:
    """Size limit, non-empty, and file TYPE BY CONTENT (never the filename or the client's MIME type)."""
    max_bytes = max_mb * 1024 * 1024
    data = file.file.read(max_bytes + 1)
    if not data:
        raise HTTPException(400, "The uploaded file is empty")
    if len(data) > max_bytes:
        raise HTTPException(413, f"File is too large (max {max_mb} MB)")
    ext = detect_extension(data)
    if ext is None or (pdf_only and ext != "pdf"):
        raise HTTPException(
            415,
            "Please upload a PDF file" if pdf_only else "Please upload a PDF, PNG or JPG file",
        )
    return ValidatedUpload(data, ext, sha256_hex(data))


# ---- PDF helpers ------------------------------------------------------------------------------

def open_pdf(data: bytes) -> pypdf.PdfReader:
    try:
        reader = pypdf.PdfReader(io.BytesIO(data))
        if reader.is_encrypted:
            raise ValueError("encrypted")
        len(reader.pages)  # force a parse
        return reader
    except Exception:
        raise HTTPException(
            422,
            "This PDF can't be read (it may be damaged or password-protected)",
        )


def outline_chapters(reader: pypdf.PdfReader) -> list[ChapterRange]:
    """Chapters proposed from the PDF's top-level bookmarks, if it has any. Teachers review/edit them."""
    total = len(reader.pages)
    starts: list[tuple[int, str]] = []
    try:
        for item in reader.outline:
            if isinstance(item, list):  # nested = sub-sections; only top level counts as chapters
                continue
            page = reader.get_destination_page_number(item)
            title = " ".join(str(item.title).split())
            if title and 0 <= page < total:
                starts.append((page + 1, title))
    except Exception:
        logger.warning("Couldn't read PDF bookmarks", exc_info=True)
        return []
    starts.sort()
    proposed, seen_pages = [], set()
    for i, (start, title) in enumerate(starts):
        if start in seen_pages:
            continue
        seen_pages.add(start)
        end = (starts[i + 1][0] - 1) if i + 1 < len(starts) else total
        if end >= start:
            proposed.append(ChapterRange(title=title[:200], start_page=start, end_page=end))
    return proposed


def split_pdf(reader: pypdf.PdfReader, start_page: int, end_page: int) -> bytes:
    writer = pypdf.PdfWriter()
    for index in range(start_page - 1, end_page):
        writer.add_page(reader.pages[index])
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


def validate_ranges(ranges: list[ChapterRange], page_count: int) -> list[ChapterRange]:
    if not ranges:
        raise HTTPException(422, "Add at least one chapter")
    if len(ranges) > settings.max_whole_book_chapters:
        raise HTTPException(
            422, f"At most {settings.max_whole_book_chapters} chapters per upload"
        )
    ordered = sorted(ranges, key=lambda r: r.start_page)
    previous_end = 0
    for r in ordered:
        if r.end_page < r.start_page:
            raise HTTPException(422, f"'{r.title}': the last page is before the first page")
        if r.end_page > page_count:
            raise HTTPException(
                422, f"'{r.title}': the PDF only has {page_count} pages"
            )
        if r.start_page <= previous_end:
            raise HTTPException(422, f"'{r.title}' overlaps the previous chapter")
        previous_end = r.end_page
    return ordered


# ---- step 1: front pages -> proposed metadata -------------------------------------------------------

def create_front_pages_draft(db: Session, teacher: User, upload: ValidatedUpload):
    """Returns (draft, metadata, matching_books). Costs one OCR call + one small LLM call."""
    if upload.ext == "pdf":
        pages = len(open_pdf(upload.data).pages)
        if pages > settings.front_pages_max_pages:
            raise HTTPException(
                422,
                f"Upload only the cover and publisher/edition pages (at most {settings.front_pages_max_pages} pages)",
            )
    try:
        layout = get_ocr_provider().extract_layout(upload.data, upload.ext)
    except Exception as exc:
        logger.exception("Front-page OCR failed")
        raise ProcessingError("Couldn't read these pages right now. Please try again, or enter the details by hand.") from exc
    text = "\n".join(p["text"] for p in layout["pages"]).strip()
    if len(text) < 10:
        raise HTTPException(
            422, "No readable text was found on these pages. Try a clearer scan."
        )
    metadata = extract_book_metadata(get_llm_provider(), text)  # ProcessingError -> 422 with a safe message

    draft = UploadDraft(
        teacher_id=teacher.id, kind="front_pages", source_file=save_by_hash(upload.data, upload.sha256, upload.ext),
        source_sha256=upload.sha256, page_count=layout["page_count"] if "page_count" in layout else len(layout["pages"]),
        payload={"metadata": metadata.model_dump(), "text_chars": len(text)},
    )
    db.add(draft)
    db.commit()
    return draft, metadata, match_metadata(db, teacher, metadata)


# ---- step 2b: whole textbook -> chapters ---------------------------------------------------------------

def create_whole_book_plan(db: Session, teacher: User, book: Book, upload: ValidatedUpload):
    reader = open_pdf(upload.data)
    proposed = outline_chapters(reader)
    draft = UploadDraft(
        teacher_id=teacher.id, kind="whole_book", book_id=book.id,
        source_file=save_by_hash(upload.data, upload.sha256, "pdf"), source_sha256=upload.sha256,
        page_count=len(reader.pages), payload={"proposed": [r.model_dump() for r in proposed]},
    )
    db.add(draft)
    db.commit()
    return draft, proposed


def get_draft(db: Session, teacher: User, draft_id: uuid.UUID, kind: str, book_id: Optional[uuid.UUID] = None) -> UploadDraft:
    draft = db.get(UploadDraft, draft_id)
    if draft is None or draft.teacher_id != teacher.id or draft.kind != kind or (book_id and draft.book_id != book_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Upload not found (it may have expired). Please upload it again.")
    return draft


def split_into_chapters(db: Session, book: Book, draft: UploadDraft, ranges: list[ChapterRange]) -> list[Chapter]:
    """Creates one Chapter per range, each with its own stored PDF slice, marked 'processing'.
    The caller commits and schedules one background job per chapter."""
    from app.core.storage import read_file
    from app.pipeline.jobs import mark_processing

    reader = open_pdf(read_file(draft.source_file))
    last = max((c.sequence_num or 0 for c in book.chapters), default=0)
    chapters = []
    for offset, r in enumerate(validate_ranges(ranges, len(reader.pages)), start=1):
        part = split_pdf(reader, r.start_page, r.end_page)
        digest = sha256_hex(part)
        chapter = Chapter(
            book_id=book.id, title=r.title.strip(), sequence_num=last + offset,
            source_file=save_by_hash(part, digest, "pdf"), source_sha256=digest,
        )
        mark_processing(chapter)
        db.add(chapter)
        chapters.append(chapter)
    return chapters
</file>

<file path="backend/app/core/__init__.py">

</file>

<file path="backend/app/core/codes.py">
import secrets
from typing import Callable

# No 0/O/1/I so codes are easy to read aloud and type on a phone.
ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def generate_code(length: int = 6) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def generate_unique_code(exists: Callable[[str], bool], length: int = 6, attempts: int = 10) -> str:
    for _ in range(attempts):
        code = generate_code(length)
        if not exists(code):
            return code
    raise RuntimeError("Could not generate a unique code")
</file>

<file path="backend/app/core/config.py">
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "dev"
    database_url: str
    supertokens_connection_uri: str = "http://localhost:3567"
    supertokens_api_key: str | None = None
    app_name: str = "Tuition Companion"
    api_domain: str = "http://localhost:8000"
    website_domain: str = "http://localhost:5173"
    cors_origins: str = "http://localhost:5173"
    storage_dir: str = "storage"
    max_upload_mb: int = 20
    chapter_processing_timeout_min: int = 15  # a 'processing' chapter older than this is treated as stuck
    ocr_provider: str = "azure"  # "fake" for local dev/tests, "azure" for Azure Document Intelligence
    azure_doc_intel_endpoint: str = ""
    azure_doc_intel_key: str = ""
    llm_provider: str = "openai_compat"  # "fake" or "openai_compat" (Azure Foundry, OpenAI, etc.)
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_model: str = "gpt-4.1-mini"  # on Azure this is your DEPLOYMENT name
    llm_timeout_s: int = 60
    concept_max_chars: int = 12000  # per-page LLM input cap
    concept_merge_similarity: float = 0.92  # name-embedding cosine at/above which two concepts in a chapter are one
    # --- cross-chapter prerequisites (pipeline/crosslink.py)
    crosslink_enabled: bool = True
    crosslink_candidates: int = 6  # nearest earlier concepts offered to the model per new concept
    crosslink_min_similarity: float = 0.40  # below this an earlier concept is never offered
    crosslink_keep_similarity: float = 0.50  # a link the model chose is dropped below this (counted as dropped_weak)
    crosslink_max_per_concept: int = 3
    crosslink_batch: int = 25  # new concepts per LLM call
    crosslink_max_concepts: int = 200  # a chapter with more new concepts is not cross-linked
    crosslink_max_relinks: int = 30  # later chapters re-linked when an earlier one changes
    link_max_concepts: int = 120  # chapters with more concepts skip the LLM linking pass
    # --- uploads & requests (content_library/upload.py, link_requests.py)
    require_front_pages: bool = False  # True: a Book can only be created from confirmed front-page metadata
    front_pages_max_pages: int = 8
    # Comma-separated usernames of teachers who may also delete OFFICIAL books and chapters from the UI/API (empty = nobody).
    # Everyone else can only delete their own books and chapters. Example: ADMIN_USERNAMES=sandy
    admin_usernames: str = ""
    max_whole_book_mb: int = 100
    max_whole_book_chapters: int = 60
    open_requests_per_student: int = 10
    # --- rate limits (per user, per process; see core/ratelimit.py)
    rate_join_per_min: int = 10  # student room join codes (brute-forceable in principle)
    rate_parent_link_per_min: int = 10  # parent->student link codes
    rate_front_pages_per_hour: int = 10  # each call costs one OCR + one LLM call
    rate_whole_book_plan_per_hour: int = 10
    # --- page matching (pipeline/fingerprint.py, pipeline/matching.py)
    fingerprint_min_words: int = 15  # shorter pages (covers, blanks) are never fingerprinted or matched
    reuse_similarity: float = 0.95  # >= this: same page, reuse its concepts (no LLM call)
    variant_min_similarity: float = 0.60  # >= this (and < reuse): page of a variant/edition
    variant_min_coverage: float = 0.50  # share of a chapter's pages that must match one book to suggest it
    # --- Layer 3: chapter-title sequence as a third signal (pipeline/structure.py)
    structure_enabled: bool = True
    structure_title_overlap: float = 0.75  # share of the shorter title's words that the other title contains
    structure_min_chapters: int = 2  # in-order matching chapters needed; one matching title proves nothing
    # --- Layer 4: embeddings as a second similarity signal (pipeline/embedmatch.py)
    embed_match_enabled: bool = True
    embed_match_similarity: float = 0.85  # page vs page cosine at or above this counts as the same content (a guess until `python -m app.db.embedmatch` shows real numbers)
    embed_match_max_pages: int = 20000  # more candidate page vectors than this: skip (keeps the in-memory compare small)
    # --- embeddings (embeddings/, pipeline/indexing.py). PostgreSQL holds the durable copy of every vector.
    embedding_provider: str = "none"  # "none" (skip) | "fake" (tests/dev) | "openai_compat" (OpenAI, Azure OpenAI/Foundry)
    embedding_base_url: str = ""  # blank -> llm_base_url (same Azure resource)
    embedding_api_key: str = ""  # blank -> llm_api_key
    embedding_model: str = "text-embedding-3-small"  # on Azure this is your DEPLOYMENT name
    embedding_dim: int = 1536  # text-embedding-3-small's native size; must match the Memgraph vector index
    embedding_batch_size: int = 32
    embedding_timeout_s: int = 60
    embedding_max_chars: int = 6000  # per-page input cap (keeps Hindi/Telugu pages under the model's token limit)
    embedding_send_dimensions: bool = False  # True: ask the API for `embedding_dim` (text-embedding-3 models only)
    # --- graph store (graph_store/). Memgraph is a rebuildable copy of what PostgreSQL holds.
    graph_store_provider: str = "none"  # "none" (skip) | "fake" (tests) | "memgraph"
    memgraph_uri: str = "bolt://localhost:7687"
    memgraph_user: str = ""
    memgraph_password: str = ""
    memgraph_vector_capacity: int = 20000  # initial vectors per index; Memgraph resizes beyond it
    memgraph_vector_metric: str = "cos"
    graph_sync_batch: int = 200  # rows per UNWIND statement when writing a chapter
    graph_search_max_candidates: int = 2000  # ceiling for the over-fetch that tenant filtering needs
    # --- Phase 3 (assignments, doubts, checks). Numbers marked "guess" are set from real output of the proof commands.
    exercise_map_top_k: int = 3  # concepts proposed per exercise page
    exercise_map_min_similarity: float = 0.30  # guess: page-vs-concept cosine below this is never proposed (python -m app.db.exercise_map)
    exercise_map_max_concepts: int = 10  # an exercise never maps to more concepts than a check may ask about
    retrieval_min_similarity: float = 0.35  # guess: best page/concept cosine below this = "not in your book" (python -m app.db.retrieval_probe)
    retrieval_candidates: int = 8  # hits fetched per kind before scoping
    retrieval_scope_overfetch: int = 6  # a scoped search fetches this many times more, because other chapters crowd the top
    retrieval_prereq_depth: int = 2  # how far up the prerequisite graph a refresher goes
    check_min_questions: int = 2  # comprehension check floor: even one concept gets a real check
    check_max_questions: int = 10  # ceiling: a whole chapter is not an exhausting test
    weak_below: float = 0.6  # mastery under this is "weak"
    photo_min_words: int = 8  # OCR text shorter than this: ask the student to retake the photo
    photo_page_words: int = 60  # OCR text at least this long is a whole page, not a doubt


settings = Settings()

FAKE_EMBEDDING_MODEL = "fake-embedding"


def refuse_fake_llm(allow_fake: bool) -> None:
    """Scripts that write public/permanent content must not run on the placeholder model by accident."""
    if settings.llm_provider.lower() == "fake" and not allow_fake:
        raise SystemExit(
            "LLM_PROVIDER is 'fake': it produces PLACEHOLDER concepts (snippets of page text chained together), "
            "not real extraction. Set LLM_PROVIDER=openai_compat plus LLM_BASE_URL / LLM_API_KEY / LLM_MODEL in "
            "backend/.env, or pass --allow-fake if you really want placeholders."
        )


def refuse_fake_embeddings(allow_fake: bool) -> None:
    """Scripts that fill the permanent vector copy must not run on hash-based placeholder vectors by accident."""
    if settings.embedding_provider.lower() == "fake" and not allow_fake:
        raise SystemExit(
            "EMBEDDING_PROVIDER is 'fake': it produces PLACEHOLDER vectors (hashed words), not real embeddings. "
            "Set EMBEDDING_PROVIDER=openai_compat plus EMBEDDING_MODEL (your Azure deployment name) in backend/.env, "
            "or pass --allow-fake if you really want placeholders."
        )
</file>

<file path="backend/app/core/errors.py">
class ProcessingError(Exception):
    """An error whose message is safe to show to the teacher."""
</file>

<file path="backend/app/core/logging.py">
import logging


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
</file>

<file path="backend/app/core/ratelimit.py">
"""Small in-memory sliding-window rate limiter, keyed by (bucket, user).

Per-process: fine for one API instance (local, demo, a single container). Behind several instances each one
counts separately, so move this to a shared store (e.g. Redis) before scaling out."""
import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException


class RateLimiter:
    def __init__(self) -> None:
        self._hits: dict[tuple[str, str], deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, bucket: str, subject: str, limit: int, per_seconds: int) -> None:
        now = time.monotonic()
        with self._lock:
            hits = self._hits[(bucket, subject)]
            while hits and now - hits[0] >= per_seconds:
                hits.popleft()
            if len(hits) >= limit:
                retry_after = max(1, int(per_seconds - (now - hits[0])) + 1)
                raise HTTPException(
                    status_code=429,
                    detail="Too many attempts. Please wait a bit and try again.",
                    headers={"Retry-After": str(retry_after)},
                )
            hits.append(now)

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


limiter = RateLimiter()
</file>

<file path="backend/app/core/storage.py">
import hashlib
import os
from pathlib import Path

from app.core.config import settings

# Magic bytes -> extension. We trust file content, never the client's filename or MIME type.
_SIGNATURES = {
    b"%PDF-": "pdf",
    b"\x89PNG\r\n\x1a\n": "png",
    b"\xff\xd8\xff": "jpg",
}


def detect_extension(data: bytes) -> str | None:
    for magic, ext in _SIGNATURES.items():
        if data.startswith(magic):
            return ext
    return None


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def save_by_hash(data: bytes, file_hash: str, ext: str) -> str:
    """Store content under its hash, so identical files are stored once.
    Returns the path relative to the storage root."""
    root = Path(settings.storage_dir)
    rel = Path(file_hash[:2]) / f"{file_hash}.{ext}"
    target = root / rel
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_suffix(target.suffix + ".tmp")
        tmp.write_bytes(data)
        os.replace(tmp, target)  # atomic: never leaves a half-written file
    return rel.as_posix()

def delete_file(rel_path: str) -> None:
    """Remove a stored file. Refuses any path that resolves outside the storage root."""
    root = Path(settings.storage_dir).resolve()
    target = (root / rel_path).resolve()
    if root not in target.parents:
        return
    target.unlink(missing_ok=True)
    
def read_file(rel_path: str) -> bytes:
    return (Path(settings.storage_dir) / rel_path).read_bytes()
</file>

<file path="backend/app/db/migrations/versions/0aa84017b2de_create_book_content_model_uuid.py">
"""create_book_content_model_uuid

Revision ID: 0aa84017b2de
Revises: 483e86509e12
Create Date: 2026-09-30 09:54:46.303627

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0aa84017b2de'
down_revision: Union[str, None] = '483e86509e12'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Cleanly drop obsolete legacy tables with CASCADE to prevent dependency conflicts
    op.execute("DROP TABLE IF EXISTS chapter_concepts CASCADE;")
    op.execute("DROP TABLE IF EXISTS chapter_extractions CASCADE;")
    op.execute("DROP TABLE IF EXISTS room_subjects CASCADE;")
    op.execute("DROP TABLE IF EXISTS chapters CASCADE;")
    op.execute("DROP TABLE IF EXISTS subjects CASCADE;")

    # 2. Create books table
    op.create_table(
        'books',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('board', sa.String(), nullable=True),
        sa.Column('class_name', sa.String(), nullable=True),
        sa.Column('subject', sa.String(), nullable=True),
        sa.Column('publisher', sa.String(), nullable=True),
        sa.Column('edition', sa.String(), nullable=True),
        sa.Column('is_customized', sa.Boolean(), nullable=True),
        sa.Column('school', sa.String(), nullable=True),
        sa.Column('variant_of_id', sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(['variant_of_id'], ['books.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_books_board'), 'books', ['board'], unique=False)
    op.create_index(op.f('ix_books_class_name'), 'books', ['class_name'], unique=False)
    op.create_index(op.f('ix_books_id'), 'books', ['id'], unique=False)
    op.create_index(op.f('ix_books_publisher'), 'books', ['publisher'], unique=False)
    op.create_index(op.f('ix_books_subject'), 'books', ['subject'], unique=False)

    # 3. Create student_book association table
    op.create_table(
        'student_book',
        sa.Column('student_id', sa.Uuid(), nullable=False),
        sa.Column('book_id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('student_id', 'book_id')
    )

    # 4. Create chapters table
    op.create_table(
        'chapters',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('book_id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('sequence_num', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chapters_id'), 'chapters', ['id'], unique=False)
    op.create_index(op.f('ix_chapters_title'), 'chapters', ['title'], unique=False)

    # 5. Create pages table
    op.create_table(
        'pages',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('chapter_id', sa.Uuid(), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('content_text', sa.Text(), nullable=False),
        sa.Column('layout_data', sa.JSON(), nullable=True),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('verified', sa.Boolean(), nullable=True),
        sa.Column('uploaded_by_id', sa.Uuid(), nullable=True),
        sa.Column('fingerprint', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['chapter_id'], ['chapters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pages_id'), 'pages', ['id'], unique=False)

    # 6. Create concepts table
    op.create_table(
        'concepts',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('page_id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('learning_objectives', sa.JSON(), nullable=True),
        sa.Column('prerequisites', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['page_id'], ['pages.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_concepts_id'), 'concepts', ['id'], unique=False)
    op.create_index(op.f('ix_concepts_name'), 'concepts', ['name'], unique=False)


def downgrade() -> None:
    op.drop_table('concepts')
    op.drop_table('pages')
    op.drop_table('chapters')
    op.drop_table('student_book')
    op.drop_table('books')
</file>

<file path="backend/app/db/migrations/versions/182f276a6fc0_add_username_and_make_phone_non_unique.py">
"""add username and make phone non-unique

Revision ID: 182f276a6fc0
Revises: 529cab5476db
Create Date: 2026-09-23 10:51:07.943140

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '182f276a6fc0'
down_revision: Union[str, Sequence[str], None] = '529cab5476db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('username', sa.String(length=30), nullable=False))
    op.drop_index(op.f('ix_users_phone'), table_name='users')
    op.create_index(op.f('ix_users_phone'), 'users', ['phone'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_phone'), table_name='users')
    op.create_index(op.f('ix_users_phone'), 'users', ['phone'], unique=True)
    op.drop_column('users', 'username')
    # ### end Alembic commands ###
</file>

<file path="backend/app/db/migrations/versions/378cd2f34a69_initial_schema.py">
"""initial schema

Revision ID: 378cd2f34a69
Revises: 
Create Date: 2026-09-22 00:04:56.782354

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '378cd2f34a69'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('firebase_uid', sa.String(length=128), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('phone', sa.String(length=20), nullable=False),
    sa.Column('role', sa.Enum('teacher', 'student', 'parent', name='role'), nullable=False),
    sa.Column('link_code', sa.String(length=12), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('link_code')
    )
    op.create_index(op.f('ix_users_firebase_uid'), 'users', ['firebase_uid'], unique=True)
    op.create_index(op.f('ix_users_phone'), 'users', ['phone'], unique=True)
    op.create_table('parent_student_links',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('parent_id', sa.Uuid(), nullable=False),
    sa.Column('student_id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['parent_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('parent_id', 'student_id', name='uq_parent_student')
    )
    op.create_index(op.f('ix_parent_student_links_parent_id'), 'parent_student_links', ['parent_id'], unique=False)
    op.create_index(op.f('ix_parent_student_links_student_id'), 'parent_student_links', ['student_id'], unique=False)
    op.create_table('rooms',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('teacher_id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('room_type', sa.Enum('single_class', 'mixed_class', name='room_type'), nullable=False),
    sa.Column('join_code', sa.String(length=12), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['teacher_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rooms_join_code'), 'rooms', ['join_code'], unique=True)
    op.create_index(op.f('ix_rooms_teacher_id'), 'rooms', ['teacher_id'], unique=False)
    op.create_table('room_members',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('room_id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('room_id', 'user_id', name='uq_room_member')
    )
    op.create_index(op.f('ix_room_members_room_id'), 'room_members', ['room_id'], unique=False)
    op.create_index(op.f('ix_room_members_user_id'), 'room_members', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_room_members_user_id'), table_name='room_members')
    op.drop_index(op.f('ix_room_members_room_id'), table_name='room_members')
    op.drop_table('room_members')
    op.drop_index(op.f('ix_rooms_teacher_id'), table_name='rooms')
    op.drop_index(op.f('ix_rooms_join_code'), table_name='rooms')
    op.drop_table('rooms')
    op.drop_index(op.f('ix_parent_student_links_student_id'), table_name='parent_student_links')
    op.drop_index(op.f('ix_parent_student_links_parent_id'), table_name='parent_student_links')
    op.drop_table('parent_student_links')
    op.drop_index(op.f('ix_users_phone'), table_name='users')
    op.drop_index(op.f('ix_users_firebase_uid'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
</file>

<file path="backend/app/db/migrations/versions/483e86509e12_add_chapter_extractions_cache.py">
"""add chapter_extractions cache

Revision ID: 483e86509e12
Revises: fc42ab2fc59f
Create Date: 2026-09-29 10:55:48.888220

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '483e86509e12'
down_revision: Union[str, Sequence[str], None] = 'fc42ab2fc59f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('chapter_extractions',
    sa.Column('file_hash', sa.String(length=64), nullable=False),
    sa.Column('text', sa.Text(), nullable=False),
    sa.Column('page_count', sa.Integer(), nullable=False),
    sa.Column('provider', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('file_hash')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('chapter_extractions')
    # ### end Alembic commands ###
</file>

<file path="backend/app/db/migrations/versions/529cab5476db_username_replaces_phone_as_unique_login_.py">
"""username replaces phone as unique login identifier

Revision ID: 529cab5476db
Revises: 7efe47816699
Create Date: 2026-09-23 10:27:54.311066

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '529cab5476db'
down_revision: Union[str, Sequence[str], None] = '7efe47816699'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
</file>

<file path="backend/app/db/migrations/versions/7a30a692ec87_small_changes_in_making_username_.py">
"""small changes in making: username replaces phone as unique login identifier

Revision ID: 7a30a692ec87
Revises: 182f276a6fc0
Create Date: 2026-09-23 16:45:14.046556

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a30a692ec87'
down_revision: Union[str, Sequence[str], None] = '182f276a6fc0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
</file>

<file path="backend/app/db/migrations/versions/7efe47816699_rename_firebase_uid_to_supertokens_user_.py">
"""rename firebase_uid to supertokens_user_id

Revision ID: 7efe47816699
Revises: 378cd2f34a69
Create Date: 2026-09-22 11:25:40.455215

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7efe47816699'
down_revision: Union[str, Sequence[str], None] = '378cd2f34a69'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('supertokens_user_id', sa.String(length=128), nullable=False))
    op.drop_index(op.f('ix_users_firebase_uid'), table_name='users')
    op.create_index(op.f('ix_users_supertokens_user_id'), 'users', ['supertokens_user_id'], unique=True)
    op.drop_column('users', 'firebase_uid')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('firebase_uid', sa.VARCHAR(length=128), autoincrement=False, nullable=False))
    op.drop_index(op.f('ix_users_supertokens_user_id'), table_name='users')
    op.create_index(op.f('ix_users_firebase_uid'), 'users', ['firebase_uid'], unique=True)
    op.drop_column('users', 'supertokens_user_id')
    # ### end Alembic commands ###
</file>

<file path="backend/app/db/migrations/versions/9c1d4e7a2b38_book_ownership_and_reference_flag.py">
"""book ownership and reference flag

Revision ID: 9c1d4e7a2b38
Revises: 0aa84017b2de
Create Date: 2026-10-03

Books become either platform-wide reference content (is_reference, no owner) or a private upload
owned by one teacher (owner_teacher_id). Existing rows are backfilled:
  1. a book whose pages were uploaded by a teacher -> owned by that teacher
  2. remaining ownerless NCERT books (the seeded corpus) -> reference
  3. anything left is an orphan: it stays as-is (nobody can see it) and should be deleted by hand.
The CHECK constraint is added NOT VALID so these legacy orphans don't block the migration;
it is enforced for every new/updated row.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '9c1d4e7a2b38'
down_revision: Union[str, None] = '0aa84017b2de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('books', sa.Column('is_reference', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('books', sa.Column('owner_teacher_id', sa.Uuid(), nullable=True))
    op.create_foreign_key('fk_books_owner_teacher', 'books', 'users', ['owner_teacher_id'], ['id'], ondelete='CASCADE')
    op.create_index(op.f('ix_books_is_reference'), 'books', ['is_reference'], unique=False)
    op.create_index(op.f('ix_books_owner_teacher_id'), 'books', ['owner_teacher_id'], unique=False)

    op.execute("""
        UPDATE books b SET owner_teacher_id = sub.teacher_id
        FROM (
            SELECT c.book_id, (array_agg(p.uploaded_by_id ORDER BY p.page_number))[1] AS teacher_id
            FROM pages p
            JOIN chapters c ON c.id = p.chapter_id
            JOIN users u ON u.id = p.uploaded_by_id AND u.role = 'teacher'
            GROUP BY c.book_id
        ) sub
        WHERE b.id = sub.book_id
    """)
    op.execute("UPDATE books SET is_reference = true WHERE owner_teacher_id IS NULL AND lower(publisher) = 'ncert'")

    op.execute("""
        ALTER TABLE books ADD CONSTRAINT ck_book_reference_xor_owner
        CHECK ((is_reference AND owner_teacher_id IS NULL) OR (NOT is_reference AND owner_teacher_id IS NOT NULL))
        NOT VALID
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE books DROP CONSTRAINT IF EXISTS ck_book_reference_xor_owner")
    op.drop_index(op.f('ix_books_owner_teacher_id'), table_name='books')
    op.drop_index(op.f('ix_books_is_reference'), table_name='books')
    op.drop_constraint('fk_books_owner_teacher', 'books', type_='foreignkey')
    op.drop_column('books', 'owner_teacher_id')
    op.drop_column('books', 'is_reference')
</file>

<file path="backend/app/db/migrations/versions/a8e2c5d7f419_page_concepts_model.py">
"""page concepts_model

Revision ID: a8e2c5d7f419
Revises: f7d5a0b4c138
Create Date: 2026-10-06

Records which model produced each page's concepts. 'fake' marks placeholder concepts (never reused by a real
run). Pages processed before this migration stay NULL ('origin unknown'): they are not reused until their
chapter is reprocessed (python -m app.db.reprocess <book-id>).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'a8e2c5d7f419'
down_revision: Union[str, None] = 'f7d5a0b4c138'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('pages', sa.Column('concepts_model', sa.String(length=60), nullable=True))


def downgrade() -> None:
    op.drop_column('pages', 'concepts_model')
</file>

<file path="backend/app/db/migrations/versions/b27e5f1c8d04_chapter_processing_status.py">
"""chapter processing status

Revision ID: b27e5f1c8d04
Revises: 9c1d4e7a2b38
Create Date: 2026-10-04

Chapters get a processing lifecycle (empty -> processing -> ready | failed), the stored source file
(for retry) and its hash (identical re-upload is a no-op). Existing chapters that already have pages
become 'ready'; the rest are 'empty'.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'b27e5f1c8d04'
down_revision: Union[str, None] = '9c1d4e7a2b38'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('chapters', sa.Column('status', sa.String(length=16), server_default='empty', nullable=False))
    op.add_column('chapters', sa.Column('error_message', sa.Text(), nullable=True))
    op.add_column('chapters', sa.Column('source_file', sa.String(), nullable=True))
    op.add_column('chapters', sa.Column('source_sha256', sa.String(length=64), nullable=True))
    op.add_column('chapters', sa.Column('processing_started_at', sa.DateTime(timezone=True), nullable=True))
    op.execute("UPDATE chapters SET status = 'ready' WHERE EXISTS (SELECT 1 FROM pages WHERE pages.chapter_id = chapters.id)")
    op.create_check_constraint('ck_chapter_status', 'chapters', "status IN ('empty','processing','ready','failed')")


def downgrade() -> None:
    op.drop_constraint('ck_chapter_status', 'chapters', type_='check')
    op.drop_column('chapters', 'processing_started_at')
    op.drop_column('chapters', 'source_sha256')
    op.drop_column('chapters', 'source_file')
    op.drop_column('chapters', 'error_message')
    op.drop_column('chapters', 'status')
</file>

<file path="backend/app/db/migrations/versions/b3d7f1a9c562_embeddings_and_graph_sync.py">
"""embeddings table + graph-sync status on chapters

Revision ID: b3d7f1a9c562
Revises: a8e2c5d7f419
Create Date: 2026-10-07

`content_embeddings` is the durable copy of every embedding vector (raw float32 bytes, one row per page or
canonical concept); Memgraph is rebuilt from it. Chapters get `embedding_status`, `graph_sync_status`,
`index_error` and `indexed_at` so a failed or pending derived copy is visible and retryable. Existing chapters
start as 'pending': run `python -m app.db.sync_graph` once embeddings / Memgraph are configured.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'b3d7f1a9c562'
down_revision: Union[str, None] = 'a8e2c5d7f419'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('chapters', sa.Column('embedding_status', sa.String(length=10), server_default='pending', nullable=False))
    op.add_column('chapters', sa.Column('graph_sync_status', sa.String(length=10), server_default='pending', nullable=False))
    op.add_column('chapters', sa.Column('index_error', sa.Text(), nullable=True))
    op.add_column('chapters', sa.Column('indexed_at', sa.DateTime(timezone=True), nullable=True))
    op.create_check_constraint('ck_chapter_embedding_status', 'chapters',
                               "embedding_status IN ('pending','done','skipped','failed')")
    op.create_check_constraint('ck_chapter_graph_sync_status', 'chapters',
                               "graph_sync_status IN ('pending','done','skipped','failed')")

    op.create_table(
        'content_embeddings',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('chapter_id', sa.Uuid(), nullable=False),
        sa.Column('page_id', sa.Uuid(), nullable=True),
        sa.Column('concept_id', sa.Uuid(), nullable=True),
        sa.Column('model', sa.String(length=60), nullable=False),
        sa.Column('dim', sa.Integer(), nullable=False),
        sa.Column('text_sha256', sa.String(length=64), nullable=False),
        sa.Column('vector', sa.LargeBinary(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            '(page_id IS NOT NULL AND concept_id IS NULL) OR (page_id IS NULL AND concept_id IS NOT NULL)',
            name='ck_embedding_page_xor_concept',
        ),
        sa.ForeignKeyConstraint(['chapter_id'], ['chapters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['concept_id'], ['concepts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['page_id'], ['pages.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('concept_id', name='uq_embedding_concept'),
        sa.UniqueConstraint('page_id', name='uq_embedding_page'),
    )
    op.create_index(op.f('ix_content_embeddings_chapter_id'), 'content_embeddings', ['chapter_id'], unique=False)
    op.create_index('ix_embedding_model_hash', 'content_embeddings', ['model', 'text_sha256'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_embedding_model_hash', table_name='content_embeddings')
    op.drop_index(op.f('ix_content_embeddings_chapter_id'), table_name='content_embeddings')
    op.drop_table('content_embeddings')
    op.drop_constraint('ck_chapter_graph_sync_status', 'chapters', type_='check')
    op.drop_constraint('ck_chapter_embedding_status', 'chapters', type_='check')
    op.drop_column('chapters', 'indexed_at')
    op.drop_column('chapters', 'index_error')
    op.drop_column('chapters', 'graph_sync_status')
    op.drop_column('chapters', 'embedding_status')
</file>

<file path="backend/app/db/migrations/versions/c4a91d6e3f72_concept_graph.py">
"""concept graph

Revision ID: c4a91d6e3f72
Revises: b27e5f1c8d04
Create Date: 2026-10-04

concept_edges (prerequisite -> concept, per chapter), concept ordering/identity columns, and
chapters.graph_report. Existing concepts get position 0, a best-effort name_key and is_canonical=true;
run `python -m app.db.relink_chapters` to build graphs for chapters processed before this migration.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'c4a91d6e3f72'
down_revision: Union[str, None] = 'b27e5f1c8d04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('concepts', sa.Column('position', sa.Integer(), server_default='0', nullable=False))
    op.add_column('concepts', sa.Column('name_key', sa.String(), nullable=True))
    op.add_column('concepts', sa.Column('is_canonical', sa.Boolean(), server_default=sa.true(), nullable=False))
    op.create_index(op.f('ix_concepts_name_key'), 'concepts', ['name_key'], unique=False)
    op.add_column('chapters', sa.Column('graph_report', sa.JSON(), nullable=True))

    op.create_table(
        'concept_edges',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('chapter_id', sa.Uuid(), nullable=False),
        sa.Column('concept_id', sa.Uuid(), nullable=False),
        sa.Column('prerequisite_id', sa.Uuid(), nullable=False),
        sa.Column('source', sa.String(length=8), nullable=False),
        sa.CheckConstraint('concept_id <> prerequisite_id', name='ck_concept_edge_not_self'),
        sa.ForeignKeyConstraint(['chapter_id'], ['chapters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['concept_id'], ['concepts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['prerequisite_id'], ['concepts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('concept_id', 'prerequisite_id', name='uq_concept_edge'),
    )
    op.create_index(op.f('ix_concept_edges_chapter_id'), 'concept_edges', ['chapter_id'], unique=False)
    op.create_index(op.f('ix_concept_edges_concept_id'), 'concept_edges', ['concept_id'], unique=False)
    op.create_index(op.f('ix_concept_edges_prerequisite_id'), 'concept_edges', ['prerequisite_id'], unique=False)


def downgrade() -> None:
    op.drop_table('concept_edges')
    op.drop_column('chapters', 'graph_report')
    op.drop_index(op.f('ix_concepts_name_key'), table_name='concepts')
    op.drop_column('concepts', 'is_canonical')
    op.drop_column('concepts', 'name_key')
    op.drop_column('concepts', 'position')
</file>

<file path="backend/app/db/migrations/versions/c8f2a4b6d913_cross_chapter_edges.py">
"""cross-chapter prerequisite edges

Revision ID: c8f2a4b6d913
Revises: b3d7f1a9c562
Create Date: 2026-10-09

`cross_chapter_edges` links a concept to prerequisites in EARLIER chapters of the same book. It is separate from
`concept_edges` so every chapter's own graph stays a self-contained DAG. Existing books have no rows until
`python -m app.db.crosslink` is run (or a chapter finishes processing).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'c8f2a4b6d913'
down_revision: Union[str, None] = 'b3d7f1a9c562'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'cross_chapter_edges',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('chapter_id', sa.Uuid(), nullable=False),
        sa.Column('concept_id', sa.Uuid(), nullable=False),
        sa.Column('prerequisite_id', sa.Uuid(), nullable=False),
        sa.Column('similarity', sa.Float(), nullable=True),
        sa.CheckConstraint('concept_id <> prerequisite_id', name='ck_cross_edge_not_self'),
        sa.ForeignKeyConstraint(['chapter_id'], ['chapters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['concept_id'], ['concepts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['prerequisite_id'], ['concepts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('concept_id', 'prerequisite_id', name='uq_cross_chapter_edge'),
    )
    op.create_index(op.f('ix_cross_chapter_edges_chapter_id'), 'cross_chapter_edges', ['chapter_id'])
    op.create_index(op.f('ix_cross_chapter_edges_concept_id'), 'cross_chapter_edges', ['concept_id'])
    op.create_index(op.f('ix_cross_chapter_edges_prerequisite_id'), 'cross_chapter_edges', ['prerequisite_id'])


def downgrade() -> None:
    op.drop_index(op.f('ix_cross_chapter_edges_prerequisite_id'), table_name='cross_chapter_edges')
    op.drop_index(op.f('ix_cross_chapter_edges_concept_id'), table_name='cross_chapter_edges')
    op.drop_index(op.f('ix_cross_chapter_edges_chapter_id'), table_name='cross_chapter_edges')
    op.drop_table('cross_chapter_edges')
</file>

<file path="backend/app/db/migrations/versions/d5b3e8f2a916_page_fingerprint_index.py">
"""page fingerprint index

Revision ID: d5b3e8f2a916
Revises: c4a91d6e3f72
Create Date: 2026-10-04

Fingerprints move from a comma-joined string (single-word MinHash) to 512 raw bytes (3-word-shingle
MinHash) plus an LSH lookup table (page_bands), so matching no longer scans every page.
The old signatures are incompatible and are dropped: run `python -m app.db.rebuild_fingerprints`
afterwards to recompute them from the stored page text. chapters.match_report holds the last
matching summary used for 'looks like a variant of X' suggestions.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'd5b3e8f2a916'
down_revision: Union[str, None] = 'c4a91d6e3f72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('pages', 'fingerprint')
    op.add_column('pages', sa.Column('fingerprint', sa.LargeBinary(), nullable=True))
    op.add_column('chapters', sa.Column('match_report', sa.JSON(), nullable=True))
    op.create_table(
        'page_bands',
        sa.Column('page_id', sa.Uuid(), nullable=False),
        sa.Column('key', sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(['page_id'], ['pages.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('page_id', 'key'),
    )
    op.create_index(op.f('ix_page_bands_key'), 'page_bands', ['key'], unique=False)


def downgrade() -> None:
    op.drop_table('page_bands')
    op.drop_column('chapters', 'match_report')
    op.drop_column('pages', 'fingerprint')
    op.add_column('pages', sa.Column('fingerprint', sa.String(), nullable=True))
</file>

<file path="backend/app/db/migrations/versions/d9a3b5c7e124_match_feedback.py">
"""teacher decisions about variant suggestions (Layer 5)

Revision ID: d9a3b5c7e124
Revises: c8f2a4b6d913
Create Date: 2026-10-10

`match_feedback` records, per (book, base book), whether the teacher confirmed, dismissed or retracted the
'this is a variant of that book' suggestion, together with the evidence the suggestion showed. Dismissed
suggestions are no longer offered for that book. Existing books have no rows.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'd9a3b5c7e124'
down_revision: Union[str, None] = 'c8f2a4b6d913'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'match_feedback',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('book_id', sa.Uuid(), nullable=False),
        sa.Column('base_book_id', sa.Uuid(), nullable=False),
        sa.Column('decision', sa.String(length=10), nullable=False),
        sa.Column('evidence', sa.JSON(), nullable=True),
        sa.Column('decided_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint('book_id <> base_book_id', name='ck_match_feedback_not_self'),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['base_book_id'], ['books.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('book_id', 'base_book_id', name='uq_match_feedback_pair'),
    )
    op.create_index(op.f('ix_match_feedback_book_id'), 'match_feedback', ['book_id'])
    op.create_index(op.f('ix_match_feedback_base_book_id'), 'match_feedback', ['base_book_id'])


def downgrade() -> None:
    op.drop_index(op.f('ix_match_feedback_base_book_id'), table_name='match_feedback')
    op.drop_index(op.f('ix_match_feedback_book_id'), table_name='match_feedback')
    op.drop_table('match_feedback')
</file>

<file path="backend/app/db/migrations/versions/e1b4c7d9a203_page_kind.py">
"""page_kind: what each page is (content / recap / exercise / other)

Revision ID: e1b4c7d9a203
Revises: d9a3b5c7e124
Create Date: 2026-10-12

Phase 2 already decided a page's kind while reading it but threw the answer away. Phase 3 needs it: an exercise
assignment ("Ex.9.5") is scoped from the chapter's exercise pages. Existing rows default to `content`; run
`python -m app.db.backfill_page_kind` to label them (no OCR, no LLM calls).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'e1b4c7d9a203'
down_revision: Union[str, None] = 'd9a3b5c7e124'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('pages') as batch:
        batch.add_column(sa.Column('page_kind', sa.String(length=10), server_default='content', nullable=False))
        batch.create_check_constraint('ck_page_kind', "page_kind IN ('content','recap','exercise','other')")


def downgrade() -> None:
    with op.batch_alter_table('pages') as batch:
        batch.drop_constraint('ck_page_kind', type_='check')
        batch.drop_column('page_kind')
</file>

<file path="backend/app/db/migrations/versions/e6c4f9a3b027_upload_drafts_and_chapter_requests.py">
"""upload drafts and chapter requests

Revision ID: e6c4f9a3b027
Revises: d5b3e8f2a916
Create Date: 2026-10-04

books: how the metadata was obtained (front pages vs manual), what the system extracted, the stored front pages.
upload_drafts: front pages / whole-textbook uploads waiting for the teacher's confirmation.
chapter_requests: student -> teacher "please add this chapter".
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'e6c4f9a3b027'
down_revision: Union[str, None] = 'd5b3e8f2a916'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('books', sa.Column('metadata_source', sa.String(length=12), server_default='manual', nullable=False))
    op.add_column('books', sa.Column('extracted_metadata', sa.JSON(), nullable=True))
    op.add_column('books', sa.Column('front_pages_file', sa.String(), nullable=True))

    op.create_table(
        'upload_drafts',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('teacher_id', sa.Uuid(), nullable=False),
        sa.Column('kind', sa.String(length=12), nullable=False),
        sa.Column('book_id', sa.Uuid(), nullable=True),
        sa.Column('source_file', sa.String(), nullable=False),
        sa.Column('source_sha256', sa.String(length=64), nullable=False),
        sa.Column('page_count', sa.Integer(), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['teacher_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_upload_drafts_teacher_id'), 'upload_drafts', ['teacher_id'], unique=False)

    op.create_table(
        'chapter_requests',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('student_id', sa.Uuid(), nullable=False),
        sa.Column('teacher_id', sa.Uuid(), nullable=False),
        sa.Column('book_id', sa.Uuid(), nullable=False),
        sa.Column('chapter_id', sa.Uuid(), nullable=True),
        sa.Column('chapter_hint', sa.String(length=200), nullable=False),
        sa.Column('status', sa.String(length=10), server_default='open', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('open','fulfilled','dismissed','cancelled')", name='ck_chapter_request_status'),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['teacher_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['chapter_id'], ['chapters.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_chapter_requests_student_id'), 'chapter_requests', ['student_id'], unique=False)
    op.create_index(op.f('ix_chapter_requests_teacher_id'), 'chapter_requests', ['teacher_id'], unique=False)
    op.create_index(op.f('ix_chapter_requests_book_id'), 'chapter_requests', ['book_id'], unique=False)


def downgrade() -> None:
    op.drop_table('chapter_requests')
    op.drop_table('upload_drafts')
    op.drop_column('books', 'front_pages_file')
    op.drop_column('books', 'extracted_metadata')
    op.drop_column('books', 'metadata_source')
</file>

<file path="backend/app/db/migrations/versions/f7d5a0b4c138_page_needs_review.py">
"""page needs_review replaces verified

Revision ID: f7d5a0b4c138
Revises: e6c4f9a3b027
Create Date: 2026-10-05

`verified` (teacher vs student upload) stopped meaning anything once student uploads were removed: every page
was True. It becomes `needs_review` + `review_note`: set by the pipeline when a page looks wrong (e.g. lots of
text but no concepts found), so teachers can re-scan it.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'f7d5a0b4c138'
down_revision: Union[str, None] = 'e6c4f9a3b027'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('pages', sa.Column('needs_review', sa.Boolean(), server_default=sa.false(), nullable=False))
    op.add_column('pages', sa.Column('review_note', sa.String(length=200), nullable=True))
    op.drop_column('pages', 'verified')


def downgrade() -> None:
    op.add_column('pages', sa.Column('verified', sa.Boolean(), nullable=True))
    op.execute("UPDATE pages SET verified = true")
    op.drop_column('pages', 'review_note')
    op.drop_column('pages', 'needs_review')
</file>

<file path="backend/app/db/migrations/versions/fc42ab2fc59f_add_subjects_chapters_room_subjects.py">
"""add subjects chapters room_subjects

Revision ID: fc42ab2fc59f
Revises: 7a30a692ec87
Create Date: 2026-09-28 18:09:12.880798

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fc42ab2fc59f'
down_revision: Union[str, Sequence[str], None] = '7a30a692ec87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('subjects',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('teacher_id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('grade', sa.String(length=20), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['teacher_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('teacher_id', 'name', name='uq_subject_teacher_name')
    )
    op.create_index(op.f('ix_subjects_teacher_id'), 'subjects', ['teacher_id'], unique=False)
    op.create_table('chapters',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('subject_id', sa.Uuid(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('uploaded', 'processing', 'ready', 'failed', name='chapter_status'), nullable=False),
    sa.Column('file_path', sa.String(length=500), nullable=True),
    sa.Column('file_hash', sa.String(length=64), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chapters_file_hash'), 'chapters', ['file_hash'], unique=False)
    op.create_index(op.f('ix_chapters_subject_id'), 'chapters', ['subject_id'], unique=False)
    op.create_table('room_subjects',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('room_id', sa.Uuid(), nullable=False),
    sa.Column('subject_id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('room_id', 'subject_id', name='uq_room_subject')
    )
    op.create_index(op.f('ix_room_subjects_room_id'), 'room_subjects', ['room_id'], unique=False)
    op.create_index(op.f('ix_room_subjects_subject_id'), 'room_subjects', ['subject_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_room_subjects_subject_id'), table_name='room_subjects')
    op.drop_index(op.f('ix_room_subjects_room_id'), table_name='room_subjects')
    op.drop_table('room_subjects')
    op.drop_index(op.f('ix_chapters_subject_id'), table_name='chapters')
    op.drop_index(op.f('ix_chapters_file_hash'), table_name='chapters')
    op.drop_table('chapters')
    op.drop_index(op.f('ix_subjects_teacher_id'), table_name='subjects')
    op.drop_table('subjects')
    # ### end Alembic commands ###
</file>

<file path="backend/app/db/migrations/env.py">
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from app.core.config import settings
from app.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url.replace("%", "%%"))


# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
</file>

<file path="backend/app/db/migrations/README">
Generic single-database configuration.
</file>

<file path="backend/app/db/migrations/script.py.mako">
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, Sequence[str], None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    """Upgrade schema."""
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """Downgrade schema."""
    ${downgrades if downgrades else "pass"}
</file>

<file path="backend/app/db/__init__.py">

</file>

<file path="backend/app/db/backfill_page_kind.py">
"""Label the pages of chapters processed before `pages.page_kind` existed (exercise / recap / content).

    python -m app.db.backfill_page_kind            # DRY RUN: prints what would change per chapter
    python -m app.db.backfill_page_kind --yes      # write it

No OCR and no LLM calls: it applies the same deterministic rules the pipeline uses (a page that STARTS with an
"Exercises" / "Summary" heading, and every page after a chapter-end summary in the last 40% of the chapter). Only
pages still labelled `content` are touched, so re-running is safe and a label the model gave is never overwritten.
Labels only decide how exercise assignments are scoped; they never change concepts or a chapter's status."""
import argparse
from collections import Counter

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Chapter, ChapterStatus, Page
from app.pipeline.concepts import SUMMARY_TAIL_FROM, heading_page_kind, looks_like_summary_page


def label_pages(pages: list[Page]) -> dict:
    """{page: new kind} for the pages that should stop being plain `content` (pages sorted by number)."""
    changes, summary_seen, total = {}, False, len(pages)
    for index, page in enumerate(pages):
        kind = "exercise" if summary_seen else heading_page_kind(page.content_text)
        if looks_like_summary_page(page.content_text) and index >= SUMMARY_TAIL_FROM * total:
            summary_seen = True
        if kind and page.page_kind == "content":
            changes[page] = kind
    return changes


def run(db_factory, yes: bool = False) -> list[str]:
    out, totals = [], Counter()
    with db_factory() as db:
        for chapter in db.scalars(select(Chapter).where(Chapter.status == ChapterStatus.READY).order_by(Chapter.book_id, Chapter.sequence_num)):
            pages = list(db.scalars(select(Page).where(Page.chapter_id == chapter.id).order_by(Page.page_number)))
            changes = label_pages(pages)
            kinds = Counter(changes.values())
            totals.update(kinds)
            out.append(f"{chapter.title}: {len(pages)} pages, " + (", ".join(f"{n} {k}" for k, n in kinds.items()) or "nothing to label"))
            if yes:
                for page, kind in changes.items():
                    page.page_kind = kind
        if yes:
            db.commit()
        else:
            db.rollback()
    out.append(("labelled " if yes else "dry run, would label ") + (", ".join(f"{n} {k}" for k, n in totals.items()) or "nothing"))
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--yes", action="store_true")
    print("\n".join(run(SessionLocal, parser.parse_args().yes)))
</file>

<file path="backend/app/db/check_probe.py">
"""See what the comprehension check would ask, on your real concepts (real model, writes nothing).

    python -m app.db.check_probe                       # 3 concepts spread over the ready chapters
    python -m app.db.check_probe --book <id> --n 5     # 5 concepts of one book
    python -m app.db.check_probe --sizes               # only: how many questions each ready chapter's check would have

Prints each question as the student would see it, then the key and explanation on a separate line (the key is never
sent to a student before submission). Judge: is the question about the concept, is exactly one option right according to
the page, are the wrong options plausible but wrong, and is it more than a copy of the page's sentence?"""
import argparse
import uuid

from sqlalchemy import select

from app.assessment.checks import CheckQuestionError, generate_question, plan_check, question_count, student_view
from app.assignments.scope import chapter_concepts
from app.core.config import refuse_fake_llm, settings
from app.db.session import SessionLocal
from app.llm import get_llm_provider
from app.models import Book, Chapter, ChapterStatus, Concept, Page


def sizes(db_factory, book_id=None) -> list[str]:
    out = [f"questions per concept count: floor {settings.check_min_questions}, ceiling {settings.check_max_questions}"]
    with db_factory() as db:
        query = select(Chapter).where(Chapter.status == ChapterStatus.READY).order_by(Chapter.book_id, Chapter.sequence_num)
        if book_id is not None:
            query = query.where(Chapter.book_id == book_id)
        for ch in db.scalars(query):
            n = len(chapter_concepts(db, ch.id))
            out.append(f"  {ch.title}: {n} concepts -> {question_count(n)} questions")
    return out


def run(db_factory, llm, book_id=None, n: int = 3) -> list[str]:
    out = []
    with db_factory() as db:
        query = select(Concept).join(Page, Page.id == Concept.page_id).join(Chapter, Chapter.id == Page.chapter_id) \
            .where(Chapter.status == ChapterStatus.READY, Concept.is_canonical.is_(True)) \
            .order_by(Chapter.book_id, Chapter.sequence_num, Page.page_number, Concept.position)
        if book_id is not None:
            query = query.where(Chapter.book_id == book_id)
        concepts = list(db.scalars(query))
        if not concepts:
            return ["no ready concepts found"]
        step = max(1, len(concepts) // n)
        picked = concepts[::step][:n]
        failures = 0
        for c in picked:
            page = db.get(Page, c.page_id)
            chapter = db.get(Chapter, page.chapter_id)
            book = db.get(Book, chapter.book_id)
            out.append(f"\n[{book.subject or ''} / {chapter.title} / p{page.page_number}] concept: {c.name}")
            try:
                q = generate_question(llm, str(c.id), c.name, c.description, page.content_text, seed=str(c.id))
            except CheckQuestionError:
                failures += 1
                out.append("    FAILED: the model did not return a valid question after retries")
                continue
            view = student_view(q)
            out.append(f"  Q: {view['question']}")
            out += [f"     {'ABCD'[i]}. {o}" for i, o in enumerate(view["options"])]
            out.append(f"  KEY (not shown to the student): {'ABCD'[q.correct_index]} - {q.explanation}")
        out.append(f"\n{len(picked) - failures}/{len(picked)} valid questions. Nothing was written.")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--book")
    parser.add_argument("--n", type=int, default=3)
    parser.add_argument("--sizes", action="store_true")
    parser.add_argument("--allow-fake", action="store_true")
    a = parser.parse_args()
    book = uuid.UUID(a.book) if a.book else None
    if a.sizes:
        print("\n".join(sizes(SessionLocal, book)))
    else:
        refuse_fake_llm(a.allow_fake)
        print("\n".join(run(SessionLocal, get_llm_provider(), book, a.n)))
</file>

<file path="backend/app/db/cleanup_drafts.py">
"""Delete abandoned upload drafts (front pages / whole-book PDFs nobody confirmed) and their stored files.

    python -m app.db.cleanup_drafts            # drafts older than 7 days
    python -m app.db.cleanup_drafts --days 1

A stored file is removed only if nothing else still points at it (another draft, a chapter's source file,
or a book's front pages), because files are stored by content hash and can be shared."""
import argparse
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.storage import delete_file
from app.db.session import SessionLocal
from app.models import Book, Chapter, UploadDraft


def cleanup(db: Session, older_than_days: int = 7) -> tuple[int, int]:
    """Returns (drafts_deleted, files_deleted)."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=older_than_days)
    old = db.scalars(select(UploadDraft).where(UploadDraft.created_at < cutoff)).all()
    paths = {d.source_file for d in old}
    for draft in old:
        db.delete(draft)
    db.flush()

    still_used = set(db.scalars(select(UploadDraft.source_file)).all())
    still_used |= {p for p in db.scalars(select(Chapter.source_file)).all() if p}
    still_used |= {p for p in db.scalars(select(Book.front_pages_file)).all() if p}
    removed = 0
    for path in paths - still_used:
        try:
            delete_file(path)
            removed += 1
        except OSError:
            pass  # already gone
    db.commit()
    return len(old), removed


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=7)
    args = parser.parse_args()
    with SessionLocal() as session:
        drafts, files = cleanup(session, args.days)
    print(f"Removed {drafts} abandoned draft(s) and {files} stored file(s).")
</file>

<file path="backend/app/db/crosslink.py">
"""Link chapters to the earlier chapters of their book (cross-chapter prerequisites), for chapters that were
processed before this existed, or after a change of model.

    python -m app.db.crosslink                 # every book
    python -m app.db.crosslink --book <id>     # one book
    python -m app.db.crosslink --force         # ask the model again even if nothing changed
    python -m app.db.crosslink --book <id> --explain   # dry run: show every candidate, its similarity and what the model chose

Needs the chapters' embeddings (run `python -m app.db.sync_graph` first if `show_graph` says embeddings are not
done). Chapters are linked in book order. Nothing here changes pages, concepts or any chapter's own graph."""
import argparse
import uuid

from sqlalchemy import select

from app.core.config import refuse_fake_llm
from app.db.session import SessionLocal
from app.models import Book, Chapter, ChapterStatus
from app.pipeline.crosslink import crosslink_chapter, explain_chapter
from app.pipeline.indexing import sync_cross_edges


def crosslink_books(db_factory, book_id=None, force: bool = False, allow_fake: bool = False) -> list[str]:
    refuse_fake_llm(allow_fake)
    from app.llm import get_llm_provider
    provider = get_llm_provider()
    out: list[str] = []
    with db_factory() as db:
        query = select(Book.id)
        if book_id is not None:
            query = query.where(Book.id == book_id)
        book_ids = list(db.scalars(query))
    for bid in book_ids:
        with db_factory() as db:
            chapters = list(db.scalars(
                select(Chapter).where(Chapter.book_id == bid, Chapter.status == ChapterStatus.READY).order_by(Chapter.sequence_num)
            ))
            for chapter in chapters:
                if force:
                    report = dict(chapter.graph_report or {})
                    report.pop("cross_chapter", None)
                    chapter.graph_report = report
                try:
                    rep = crosslink_chapter(db, chapter, provider)
                    db.commit()
                    out.append(f"{rep.get('status'):14} {chapter.title}: {rep.get('edges', 0)} cross-chapter edges")
                except Exception as exc:
                    db.rollback()
                    out.append(f"FAILED         {chapter.title}: {type(exc).__name__}")
            if chapters:
                out.append(f"  graph store {'updated' if sync_cross_edges(db, bid) else 'not updated (off or unreachable)'}")
    return out


def explain_books(db_factory, book_id=None, allow_fake: bool = False) -> list[str]:
    """Writes nothing (the model is still asked, so it costs a few LLM calls)."""
    refuse_fake_llm(allow_fake)
    from app.llm import get_llm_provider
    provider = get_llm_provider()
    out: list[str] = []
    with db_factory() as db:
        query = select(Chapter).where(Chapter.status == ChapterStatus.READY).order_by(Chapter.book_id, Chapter.sequence_num)
        if book_id is not None:
            query = query.where(Chapter.book_id == book_id)
        for chapter in db.scalars(query):
            out += explain_chapter(db, chapter, provider)
        db.rollback()
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--book")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--explain", action="store_true", help="dry run, writes nothing")
    parser.add_argument("--allow-fake", action="store_true")
    a = parser.parse_args()
    if a.explain:
        print("\n".join(explain_books(SessionLocal, uuid.UUID(a.book) if a.book else None, a.allow_fake)))
        raise SystemExit(0)
    print("\n".join(crosslink_books(SessionLocal, uuid.UUID(a.book) if a.book else None, a.force, a.allow_fake)))
</file>

<file path="backend/app/db/drop_book.py">
"""Remove a whole OFFICIAL book (for example an empty duplicate left behind by an ingest with a different --edition).

    python -m app.db.drop_book --book <book-id>          # dry run: shows what would go
    python -m app.db.drop_book --book <book-id> --yes    # really delete it

Deletes the book with all its chapters, pages, concepts, edges and embeddings, and its copy in the graph store.
Official books only; teachers' books are deleted by their owners in the app."""
import argparse
import uuid

from sqlalchemy import func, select

from app.content_library import deletion
from app.db.session import SessionLocal
from app.models import Book, Concept, Page, Chapter


def run(db_factory, book_id: uuid.UUID, confirm: bool) -> list[str]:
    with db_factory() as db:
        book = db.get(Book, book_id)
        if book is None:
            return ["Book not found."]
        if not book.is_reference:
            return ["Refused: this is not an official book. Teachers delete their own books in the app."]
        chapters = db.scalar(select(func.count()).select_from(Chapter).where(Chapter.book_id == book.id))
        pages = db.scalar(select(func.count()).select_from(Page).join(Chapter, Chapter.id == Page.chapter_id).where(Chapter.book_id == book.id))
        concepts = db.scalar(select(func.count()).select_from(Concept).join(Page, Page.id == Concept.page_id).join(Chapter, Chapter.id == Page.chapter_id).where(Chapter.book_id == book.id))
        line = f"{book.publisher} {book.class_name} {book.subject} (edition {book.edition or '-'}): {chapters} chapters, {pages} pages, {concepts} concepts"
        if not confirm:
            return [f"would delete {line}", "dry run, nothing deleted (add --yes)"]
        deletion.delete_book(db, book)
        return [f"deleted {line}"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--book", required=True)
    parser.add_argument("--yes", action="store_true")
    a = parser.parse_args()
    print("\n".join(run(SessionLocal, uuid.UUID(a.book), a.yes)))
</file>

<file path="backend/app/db/drop_chapter.py">
"""Remove one chapter of an OFFICIAL book (for example a leftover test chapter).

    python -m app.db.drop_chapter --book <book-id> --number 3          # dry run: shows what would go
    python -m app.db.drop_chapter --book <book-id> --number 3 --yes    # really delete it

Deletes the chapter with its pages, concepts, edges and embeddings (database cascade) and its copy in the graph store.
Official books only; teachers' chapters are never touched here. Afterwards run
`python -m app.db.crosslink --book <book-id> --force` so cross-chapter links stop pointing at the removed chapter."""
import argparse
import uuid

from sqlalchemy import func, select

from app.db.session import SessionLocal
from app.graph_store import get_graph_store
from app.models import Book, Chapter, Concept, Page


def run(db_factory, book_id: uuid.UUID, number: int, confirm: bool) -> list[str]:
    with db_factory() as db:
        book = db.get(Book, book_id)
        if book is None:
            return ["Book not found."]
        if not book.is_reference:
            return ["Refused: this is not an official book. This tool only removes chapters of official books."]
        chapter = db.scalar(select(Chapter).where(Chapter.book_id == book.id, Chapter.sequence_num == number))
        if chapter is None:
            return [f"No chapter number {number} in this book."]
        pages = db.scalar(select(func.count()).select_from(Page).where(Page.chapter_id == chapter.id))
        concepts = db.scalar(select(func.count()).select_from(Concept).join(Page, Page.id == Concept.page_id).where(Page.chapter_id == chapter.id))
        line = f"chapter {chapter.sequence_num} '{chapter.title}' [{chapter.status}]: {pages} pages, {concepts} concepts"
        if not confirm:
            return [f"would delete {line}", "dry run, nothing deleted (add --yes)"]
        store = get_graph_store()
        if store is not None:
            store.delete_chapter(str(chapter.id))
        db.delete(chapter)
        db.commit()
        return [f"deleted {line}", f"now run: python -m app.db.crosslink --book {book_id} --force"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--book", required=True)
    parser.add_argument("--number", type=int, required=True)
    parser.add_argument("--yes", action="store_true")
    a = parser.parse_args()
    print("\n".join(run(SessionLocal, uuid.UUID(a.book), a.number, a.yes)))
</file>

<file path="backend/app/db/embedmatch.py">
"""Layer 4 from the command line: compare chapters' stored page vectors with the books a teacher can see.

    python -m app.db.embedmatch                  # every book, DRY RUN: prints what it would suggest and the closest books
    python -m app.db.embedmatch --book <id>      # one book
    python -m app.db.embedmatch --save           # also store the suggestions in each chapter's match report

Needs the chapters' embeddings (run `python -m app.db.sync_graph` first if `show_graph` says they are not done).
No embedding or LLM calls. Use the dry run to judge EMBED_MATCH_SIMILARITY on real data before relying on it."""
import argparse
import uuid

from sqlalchemy import select

from app.core.config import settings
from app.db.session import SessionLocal
from app.models import Chapter, ChapterStatus
from app.pipeline.embedmatch import compute, embedmatch_chapter


def run(db_factory, book_id=None, save: bool = False) -> list[str]:
    out = [f"similarity >= {settings.embed_match_similarity} per page, coverage >= {settings.variant_min_coverage} of the chapter's pages"]
    with db_factory() as db:
        query = select(Chapter).where(Chapter.status == ChapterStatus.READY).order_by(Chapter.book_id, Chapter.sequence_num)
        if book_id is not None:
            query = query.where(Chapter.book_id == book_id)
        for chapter in db.scalars(query):
            found, info = compute(db, chapter)
            out.append(f"{chapter.title}: {info.get('status')} ({info.get('pages_compared', 0)} pages)")
            for near in info.get("closest", []):
                out.append(f"    closest: {near['book']} / {near['chapter']}: {near['matched_pages']}/{near['pages_checked']} pages, avg {near['avg_similarity']}")
            for s in found:
                out.append(f"    SUGGEST: {s['chapter_title']} ({s['matched_pages']}/{s['pages_checked']} pages, avg {s['avg_similarity']})")
            if save:
                embedmatch_chapter(db, chapter)
                db.commit()
        if not save:
            db.rollback()
    out.append("saved" if save else "dry run, nothing saved (use --save)")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--book")
    parser.add_argument("--save", action="store_true")
    a = parser.parse_args()
    print("\n".join(run(SessionLocal, uuid.UUID(a.book) if a.book else None, a.save)))
</file>

<file path="backend/app/db/exercise_map.py">
"""See which concepts each exercise page would be mapped to, on your real chapters (read-only, no model calls).

    python -m app.db.exercise_map                       # every ready chapter that has exercise pages
    python -m app.db.exercise_map --book <id>           # one book
    python -m app.db.exercise_map --book <id> --chapter 9 --pages 7,8   # the pages of one exercise (e.g. Ex.9.5)
    python -m app.db.exercise_map --min-similarity 0.4  # try another cut-off without touching the settings

For each exercise page it prints the closest concepts WITH their similarity, kept or not, and then the list that would
be proposed to the teacher. Judge two things: are the kept concepts really what the exercise practises, and does the
cut-off (EXERCISE_MAP_MIN_SIMILARITY) sit between the right and the wrong ones? Needs `python -m app.db.sync_graph`
to have created the embeddings and `python -m app.db.backfill_page_kind --yes` to have labelled old pages."""
import argparse
import uuid

from sqlalchemy import select

from app.core.config import settings
from app.db.session import SessionLocal
from app.assignments.scope import propose_exercise_concepts
from app.models import Book, Chapter, ChapterStatus


def run(db_factory, book_id=None, chapter_number=None, pages=None, min_similarity=None) -> list[str]:
    floor = settings.exercise_map_min_similarity if min_similarity is None else min_similarity
    out = [f"top {settings.exercise_map_top_k} per page, kept when similarity >= {floor}, at most {settings.exercise_map_max_concepts} concepts"]
    with db_factory() as db:
        query = select(Chapter).where(Chapter.status == ChapterStatus.READY).order_by(Chapter.book_id, Chapter.sequence_num)
        if book_id is not None:
            query = query.where(Chapter.book_id == book_id)
        if chapter_number is not None:
            query = query.where(Chapter.sequence_num == chapter_number)
        for chapter in db.scalars(query):
            mapping = propose_exercise_concepts(db, chapter, pages, min_similarity=floor)
            if mapping.status == "no_exercise_pages":
                continue
            book = db.get(Book, chapter.book_id)
            out.append(f"\n{book.publisher or ''} {book.class_name or ''} {book.subject or ''} / {chapter.title}  [{mapping.status}]")
            if mapping.status != "ok":
                out.append("    no vectors: run python -m app.db.sync_graph first")
                continue
            for number in mapping.exercise_pages:
                rows = mapping.per_page.get(number)
                if rows is None:
                    out.append(f"  page {number}: too short to embed")
                    continue
                out.append(f"  page {number}: " + "; ".join(f"{'*' if s >= floor else ' '}{n} {s}" for n, s in rows))
            out.append("  PROPOSED: " + (", ".join(f"{c.name} ({c.similarity:.2f}, p{','.join(map(str, c.pages))})" for c in mapping.proposed) or "nothing above the cut-off"))
    out.append("\n* = kept. Nothing was written.")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--book")
    parser.add_argument("--chapter", type=int)
    parser.add_argument("--pages", help="comma-separated page numbers of one exercise")
    parser.add_argument("--min-similarity", type=float)
    a = parser.parse_args()
    print("\n".join(run(SessionLocal, uuid.UUID(a.book) if a.book else None, a.chapter,
                        [int(x) for x in a.pages.split(",")] if a.pages else None, a.min_similarity)))
</file>

<file path="backend/app/db/ingest_reference.py">
"""Load an official textbook (NCERT, SCERT...) into the Reference Corpus from a PDF.

    python -m app.db.ingest_reference book.pdf --board CBSE --class "Class 9" --subject Science \
        --publisher NCERT [--edition "2025"] [--chapters "Matter:1-12,Atoms:13-30"] [--append] [--number 5]

Without --chapters the PDF's top-level bookmarks define the chapters. NCERT publishes one PDF per chapter:
ingest the first with --append (or without it), then every further chapter of the SAME book with --append,
and --number N to give a chapter its textbook number (default: the next free number). Without --append an
existing reference book is never touched. Runs the same OCR -> fingerprint ->
concept -> graph pipeline as a teacher upload (use OCR_PROVIDER / LLM_PROVIDER in .env), one chapter at a time,
each in its own transaction, so a failure only affects that chapter. Reference books are public and read-only
through the API; this script is the only way to create them."""
import argparse
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.content_library.upload import open_pdf, outline_chapters, split_pdf, validate_ranges
from app.core.storage import save_by_hash, sha256_hex
from app.core.config import refuse_fake_llm
from app.db.session import SessionLocal
from app.models import Book, Chapter, ChapterStatus
from app.pipeline.jobs import mark_processing, run_chapter_job
from app.schemas import ChapterRange


def parse_ranges(text: str) -> list[ChapterRange]:
    ranges = []
    for part in text.split(","):
        title, _, pages = part.rpartition(":")
        start, _, end = pages.partition("-")
        ranges.append(ChapterRange(title=title.strip(), start_page=int(start), end_page=int(end or start)))
    return ranges


def ingest(db_factory, pdf_bytes: bytes, *, board: str, class_name: str, subject: str, publisher: str,
           edition: str | None = None, ranges: list[ChapterRange] | None = None,
           append: bool = False, first_number: int | None = None, allow_fake: bool = False) -> tuple[str, list[str]]:
    """Returns (book_id, per-chapter result lines). Refuses to create a duplicate reference book unless
    append=True, which adds the chapters to the existing one (refusing duplicate titles/numbers)."""
    refuse_fake_llm(allow_fake)
    reader = open_pdf(pdf_bytes)
    chapters = validate_ranges(ranges or outline_chapters(reader), len(reader.pages))

    with db_factory() as db:
        dup = db.scalar(select(Book).where(
            Book.is_reference.is_(True), Book.board == board, Book.class_name == class_name,
            Book.subject == subject, Book.publisher == publisher, Book.edition == edition,
        ))
        if dup is not None and not append:
            raise SystemExit(
                f"This reference book already exists (id {dup.id}). Use --append to add chapters to it, "
                "or delete it first to re-ingest."
            )
        existing = list(db.scalars(select(Chapter).where(Chapter.book_id == dup.id))) if dup else []
        first = first_number or (max((c.sequence_num or 0 for c in existing), default=0) + 1)
        titles = {c.title.casefold() for c in existing}
        numbers = {c.sequence_num for c in existing}
        for offset, r in enumerate(chapters):
            if r.title.casefold() in titles:
                raise SystemExit(f"This book already has a chapter called '{r.title}'. Nothing was changed.")
            if first + offset in numbers:
                raise SystemExit(f"This book already has a chapter number {first + offset}. Use --number to pick another.")
        if dup is not None:
            book = dup
        else:
            book = Book(board=board, class_name=class_name, subject=subject, publisher=publisher,
                        edition=edition, is_reference=True, owner_teacher_id=None, metadata_source="manual")
            db.add(book)
            db.flush()
        chapter_ids = []
        for number, r in enumerate(chapters, start=first):
            part = split_pdf(reader, r.start_page, r.end_page)
            digest = sha256_hex(part)
            chapter = Chapter(book_id=book.id, title=r.title, sequence_num=number,
                              source_file=save_by_hash(part, digest, "pdf"), source_sha256=digest)
            mark_processing(chapter)
            db.add(chapter)
            db.flush()
            chapter_ids.append(chapter.id)
        db.commit()
        book_id = str(book.id)

    results = []
    for chapter_id in chapter_ids:
        run_chapter_job(chapter_id, None, db_factory)  # owns its session; failures are recorded on the chapter
        with db_factory() as db:
            ch = db.get(Chapter, chapter_id)
            ok = ch.status == ChapterStatus.READY
            results.append(f"{'ok    ' if ok else 'FAILED'} {ch.title}" + ("" if ok else f": {ch.error_message}"))
    return book_id, results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pdf")
    parser.add_argument("--board", required=True)
    parser.add_argument("--class", dest="class_name", required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--publisher", required=True)
    parser.add_argument("--edition")
    parser.add_argument("--allow-fake", action="store_true", help="allow the placeholder LLM (tests only)")
    parser.add_argument("--append", action="store_true", help="add the chapter(s) to the existing reference book")
    parser.add_argument("--number", type=int, dest="first_number", help="textbook number of the first chapter")
    parser.add_argument("--chapters", help='"Title:first-last,Title2:first-last"; default: the PDF bookmarks')
    a = parser.parse_args()
    book_id, results = ingest(
        SessionLocal, Path(a.pdf).read_bytes(), board=a.board, class_name=a.class_name, subject=a.subject,
        publisher=a.publisher, edition=a.edition, ranges=parse_ranges(a.chapters) if a.chapters else None,
        append=a.append, first_number=a.first_number, allow_fake=a.allow_fake,
    )
    print(f"Reference book {book_id}")
    print("\n".join(results))
    if any(line.startswith("FAILED") for line in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
</file>

<file path="backend/app/db/match_feedback.py">
"""Layer 5 report: what teachers decided about variant suggestions, and how often they correct the front-page metadata.

    python -m app.db.match_feedback             # counts and number ranges only
    python -m app.db.match_feedback --changes   # also list each corrected front-page field as read -> confirmed

Read-only, operator use: no book titles, ids or teachers (`--changes` shows only the metadata values the teacher edited). Nothing here changes a
threshold on its own; use it to set the guesses (EMBED_MATCH_SIMILARITY, STRUCTURE_TITLE_OVERLAP, VARIANT_MIN_COVERAGE)
from real decisions: a threshold should sit above the biggest number among `dismissed` and below the smallest among
`confirmed`. `confirmed without a suggestion` are books the system missed entirely."""
import statistics
from collections import defaultdict

from sqlalchemy import select

from app.content_library.search import normalize_class
from app.db.session import SessionLocal
from app.models import Book, MatchFeedback
from app.pipeline.graph import normalize_name

FIELDS = ("board", "class_name", "subject", "publisher", "edition", "school")


def _range(values: list[float]) -> str:
    return "n/a" if not values else f"min {min(values):.2f}, median {statistics.median(values):.2f}, max {max(values):.2f}"


def _same(field: str, read, final) -> bool:
    """Equal after the same tidying the library search uses ('IX', 'Class 9' and '9' are one class)."""
    if field == "class_name":
        return normalize_class(read or "") == normalize_class(final or "")
    return normalize_name(read or "") == normalize_name(final or "")


def summarize(db, show_changes: bool = False) -> list[str]:
    rows = list(db.scalars(select(MatchFeedback)))
    out = [f"variant suggestions: {len(rows)} teacher decisions"]
    by: dict = defaultdict(lambda: defaultdict(list))  # signal -> decision -> [evidence]
    missed = 0
    for r in rows:
        if r.evidence is None:
            if r.decision == "confirmed":
                missed += 1
            continue
        by[r.evidence.get("signal", "pages")][r.decision].append(r.evidence)
    for signal in sorted(by):
        out.append(f"  signal {signal}:")
        for decision in ("confirmed", "dismissed", "retracted"):
            ev = by[signal].get(decision, [])
            if ev:
                out.append(f"    {decision}: {len(ev)}  coverage {_range([e.get('coverage', 0) for e in ev])}  "
                           f"avg similarity {_range([e.get('avg_similarity', 0) for e in ev])}")
    out.append(f"  confirmed without a suggestion (the system missed it): {missed}")

    books = [b for b in db.scalars(select(Book).where(Book.extracted_metadata.is_not(None)))]
    out.append(f"front-page metadata: {len(books)} books confirmed from front pages")
    for f in FIELDS:
        pairs = [((b.extracted_metadata or {}).get(f), getattr(b, f)) for b in books]
        changed = [(read, final) for read, final in pairs if not _same(f, read, final)]
        if books:
            out.append(f"  {f}: teacher changed {len(changed)} of {len(books)}")
        if show_changes:
            out += [f"      {read!r} -> {final!r}" for read, final in changed]
    return out


if __name__ == "__main__":
    import sys
    with SessionLocal() as session:
        print("\n".join(summarize(session, show_changes="--changes" in sys.argv)))
</file>

<file path="backend/app/db/phase2_check.py">
"""Phase 2 exit check: one command that tests every Phase 2 piece on the REAL database and prints PASS / FAIL / REVIEW.

    python -m app.db.phase2_check                 # everything (makes about 10 LLM + 10 embedding calls for Layer 4)
    python -m app.db.phase2_check --skip-probe    # no LLM / embedding calls (Layer 4 shows as REVIEW)

PASS = verified by a rule. FAIL = must be fixed (the line says how), then run it again. REVIEW = a person has to look at the
printed lines (extracted metadata, cross-chapter links). Phase 2 is finished when there is no FAIL and every REVIEW was judged.
Writes nothing: checks that need throwaway rows (Layers 3 and 5) run inside a transaction that is always rolled back."""
import argparse
import sys
import uuid
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.content_library import feedback
from app.core.config import settings
from app.db.match_feedback import FIELDS, _same
from app.db.session import SessionLocal
from app.models import Book, Chapter, ChapterStatus, Concept, CrossChapterEdge, MatchFeedback, Page, Role, User
from app.pipeline import structure

Result = tuple[str, str, str]  # (PASS | FAIL | REVIEW, id, message)
MIN_CONCEPTS = 5  # an official chapter with fewer concepts is a test leftover or a failed extraction
UNRESOLVED_SHARE = 0.05  # unresolved prerequisites up to 5% of a chapter's concepts are tolerated (and shown for review)
MIN_READY_CHAPTERS = 3  # fewer cannot show cross-chapter links or judge graph quality across a book


def _official(db: Session) -> list[Book]:
    return list(db.scalars(select(Book).where(Book.is_reference.is_(True)).order_by(Book.publisher, Book.class_name, Book.subject)))


def _label(book: Book) -> str:
    return f"{book.publisher} {book.class_name} {book.subject}"


def check_migrations(db: Session) -> list[Result]:
    from alembic.config import Config
    from alembic.runtime.migration import MigrationContext
    from alembic.script import ScriptDirectory
    backend = Path(__file__).resolve().parents[2]
    head = ScriptDirectory.from_config(Config(str(backend / "alembic.ini"))).get_current_head()
    current = MigrationContext.configure(db.connection()).get_current_revision()
    if current == head:
        return [("PASS", "M1", f"database is at the latest migration ({head})")]
    return [("FAIL", "M1", f"database is at {current}, code expects {head}: run `alembic upgrade head`")]


def check_official_books(db: Session) -> list[Result]:
    books = _official(db)
    if not books:
        return [("FAIL", "D1", "no official book in the database: ingest one with `python -m app.db.ingest_reference`")]
    out: list[Result] = []
    for book in books:
        chapters = list(db.scalars(select(Chapter).where(Chapter.book_id == book.id).order_by(Chapter.sequence_num)))
        ready = [c for c in chapters if c.status == ChapterStatus.READY]
        if not chapters:
            out.append(("FAIL", "D2", f"{_label(book)} (edition {book.edition or '-'}, id {book.id}) has no chapters at all: an empty leftover. "
                                      f"Remove it with `python -m app.db.drop_book --book {book.id} --yes` (or as an administrator in the app)"))
            continue
        out.append(("PASS" if len(ready) >= MIN_READY_CHAPTERS else "FAIL", "D2",
                    f"{_label(book)}: {len(ready)} ready chapters of {len(chapters)}"
                    + ("" if len(ready) >= MIN_READY_CHAPTERS else f" (need at least {MIN_READY_CHAPTERS}: ingest more with `ingest_reference ... --append`)")))
        for c in chapters:
            r = c.graph_report or {}
            pages = db.scalar(select(func.count()).select_from(Page).where(Page.chapter_id == c.id))
            name = f"chapter {c.sequence_num} '{c.title}'"
            problems = []
            if c.status != ChapterStatus.READY:
                problems.append(f"status is {c.status}" + (f" ({c.error_message})" if c.error_message else ""))
            else:
                if r.get("model") == "fake":
                    problems.append("concepts were made by the fake LLM (placeholders)")
                if r.get("concepts", 0) < MIN_CONCEPTS:
                    problems.append(f"only {r.get('concepts', 0)} concepts on {pages} pages: a test leftover or a failed extraction "
                                    f"(remove with `python -m app.db.drop_chapter --book {book.id} --number {c.sequence_num} --yes`, or re-ingest it)")
                if c.embedding_status != "done":
                    problems.append(f"embeddings {c.embedding_status}" + (f" ({c.index_error})" if c.index_error else "") + ": run `python -m app.db.sync_graph`")
                if c.graph_sync_status != "done" and settings.graph_store_provider.lower() != "none":
                    problems.append(f"graph store copy {c.graph_sync_status}: run `python -m app.db.sync_graph`")
                unresolved = r.get("unresolved_prerequisites") or []
                if len(unresolved) > max(1, int(UNRESOLVED_SHARE * r.get("concepts", 0))):  # a stray one is normal, many means the linking failed
                    problems.append(f"{len(unresolved)} unresolved prerequisites among {r.get('concepts', 0)} concepts (more than {UNRESOLVED_SHARE:.0%})")
                if r.get("llm_linking") not in ("done",):
                    problems.append(f"concept linking is '{r.get('llm_linking', '-')}', not done")
            if problems:
                out.append(("FAIL", "D3", f"{name}: " + "; ".join(problems)))
            else:
                out.append(("PASS", "D3", f"{name}: {r.get('concepts', 0)} concepts, {r.get('edges', 0)} edges, {pages} pages, embeddings and graph copy done"))
                if unresolved:
                    out.append(("REVIEW", "D4", f"{name}: the text names prerequisites that are not concepts of the chapter (no edge made): "
                                                + "; ".join(f"'{u['concept']}' needs '{u['prerequisite']}'" for u in unresolved[:5])))
                if r.get("review_pages"):
                    out.append(("REVIEW", "D4", f"{name}: pages flagged for review: {[p['page'] for p in r['review_pages']]}"))
    return out


def check_cross_chapter(db: Session) -> list[Result]:
    out: list[Result] = []
    for book in _official(db):
        ready = list(db.scalars(select(Chapter).where(Chapter.book_id == book.id, Chapter.status == ChapterStatus.READY).order_by(Chapter.sequence_num)))
        if len(ready) < 2:
            continue
        missing = [c for c in ready[1:] if ((c.graph_report or {}).get("cross_chapter") or {}).get("status") not in ("done",)]
        if missing:
            out.append(("FAIL", "X1", f"{_label(book)}: cross-chapter step not done for chapter(s) {[c.sequence_num for c in missing]}: "
                                      f"run `python -m app.db.crosslink --book {book.id} --force`"))
            continue
        out.append(("PASS", "X1", f"{_label(book)}: cross-chapter step done for all {len(ready) - 1} later chapters"))
        names = {c.id: c.title for c in ready}
        edges = db.execute(
            select(CrossChapterEdge, Concept).join(Concept, Concept.id == CrossChapterEdge.concept_id)
            .where(CrossChapterEdge.chapter_id.in_(names))
        ).all()
        for edge, concept in edges:
            prereq = db.get(Concept, edge.prerequisite_id)
            pc = db.scalar(select(Chapter).join(Page, Page.chapter_id == Chapter.id).where(Page.id == prereq.page_id))
            out.append(("REVIEW", "X2", f"link to judge (sim {edge.similarity}): '{concept.name}' [{names[edge.chapter_id]}] needs '{prereq.name}' [{pc.title}]"))
        if not edges:
            out.append(("REVIEW", "X2", f"{_label(book)}: no cross-chapter links among {len(ready)} chapters; see candidates with "
                                        f"`python -m app.db.crosslink --book {book.id} --explain` and judge whether zero is right"))
    return out or [("FAIL", "X1", "no official book with two ready chapters, so cross-chapter links cannot be judged")]


def check_front_pages(db: Session) -> list[Result]:
    books = list(db.scalars(select(Book).where(Book.extracted_metadata.is_not(None))))
    if not books:
        return [("FAIL", "L1", "no book was ever created from front pages: upload a teacher book with front pages once")]
    out: list[Result] = [("PASS", "L1", f"{len(books)} book(s) confirmed from front pages")]
    for f in FIELDS:
        for b in books:
            read, final = (b.extracted_metadata or {}).get(f), getattr(b, f)
            if not _same(f, read, final):
                out.append(("REVIEW", "L2", f"front-page field '{f}': read {read!r}, teacher confirmed {final!r} (extraction wrong, or a harmless formatting difference?)"))
    return out


def _throwaway_teacher(db: Session) -> User:
    tag = uuid.uuid4().hex[:10]
    teacher = User(supertokens_user_id=f"check-{tag}", name="phase2 check", username=f"chk{tag}"[:30], phone="0" + tag[:9], role=Role.teacher)
    db.add(teacher)
    db.flush()
    return teacher


def _shortened(title: str, i: int) -> str:
    words = [w for w in title.replace(":", " ").split() if w.lower() not in structure.STOP]
    return " ".join(words[:2]) if len(words) > 2 else title


def check_structure(db: Session) -> list[Result]:
    """SIMULATED editions built from the real official chapter titles (a real second edition is not needed)."""
    out: list[Result] = []
    nested = db.begin_nested()
    try:
        teacher = _throwaway_teacher(db)
        books = [b for b in _official(db) if len(structure._titles(db, b.id, ready_only=True)) >= 2]
        if not books:
            return [("FAIL", "S1", "no official book with two ready chapters to compare titles against")]
        for official in books:
            titles = structure._titles(db, official.id, ready_only=True)
            variants = {
                "shortened titles": [_shortened(t, i) for i, t in enumerate(titles, 1)],
                "titles with 'Unit n:' and a subtitle": [f"Unit {i}: {t} (a complete overview)" for i, t in enumerate(titles, 1)],
            }
            for label, edition in variants.items():
                book = Book(board="X", class_name="9", subject="check", publisher="check", is_reference=False, owner_teacher_id=teacher.id)
                db.add(book)
                db.flush()
                for i, t in enumerate(edition, 1):
                    db.add(Chapter(book_id=book.id, title=t, sequence_num=i, status=ChapterStatus.EMPTY))
                db.flush()
                hit = next((h for h in structure.suggest(db, book, teacher.id) if h["book"].id == official.id), None)
                out.append(("PASS" if hit else "FAIL", "S1", f"{_label(official)}: simulated edition with {label} -> "
                            + (f"suggested ({hit['matched_chapters']}/{hit['chapters_checked']} chapters)" if hit else "NOT suggested")))
            control = Book(board="X", class_name="9", subject="check", publisher="check", is_reference=False, owner_teacher_id=teacher.id)
            db.add(control)
            db.flush()
            for i, t in enumerate(["Gravitation and Free Fall", "Work, Power and Energy", "Sound Waves"], 1):
                db.add(Chapter(book_id=control.id, title=t, sequence_num=i, status=ChapterStatus.EMPTY))
            db.flush()
            wrong = any(h["book"].id == official.id for h in structure.suggest(db, control, teacher.id))
            out.append(("FAIL" if wrong else "PASS", "S2", f"{_label(official)}: book with unrelated chapter titles -> " + ("WRONGLY suggested" if wrong else "not suggested")))
        out.append(("REVIEW", "S3", "Layer 3 was tested on SIMULATED editions made from the real titles; it will not match an edition that rewords titles "
                                    "heavily (e.g. 'Matter in Our Surroundings' vs 'Matter around us'); the page signals cover that case"))
    except Exception as exc:
        out.append(("FAIL", "S1", f"check crashed: {type(exc).__name__}: {str(exc)[:200]}"))
    finally:
        nested.rollback()
    return out


def check_feedback(db: Session) -> list[Result]:
    """Layer 5 round trip on the real database (columns, JSON, unique and check constraints), then rolled back."""
    out: list[Result] = []
    nested = db.begin_nested()
    try:
        official = next(iter(_official(db)), None)
        if official is None:
            return [("FAIL", "F1", "no official book to use as a base")]
        teacher = _throwaway_teacher(db)
        mine = Book(board="X", class_name="9", subject="check", publisher="check", is_reference=False, owner_teacher_id=teacher.id)
        db.add(mine)
        db.flush()
        evidence = {"signal": "pages", "coverage": 0.5, "avg_similarity": 0.91}
        feedback.record(db, mine.id, official.id, "dismissed", evidence)
        ok_dismiss = official.id in feedback.dismissed_ids(db, mine.id)
        feedback.record(db, mine.id, official.id, "confirmed")
        rows = list(db.scalars(select(MatchFeedback).where(MatchFeedback.book_id == mine.id)))
        db.expire_all()
        row = db.scalar(select(MatchFeedback).where(MatchFeedback.book_id == mine.id))
        ok_replace = len(rows) == 1 and row.decision == "confirmed" and row.evidence == evidence and not feedback.dismissed_ids(db, mine.id)
        try:
            with db.begin_nested():
                db.add(MatchFeedback(book_id=mine.id, base_book_id=mine.id, decision="confirmed"))
                db.flush()
            self_pair_blocked = False
        except IntegrityError:
            self_pair_blocked = True
        for ok, what in ((ok_dismiss, "a dismissal is stored and hides the suggestion"),
                         (ok_replace, "a later confirmation replaces it, keeps the evidence, one row per pair"),
                         (self_pair_blocked, "the database refuses a book being its own base")):
            out.append(("PASS" if ok else "FAIL", "F1", what))
        real = db.scalar(select(func.count()).select_from(MatchFeedback).where(MatchFeedback.book_id != mine.id))
        out.append(("REVIEW", "F2", f"{real} real teacher decision(s) recorded so far; thresholds cannot be tuned from decisions until there are "
                                    f"some (`python -m app.db.match_feedback`), the first guesses stay in force until then"))
    except Exception as exc:
        out.append(("FAIL", "F1", f"check crashed: {type(exc).__name__}: {str(exc)[:200]}"))
    finally:
        nested.rollback()
    return out


def check_embedding(db: Session, skip_probe: bool, pages: int = 10) -> list[Result]:
    if skip_probe:
        return [("REVIEW", "E1", "Layer 4 calibration skipped (--skip-probe): run without it")]
    if settings.llm_provider.lower() == "fake" or settings.embedding_provider.lower() in ("fake", "none"):
        return [("FAIL", "E1", "Layer 4 calibration needs the real LLM and the real embedding model (LLM_PROVIDER / EMBEDDING_PROVIDER are fake or none)")]
    from app.embeddings import get_embedding_provider
    from app.llm import get_llm_provider
    from app.pipeline.embedprobe import probe
    r = probe(db, get_llm_provider(), get_embedding_provider(), pages)
    if r["status"] != "done":
        return [("FAIL", "E1", f"calibration could not run: {r}")]
    detail = (f"{r['pages']} pages; reworded copy similarity min {r['same_min']:.3f} / median {r['same_median']:.3f} "
              f"(phrases kept from the original: {r['kept_phrases_median']:.0%}); different pages up to {r['other_max']:.3f} / median {r['other_median']:.3f}"
              + ("" if r["several_chapters"] else " (only one chapter available: 'different' pages come from the same chapter)"))
    if r["pass"]:
        return [("PASS", "E1", f"EMBED_MATCH_SIMILARITY={r['threshold']} finds {r['recall']:.0%} of reworded pages and {r['false_rate']:.0%} of different pages; {detail}")]
    advice = (f"set EMBED_MATCH_SIMILARITY={r['recommended']} in .env and run again" if r["separable"]
              else "reworded and different pages overlap: page embeddings cannot separate them reliably (set EMBED_MATCH_ENABLED=false or raise VARIANT_MIN_COVERAGE)")
    return [("FAIL", "E1", f"EMBED_MATCH_SIMILARITY={r['threshold']} finds {r['recall']:.0%} of reworded pages and {r['false_rate']:.0%} of different pages; "
                           f"{detail}. {advice}")]


def run(db_factory, skip_probe: bool = False) -> tuple[list[str], int]:
    lines: list[str] = []
    counts = {"PASS": 0, "FAIL": 0, "REVIEW": 0}
    sections = [
        ("Database", check_migrations), ("Official books: chapters, graph, embeddings", check_official_books),
        ("Cross-chapter prerequisites", check_cross_chapter), ("Layer 1: front-page metadata", check_front_pages),
        ("Layer 3: chapter-title sequence", check_structure), ("Layer 4: embedding similarity", lambda db: check_embedding(db, skip_probe)),
        ("Layer 5: teacher decisions", check_feedback),
    ]
    with db_factory() as db:
        for title, fn in sections:
            lines.append(f"\n== {title}")
            try:
                results = fn(db)
            except Exception as exc:
                results = [("FAIL", "?", f"check crashed: {type(exc).__name__}: {str(exc)[:200]}")]
            finally:
                db.rollback()  # nothing this script does is ever kept
            for status, tag, message in results:
                counts[status] += 1
                lines.append(f"{status:<6} {tag:<3} {message}")
    lines.append(f"\nRESULT: {counts['PASS']} PASS, {counts['FAIL']} FAIL, {counts['REVIEW']} REVIEW")
    lines.append("Phase 2 can be closed once there is no FAIL and every REVIEW line has been judged." if not counts["FAIL"]
                 else "Phase 2 is NOT finished: fix the FAIL lines (each says how) and run this again.")
    return lines, counts["FAIL"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skip-probe", action="store_true")
    a = parser.parse_args()
    text, fails = run(SessionLocal, a.skip_probe)
    print("\n".join(text))
    sys.exit(1 if fails else 0)
</file>

<file path="backend/app/db/rebuild_fingerprints.py">
"""Recompute every page's fingerprint + LSH index from its stored text.

    python -m app.db.rebuild_fingerprints

Run once after the migration that introduced shingle fingerprints (it clears the old ones), and any time
the fingerprint settings change. No OCR or LLM calls."""
from sqlalchemy import delete, select

from app.db.session import SessionLocal
from app.models.content import Page, PageBand
from app.pipeline.fingerprint import apply_fingerprint


def rebuild(db) -> int:
    db.execute(delete(PageBand))
    count = 0
    for page in db.scalars(select(Page)).all():
        if apply_fingerprint(page, page.content_text):
            count += 1
    db.commit()
    return count


if __name__ == "__main__":
    with SessionLocal() as session:
        print(f"Fingerprinted {rebuild(session)} page(s).")
</file>

<file path="backend/app/db/relink_chapters.py">
"""Build concept graphs for chapters that were processed before the graph existed.

    python -m app.db.relink_chapters            # real LLM per your .env (one call per chapter)

Re-uses the concepts already stored (no OCR, no per-page LLM calls). Run `python -m app.db.sync_graph`
afterwards to refresh the embeddings and the graph-store copy."""
from sqlalchemy import select

from app.db.session import SessionLocal
from app.llm import get_llm_provider
from app.models.content import Chapter, ChapterStatus, IndexStatus
from app.pipeline.graph import build_chapter_graph


def main() -> None:
    llm = get_llm_provider()
    with SessionLocal() as db:
        chapters = db.scalars(
            select(Chapter).where(Chapter.status == ChapterStatus.READY, Chapter.graph_report.is_(None))
        ).all()
        for chapter in chapters:
            try:
                report = build_chapter_graph(db, chapter, llm)
                # concept identity may have changed, so the derived copies (vectors, graph store) are stale
                chapter.embedding_status = chapter.graph_sync_status = IndexStatus.PENDING
                db.commit()
                print(f"{chapter.title!r}: {report['concepts']} concepts, {report['edges']} edges")
            except Exception as exc:  # keep going; one bad chapter shouldn't block the rest
                db.rollback()
                print(f"{chapter.title!r}: FAILED ({exc})")
        print(f"Done. {len(chapters)} chapter(s) checked.")


if __name__ == "__main__":
    main()
</file>

<file path="backend/app/db/reprocess.py">
"""Re-run processing for a book's chapters from their stored files (no re-upload).

    python -m app.db.reprocess <book-id>              # every chapter
    python -m app.db.reprocess <book-id> --chapter 2  # one chapter number

Use it after fixing .env (e.g. switching from the fake LLM to a real one): each chapter's pages and concepts
are replaced. Concepts made by the fake model are never reused by a real run.
--fresh ignores ALL stored concepts (use it after changing the extraction prompt) and costs one LLM call per page."""
import argparse
import uuid

from sqlalchemy import select

from app.core.config import refuse_fake_llm
from app.db.session import SessionLocal
from app.models import Book, Chapter, ChapterStatus
from app.pipeline.jobs import is_actively_processing, mark_processing, run_chapter_job


def reprocess(db_factory, book_id: uuid.UUID, chapter_number: int | None = None, allow_fake: bool = False, fresh: bool = False) -> list[str]:
    refuse_fake_llm(allow_fake)
    with db_factory() as db:
        book = db.get(Book, book_id)
        if book is None:
            raise SystemExit("Book not found.")
        query = select(Chapter).where(Chapter.book_id == book.id).order_by(Chapter.sequence_num)
        if chapter_number is not None:
            query = query.where(Chapter.sequence_num == chapter_number)
        targets, results = [], []
        for chapter in db.scalars(query).all():
            if not chapter.source_file:
                results.append(f"skipped {chapter.title}: no stored file")
            elif is_actively_processing(chapter):
                results.append(f"skipped {chapter.title}: still processing")
            else:
                mark_processing(chapter)
                targets.append(chapter.id)
        db.commit()
        owner = book.owner_teacher_id
    for chapter_id in targets:
        run_chapter_job(chapter_id, owner, db_factory, fresh=fresh)
        with db_factory() as db:
            ch = db.get(Chapter, chapter_id)
            ok = ch.status == ChapterStatus.READY
            results.append(f"{'ok    ' if ok else 'FAILED'} {ch.title}" + ("" if ok else f": {ch.error_message}"))
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("book_id")
    parser.add_argument("--chapter", type=int)
    parser.add_argument("--allow-fake", action="store_true")
    parser.add_argument("--fresh", action="store_true", help="extract every page again; reuse no stored concepts")
    args = parser.parse_args()
    print("\n".join(reprocess(SessionLocal, uuid.UUID(args.book_id), args.chapter, args.allow_fake, args.fresh)))
</file>

<file path="backend/app/db/retrieval_probe.py">
"""Measure the "not in your book" cut-off on your real chapters (real LLM + real embeddings + the real graph store).

    python -m app.db.retrieval_probe                    # official books, 12 sampled pages
    python -m app.db.retrieval_probe --book <id> --pages 20

The model writes student-style doubts about sampled pages; ten off-topic questions are added; every question goes
through the same retrieval the Tutor will use. It prints how similar each group scored and where a cut-off could sit
(PASS / FAIL like the Phase 2 exit check). Needs embeddings + Memgraph synced (`python -m app.db.sync_graph`). Writes nothing."""
import argparse
import uuid

from sqlalchemy import select

from app.core.config import refuse_fake_embeddings, refuse_fake_llm, settings
from app.db.session import SessionLocal
from app.doubts.calibration import probe
from app.embeddings import get_embedding_provider
from app.graph_store import get_graph_store
from app.llm import get_llm_provider
from app.models import Book


def format_report(r: dict) -> list[str]:
    if r["status"] != "done":
        return [f"cannot judge: {r}"]
    out = [
        f"{r['doubts']} student-style doubts, {len(r['off_topic_values'])} off-topic questions",
        f"in-book doubts   best similarity: min {r['in_book_min']:.3f}, 10th percentile {r['in_book_p10']:.3f}, median {r['in_book_median']:.3f}",
        f"off-topic        best similarity: median {r['off_topic_median']:.3f}, max {r['off_topic_max']:.3f}",
        f"top hit was the right chapter for {r['right_chapter_top_hit']:.0%} of in-book doubts",
    ]
    if r["wrong_chapter_outside"] is not None:
        out.append(f"asked inside the WRONG chapter: {r['wrong_chapter_outside']:.0%} came back `outside_assignment` (scoped max {r['wrong_chapter_scoped_max']:.3f})")
    out.append(f"current RETRIEVAL_MIN_SIMILARITY {r['threshold']}: answers {r['answered_in_book']:.0%} of in-book doubts, wrongly answers {r['wrongly_answered_off_topic']:.0%} of off-topic")
    if r["separable"]:
        out.append(f"groups are separable. Suggested cut-off: {r['recommended']}")
    else:
        out.append("groups OVERLAP: no single cut-off separates them cleanly. Do not rely on the threshold alone; paste this output.")
    out.append("PASS" if r["pass"] else "FAIL (at the current cut-off)")
    out.append("in-book values:   " + " ".join(map(str, r["in_book_values"])))
    out.append("off-topic values: " + " ".join(map(str, r["off_topic_values"])))
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--book")
    parser.add_argument("--pages", type=int, default=12)
    parser.add_argument("--allow-fake", action="store_true")
    a = parser.parse_args()
    refuse_fake_llm(a.allow_fake)
    refuse_fake_embeddings(a.allow_fake)
    embedder, store = get_embedding_provider(), get_graph_store()
    if embedder is None or store is None:
        raise SystemExit("Set EMBEDDING_PROVIDER and GRAPH_STORE_PROVIDER (see the Phase 2 run-book) first.")
    with SessionLocal() as db:
        ids = [uuid.UUID(a.book)] if a.book else list(db.scalars(select(Book.id).where(Book.is_reference.is_(True))))
        print("\n".join(format_report(probe(db, get_llm_provider(), embedder, store, ids, a.pages))))
</file>

<file path="backend/app/db/seed_ncert.py">
"""
Pre-seed free official textbooks (NCERT Class 9 & 10 Science/Math)
into the reference corpus.
Run: python -m app.db.seed_ncert
"""
from app.db.session import SessionLocal
from app.models.content import Book, Chapter, ChapterStatus, Page, Concept
from app.pipeline.graph import build_chapter_graph
from app.pipeline.fingerprint import apply_fingerprint


class _NoLinksLLM:
    """The seeded concepts already name their prerequisites, so no model call is needed to link them."""

    model_name = "manual"

    def complete_json(self, system: str, user: str) -> str:
        return '{"edges": []}'


def seed_ncert_corpus():
    db = SessionLocal()
    try:
        # Check if already seeded
        existing = db.query(Book).filter(Book.is_reference.is_(True), Book.publisher == "NCERT").first()
        if existing:
            print("NCERT reference corpus is already seeded.")
            return

        print("Seeding NCERT Reference Books...")

        # 1. Class 9 Science
        book_c9_sci = Book(
            board="CBSE",
            class_name="Class 9",
            subject="Science",
            publisher="NCERT",
            edition="2026",
            is_customized=False,
            is_reference=True,
        )
        db.add(book_c9_sci)
        db.flush()

        ch1 = Chapter(
            book_id=book_c9_sci.id,
            title="Matter in Our Surroundings",
            sequence_num=1,
        )
        db.add(ch1)
        db.flush()

        sample_p1_text = (
            "Matter in Our Surroundings: Everything in this universe is made up of material "
            "which scientists have named 'matter'. The air we breathe, the food we eat, stones, "
            "clouds, stars, plants and animals, even a small drop of water or a particle of sand "
            "— everything is matter. Physical Nature of Matter: Matter is made up of particles."
        )

        page1 = Page(
            chapter_id=ch1.id,
            page_number=1,
            content_text=sample_p1_text,
        )
        apply_fingerprint(page1, sample_p1_text)
        page1.concepts_model = "manual"  # hand-written sample concepts
        db.add(page1)
        db.flush()

        c1 = Concept(
            page_id=page1.id,
            name="Definition of Matter",
            description="Anything that occupies space and has mass is defined as matter.",
            learning_objectives=["Understand what constitutes matter", "Identify examples of physical matter"],
            prerequisites=[],
        )
        c2 = Concept(
            page_id=page1.id,
            name="Particulate Nature of Matter",
            description="Matter is not continuous; it is composed of tiny discrete particles.",
            learning_objectives=["Describe evidence for particulate nature of matter"],
            prerequisites=["Definition of Matter"],
        )
        db.add_all([c1, c2])
        db.flush()

        ch1.status = ChapterStatus.READY  # visible to students; pages + concepts are already in place
        build_chapter_graph(db, ch1, _NoLinksLLM())

        db.commit()
        print("NCERT Reference Corpus successfully seeded!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding NCERT corpus: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_ncert_corpus()
</file>

<file path="backend/app/db/session.py">
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def get_session_factory():
    """Lets background tasks open their own session using the same factory the
    request used. Overridden in tests so background work hits the test database."""
    return SessionLocal
</file>

<file path="backend/app/db/show_graph.py">
"""Print a book's concept graph as text, to judge (and tune) extraction quality on real chapters.

    python -m app.db.show_graph <book-id>              # every chapter
    python -m app.db.show_graph <book-id> --chapter 3  # one chapter number

For each chapter: the pipeline's report (merged names, edges, dropped loops, unresolved prerequisites,
pages flagged for review), then each concept with what it needs. Paste the output when asking for tuning."""
import argparse
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.content_library.graph_view import chapter_graph
from app.db.session import SessionLocal
from app.models import Book, Chapter


def render_book(db: Session, book_id: uuid.UUID, chapter_number: int | None = None) -> str:
    book = db.get(Book, book_id)
    if book is None:
        return "Book not found."
    query = select(Chapter).where(Chapter.book_id == book.id).order_by(Chapter.sequence_num)
    if chapter_number is not None:
        query = query.where(Chapter.sequence_num == chapter_number)
    out = [f"{book.board} {book.class_name} {book.subject} ({book.publisher}"
           f"{', ' + book.edition if book.edition else ''})" + ("  [official]" if book.is_reference else "")]
    for chapter in db.scalars(query).all():
        graph = chapter_graph(db, chapter)
        r = graph.report or {}
        out += ["", f"== Chapter {chapter.sequence_num}: {chapter.title}  [{chapter.status}]"]
        if chapter.error_message:
            out.append(f"   error: {chapter.error_message}")
        if r.get("model") == "fake":
            out.append("   !! PLACEHOLDER concepts: made by the fake LLM (LLM_PROVIDER=fake). Not real extraction.")
        out.append(f"   search copy: embeddings={chapter.embedding_status}  graph store={chapter.graph_sync_status}"
                   + (f"  ({chapter.index_error})" if chapter.index_error else ""))
        out.append(
            f"   model={r.get('model', 'unknown (made before models were recorded)')}\n"
            f"   concepts={r.get('concepts', 0)}  edges={r.get('edges', 0)}  merged_duplicates={r.get('duplicate_names_merged', 0)}"
            f"  dropped_loops={len(r.get('dropped_cycle_edges', []))}  unresolved={len(r.get('unresolved_prerequisites', []))}"
            f"  llm_linking={r.get('llm_linking', '-')}  review_pages={[p['page'] for p in r.get('review_pages', [])]}\n"
            f"   dropped_backward={len(r.get('dropped_backward_edges', []))}  dropped_concepts={r.get('dropped_concepts', 0)}"
            f"  recap_pages={r.get('recap_pages', 0)}  name_merge_by_embedding={r.get('merge_by_embedding', '-')}"
            f"  edges_copied={r.get('edges_copied', False)}"
        )
        names = {n.id: n.name for n in graph.nodes}
        needs: dict = {}
        for e in graph.edges:
            needs.setdefault(e.concept_id, []).append(f"{names[e.prerequisite_id]} ({e.source})")
        for node in graph.nodes:
            line = f"   - {node.name}  [p. {', '.join(map(str, node.pages))}]"
            if node.id in needs:
                line += "\n       needs: " + "; ".join(needs[node.id])
            out.append(line)
        for item in r.get("unresolved_prerequisites", []):
            out.append(f"   ? '{item['concept']}' mentions '{item['prerequisite']}' (no such concept in this chapter)")
        xc = r.get("cross_chapter") or {}
        if xc:
            out.append(f"   cross-chapter: {xc.get('status')}  edges={xc.get('edges', 0)}  dropped_weak={xc.get('dropped_weak', 0)}  earlier_chapters={xc.get('earlier_chapters', 0)}")
        for item in graph.cross_chapter:
            out.append(f"   ^ '{names[item.concept_id]}' needs '{item.prerequisite_name}' (chapter: {item.prerequisite_chapter_title}, sim {item.similarity})")
        for item in r.get("near_duplicates_not_merged", [])[:15]:
            out.append(f"   ~ near duplicate, not merged ({item['similarity']}): '{item['a']}' / '{item['b']}'")
        for item in r.get("dropped_backward_edges", []):
            out.append(f"   < dropped backward edge: '{item['prerequisite']}' comes later than '{item['concept']}'")
        for item in r.get("dropped_cycle_edges", []):
            out.append(f"   x dropped loop: '{item['prerequisite']}' before '{item['concept']}'")
    return "\n".join(out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("book_id")
    parser.add_argument("--chapter", type=int)
    args = parser.parse_args()
    with SessionLocal() as session:
        print(render_book(session, uuid.UUID(args.book_id), args.chapter))
</file>

<file path="backend/app/db/smoke_memgraph.py">
"""Check a running Memgraph with the app's OWN store code: connect, create the real indexes, write chapters,
vector-search with the tenant (book) filter, walk prerequisites, replace/delete, clean up.

    docker compose up -d memgraph
    python -m app.db.smoke_memgraph                       # uses MEMGRAPH_* / EMBEDDING_DIM from backend/.env
    python -m app.db.smoke_memgraph --uri bolt://localhost:7687 --keep

It only touches nodes it creates itself (random ids) and removes them at the end, unless --keep is given. The
indexes it creates are the app's real ones (concept_embedding_idx, page_embedding_idx) and stay in place.
Send the whole output back, including any FAIL line. Exit code 0 only when every check passed.
"""
import argparse
import sys
import time
import uuid

import numpy as np

from app.core.config import settings
from app.graph_store.base import ChapterGraph, ConceptNode, EdgeRow, PageNode
from app.graph_store.memgraph_store import CONCEPT_INDEX, PAGE_INDEX, MemgraphStore

results: list[bool] = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    results.append(bool(ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  -> {detail}" if detail else ""))
    return bool(ok)


def unit(rng, dim: int) -> np.ndarray:
    v = rng.normal(size=dim)
    return v / np.linalg.norm(v)


def near(base: np.ndarray, rng, noise: float) -> list[float]:
    v = base + rng.normal(size=base.shape) * noise / np.sqrt(base.shape[0])
    return (v / np.linalg.norm(v)).tolist()


def chapter(book_id, concepts: list[tuple[str, list[float]]], pages: list[list[float]], edges: list[tuple[int, int]]) -> ChapterGraph:
    chapter_id = str(uuid.uuid4())
    page_nodes = [PageNode(str(uuid.uuid4()), i + 1, vec) for i, vec in enumerate(pages)]
    nodes = [ConceptNode(str(uuid.uuid4()), name, f"About {name}", i, vec) for i, (name, vec) in enumerate(concepts)]
    return ChapterGraph(
        book_id=str(book_id), chapter_id=chapter_id, title="Smoke test chapter", sequence_num=1, is_reference=False,
        owner_teacher_id=str(uuid.uuid4()), embedding_model="smoke-test", pages=page_nodes, concepts=nodes,
        edges=[EdgeRow(nodes[c].id, nodes[p].id, "llm") for c, p in edges],
        concept_pages=[(n.id, page_nodes[0].id) for n in nodes],
    )


def run_store_checks(store, dim: int, made: list[str]) -> None:
    """The checks that need only the GraphStore interface (so tests can run them on the in-memory fake too).
    Chapter ids it creates are appended to `made` so the caller can clean up."""
    rng = np.random.default_rng(11)
    topic = unit(rng, dim)      # what the "student" asks about
    other = unit(rng, dim)      # unrelated content
    book_a, book_b = uuid.uuid4(), uuid.uuid4()
    query = near(topic, rng, 0.05)

    # Book A: the student's book. Book B: someone else's, with content EVEN CLOSER to the question.
    a = chapter(book_a,
                [("Cell", near(topic, rng, 0.3)), ("Cell membrane", near(topic, rng, 0.35)), ("Osmosis", near(topic, rng, 0.4)),
                 ("Photosynthesis", near(other, rng, 0.1))],
                pages=[near(topic, rng, 0.3), near(other, rng, 0.1)],
                edges=[(1, 0), (2, 1)])  # membrane needs cell; osmosis needs membrane
    b = chapter(book_b, [("Other book's cell", near(topic, rng, 0.02))] + [(f"Filler {i}", near(topic, rng, 0.05)) for i in range(40)],
                pages=[near(topic, rng, 0.02)], edges=[])
    made += [a.chapter_id, b.chapter_id]
    try:
        store.replace_chapter(a)
        store.replace_chapter(b)
        check("write two chapters (one transaction each)", True)
    except Exception as exc:
        check("write two chapters", False, str(exc))
        return

    s = store.stats()
    check("stats count what was written", s["Concept"] >= len(a.concepts) + len(b.concepts) and s["REQUIRES"] >= 2, str(s))

    hits = store.search_concepts(query, [str(book_a)], k=3)
    check("search finds the student's own concepts", bool(hits) and hits[0].name == "Cell", str([(h.name, round(h.similarity, 3)) for h in hits]))
    check("search NEVER returns another book's content", all(h.book_id == str(book_a) for h in hits) and bool(hits))
    check("search stays correct when other books dominate the nearest 20",
          len(hits) == 3, f"got {len(hits)} of 3 (40 closer concepts belong to the other book)")
    both = store.search_concepts(query, [str(book_a), str(book_b)], k=1)
    check("search over both books returns the nearer one", bool(both) and both[0].book_id == str(book_b))
    check("empty book list returns nothing", store.search_concepts(query, [], k=3) == [])
    pages = store.search_pages(query, [str(book_a)], k=2)
    check("page search is filtered the same way", bool(pages) and all(p.book_id == str(book_a) for p in pages) and pages[0].page_number == 1,
          str([(p.page_number, round(p.similarity, 3)) for p in pages]))

    osmosis = next(c for c in a.concepts if c.name == "Osmosis")
    prereqs = store.prerequisites(osmosis.id, [str(book_a)])
    check("prerequisites come back nearest first", [(p.name, p.depth) for p in prereqs] == [("Cell membrane", 1), ("Cell", 2)],
          str([(p.name, p.depth) for p in prereqs]))
    check("prerequisites respect the book filter", store.prerequisites(osmosis.id, [str(book_b)]) == [])

    before = store.stats()
    store.replace_chapter(a)
    check("writing the same chapter again changes nothing", store.stats() == before, f"{before} -> {store.stats()}")

    ids = store.list_chapter_ids()
    check("chapters are listed", a.chapter_id in ids and b.chapter_id in ids)
    store.delete_chapter(b.chapter_id)
    made.remove(b.chapter_id)
    time.sleep(0.5)
    check("delete removes a chapter completely", b.chapter_id not in store.list_chapter_ids()
          and store.search_concepts(query, [str(book_b)], k=1) == [])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--uri", default=settings.memgraph_uri)
    ap.add_argument("--keep", action="store_true", help="leave the test chapters in Memgraph")
    args = ap.parse_args()
    dim = settings.embedding_dim
    print(f"target {args.uri}; vector dimension {dim} (EMBEDDING_DIM); metric {settings.memgraph_vector_metric}")

    store = MemgraphStore(
        args.uri, settings.memgraph_user, settings.memgraph_password, dim=dim,
        capacity=settings.memgraph_vector_capacity, metric=settings.memgraph_vector_metric,
        batch=settings.graph_sync_batch, max_candidates=settings.graph_search_max_candidates,
    )
    made: list[str] = []
    try:
        try:
            store.driver.verify_connectivity()
            check("connect over Bolt", True)
        except Exception as exc:
            check("connect over Bolt", False, repr(exc))
            print("Is the container running?  docker compose ps   (and is MEMGRAPH_URI right?)")
            return 1

        try:
            rows = store.run_admin("SHOW VERSION")
            check("server version", True, str(list(rows[0].values())) if rows else "no rows")
        except Exception as exc:
            check("server version", False, str(exc))

        try:
            store.ensure_schema()
            check("create indexes (label + vector)", True)
        except Exception as exc:
            check("create indexes (label + vector)", False, str(exc))
            print("Vector indexes failed. If this is an older Memgraph, the message above says whether a feature flag "
                  "is needed; otherwise send it to me and we will pin another tag.")
            return 1
        try:
            info = store.run_admin("SHOW VECTOR INDEX INFO")
            names = [str(r.get("index_name") or r.get("name")) for r in info]
            check("both vector indexes exist", CONCEPT_INDEX in names and PAGE_INDEX in names, str(info))
        except Exception as exc:
            check("SHOW VECTOR INDEX INFO", False, str(exc))

        run_store_checks(store, dim, made)
    finally:
        if args.keep:
            print("--keep given: test chapters left in Memgraph:", made)
        else:
            for chapter_id in made:
                try:
                    store.delete_chapter(chapter_id)
                except Exception as exc:
                    print("cleanup failed for", chapter_id, exc)
            if made:
                print("cleaned up the test chapters")
        store.close()

    print(f"\n{sum(results)}/{len(results)} checks passed")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
</file>

<file path="backend/app/db/sync_graph.py">
"""Create embeddings and (re)build the graph-store copy from PostgreSQL.

    python -m app.db.sync_graph                  # every ready chapter whose embeddings/graph copy is pending or failed
    python -m app.db.sync_graph --book <id>      # only that book's chapters
    python -m app.db.sync_graph --chapter <id>   # one chapter, whatever its state
    python -m app.db.sync_graph --status         # just print the counts
    python -m app.db.sync_graph --rebuild        # wipe the graph-store copy and write EVERY ready chapter again from
                                                 # PostgreSQL, using the stored vectors: NO embedding calls
    python -m app.db.sync_graph --prune          # remove graph-store chapters that PostgreSQL no longer has as ready

Use it after switching on embeddings / Memgraph (it fills in chapters processed before), after a Memgraph outage
(failed chapters are retried), or after wiping the Memgraph volume (--rebuild). PostgreSQL stays the source of truth:
nothing here changes pages, concepts or the concept graph.
"""
import argparse
import sys
import uuid
from collections import Counter

from sqlalchemy import select

from app.core.config import refuse_fake_embeddings, settings
from app.db.session import SessionLocal
from app.graph_store import get_graph_store
from app.models import Book, Chapter, ChapterStatus
from app.pipeline.indexing import IndexReport, chapters_needing_index, index_chapter


def status_lines(db) -> list[str]:
    counts = Counter()
    for c in db.scalars(select(Chapter).where(Chapter.status == ChapterStatus.READY)):
        counts[(c.embedding_status, c.graph_sync_status)] += 1
    lines = [
        f"embeddings provider: {settings.embedding_provider}   graph store: {settings.graph_store_provider}",
        f"ready chapters: {sum(counts.values())}",
    ]
    lines += [f"  embeddings={e:8} graph={g:8} chapters={n}" for (e, g), n in sorted(counts.items())]
    return lines


def _describe(db, chapter_id, report: IndexReport) -> str:
    chapter = db.get(Chapter, chapter_id)
    book = db.get(Book, chapter.book_id)
    head = f"{'ok    ' if not report.errors else 'FAILED'} {book.publisher or ''} {book.class_name or ''} {book.subject or ''}: {chapter.title}"
    parts = []
    if report.embedding:
        parts.append(f"embeddings {report.embedding} (new {report.embedded}, reused {report.reused}, kept {report.kept}, removed {report.removed})")
    if report.graph == "done":
        parts.append(f"graph done ({report.graph_concepts} concepts, {report.graph_edges} edges, {report.graph_pages} pages"
                     + (f", {report.without_vectors} without vectors" if report.without_vectors else "") + ")")
    elif report.graph:
        parts.append(f"graph {report.graph}")
    line = f"{head} - " + "; ".join(parts) if parts else head
    return line + "".join(f"\n       ! {e}" for e in report.errors)


def sync_all(db_factory, *, book_id=None, chapter_id=None, rebuild: bool = False, prune: bool = False,
             allow_fake: bool = False) -> list[str]:
    refuse_fake_embeddings(allow_fake)
    out: list[str] = []
    store = get_graph_store()
    with db_factory() as db:
        ready_ids = {str(c.id) for c in db.scalars(select(Chapter).where(Chapter.status == ChapterStatus.READY))}
        if rebuild:
            if store is None:
                raise SystemExit("GRAPH_STORE_PROVIDER is 'none': there is no graph-store copy to rebuild.")
            store.ensure_schema()
            store.clear()
            out.append("graph store cleared; writing every ready chapter again from PostgreSQL (stored vectors, no embedding calls)")
            query = select(Chapter).where(Chapter.status == ChapterStatus.READY)
            if chapter_id is not None:
                query = query.where(Chapter.id == chapter_id)
            elif book_id is not None:
                query = query.where(Chapter.book_id == book_id)
            targets = [c.id for c in db.scalars(query.order_by(Chapter.book_id, Chapter.sequence_num))]
        else:
            targets = [c.id for c in chapters_needing_index(db, book_id, chapter_id)]

        if prune and store is not None and not rebuild:
            stale = sorted(store.list_chapter_ids() - ready_ids)
            for cid in stale:
                store.delete_chapter(cid)
            out.append(f"pruned {len(stale)} chapter(s) that PostgreSQL no longer has as ready")

    failed = False
    for cid in targets:
        report = index_chapter(db_factory, cid, embed=not rebuild)
        failed = failed or bool(report.errors)
        with db_factory() as db:
            out.append(_describe(db, cid, report))
    out.append(f"{len(targets)} chapter(s) processed" + ("; some FAILED, run again after fixing the cause" if failed else ""))
    if store is not None:
        try:
            out.append("graph store now holds: " + ", ".join(f"{k} {v}" for k, v in store.stats().items()))
        except Exception as exc:
            out.append(f"(could not read graph-store stats: {exc})")
    if failed:
        out.append("!FAILED")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--book")
    parser.add_argument("--chapter")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--rebuild", action="store_true")
    parser.add_argument("--prune", action="store_true")
    parser.add_argument("--allow-fake", action="store_true", help="allow placeholder vectors (tests only)")
    a = parser.parse_args()
    if a.status:
        with SessionLocal() as db:
            print("\n".join(status_lines(db)))
        return
    lines = sync_all(
        SessionLocal, book_id=uuid.UUID(a.book) if a.book else None,
        chapter_id=uuid.UUID(a.chapter) if a.chapter else None,
        rebuild=a.rebuild, prune=a.prune, allow_fake=a.allow_fake,
    )
    print("\n".join(line for line in lines if line != "!FAILED"))
    if "!FAILED" in lines:
        sys.exit(1)


if __name__ == "__main__":
    main()
</file>

<file path="backend/app/db/try_doubt_photo.py">
"""See what a student's photographed (or typed) doubt would retrieve, on your real books. Writes nothing; the photo is not kept.

    python -m app.db.try_doubt_photo <photo.jpg|png|pdf> --book <id> [--book <id> ...] [--chapter <id>]
    python -m app.db.try_doubt_photo --text "why does ice float" --book <id>

The same OCR service as the front pages reads the photo. Prints the text read, how it is classified (too short /
a doubt / a whole page), and what retrieval returns: status, best similarity, matching pages, concepts and prerequisites.
`--chapter` narrows the search the way the assignment's Doubt button will."""
import argparse
import os
import uuid

from app.core.config import refuse_fake_embeddings, settings
from app.db.session import SessionLocal
from app.doubts.query import DOUBT, PAGE, RETAKE_MESSAGE, TOO_SHORT, classify_doubt_text
from app.doubts.retrieval import Scope, concepts_on_page, retrieve
from app.embeddings import get_embedding_provider
from app.graph_store import get_graph_store
from app.ocr import get_ocr_provider


def run(db, text: str, from_photo: bool, book_ids, chapter_ids, embedder, store) -> list[str]:
    q = classify_doubt_text(text, from_photo)
    out = [f"text read ({q.words} words): {' '.join(text.split())[:300]}{'...' if len(text) > 300 else ''}", f"classified as: {q.kind}"]
    if q.kind == TOO_SHORT:
        return out + [f"-> would tell the student: {RETAKE_MESSAGE}"]
    scope = Scope(chapter_ids={str(c) for c in chapter_ids}) if chapter_ids else None
    r = retrieve(db, q.text, embedder=embedder, store=store, book_ids=book_ids, scope=scope)
    out.append(f"retrieval: {r.status} (best similarity {r.confidence:.3f} in scope, {r.elsewhere_confidence:.3f} anywhere; cut-off {r.threshold})")
    for p in r.pages[:3]:
        out.append(f"  page {p.page_number} of '{p.chapter_title}' ({p.similarity:.3f}): {' '.join(p.text.split())[:100]}...")
    for c in r.concepts[:5]:
        out.append(f"  concept {c.name} ({c.similarity:.3f})")
    if r.prerequisites:
        out.append("  refresher (prerequisites): " + ", ".join(f"{p.name} (depth {p.depth})" for p in r.prerequisites[:6]))
    if q.kind == PAGE and r.pages:
        out.append("  whole page: the student would now pick the concept that confused them: "
                   + ", ".join(c.name for c in concepts_on_page(db, uuid.UUID(r.pages[0].page_id))))
    if r.status == "outside_assignment":
        out.append("  -> would offer the standalone Ask a Doubt: " + ", ".join(h.name for h in r.elsewhere))
    if r.status == "not_in_book":
        out.append("  -> would say: this isn't in your book yet, ask your teacher to add it")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("file", nargs="?")
    parser.add_argument("--text")
    parser.add_argument("--book", action="append", required=True)
    parser.add_argument("--chapter", action="append")
    parser.add_argument("--allow-fake", action="store_true")
    a = parser.parse_args()
    refuse_fake_embeddings(a.allow_fake)
    if not a.file and not a.text:
        raise SystemExit("Give a photo file or --text.")
    embedder, store = get_embedding_provider(), get_graph_store()
    if embedder is None or store is None:
        raise SystemExit("Set EMBEDDING_PROVIDER and GRAPH_STORE_PROVIDER first.")
    if a.file:
        with open(a.file, "rb") as fh:
            data = fh.read()
        text = get_ocr_provider().extract(data, os.path.splitext(a.file)[1].lstrip(".").lower()).text
    else:
        text = a.text
    with SessionLocal() as db:
        print("\n".join(run(db, text, bool(a.file), [uuid.UUID(b) for b in a.book], [uuid.UUID(c) for c in a.chapter or []], embedder, store)))
</file>

<file path="backend/app/db/try_front_pages.py">
"""See exactly what the front-page reader gets and says, without creating anything.

    python -m app.db.try_front_pages "C:/path/cover_and_publisher_pages.pdf"

Prints how much text the OCR found (and the start of it), the model's raw answer, the details that would fill the form,
and which books already in the library (official ones) the app would offer as a match for them.
Use it when the 'Add a book' form comes back empty: it shows whether the OCR text is missing or the model said nothing."""
import argparse
import uuid
from pathlib import Path
from types import SimpleNamespace

from app.llm import get_llm_provider
from app.ocr import get_ocr_provider
from app.pipeline.front_matter import SYSTEM, is_empty, parse_reply

EXT = {".pdf": "pdf", ".png": "png", ".jpg": "jpg", ".jpeg": "jpg"}


def run(path: str, ocr=None, llm=None, db_factory=None) -> list[str]:
    p = Path(path)
    ext = EXT.get(p.suffix.lower())
    if ext is None:
        return [f"Unsupported file type {p.suffix!r} (use pdf, png or jpg)."]
    layout = (ocr or get_ocr_provider()).extract_layout(p.read_bytes(), ext)
    text = "\n".join(pg["text"] for pg in layout["pages"]).strip()
    out = [f"OCR: {len(layout['pages'])} page(s), {len(text)} characters of text", "--- start of the text the model receives ---", text[:1500] or "(nothing)", "--- end ---"]
    if len(text) < 10:
        return out + ["The app would stop here with 'No readable text was found on these pages'."]
    raw = (llm or get_llm_provider()).complete_json(SYSTEM, f"FRONT PAGES TEXT:\n{text[:6000]}")
    out += ["model's raw answer:", raw.strip()]
    try:
        m = parse_reply(raw)
        out += ["parsed: " + str(m.model_dump()), "RESULT: nothing was found (the form would be empty)" if is_empty(m) else "RESULT: the form would be filled with the details above"]
        if db_factory is not None and not is_empty(m):
            from app.content_library.search import match_metadata
            with db_factory() as db:
                found = match_metadata(db, SimpleNamespace(id=uuid.uuid4()), m)  # a stranger: sees official books only
                names = [f"{b.publisher} {b.class_name} {b.subject} (edition {b.edition or '-'})" for b in found]
            out.append("library match: " + ("; ".join(names) if names else "none (no official book agrees on class, subject and publisher)"))
    except Exception as exc:
        out.append(f"RESULT: the answer could not be parsed ({exc})")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("file")
    from app.db.session import SessionLocal
    print("\n".join(run(parser.parse_args().file, db_factory=SessionLocal)))
</file>

<file path="backend/app/doubts/__init__.py">

</file>

<file path="backend/app/doubts/calibration.py">
"""Measuring the "not in your book" cut-off instead of guessing it (same idea as pipeline/embedprobe.py for Layer 4).

Three groups of questions are run through the real retrieval path:
  in_book        a student-style doubt written by the model about a real page of the books (must be answered)
  off_topic      questions about things no school book here covers (must be refused)
  wrong_chapter  the same doubts, asked INSIDE the scope of a different chapter (must come back `outside_assignment`)
A cut-off is only trustworthy if it sits in the gap between `in_book` and `off_topic`."""
import json
import math
import re
import statistics
import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.doubts.retrieval import GROUNDED, OUTSIDE, Scope, retrieve
from app.models.content import Chapter, ChapterStatus, Concept, Page, PageKind
from app.pipeline.fingerprint import tokenize

OFF_TOPIC = [
    "Who won the cricket world cup last time?",
    "How do I install Python on my laptop?",
    "What is the capital of Australia?",
    "How do I make a cup of tea?",
    "Explain how GST is calculated on a restaurant bill",
    "Which phone should I buy for gaming?",
    "What is the plot of the movie Titanic?",
    "How do I improve my handwriting?",
    "What is the price of gold today?",
    "Tell me a joke about teachers",
]

SYSTEM = (
    "You are a school student reading one textbook page. Write ONE question you might ask your tutor about the main "
    "idea of this page, in your own everyday words, 8 to 25 words, as a confused student would. Do not copy any run of "
    "three or more words from the page. Reply with JSON only: {\"doubt\": \"<your question>\"}."
)


def write_doubt(llm, page_text: str) -> Optional[str]:
    try:
        raw = llm.complete_json(SYSTEM, "STUDENT DOUBT\nPAGE:\n" + page_text[: settings.concept_max_chars])
        doubt = json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())).get("doubt")
        return doubt.strip() if isinstance(doubt, str) and doubt.strip() else None
    except Exception:
        return None


def percentile_low(values: list[float], share: float = 0.10) -> float:
    """Nearest-rank low percentile (the value 90% of the group is at or above)."""
    ordered = sorted(values)
    return ordered[max(0, math.ceil(share * len(ordered)) - 1)]


def summarize(in_book: list[float], off_topic: list[float], wrong_chapter: list[float], threshold: float) -> dict:
    """Pure function of the measured similarities (testable without any service)."""
    low_in, high_off = percentile_low(in_book), max(off_topic)
    separable = low_in > high_off
    return {
        "in_book_min": min(in_book), "in_book_p10": low_in, "in_book_median": statistics.median(in_book),
        "off_topic_max": high_off, "off_topic_median": statistics.median(off_topic),
        "wrong_chapter_scoped_max": max(wrong_chapter) if wrong_chapter else None,
        "threshold": threshold,
        "answered_in_book": sum(1 for s in in_book if s >= threshold) / len(in_book),
        "wrongly_answered_off_topic": sum(1 for s in off_topic if s >= threshold) / len(off_topic),
        "separable": separable,
        "recommended": round((low_in + high_off) / 2, 2) if separable else None,
        "pass": separable
                and sum(1 for s in in_book if s >= threshold) / len(in_book) >= 0.9
                and all(s < threshold for s in off_topic),
    }


def probe(db: Session, llm, embedder, store, book_ids: list[uuid.UUID], pages: int = 12) -> dict:
    chapters = list(db.scalars(select(Chapter).where(Chapter.book_id.in_(book_ids), Chapter.status == ChapterStatus.READY)
                               .order_by(Chapter.book_id, Chapter.sequence_num)))
    candidates = []
    for ch in chapters:
        for p in db.scalars(select(Page).where(Page.chapter_id == ch.id, Page.page_kind == PageKind.CONTENT).order_by(Page.page_number)):
            if len(tokenize(p.content_text)) >= settings.fingerprint_min_words and db.scalar(select(Concept.id).where(Concept.page_id == p.id).limit(1)):
                candidates.append((ch, p))
    if len(candidates) < 4 or len(chapters) < 1:
        return {"status": "not_enough_pages", "pages_available": len(candidates)}
    step = max(1, len(candidates) // pages)
    picked = candidates[::step][:pages]

    in_book, wrong, right_chapter, outside_hits = [], [], 0, 0
    for ch, page in picked:
        doubt = write_doubt(llm, page.content_text)
        if not doubt:
            continue
        r = retrieve(db, doubt, embedder=embedder, store=store, book_ids=book_ids, threshold=0.0)
        in_book.append(r.confidence)
        right_chapter += 1 if r.pages and r.pages[0].chapter_id == str(ch.id) else 0
        others = [c for c in chapters if c.id != ch.id]
        if others:
            scoped = retrieve(db, doubt, embedder=embedder, store=store, book_ids=book_ids,
                              scope=Scope(chapter_ids={str(others[0].id)}), threshold=settings.retrieval_min_similarity)
            wrong.append(scoped.confidence)
            outside_hits += 1 if scoped.status == OUTSIDE else 0
    off = [retrieve(db, q, embedder=embedder, store=store, book_ids=book_ids, threshold=0.0).confidence for q in OFF_TOPIC]
    if len(in_book) < 3:
        return {"status": "doubt_writing_failed", "written": len(in_book), "asked": len(picked)}
    summary = summarize(in_book, off, wrong, settings.retrieval_min_similarity)
    summary.update({
        "status": "done", "doubts": len(in_book), "right_chapter_top_hit": right_chapter / len(in_book),
        "wrong_chapter_outside": (outside_hits / len(wrong)) if wrong else None, "in_book_values": sorted(round(v, 3) for v in in_book),
        "off_topic_values": sorted(round(v, 3) for v in off),
    })
    return summary
</file>

<file path="backend/app/doubts/query.py">
"""Turning what the student sent (typed text, or the OCR text of a photo) into something searchable.

Decided in Phase 3 (see Phases.md "Settled before building"): the photo is read by the same OCR service as front pages
and is NOT stored. By length of the text read:
  < PHOTO_MIN_WORDS      too_short -> "retake the photo" (a bad scan would only retrieve noise)
  < PHOTO_PAGE_WORDS     doubt     -> the text IS the doubt, searched as it is
  >= PHOTO_PAGE_WORDS    page      -> a whole page: matched to its page in the book, then the student picks the concept
                                      that confused them (searching a whole page as a "question" is meaningless)
Typed text is never "too short" (a single word is a legitimate doubt); only an empty message is. It can still be a page."""
from dataclasses import dataclass

from app.core.config import settings
from app.pipeline.fingerprint import tokenize

TOO_SHORT, DOUBT, PAGE = "too_short", "doubt", "page"


@dataclass
class DoubtInput:
    kind: str
    words: int
    text: str  # cleaned text to search with (empty when too_short)


def classify_doubt_text(text: str, from_photo: bool = False) -> DoubtInput:
    clean = " ".join((text or "").split())
    words = len(tokenize(clean))
    if words == 0 or (from_photo and words < settings.photo_min_words):
        return DoubtInput(TOO_SHORT, words, "")
    if words >= settings.photo_page_words:
        return DoubtInput(PAGE, words, clean)
    return DoubtInput(DOUBT, words, clean)


RETAKE_MESSAGE = "We couldn't read enough of that photo. Please retake it in good light, with the page flat and filling the frame."
</file>

<file path="backend/app/doubts/retrieval.py">
"""Retrieval for a doubt: the part of Phase 3 that decides WHAT the Tutor may answer from. It never writes an answer.

    doubt text -> vector -> graph-store search restricted to the student's linked books (never "everything")
               -> optional narrowing to the assignment's chapters / concepts
               -> the best pages (their text is read from PostgreSQL, the source of truth) and concepts
               -> prerequisites of the best concepts by walking the graph (the refresher)

`status` says what the caller may do:
  grounded            enough evidence inside the scope: the Tutor may answer from `pages` / `concepts`
  outside_assignment  nothing good inside the assignment, but the student's books do cover it: offer standalone "Ask a Doubt"
  not_in_book         nothing good anywhere in the linked books: "ask your teacher to add it" (Rules.md §4: no ungrounded answer)
  unavailable         the embedding service or graph store failed: say "couldn't do this right now", never guess

Tenancy: the books are re-checked in PostgreSQL after the search (a page is returned only if its chapter is ready and
belongs to one of `book_ids`), so a wrong answer from the store can never leak another teacher's text."""
import logging
import uuid
from dataclasses import dataclass, field
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.embeddings import EmbeddingError
from app.graph_store.base import ConceptHit, GraphStoreError, PageHit, PrerequisiteRow
from app.models.content import Chapter, ChapterStatus, Concept, Page

logger = logging.getLogger(__name__)

GROUNDED, OUTSIDE, NOT_IN_BOOK, UNAVAILABLE = "grounded", "outside_assignment", "not_in_book", "unavailable"


@dataclass
class Scope:
    """What an assignment covers. Chapter / subject level: `chapter_ids` only (a hit is inside if its chapter is). Concept
    or exercise level: also `concept_ids` and `page_ids` (the pages those concepts are explained on), which narrow it
    below the chapter, so a doubt about ANOTHER concept of the same chapter is `outside_assignment` too.
    Empty scope = nothing is inside it. Build one from concepts with `scope_for_concepts`."""
    chapter_ids: set[str] = field(default_factory=set)
    concept_ids: set[str] = field(default_factory=set)
    page_ids: set[str] = field(default_factory=set)

    def has_concept(self, concept_id: str, chapter_id: str) -> bool:
        return concept_id in self.concept_ids or (not self.concept_ids and chapter_id in self.chapter_ids)

    def has_page(self, page_id: str, chapter_id: str) -> bool:
        return page_id in self.page_ids if self.page_ids else chapter_id in self.chapter_ids


def scope_for_concepts(db: Session, concepts: Sequence[Concept]) -> Scope:
    """The scope of a concept- or exercise-level assignment: those concepts, the pages they are explained on (the page
    that holds them and any page of the same chapter where the same idea recurs), and their chapters."""
    scope = Scope()
    wanted: dict[uuid.UUID, set[str]] = {}
    for c in concepts:
        page = db.get(Page, c.page_id)
        scope.concept_ids.add(str(c.id))
        scope.chapter_ids.add(str(page.chapter_id))
        scope.page_ids.add(str(page.id))
        if c.name_key:
            wanted.setdefault(page.chapter_id, set()).add(c.name_key)
    for chapter_id, keys in wanted.items():  # the same idea repeated on a later page is explained there too
        rows = db.execute(select(Concept.page_id).join(Page, Page.id == Concept.page_id)
                          .where(Page.chapter_id == chapter_id, Concept.name_key.in_(keys))).all()
        scope.page_ids.update(str(r[0]) for r in rows)
    return scope


@dataclass
class RetrievedPage:
    page_id: str
    page_number: int
    chapter_id: str
    chapter_title: str
    book_id: str
    similarity: float
    text: str


@dataclass
class RetrievalResult:
    status: str
    confidence: float = 0.0              # best similarity inside the scope (the whole books when there is no scope)
    elsewhere_confidence: float = 0.0    # best similarity anywhere in the linked books (what "outside_assignment" is judged on)
    threshold: float = 0.0
    pages: list[RetrievedPage] = field(default_factory=list)
    concepts: list[ConceptHit] = field(default_factory=list)
    prerequisites: list[PrerequisiteRow] = field(default_factory=list)  # refresher, nearest first, without the hits themselves
    elsewhere: list[ConceptHit] = field(default_factory=list)  # for outside_assignment: where the books do cover it


def retrieve(db: Session, text: str, *, embedder, store, book_ids: Sequence[uuid.UUID], scope: Optional[Scope] = None,
             threshold: Optional[float] = None, k: Optional[int] = None) -> RetrievalResult:
    threshold = settings.retrieval_min_similarity if threshold is None else threshold
    k = k or settings.retrieval_candidates
    result = RetrievalResult(NOT_IN_BOOK, threshold=threshold)
    ids = [str(b) for b in book_ids]
    if not ids or not (text or "").strip():
        return result  # no linked books (or nothing asked): never "search everything"
    if store is None or embedder is None:
        return RetrievalResult(UNAVAILABLE, threshold=threshold)

    try:
        vector = embedder.embed([text.strip()[: settings.embedding_max_chars]])[0]
        window = k * (settings.retrieval_scope_overfetch if scope else 1)
        concept_hits = store.search_concepts(vector, ids, k=window)
        page_hits = store.search_pages(vector, ids, k=window)
    except (EmbeddingError, GraphStoreError):
        logger.warning("Retrieval failed", exc_info=True)
        return RetrievalResult(UNAVAILABLE, threshold=threshold)

    result.elsewhere_confidence = max([h.similarity for h in concept_hits + page_hits], default=0.0)
    if scope is not None:
        inside_concepts = [h for h in concept_hits if scope.has_concept(h.concept_id, h.chapter_id)]
        inside_pages = [h for h in page_hits if scope.has_page(h.page_id, h.chapter_id)]
    else:
        inside_concepts, inside_pages = concept_hits, page_hits
    inside_concepts, inside_pages = inside_concepts[:k], inside_pages[:k]
    result.confidence = max([h.similarity for h in inside_concepts + inside_pages], default=0.0)

    if result.confidence >= threshold:
        result.status = GROUNDED
        result.concepts = [h for h in inside_concepts if h.similarity >= threshold]
        result.pages = _load_pages(db, [h for h in inside_pages if h.similarity >= threshold], set(ids))
        result.prerequisites = _refresher(store, result.concepts, ids)
        if not result.pages and not result.concepts:  # the store named hits PostgreSQL does not stand behind
            result.status = NOT_IN_BOOK
    elif scope is not None and result.elsewhere_confidence >= threshold:
        result.status = OUTSIDE
        result.elsewhere = [h for h in concept_hits if h.similarity >= threshold][:3]
    return result


def _load_pages(db: Session, hits: list[PageHit], book_ids: set[str]) -> list[RetrievedPage]:
    """Page text comes from PostgreSQL, and only for ready chapters of the allowed books."""
    if not hits:
        return []
    by_id = {uuid.UUID(h.page_id): h for h in hits}
    rows = db.execute(
        select(Page, Chapter).join(Chapter, Chapter.id == Page.chapter_id)
        .where(Page.id.in_(list(by_id)), Chapter.status == ChapterStatus.READY)
    ).all()
    loaded = [
        RetrievedPage(str(p.id), p.page_number, str(c.id), c.title or "", str(c.book_id), by_id[p.id].similarity, p.content_text)
        for p, c in rows if str(c.book_id) in book_ids
    ]
    return sorted(loaded, key=lambda r: -r.similarity)


def _refresher(store, concepts: list[ConceptHit], book_ids: list[str]) -> list[PrerequisiteRow]:
    """Prerequisites of the best 3 concepts, nearest first, each once, never a concept that is itself a hit."""
    hit_ids = {c.concept_id for c in concepts}
    seen: dict[str, PrerequisiteRow] = {}
    try:
        for hit in concepts[:3]:
            for row in store.prerequisites(hit.concept_id, book_ids, max_depth=settings.retrieval_prereq_depth):
                if row.concept_id not in hit_ids and (row.concept_id not in seen or row.depth < seen[row.concept_id].depth):
                    seen[row.concept_id] = row
    except GraphStoreError:
        logger.warning("Prerequisite lookup failed; answering without a refresher", exc_info=True)
    return sorted(seen.values(), key=lambda r: (r.depth, r.name))


def concepts_on_page(db: Session, page_id: uuid.UUID) -> list[Concept]:
    """For a photographed whole page: the concepts the student can pick from."""
    return list(db.scalars(select(Concept).where(Concept.page_id == page_id, Concept.is_canonical.is_(True)).order_by(Concept.position)))
</file>

<file path="backend/app/embeddings/__init__.py">
from typing import Optional

from app.core.config import settings

from .base import EmbeddingError, EmbeddingProvider
from .fake_provider import FakeEmbeddingProvider


def get_embedding_provider() -> Optional[EmbeddingProvider]:
    """None means embeddings are switched off (EMBEDDING_PROVIDER=none): the pipeline skips them."""
    kind = settings.embedding_provider.lower()
    if kind == "openai_compat":
        api_key = settings.embedding_api_key or settings.llm_api_key  # same Azure resource by default
        base_url = settings.embedding_base_url or settings.llm_base_url
        if not api_key or not settings.embedding_model:
            raise RuntimeError(
                "Embeddings are not configured. Set EMBEDDING_MODEL (your Azure deployment name) and either "
                "EMBEDDING_API_KEY / EMBEDDING_BASE_URL or the LLM_* ones (used when the EMBEDDING_* ones are blank)."
            )
        from .openai_compat_provider import OpenAICompatEmbeddingProvider

        return OpenAICompatEmbeddingProvider(
            base_url, api_key, settings.embedding_model, settings.embedding_dim,
            batch_size=settings.embedding_batch_size, timeout_s=settings.embedding_timeout_s,
            send_dimensions=settings.embedding_send_dimensions,
        )
    if kind == "fake":
        return FakeEmbeddingProvider(settings.embedding_dim)
    return None


__all__ = ["EmbeddingError", "EmbeddingProvider", "get_embedding_provider"]
</file>

<file path="backend/app/embeddings/base.py">
from typing import Protocol


class EmbeddingError(Exception):
    """An embedding call failed or returned something unusable. The message is for logs, not for users:
    embeddings are derived data, so nothing here is ever shown to a teacher or student."""


class EmbeddingProvider(Protocol):
    model_name: str  # recorded next to every vector; vectors of different models are never mixed
    dim: int

    def embed(self, texts: list[str]) -> list[list[float]]:
        """One vector per text, in the same order, each of length `dim`. Texts must be non-empty."""
        ...
</file>

<file path="backend/app/embeddings/fake_provider.py">
import hashlib
import math

from app.core.config import FAKE_EMBEDDING_MODEL
from app.pipeline.fingerprint import tokenize


class FakeEmbeddingProvider:
    """Deterministic stand-in for tests and keyless local dev: words (and word pairs) are hashed into the
    vector, so texts that share words have a higher cosine similarity. Placeholder vectors, not real meaning:
    scripts refuse it unless --allow-fake, and a real run never reuses them (the model name differs)."""

    model_name = FAKE_EMBEDDING_MODEL

    def __init__(self, dim: int):
        self.dim = dim
        self.calls = 0  # how many embed() calls were made (tests assert on this)
        self.texts_embedded = 0

    def embed(self, texts: list[str]) -> list[list[float]]:
        self.calls += 1
        self.texts_embedded += len(texts)
        return [self._one(t) for t in texts]

    def _one(self, text: str) -> list[float]:
        vector = [0.0] * self.dim
        tokens = tokenize(text) or ["<empty>"]
        features = tokens + [f"{a} {b}" for a, b in zip(tokens, tokens[1:])]
        for feature in features:
            digest = hashlib.blake2b(feature.encode("utf8"), digest_size=8).digest()
            index = int.from_bytes(digest[:4], "big") % self.dim
            vector[index] += 1.0 if digest[4] & 1 else -1.0
        norm = math.sqrt(sum(x * x for x in vector)) or 1.0
        return [x / norm for x in vector]
</file>

<file path="backend/app/embeddings/openai_compat_provider.py">
import logging

from openai import OpenAI

from app.embeddings.base import EmbeddingError

logger = logging.getLogger(__name__)


class OpenAICompatEmbeddingProvider:
    """Any OpenAI-compatible embeddings endpoint: OpenAI, or Azure OpenAI / Foundry via its /openai/v1/ base URL.
    On Azure, `model` is your embedding DEPLOYMENT name (e.g. one that serves text-embedding-3-small)."""

    def __init__(self, base_url: str, api_key: str, model: str, dim: int, *, batch_size: int = 32,
                 timeout_s: int = 60, send_dimensions: bool = False, client=None):
        self.model_name = model
        self.dim = dim
        self._batch_size = max(1, batch_size)
        self._send_dimensions = send_dimensions
        self._client = client or OpenAI(base_url=base_url or None, api_key=api_key, timeout=timeout_s, max_retries=2)

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for start in range(0, len(texts), self._batch_size):
            batch = texts[start:start + self._batch_size]
            extra = {"dimensions": self.dim} if self._send_dimensions else {}
            try:
                response = self._client.embeddings.create(model=self.model_name, input=batch, **extra)
            except Exception as exc:  # network, auth, quota, unknown deployment
                logger.exception("Embedding call failed")
                raise EmbeddingError("The embedding service couldn't be reached.") from exc
            items = sorted(response.data, key=lambda item: item.index)
            if len(items) != len(batch):
                raise EmbeddingError(f"Asked for {len(batch)} embeddings, got {len(items)}.")
            for item in items:
                if len(item.embedding) != self.dim:
                    raise EmbeddingError(
                        f"The model returned {len(item.embedding)}-number vectors but EMBEDDING_DIM is {self.dim}. "
                        "Set EMBEDDING_DIM to the model's size (1536 for text-embedding-3-small)."
                    )
                vectors.append(list(item.embedding))
        return vectors
</file>

<file path="backend/app/embeddings/vectors.py">
"""Vector storage helpers. PostgreSQL keeps each vector as raw float32 bytes (no pgvector extension needed:
similarity search happens in Memgraph; PostgreSQL is only the durable copy)."""
import numpy as np


def to_bytes(vector) -> bytes:
    return np.asarray(vector, dtype="<f4").tobytes()


def from_bytes(data: bytes) -> list[float]:
    return np.frombuffer(data, dtype="<f4").astype(float).tolist()


def cosine(a, b) -> float:
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.dot(a, b) / denominator) if denominator else 0.0
</file>

<file path="backend/app/graph_store/__init__.py">
import threading
from typing import Optional

from app.core.config import settings

from .base import GraphStore, GraphStoreError
from .fake_store import FakeGraphStore

FAKE_STORE = FakeGraphStore()  # one per process, like a real server (tests clear it between runs)
_cache: dict = {}
_lock = threading.Lock()


def get_graph_store() -> Optional[GraphStore]:
    """None means the graph store is switched off (GRAPH_STORE_PROVIDER=none): the pipeline skips that stage.
    The Memgraph store is cached per process (its driver pools connections and is thread-safe)."""
    kind = settings.graph_store_provider.lower()
    if kind == "fake":
        return FAKE_STORE
    if kind == "memgraph":
        key = (
            settings.memgraph_uri, settings.memgraph_user, settings.memgraph_password, settings.embedding_dim,
            settings.memgraph_vector_capacity, settings.memgraph_vector_metric,
        )
        with _lock:
            if key not in _cache:
                from .memgraph_store import MemgraphStore  # imported late: the driver is only needed when used

                _cache[key] = MemgraphStore(
                    settings.memgraph_uri, settings.memgraph_user, settings.memgraph_password,
                    dim=settings.embedding_dim, capacity=settings.memgraph_vector_capacity,
                    metric=settings.memgraph_vector_metric, batch=settings.graph_sync_batch,
                    max_candidates=settings.graph_search_max_candidates,
                )
            return _cache[key]
    return None


def close_graph_stores() -> None:
    with _lock:
        for store in _cache.values():
            store.close()
        _cache.clear()


__all__ = ["FAKE_STORE", "GraphStore", "GraphStoreError", "close_graph_stores", "get_graph_store"]
</file>

<file path="backend/app/graph_store/base.py">
"""What a graph store must offer, plus the plain-data shapes it exchanges with the pipeline.

Rules every store follows:
  * PostgreSQL is the source of truth. A store only holds a rebuildable COPY, written per chapter and replaced
    as a whole (`replace_chapter`), so writing the same chapter twice gives the same result.
  * No page text goes into a store: only ids, page numbers, concept names/descriptions and vectors.
  * Every search takes `book_ids` and returns only nodes of those books. An empty list returns nothing, never
    "everything". The caller (the Tutor, in Phase 3) passes the books the student is linked to.
"""
from dataclasses import dataclass, field
from typing import Optional, Protocol, Sequence


class GraphStoreError(Exception):
    """The graph store failed or is unreachable. The message is for logs and the sync report, not for users."""


@dataclass
class PageNode:
    id: str
    page_number: int
    embedding: Optional[list[float]] = None


@dataclass
class ConceptNode:
    id: str
    name: str
    description: str
    position: int
    embedding: Optional[list[float]] = None


@dataclass
class EdgeRow:
    concept_id: str       # the concept that needs...
    prerequisite_id: str  # ...this one first
    source: str           # "page" | "llm"


@dataclass
class ChapterGraph:
    book_id: str
    chapter_id: str
    title: str
    sequence_num: int
    is_reference: bool
    owner_teacher_id: Optional[str]
    embedding_model: Optional[str]
    pages: list[PageNode] = field(default_factory=list)
    concepts: list[ConceptNode] = field(default_factory=list)  # canonical concepts only
    edges: list[EdgeRow] = field(default_factory=list)
    concept_pages: list[tuple[str, str]] = field(default_factory=list)  # (concept id, page id) it is explained on


@dataclass
class ConceptHit:
    concept_id: str
    name: str
    description: str
    chapter_id: str
    book_id: str
    similarity: float


@dataclass
class PageHit:
    page_id: str
    page_number: int
    chapter_id: str
    book_id: str
    similarity: float


@dataclass
class PrerequisiteRow:
    concept_id: str
    name: str
    depth: int  # 1 = direct prerequisite


class GraphStore(Protocol):
    def ensure_schema(self) -> None:
        """Create indexes (idempotent). Raises GraphStoreError if a vector index has a different dimension."""

    def replace_chapter(self, graph: ChapterGraph) -> None:
        """Delete everything stored for the chapter and write `graph`, atomically."""

    def replace_cross_edges(self, book_id: str, edges: Sequence["EdgeRow"]) -> None:
        """Replace every cross-chapter prerequisite edge of the book (REQUIRES with source "book"). Replacing a
        chapter removes its edges to other chapters, so this is called again after each chapter write."""

    def delete_chapter(self, chapter_id: str) -> None: ...

    def list_chapter_ids(self) -> set[str]: ...

    def clear(self) -> None:
        """Remove everything this app wrote (used by a full rebuild)."""

    def search_concepts(self, vector: Sequence[float], book_ids: Sequence[str], k: int = 5) -> list[ConceptHit]: ...

    def search_pages(self, vector: Sequence[float], book_ids: Sequence[str], k: int = 5) -> list[PageHit]: ...

    def prerequisites(self, concept_id: str, book_ids: Sequence[str], max_depth: int = 5) -> list[PrerequisiteRow]:
        """Everything the concept needs, nearest first (breadth of the prerequisite graph)."""

    def stats(self) -> dict: ...

    def close(self) -> None: ...
</file>

<file path="backend/app/graph_store/fake_store.py">
import threading
from collections import deque
from typing import Sequence

from app.embeddings.vectors import cosine
from app.graph_store.base import (
    ChapterGraph, ConceptHit, GraphStoreError, PageHit, PrerequisiteRow,
)


class FakeGraphStore:
    """In-memory store with the same behaviour as the Memgraph one (replace-per-chapter, tenant-filtered
    search), for tests and for running the pipeline without Docker. Process-wide singleton: see factory."""

    def __init__(self):
        self._chapters: dict[str, ChapterGraph] = {}
        self._cross: dict[str, list] = {}  # book id -> cross-chapter EdgeRows
        self._lock = threading.Lock()
        self.fail_with: Exception | None = None  # tests set this to simulate an outage
        self.replace_calls = 0

    def _check(self):
        if self.fail_with is not None:
            raise GraphStoreError("simulated graph store outage") from self.fail_with

    def ensure_schema(self) -> None:
        self._check()

    def replace_chapter(self, graph: ChapterGraph) -> None:
        self._check()
        with self._lock:
            self.replace_calls += 1
            self._chapters[graph.chapter_id] = graph

    def replace_cross_edges(self, book_id: str, edges) -> None:
        self._check()
        with self._lock:
            self._cross[book_id] = list(edges)

    def cross_edges(self, book_id: str) -> list:  # test helper
        return list(self._cross.get(book_id, []))

    def delete_chapter(self, chapter_id: str) -> None:
        self._check()
        with self._lock:
            self._chapters.pop(chapter_id, None)

    def list_chapter_ids(self) -> set[str]:
        self._check()
        return set(self._chapters)

    def clear(self) -> None:
        self._check()
        with self._lock:
            self._chapters.clear()
            self._cross.clear()

    def chapter(self, chapter_id: str) -> ChapterGraph | None:  # test helper
        return self._chapters.get(chapter_id)

    def search_concepts(self, vector: Sequence[float], book_ids: Sequence[str], k: int = 5) -> list[ConceptHit]:
        self._check()
        allowed = set(book_ids)
        hits = [
            ConceptHit(c.id, c.name, c.description, g.chapter_id, g.book_id, cosine(vector, c.embedding))
            for g in self._chapters.values() if g.book_id in allowed
            for c in g.concepts if c.embedding is not None
        ]
        return sorted(hits, key=lambda h: -h.similarity)[:k]

    def search_pages(self, vector: Sequence[float], book_ids: Sequence[str], k: int = 5) -> list[PageHit]:
        self._check()
        allowed = set(book_ids)
        hits = [
            PageHit(p.id, p.page_number, g.chapter_id, g.book_id, cosine(vector, p.embedding))
            for g in self._chapters.values() if g.book_id in allowed
            for p in g.pages if p.embedding is not None
        ]
        return sorted(hits, key=lambda h: -h.similarity)[:k]

    def prerequisites(self, concept_id: str, book_ids: Sequence[str], max_depth: int = 5) -> list[PrerequisiteRow]:
        self._check()
        allowed = set(book_ids)
        for g in self._chapters.values():
            if g.book_id not in allowed or concept_id not in {c.id for c in g.concepts}:
                continue
            names = {c.id: c.name for other in self._chapters.values() if other.book_id == g.book_id for c in other.concepts}
            needs: dict[str, list[str]] = {}
            for e in [*g.edges, *self._cross.get(g.book_id, [])]:
                needs.setdefault(e.concept_id, []).append(e.prerequisite_id)
            depth_of: dict[str, int] = {}
            queue = deque([(concept_id, 0)])
            while queue:
                node, depth = queue.popleft()
                if depth >= max_depth:
                    continue
                for prerequisite in needs.get(node, []):
                    if prerequisite not in depth_of and prerequisite != concept_id:
                        depth_of[prerequisite] = depth + 1
                        queue.append((prerequisite, depth + 1))
            rows = [PrerequisiteRow(i, names[i], d) for i, d in depth_of.items()]
            return sorted(rows, key=lambda r: (r.depth, r.name))
        return []

    def stats(self) -> dict:
        self._check()
        graphs = list(self._chapters.values())
        return {
            "Chapter": len(graphs),
            "Page": sum(len(g.pages) for g in graphs),
            "Concept": sum(len(g.concepts) for g in graphs),
            "REQUIRES": sum(len(g.edges) for g in graphs) + sum(len(v) for v in self._cross.values()),
        }

    def close(self) -> None:
        pass
</file>

<file path="backend/app/graph_store/memgraph_store.py">
"""Memgraph implementation of the GraphStore (Bolt, via the `neo4j` driver).

Graph written per chapter:

    (:Chapter {id, book_id, title, sequence_num, is_reference, owner_teacher_id})
    (:Page    {id, chapter_id, book_id, page_number, embedding, embedding_model})
    (:Concept {id, chapter_id, book_id, name, description, position, embedding, embedding_model})
    (Concept)-[:REQUIRES {source}]->(Concept)   # "needs this first": the prerequisite graph, a DAG
    (Concept)-[:EXPLAINED_ON]->(Page)           # every page the concept is on
    (Page)-[:IN_CHAPTER]->(Chapter), (Concept)-[:IN_CHAPTER]->(Chapter)

Vector indexes: concept_embedding_idx on :Concept(embedding) and page_embedding_idx on :Page(embedding).
Nothing here is the source of truth: `python -m app.db.sync_graph --rebuild` recreates all of it from PostgreSQL.
"""
import logging
import re
import time
from contextlib import contextmanager
from typing import Iterable, Optional, Sequence

from neo4j import GraphDatabase

from app.graph_store.base import (
    ChapterGraph, ConceptHit, GraphStoreError, PageHit, PrerequisiteRow,
)

logger = logging.getLogger(__name__)

CONCEPT_INDEX = "concept_embedding_idx"
PAGE_INDEX = "page_embedding_idx"
LABEL_INDEXES = (("Chapter", "id"), ("Page", "id"), ("Page", "chapter_id"), ("Concept", "id"), ("Concept", "chapter_id"))
_SAFE_WORD = re.compile(r"^[a-z0-9_]+$")


def _chunks(rows: list, size: int) -> Iterable[list]:
    for start in range(0, len(rows), max(1, size)):
        yield rows[start:start + size]


class MemgraphStore:
    def __init__(self, uri: str, user: str = "", password: str = "", *, dim: int, capacity: int = 20000,
                 metric: str = "cos", batch: int = 200, max_candidates: int = 2000, driver=None):
        if not isinstance(dim, int) or dim <= 0:
            raise ValueError("dim must be a positive integer")
        if not _SAFE_WORD.match(metric):
            raise ValueError("unsupported vector metric")
        self.dim, self.capacity, self.metric = dim, int(capacity), metric
        self._batch, self._max_candidates = batch, max_candidates
        self._uri, self._auth = uri, ((user, password) if user else None)
        self._driver = driver  # tests inject a stub; otherwise created on first use
        self._schema_ready = False

    # ---- plumbing -----------------------------------------------------------------------------
    @property
    def driver(self):
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                self._uri, auth=self._auth, connection_timeout=10, max_transaction_retry_time=10,
            )
        return self._driver

    @contextmanager
    def _guard(self, what: str):
        try:
            yield
        except GraphStoreError:
            raise
        except Exception as exc:  # connection refused, auth, syntax on an old server, ...
            logger.exception("Memgraph: %s failed", what)
            raise GraphStoreError(f"Memgraph {what} failed: {type(exc).__name__}: {str(exc)[:200]}") from exc

    def close(self) -> None:
        if self._driver is not None:
            self._driver.close()
            self._driver = None
            self._schema_ready = False

    def _read(self, query: str, **params) -> list[dict]:
        def work(tx):
            return [record.data() for record in tx.run(query, **params)]

        with self.driver.session() as session:
            return session.execute_read(work)

    def run_admin(self, statement: str) -> list[dict]:
        """Run a SHOW ... / admin statement in an auto-commit session. Memgraph refuses these inside the explicit
        transaction that session.execute_read opens, which is why `_read("SHOW VERSION")` raised ClientError."""
        with self.driver.session() as session:
            return session.run(statement).data()

    # ---- schema -------------------------------------------------------------------------------
    @staticmethod
    def _ddl(session, statement: str) -> None:
        try:
            session.run(statement).consume()
        except Exception as exc:
            if "already exist" in str(exc).lower():  # idempotent: the index is there
                return
            raise

    def ensure_schema(self) -> None:
        if self._schema_ready:
            return
        with self._guard("schema setup"):
            with self.driver.session() as session:
                for label, prop in LABEL_INDEXES:
                    self._ddl(session, f"CREATE INDEX ON :{label}({prop})")
                for name, label in ((CONCEPT_INDEX, "Concept"), (PAGE_INDEX, "Page")):
                    self._ddl(
                        session,
                        f"CREATE VECTOR INDEX {name} ON :{label}(embedding) WITH CONFIG "
                        f'{{"dimension": {self.dim}, "capacity": {self.capacity}, "metric": "{self.metric}"}}',
                    )
                self._check_dimensions(session)
        self._schema_ready = True

    def _check_dimensions(self, session) -> None:
        try:
            rows = session.run("SHOW VECTOR INDEX INFO").data()
        except Exception:  # an older/odd server: creation above already proved vector indexes exist
            logger.warning("Memgraph: could not read SHOW VECTOR INDEX INFO; skipping the dimension check")
            return
        for row in rows:
            name = row.get("index_name") or row.get("name")
            found = row.get("dimension")
            if name in (CONCEPT_INDEX, PAGE_INDEX) and found is not None and int(found) != self.dim:
                raise GraphStoreError(
                    f"Memgraph index {name} has dimension {found} but EMBEDDING_DIM is {self.dim}. Drop the "
                    f"vector indexes (DROP VECTOR INDEX {name}) and run `python -m app.db.sync_graph --rebuild`."
                )

    # ---- writing ------------------------------------------------------------------------------
    def replace_chapter(self, graph: ChapterGraph) -> None:
        self.ensure_schema()
        cid, bid, model = graph.chapter_id, graph.book_id, graph.embedding_model
        page_rows = [{"id": p.id, "page_number": p.page_number, "embedding": p.embedding} for p in graph.pages]
        concept_rows = [
            {"id": c.id, "name": c.name, "description": c.description, "position": c.position, "embedding": c.embedding}
            for c in graph.concepts
        ]
        edge_rows = [{"concept_id": e.concept_id, "prerequisite_id": e.prerequisite_id, "source": e.source} for e in graph.edges]
        link_rows = [{"concept_id": c, "page_id": p} for c, p in graph.concept_pages]

        def work(tx):  # one transaction; safe to run again (it starts by deleting the chapter's old copy)
            tx.run("MATCH (n:Concept {chapter_id: $cid}) DETACH DELETE n", cid=cid).consume()
            tx.run("MATCH (n:Page {chapter_id: $cid}) DETACH DELETE n", cid=cid).consume()
            tx.run("MATCH (n:Chapter {id: $cid}) DETACH DELETE n", cid=cid).consume()
            tx.run(
                "CREATE (:Chapter {id: $cid, book_id: $bid, title: $title, sequence_num: $seq, "
                "is_reference: $is_reference, owner_teacher_id: $owner})",
                cid=cid, bid=bid, title=graph.title, seq=graph.sequence_num,
                is_reference=graph.is_reference, owner=graph.owner_teacher_id,
            ).consume()
            for batch in _chunks(page_rows, self._batch):
                tx.run(
                    "UNWIND $rows AS r CREATE (:Page {id: r.id, chapter_id: $cid, book_id: $bid, "
                    "page_number: r.page_number, embedding: r.embedding, embedding_model: $model})",
                    rows=batch, cid=cid, bid=bid, model=model,
                ).consume()
            for batch in _chunks(concept_rows, self._batch):
                tx.run(
                    "UNWIND $rows AS r CREATE (:Concept {id: r.id, chapter_id: $cid, book_id: $bid, name: r.name, "
                    "description: r.description, position: r.position, embedding: r.embedding, embedding_model: $model})",
                    rows=batch, cid=cid, bid=bid, model=model,
                ).consume()
            tx.run("MATCH (ch:Chapter {id: $cid}) MATCH (p:Page {chapter_id: $cid}) CREATE (p)-[:IN_CHAPTER]->(ch)", cid=cid).consume()
            tx.run("MATCH (ch:Chapter {id: $cid}) MATCH (c:Concept {chapter_id: $cid}) CREATE (c)-[:IN_CHAPTER]->(ch)", cid=cid).consume()
            for batch in _chunks(edge_rows, self._batch):
                tx.run(
                    "UNWIND $rows AS e MATCH (c:Concept {id: e.concept_id}), (p:Concept {id: e.prerequisite_id}) "
                    "CREATE (c)-[:REQUIRES {source: e.source}]->(p)",
                    rows=batch,
                ).consume()
            for batch in _chunks(link_rows, self._batch):
                tx.run(
                    "UNWIND $rows AS l MATCH (c:Concept {id: l.concept_id}), (p:Page {id: l.page_id}) "
                    "CREATE (c)-[:EXPLAINED_ON]->(p)",
                    rows=batch,
                ).consume()

        with self._guard("chapter write"):
            with self.driver.session() as session:
                session.execute_write(work)

    def replace_cross_edges(self, book_id: str, edges) -> None:
        self.ensure_schema()
        rows = [{"concept_id": e.concept_id, "prerequisite_id": e.prerequisite_id} for e in edges]

        def work(tx):
            tx.run(
                "MATCH (:Concept {book_id: $bid})-[r:REQUIRES {source: 'book'}]->(:Concept) DELETE r", bid=book_id
            ).consume()
            for batch in _chunks(rows, self._batch):
                tx.run(
                    "UNWIND $rows AS e MATCH (c:Concept {id: e.concept_id}), (p:Concept {id: e.prerequisite_id}) "
                    "CREATE (c)-[:REQUIRES {source: 'book'}]->(p)",
                    rows=batch,
                ).consume()

        with self._guard("cross-chapter edge write"):
            with self.driver.session() as session:
                session.execute_write(work)

    def delete_chapter(self, chapter_id: str) -> None:
        def work(tx):
            tx.run("MATCH (n:Concept {chapter_id: $cid}) DETACH DELETE n", cid=chapter_id).consume()
            tx.run("MATCH (n:Page {chapter_id: $cid}) DETACH DELETE n", cid=chapter_id).consume()
            tx.run("MATCH (n:Chapter {id: $cid}) DETACH DELETE n", cid=chapter_id).consume()

        with self._guard("chapter delete"):
            with self.driver.session() as session:
                session.execute_write(work)

    def list_chapter_ids(self) -> set[str]:
        with self._guard("chapter listing"):
            return {row["id"] for row in self._read("MATCH (c:Chapter) RETURN c.id AS id")}

    def clear(self) -> None:
        def work(tx):
            for label in ("Concept", "Page", "Chapter"):
                tx.run(f"MATCH (n:{label}) DETACH DELETE n").consume()

        with self._guard("clear"):
            with self.driver.session() as session:
                session.execute_write(work)

    # ---- reading (tenant-filtered) ------------------------------------------------------------
    def _vector_search(self, index: str, label: str, vector: Sequence[float], book_ids: Sequence[str], k: int, returns: str) -> list[dict]:
        """Memgraph's vector search is global, so the book filter is applied to its hits. When most of the
        index belongs to other books the first window can hold fewer than k of ours: widen it (x4) up to the
        configured ceiling instead of silently returning too little.

        Deleted nodes linger in the vector index until Memgraph's garbage collector runs (default every 30 s),
        and reading ANY property of such a hit raises "Trying to get a property from a deleted object". So the
        hits are reduced to their internal id first (id() touches no storage) and the live nodes are re-matched
        by that id: a deleted node simply fails to match and drops out."""
        wanted = list(dict.fromkeys(str(b) for b in book_ids))
        if not wanted or k <= 0:
            return []
        query = (
            f'CALL vector_search.search("{index}", $limit, $vector) YIELD node AS hit, similarity '
            f"WITH id(hit) AS gid, similarity "
            f"MATCH (node:{label}) WHERE id(node) = gid AND node.book_id IN $book_ids "
            f"RETURN {returns}, similarity ORDER BY similarity DESC LIMIT $k"
        )
        ceiling = max(self._max_candidates, k)
        vec = [float(x) for x in vector]

        with self._guard("vector search"):
            retries = 5
            limit = min(max(k * 5, 20), ceiling)
            while True:
                try:
                    rows = self._read(query, limit=limit, vector=vec, book_ids=wanted, k=k)
                except Exception as exc:
                    # Safety net only: if some server build still trips over a not-yet-collected node, wait for GC.
                    if "deleted" in f"{exc} {exc!r}".lower() and retries > 0:
                        retries -= 1
                        time.sleep(1.0)
                        continue
                    raise
                if len(rows) >= k or limit >= ceiling:
                    return rows
                limit = min(limit * 4, ceiling)

    def search_concepts(self, vector: Sequence[float], book_ids: Sequence[str], k: int = 5) -> list[ConceptHit]:
        rows = self._vector_search(
            CONCEPT_INDEX, "Concept", vector, book_ids, k,
            "node.id AS id, node.name AS name, node.description AS description, "
            "node.chapter_id AS chapter_id, node.book_id AS book_id",
        )
        return [ConceptHit(r["id"], r["name"], r["description"] or "", r["chapter_id"], r["book_id"], r["similarity"]) for r in rows]

    def search_pages(self, vector: Sequence[float], book_ids: Sequence[str], k: int = 5) -> list[PageHit]:
        rows = self._vector_search(
            PAGE_INDEX, "Page", vector, book_ids, k,
            "node.id AS id, node.page_number AS page_number, node.chapter_id AS chapter_id, node.book_id AS book_id",
        )
        return [PageHit(r["id"], r["page_number"], r["chapter_id"], r["book_id"], r["similarity"]) for r in rows]

    def prerequisites(self, concept_id: str, book_ids: Sequence[str], max_depth: int = 5) -> list[PrerequisiteRow]:
        wanted = list(dict.fromkeys(str(b) for b in book_ids))
        if not wanted:
            return []
        depth = max(1, min(int(max_depth), 20))
        query = (
            "MATCH (c:Concept {id: $id}) WHERE c.book_id IN $book_ids "
            f"MATCH (c)-[rels:REQUIRES*1..{depth}]->(p:Concept) "
            "RETURN p.id AS id, p.name AS name, min(size(rels)) AS depth ORDER BY depth, name"
        )
        with self._guard("prerequisite lookup"):
            rows = self._read(query, id=str(concept_id), book_ids=wanted)
        return [PrerequisiteRow(r["id"], r["name"], int(r["depth"])) for r in rows]

    def stats(self) -> dict:
        with self._guard("stats"):
            out = {"Chapter": 0, "Page": 0, "Concept": 0, "REQUIRES": 0}
            for row in self._read("MATCH (n) WHERE n:Chapter OR n:Page OR n:Concept RETURN labels(n)[0] AS label, count(n) AS n"):
                out[row["label"]] = row["n"]
            rows = self._read("MATCH (:Concept)-[r:REQUIRES]->(:Concept) RETURN count(r) AS n")
            out["REQUIRES"] = rows[0]["n"] if rows else 0
            return out
</file>

<file path="backend/app/llm/__init__.py">
from app.core.config import settings

from .base import LLMProvider
from .fake_provider import FakeLLMProvider


def get_llm_provider() -> LLMProvider:
    if settings.llm_provider == "openai_compat":
        if not settings.llm_api_key or not settings.llm_model:
            raise RuntimeError("LLM is not configured. Set LLM_API_KEY, LLM_MODEL (and LLM_BASE_URL for Azure).")
        from .openai_compat_provider import OpenAICompatProvider

        return OpenAICompatProvider(
            settings.llm_base_url, settings.llm_api_key, settings.llm_model, settings.llm_timeout_s
        )
    return FakeLLMProvider()


__all__ = ["LLMProvider", "get_llm_provider"]
</file>

<file path="backend/app/llm/base.py">
from typing import Protocol


class LLMProvider(Protocol):
    model_name: str

    def complete_json(self, system: str, user: str) -> str:
        """Return the model's raw reply, expected to be a JSON object."""
        ...
</file>

<file path="backend/app/llm/check.py">
from app.llm import get_llm_provider

if __name__ == "__main__":
    p = get_llm_provider()
    print("model:", p.model_name)
    print(p.complete_json("Reply with a JSON object only.", 'Return this JSON: {"ok": true}'))
</file>

<file path="backend/app/llm/fake_provider.py">
import json
import re


class FakeLLMProvider:
    """Deterministic stand-in for tests and keyless local dev.
    Builds up to 3 chained concepts from the first lines of the text after the 'TEXT:' marker."""

    model_name = "fake"

    def complete_json(self, system: str, user: str) -> str:
        if user.startswith("FRONT PAGES TEXT:\n"):  # reads 'Board: CBSE' style lines
            found = {}
            for key in ("board", "class", "subject", "publisher", "edition", "school"):
                m = re.search(rf"^\s*{key}\s*:\s*(.+)$", user, flags=re.IGNORECASE | re.MULTILINE)
                found[key] = m.group(1).strip() if m else None
            return json.dumps({
                "board": found["board"], "class_name": found["class"], "subject": found["subject"],
                "publisher": found["publisher"], "edition": found["edition"],
                "is_customized": bool(found["school"]), "school": found["school"],
            })
        if user.startswith("CONCEPTS:\n"):  # chapter linking pass: each concept depends on the previous one
            n = len(re.findall(r"^\d+\. ", user, flags=re.MULTILINE))
            return json.dumps({"edges": [{"concept": i, "prerequisites": [i - 1]} for i in range(2, n + 1)]})
        if user.startswith("CROSS-CHAPTER\n"):  # cross-chapter linking: each new concept needs its first candidate
            links, current, in_new = [], None, False
            for line in user.splitlines():
                if line.startswith("NEW CONCEPTS"):
                    in_new = True
                elif line.startswith("EARLIER CONCEPTS"):
                    in_new = False
                m = re.match(r"^(\d+)\. ", line)
                if in_new and m:
                    current = int(m.group(1))
                c = re.match(r"^\s+candidates: (.+)$", line)
                if in_new and c and current is not None:
                    links.append({"concept": current, "prerequisites": [int(c.group(1).split(",")[0])]})
            return json.dumps({"links": links})
        if user.startswith("STUDENT DOUBT\n"):  # calibration: a student's own words about the page
            body = user.split("PAGE:\n", 1)[-1].split()
            return json.dumps({"doubt": "I do not understand " + " ".join(body[:6])})
        if user.startswith("CHECK QUESTION\n"):  # one multiple-choice question about one concept
            name = re.search(r"^CONCEPT: (.+)$", user, flags=re.MULTILINE)
            name = name.group(1) if name else "the idea"
            return json.dumps({"question": f"Which statement about {name} is correct?",
                               "options": [f"{name} is described in the text", "It is unrelated to the chapter",
                                           "It is only a figure", "It is a sidebar"],
                               "correct_index": 0, "explanation": f"The text describes {name}."})
        text = user.split("TEXT:\n", 1)[-1]
        lines: list[str] = []
        for line in text.splitlines():
            line = line.strip()[:60]
            if len(line) >= 2 and line.lower() not in [x.lower() for x in lines]:
                lines.append(line)
            if len(lines) == 3:
                break
        if not lines:
            lines = ["General overview"]
        concepts = [
            {
                "name": name,
                "description": f"Key idea from this page: {name}",
                "learning_objectives": [f"Understand {name}"],
                "prerequisites": [lines[i - 1]] if i else [],
            }
            for i, name in enumerate(lines)
        ]
        return json.dumps({"concepts": concepts})
</file>

<file path="backend/app/llm/openai_compat_provider.py">
import logging

from openai import OpenAI

from app.core.errors import ProcessingError

logger = logging.getLogger(__name__)


class OpenAICompatProvider:
    """Any OpenAI-compatible endpoint: OpenAI, or Azure OpenAI / Foundry via its /openai/v1/ base URL.
    On Azure, `model` is your DEPLOYMENT name."""

    def __init__(self, base_url: str, api_key: str, model: str, timeout_s: int = 60):
        self.model_name = model
        self._client = OpenAI(base_url=base_url or None, api_key=api_key, timeout=timeout_s, max_retries=1)

    def complete_json(self, system: str, user: str) -> str:
        try:
            resp = self._client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
        except Exception as exc:  # network, auth, quota, timeout
            logger.exception("LLM call failed")
            raise ProcessingError("The AI service couldn't be reached. Please try again in a moment.") from exc
        return resp.choices[0].message.content or ""
</file>

<file path="backend/app/models/__init__.py">
from .base import Base
from .content import (
    Book, Chapter, ChapterRequest, ChapterStatus, Concept, ConceptEdge, ContentEmbedding, CrossChapterEdge, IndexStatus, MatchFeedback, Page, PageBand, PageKind,
    UploadDraft, student_book,
)
from .links import ParentStudentLink
from .room import Room, RoomMember, RoomType
from .user import Role, User

__all__ = [
    "Base", "Book", "Chapter", "ChapterRequest", "ChapterStatus", "Concept", "ConceptEdge", "ContentEmbedding", "CrossChapterEdge", "IndexStatus", "MatchFeedback", "Page",
    "PageBand", "PageKind", "UploadDraft", "ParentStudentLink",
    "Role", "Room", "RoomMember", "RoomType", "User", "student_book",
]
</file>

<file path="backend/app/models/base.py">
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
</file>

<file path="backend/app/models/content.py">
import uuid
from datetime import datetime, timezone
from sqlalchemy import BigInteger, CheckConstraint, Column, DateTime, Float, Index, Integer, LargeBinary, String, Boolean, ForeignKey, JSON, Text, Table, UniqueConstraint, Uuid, true
from sqlalchemy.orm import relationship
from app.models.base import Base

# Association table for Student to Book linkage
student_book = Table(
    'student_book',
    Base.metadata,
    Column('student_id', Uuid, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True),
    Column('book_id', Uuid, ForeignKey('books.id', ondelete="CASCADE"), primary_key=True)
)

class Book(Base):
    __tablename__ = "books"
    __table_args__ = (
        # A book is EITHER platform-wide reference content (no owner) OR a private upload owned by one teacher.
        CheckConstraint(
            "(is_reference AND owner_teacher_id IS NULL) OR (NOT is_reference AND owner_teacher_id IS NOT NULL)",
            name="ck_book_reference_xor_owner",
        ),
    )

    id = Column(Uuid, primary_key=True, default=uuid.uuid4, index=True)
    board = Column(String, index=True)  # e.g., CBSE, State Board
    class_name = Column(String, index=True)  # e.g., Class 9
    subject = Column(String, index=True)  # e.g., Science
    publisher = Column(String, index=True)  # e.g., NCERT
    edition = Column(String, nullable=True)
    is_customized = Column(Boolean, default=False)
    school = Column(String, nullable=True)
    variant_of_id = Column(Uuid, ForeignKey("books.id"), nullable=True)
    is_reference = Column(Boolean, nullable=False, default=False, server_default="false", index=True)
    owner_teacher_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    metadata_source = Column(String(12), nullable=False, default="manual", server_default="manual")  # "front_pages" | "manual"
    extracted_metadata = Column(JSON, nullable=True)  # what the system read from the front pages, before the teacher edited it
    front_pages_file = Column(String, nullable=True)

    chapters = relationship("Chapter", back_populates="book", cascade="all, delete-orphan", order_by="Chapter.sequence_num")
    variants = relationship("Book", backref="base_book", remote_side=[id])
    students = relationship("User", secondary=student_book, back_populates="books")

class ChapterStatus:
    EMPTY = "empty"            # no file uploaded yet
    PROCESSING = "processing"  # OCR + concept extraction running in the background
    READY = "ready"            # pages + concepts saved; visible to students
    FAILED = "failed"          # last attempt failed; error_message says why; retry is possible
    ALL = (EMPTY, PROCESSING, READY, FAILED)


class IndexStatus:
    """State of a chapter's DERIVED data (embeddings in PostgreSQL, the copy in Memgraph). It never affects
    whether the chapter is `ready`: the graph in PostgreSQL is what students use; this is for search."""
    PENDING = "pending"  # not done yet (or reset because the chapter was reprocessed)
    DONE = "done"
    SKIPPED = "skipped"  # that provider/store is switched off in the settings
    FAILED = "failed"    # last attempt failed; `python -m app.db.sync_graph` retries
    ALL = (PENDING, DONE, SKIPPED, FAILED)


class Chapter(Base):
    __tablename__ = "chapters"
    __table_args__ = (
        CheckConstraint("status IN ('empty','processing','ready','failed')", name="ck_chapter_status"),
        CheckConstraint("embedding_status IN ('pending','done','skipped','failed')", name="ck_chapter_embedding_status"),
        CheckConstraint("graph_sync_status IN ('pending','done','skipped','failed')", name="ck_chapter_graph_sync_status"),
    )

    id = Column(Uuid, primary_key=True, default=uuid.uuid4, index=True)
    book_id = Column(Uuid, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, index=True)
    sequence_num = Column(Integer)
    status = Column(String(16), nullable=False, default=ChapterStatus.EMPTY, server_default=ChapterStatus.EMPTY)
    error_message = Column(Text, nullable=True)  # teacher-safe text, set when status == failed
    source_file = Column(String, nullable=True)  # stored upload (path relative to storage root); used for retry
    source_sha256 = Column(String(64), nullable=True)  # identical re-upload of a ready chapter is a no-op
    processing_started_at = Column(DateTime(timezone=True), nullable=True)
    graph_report = Column(JSON, nullable=True)  # summary of the last concept-linking pass (see pipeline/graph.py)
    match_report = Column(JSON, nullable=True)  # how this chapter matched known pages/books (see pipeline/matching.py)
    embedding_status = Column(String(10), nullable=False, default=IndexStatus.PENDING, server_default=IndexStatus.PENDING)
    graph_sync_status = Column(String(10), nullable=False, default=IndexStatus.PENDING, server_default=IndexStatus.PENDING)
    index_error = Column(Text, nullable=True)  # short, secret-free reason when embedding_status/graph_sync_status is failed
    indexed_at = Column(DateTime(timezone=True), nullable=True)  # last time both stages finished

    book = relationship("Book", back_populates="chapters")
    pages = relationship("Page", back_populates="chapter", cascade="all, delete-orphan")

class PageKind:
    """What a page IS, saved by the pipeline (Phase 3 needs it: exercise pages carry no concepts, so an exercise
    assignment is scoped from them). `content` teaches, `recap` is a chapter summary, `exercise` holds questions."""
    CONTENT = "content"
    RECAP = "recap"
    EXERCISE = "exercise"
    OTHER = "other"  # covers, indexes, blanks
    ALL = (CONTENT, RECAP, EXERCISE, OTHER)


class Page(Base):
    __tablename__ = "pages"
    __table_args__ = (
        CheckConstraint("page_kind IN ('content','recap','exercise','other')", name="ck_page_kind"),
    )

    id = Column(Uuid, primary_key=True, default=uuid.uuid4, index=True)
    chapter_id = Column(Uuid, ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False)
    page_number = Column(Integer)
    content_text = Column(Text, nullable=False)
    layout_data = Column(JSON, nullable=True)  # Azure Document Intelligence layout data
    image_url = Column(String, nullable=True)
    page_kind = Column(String(10), nullable=False, default=PageKind.CONTENT, server_default=PageKind.CONTENT)  # see PageKind
    needs_review = Column(Boolean, nullable=False, default=False, server_default="false")  # pipeline doubts about this page
    review_note = Column(String(200), nullable=True)  # why (shown to the teacher)
    concepts_model = Column(String(60), nullable=True)  # model that produced this page's concepts ('fake' = placeholders)
    uploaded_by_id = Column(Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    fingerprint = Column(LargeBinary, nullable=True)  # MinHash signature (512 bytes); None for very short pages

    chapter = relationship("Chapter", back_populates="pages")
    concepts = relationship("Concept", back_populates="page", cascade="all, delete-orphan")
    bands = relationship("PageBand", back_populates="page", cascade="all, delete-orphan")
    embedding = relationship("ContentEmbedding", foreign_keys="ContentEmbedding.page_id", back_populates="page",
                             uselist=False, cascade="all, delete-orphan")


class PageBand(Base):
    """LSH index: a page shares >= 1 band key with every page it is similar to, so matching looks up
    ~32 keys instead of comparing against every page in the database."""
    __tablename__ = "page_bands"

    page_id = Column(Uuid, ForeignKey("pages.id", ondelete="CASCADE"), primary_key=True)
    key = Column(BigInteger, primary_key=True, index=True)

    page = relationship("Page", back_populates="bands")


class Concept(Base):
    __tablename__ = "concepts"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4, index=True)
    page_id = Column(Uuid, ForeignKey("pages.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, index=True)
    description = Column(Text)
    learning_objectives = Column(JSON, nullable=True)
    prerequisites = Column(JSON, nullable=True)  # raw prerequisite NAMES as the page-level LLM wrote them
    position = Column(Integer, nullable=False, default=0, server_default="0")  # order within its page
    name_key = Column(String, index=True, nullable=True)  # normalized name; equal keys in a chapter = same concept
    is_canonical = Column(Boolean, nullable=False, default=True, server_default=true())  # first occurrence in chapter

    page = relationship("Page", back_populates="concepts")
    embedding = relationship("ContentEmbedding", foreign_keys="ContentEmbedding.concept_id", back_populates="concept",
                             uselist=False, cascade="all, delete-orphan")
    edges_in = relationship("ConceptEdge", foreign_keys="ConceptEdge.concept_id", back_populates="concept", cascade="all, delete-orphan")
    edges_out = relationship("ConceptEdge", foreign_keys="ConceptEdge.prerequisite_id", back_populates="prerequisite", cascade="all, delete-orphan")

    @property
    def prerequisite_ids(self) -> list[uuid.UUID]:
        return [e.prerequisite_id for e in self.edges_in]


class ConceptEdge(Base):
    """'prerequisite_id must be understood before concept_id'. Only canonical concepts of one chapter are
    linked, and the stored graph is always acyclic (pipeline/graph.py enforces that)."""
    __tablename__ = "concept_edges"
    __table_args__ = (
        UniqueConstraint("concept_id", "prerequisite_id", name="uq_concept_edge"),
        CheckConstraint("concept_id <> prerequisite_id", name="ck_concept_edge_not_self"),
    )

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    chapter_id = Column(Uuid, ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False, index=True)
    concept_id = Column(Uuid, ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    prerequisite_id = Column(Uuid, ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    source = Column(String(8), nullable=False, default="page")  # "page" = name match, "llm" = chapter linking pass

    concept = relationship("Concept", foreign_keys=[concept_id], back_populates="edges_in")
    prerequisite = relationship("Concept", foreign_keys=[prerequisite_id], back_populates="edges_out")


class CrossChapterEdge(Base):
    """'prerequisite_id (in an EARLIER chapter of the same book) must be understood before concept_id'.
    Kept apart from `concept_edges` so each chapter's own graph stays a self-contained DAG; because these edges
    only ever point from a lower chapter number to a higher one, the whole-book graph is acyclic too.
    Rows vanish with either concept (ON DELETE CASCADE) and are rebuilt by pipeline/crosslink.py."""
    __tablename__ = "cross_chapter_edges"
    __table_args__ = (
        UniqueConstraint("concept_id", "prerequisite_id", name="uq_cross_chapter_edge"),
        CheckConstraint("concept_id <> prerequisite_id", name="ck_cross_edge_not_self"),
    )

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    chapter_id = Column(Uuid, ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False, index=True)  # the dependent's chapter
    concept_id = Column(Uuid, ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    prerequisite_id = Column(Uuid, ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    similarity = Column(Float, nullable=True)  # name+description vector similarity that proposed the pair


class MatchFeedback(Base):
    """Layer 5: one teacher decision about 'is my book a variant of that one?'. `decision` is `confirmed` (variant_of set),
    `dismissed` (hide this suggestion for this book from now on) or `retracted` (was confirmed, later cleared or changed;
    does NOT hide the suggestion). `evidence` is what the suggestion showed at that moment (signal, coverage, similarity,
    matched counts) or null when the teacher confirmed a book we had not suggested. Nothing here changes a threshold by
    itself: `python -m app.db.match_feedback` summarises it so the thresholds can be set from real decisions.
    Private to the owning teacher; rows vanish with either book."""
    __tablename__ = "match_feedback"
    __table_args__ = (
        UniqueConstraint("book_id", "base_book_id", name="uq_match_feedback_pair"),
        CheckConstraint("book_id <> base_book_id", name="ck_match_feedback_not_self"),
    )

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    book_id = Column(Uuid, ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)  # the teacher's book
    base_book_id = Column(Uuid, ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    decision = Column(String(10), nullable=False)  # "confirmed" | "dismissed" | "retracted"
    evidence = Column(JSON, nullable=True)
    decided_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


class ContentEmbedding(Base):
    """The durable copy of one embedding vector (float32, little-endian). Memgraph's vector index is rebuilt
    from these rows, so a rebuild never calls the embedding service again.

    Belongs to exactly one Page (its text) or one canonical Concept (name + description). `text_sha256` is the
    hash of the exact text that was embedded: unchanged text is never re-embedded, and identical text anywhere
    reuses the vector (same idea as the >=95% page reuse: the uploader already holds that text). Rows go away
    with their page/concept, so reprocessing a chapter replaces its vectors."""
    __tablename__ = "content_embeddings"
    __table_args__ = (
        CheckConstraint(
            "(page_id IS NOT NULL AND concept_id IS NULL) OR (page_id IS NULL AND concept_id IS NOT NULL)",
            name="ck_embedding_page_xor_concept",
        ),
        UniqueConstraint("page_id", name="uq_embedding_page"),
        UniqueConstraint("concept_id", name="uq_embedding_concept"),
        Index("ix_embedding_model_hash", "model", "text_sha256"),
    )

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    chapter_id = Column(Uuid, ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False, index=True)
    page_id = Column(Uuid, ForeignKey("pages.id", ondelete="CASCADE"), nullable=True)
    concept_id = Column(Uuid, ForeignKey("concepts.id", ondelete="CASCADE"), nullable=True)
    model = Column(String(60), nullable=False)  # embedding model/deployment that produced the vector
    dim = Column(Integer, nullable=False)
    text_sha256 = Column(String(64), nullable=False)
    vector = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    page = relationship("Page", foreign_keys=[page_id], back_populates="embedding")
    concept = relationship("Concept", foreign_keys=[concept_id], back_populates="embedding")


class UploadDraft(Base):
    """A teacher's upload that waits for confirmation: front pages (-> new Book) or a whole-textbook PDF
    (-> chapter split). Nothing heavy runs until the teacher confirms."""
    __tablename__ = "upload_drafts"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    teacher_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    kind = Column(String(12), nullable=False)  # "front_pages" | "whole_book"
    book_id = Column(Uuid, ForeignKey("books.id", ondelete="CASCADE"), nullable=True)
    source_file = Column(String, nullable=False)
    source_sha256 = Column(String(64), nullable=False)
    page_count = Column(Integer, nullable=False, default=0)
    payload = Column(JSON, nullable=True)  # extracted metadata / proposed chapter split
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


class ChapterRequest(Base):
    """A student asking their teacher to add a chapter that isn't in the teacher's uploaded book yet."""
    __tablename__ = "chapter_requests"
    __table_args__ = (
        CheckConstraint("status IN ('open','fulfilled','dismissed','cancelled')", name="ck_chapter_request_status"),
    )

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    teacher_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)  # the book's owner
    book_id = Column(Uuid, ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    chapter_id = Column(Uuid, ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True)
    chapter_hint = Column(String(200), nullable=False)
    status = Column(String(10), nullable=False, default="open", server_default="open")
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime(timezone=True), nullable=True)
</file>

<file path="backend/app/models/links.py">
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ParentStudentLink(Base):
    __tablename__ = "parent_student_links"
    __table_args__ = (UniqueConstraint("parent_id", "student_id", name="uq_parent_student"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    parent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
</file>

<file path="backend/app/models/room.py">
import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class RoomType(str, enum.Enum):
    single_class = "single_class"
    mixed_class = "mixed_class"


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    teacher_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    room_type: Mapped[RoomType] = mapped_column(Enum(RoomType, name="room_type"))
    join_code: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RoomMember(Base):
    __tablename__ = "room_members"
    __table_args__ = (UniqueConstraint("room_id", "user_id", name="uq_room_member"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    room_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
</file>

<file path="backend/app/models/user.py">
from __future__ import annotations

import enum
from typing import TYPE_CHECKING
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from app.models.content import student_book

if TYPE_CHECKING:
    from app.models.content import Book


class Role(str, enum.Enum):
    teacher = "teacher"
    student = "student"
    parent = "parent"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    supertokens_user_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    username: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(20), index=True)  # contact info only — a household can share one number
    role: Mapped[Role] = mapped_column(Enum(Role, name="role"))
    link_code: Mapped[str | None] = mapped_column(String(12), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Reverse relationship for student linking to books
    books: Mapped[list[Book]] = relationship(
        "Book", secondary=student_book, back_populates="students"
    )
</file>

<file path="backend/app/ocr/__init__.py">
from app.core.config import settings

from .base import OCRProvider, OCRResult
from .fake_provider import FakeOCRProvider


def get_ocr_provider() -> OCRProvider:
    if settings.ocr_provider == "azure":
        if not settings.azure_doc_intel_endpoint or not settings.azure_doc_intel_key:
            raise RuntimeError(
                "Azure Document Intelligence is not configured. Set AZURE_DOC_INTEL_ENDPOINT and "
                "AZURE_DOC_INTEL_KEY, or set OCR_PROVIDER=fake for local development."
            )
        from .azure_provider import AzureDocIntelProvider

        return AzureDocIntelProvider(settings.azure_doc_intel_endpoint, settings.azure_doc_intel_key)
    return FakeOCRProvider()


__all__ = ["OCRProvider", "OCRResult", "get_ocr_provider"]
</file>

<file path="backend/app/ocr/azure_provider.py">
import io
from app.core.errors import ProcessingError
from .base import OCRResult


def _pdf_page_count(data: bytes) -> int | None:
    try:
        import pypdf
        return len(pypdf.PdfReader(io.BytesIO(data)).pages)
    except Exception:
        return None


class AzureDocIntelProvider:
    """Azure Document Intelligence using prebuilt-layout (text, layout, and page-by-page structure)."""

    def __init__(self, endpoint: str, key: str):
        self._endpoint = endpoint
        self._key = key

    def _analyze(self, data: bytes, ext: str):
        from azure.ai.documentintelligence import DocumentIntelligenceClient
        from azure.core.credentials import AzureKeyCredential

        client = DocumentIntelligenceClient(self._endpoint, AzureKeyCredential(self._key))
        poller = client.begin_analyze_document("prebuilt-layout", body=io.BytesIO(data))
        result = poller.result()
        analyzed = len(result.pages or [])

        # The free F0 tier silently returns only the first 2 pages. Never save a partial upload.
        expected = _pdf_page_count(data) if ext == "pdf" else None
        if expected and analyzed < expected:
            raise ProcessingError(
                f"Only {analyzed} of {expected} pages were read. The OCR resource may be on the "
                "free tier (2-page limit). Upgrade it to Standard (S0), then retry."
            )
        return result, analyzed

    def extract(self, data: bytes, ext: str) -> OCRResult:
        result, analyzed = self._analyze(data, ext)
        return OCRResult(text=result.content or "", page_count=analyzed)

    def extract_layout(self, data: bytes, ext: str) -> dict:
        result, analyzed = self._analyze(data, ext)

        pages_data = []
        for page in (result.pages or []):
            lines = getattr(page, "lines", []) or []
            page_text = " ".join([line.content for line in lines if getattr(line, "content", None)])
            pages_data.append({
                "page_number": getattr(page, "page_number", len(pages_data) + 1),
                "text": page_text,
                "lines": [
                    {
                        "content": getattr(line, "content", ""),
                        "polygon": getattr(line, "polygon", None),
                    }
                    for line in lines
                ],
            })

        paragraphs_data = []
        for p in (result.paragraphs or []):
            paragraphs_data.append({
                "role": getattr(p, "role", None),
                "content": getattr(p, "content", ""),
            })

        return {
            "text": result.content or "",
            "page_count": analyzed,
            "pages": pages_data,
            "paragraphs": paragraphs_data,
        }
</file>

<file path="backend/app/ocr/base.py">
from dataclasses import dataclass
from typing import Protocol


@dataclass
class OCRResult:
    text: str
    page_count: int


class OCRProvider(Protocol):
    def extract(self, data: bytes, ext: str) -> OCRResult: ...
    def extract_layout(self, data: bytes, ext: str) -> dict:
        """Page-by-page result:
        {"text": str, "page_count": int,
         "pages": [{"page_number": int, "text": str, "lines": [...]}],
         "paragraphs": [{"role": str | None, "content": str}]}"""
        ...
</file>

<file path="backend/app/ocr/fake_provider.py">
import io

import pypdf

from .base import OCRResult

_PLACEHOLDER = "[fake-ocr] No extractable text in this file. Set OCR_PROVIDER=azure for real OCR."


class FakeOCRProvider:
    """Local stand-in for Azure Document Intelligence, for development and tests
    without Azure credentials. Extracts real text from text-based PDFs; falls back
    to a placeholder for scanned PDFs or images, since this fake does no real OCR."""

    def _pages(self, data: bytes, ext: str) -> list[str]:
        if ext == "pdf":
            try:
                reader = pypdf.PdfReader(io.BytesIO(data))
                pages = [(p.extract_text() or "").strip() for p in reader.pages]
                if any(pages):
                    return pages
            except Exception:
                pass  # not a real/parseable PDF (common for test fixtures) - fall through
        return [_PLACEHOLDER]

    def extract(self, data: bytes, ext: str) -> OCRResult:
        pages = self._pages(data, ext)
        return OCRResult(text="\n".join(pages), page_count=len(pages))

    def extract_layout(self, data: bytes, ext: str) -> dict:
        pages = self._pages(data, ext)
        return {
            "text": "\n".join(pages),
            "page_count": len(pages),
            "pages": [{"page_number": i + 1, "text": t, "lines": []} for i, t in enumerate(pages)],
            "paragraphs": [],
        }
</file>

<file path="backend/app/parent/__init__.py">

</file>

<file path="backend/app/parent/routes.py">
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.dependencies import require_parent
from app.core.config import settings
from app.core.ratelimit import limiter
from app.db.session import get_db
from app.models import ParentStudentLink, Role, Room, RoomMember, User
from app.schemas import ChildOut, LinkStudentIn, RoomBrief

router = APIRouter(prefix="/parent", tags=["parent"], dependencies=[Depends(require_parent)])


@router.get("/ping")
def ping(user=Depends(require_parent)):
    return {"role": user.role}


@router.post("/link", response_model=ChildOut)
def link_student(body: LinkStudentIn, parent=Depends(require_parent), db: Session = Depends(get_db)):
    limiter.check("parent-link", str(parent.id), settings.rate_parent_link_per_min, 60)
    student = db.scalar(select(User).where(User.link_code == body.link_code, User.role == Role.student))
    if student is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invalid link code")
    exists = db.scalar(
        select(ParentStudentLink.id).where(
            ParentStudentLink.parent_id == parent.id, ParentStudentLink.student_id == student.id
        )
    )
    if exists:
        raise HTTPException(status.HTTP_409_CONFLICT, "Already linked")
    try:
        db.add(ParentStudentLink(parent_id=parent.id, student_id=student.id))
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Already linked")
    return _child(db, student)


@router.get("/children", response_model=list[ChildOut])
def children(parent=Depends(require_parent), db: Session = Depends(get_db)):
    # Scoped query: only students linked to THIS parent are ever returned.
    students = db.scalars(
        select(User)
        .join(ParentStudentLink, ParentStudentLink.student_id == User.id)
        .where(ParentStudentLink.parent_id == parent.id)
    ).all()
    return [_child(db, s) for s in students]


def _child(db: Session, student: User) -> ChildOut:
    rooms = db.scalars(
        select(Room).join(RoomMember, RoomMember.room_id == Room.id).where(RoomMember.user_id == student.id)
    ).all()
    return ChildOut(id=student.id, name=student.name, rooms=[RoomBrief(id=r.id, name=r.name) for r in rooms])
</file>

<file path="backend/app/pipeline/__init__.py">

</file>

<file path="backend/app/pipeline/concepts.py">
"""Page-level concept extraction: LLM call + schema validation + correction retries (Rules.md §3)."""
import re
from dataclasses import dataclass, field

from pydantic import BaseModel, Field, ValidationError

from app.core.config import settings
from app.core.errors import ProcessingError

MAX_RETRIES = 2

SYSTEM = (
    "You are an educational curriculum parser. From one textbook page, extract the concepts a student must "
    "understand. Reply with JSON only, shaped exactly as: "
    '{"concepts":[{"name":str,"description":str,"learning_objectives":[str],"prerequisites":[str]}]}. '
    "Use 0-10 concepts (an empty list is fine for a cover, index or blank page). Concept names must be unique "
    "on the page. 'prerequisites' are names of earlier concepts a student needs first, only if the text "
    "mentions or clearly implies them. Use only what the page supports; add no outside knowledge. "
    "A concept is an IDEA a student must understand (a definition, law, process, structure, term). Hands-on "
    "activities, experiments, figures, exercises, questions and boxed trivia are NOT concepts: if you list one, "
    "set its \"kind\" to \"activity\" or \"exercise\"; boxed side notes (biographies, trivia, 'Threads of Curiosity', "
    "ethics or career notes) get \"sidebar\"; otherwise use \"idea\". Name each idea in its plain, "
    "standard textbook form (e.g. 'Cell membrane', not 'Cell Membrane Structure and Function Overview'). "
    "Also set the top-level \"page_kind\": \"content\" for pages that teach, \"recap\" for chapter "
    "summaries / 'At a Glance' pages, \"exercise\" for question and exercise pages, \"other\" for covers, "
    "indexes and blanks. Full shape: "
    '{"page_kind":str,"concepts":[{"name":str,"kind":str,"description":str,"learning_objectives":[str],"prerequisites":[str]}]}.'
)

DROPPED_KINDS = {"activity", "exercise", "figure", "question", "sidebar"}
NON_TEACHING_PAGES = {"recap", "exercise"}  # their concepts only repeat or test earlier ones
_ACTIVITY_NAME = re.compile(r"\b(experiments?|activity|activities|exercises?)\b|^\s*(fig(ure)?\.?|question|let'?s)\b", re.I)
_RECAP_HEADING = re.compile(
    r"^\W*(at a glance|chapter summary|summary|key points|points to remember|let'?s recall|"
    r"exercises?|review questions|questions)\b", re.I | re.M,
)


_SUMMARY_HEADING = re.compile(r"^\W*(at a glance|chapter summary|summary|key points|points to remember)\b", re.I | re.M)
SUMMARY_TAIL_FROM = 0.6  # a summary heading only ends the teaching part if it sits in the last 40% of the chapter


def looks_like_summary_page(text: str) -> bool:
    """A chapter-end summary ('At a Glance', 'Summary'). Everything after it is exercise material."""
    return bool(_SUMMARY_HEADING.search((text or "")[:250]))


_EXERCISE_HEADING = re.compile(r"^\W*(exercises?|review questions|questions)\b", re.I | re.M)


def heading_page_kind(text: str) -> str | None:
    """'exercise' / 'recap' when the page STARTS with such a heading (first 250 chars), else None. Deterministic,
    so old chapters can be labelled without a model call (python -m app.db.backfill_page_kind)."""
    head = (text or "")[:250]
    if _EXERCISE_HEADING.search(head):
        return "exercise"
    if _SUMMARY_HEADING.search(head):
        return "recap"
    return None


def normalize_page_kind(kind: str | None) -> str:
    kind = (kind or "content").strip().lower()
    return kind if kind in ("content", "recap", "exercise", "other") else "content"


def looks_like_activity(name: str) -> bool:
    """Deterministic backstop for the prompt rule: an experiment or exercise title is not an idea."""
    return bool(_ACTIVITY_NAME.search(name or ""))


def looks_like_recap_page(text: str) -> bool:
    """A page that STARTS (first 250 chars, at a line start) with a summary / exercise heading."""
    return bool(_RECAP_HEADING.search((text or "")[:250]))


class ConceptExtractionError(ProcessingError):
    pass


class ExtractedConcept(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    kind: str = Field(default="idea", max_length=20)
    description: str = Field(default="", max_length=600)
    learning_objectives: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)


class PageConcepts(BaseModel):
    page_kind: str = Field(default="content", max_length=20)
    concepts: list[ExtractedConcept] = Field(default_factory=list, max_length=25)


def _strip_fences(raw: str) -> str:
    return re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())


@dataclass
class PageExtraction:
    concepts: list[ExtractedConcept] = field(default_factory=list)
    dropped: int = 0  # activities / exercises / recap concepts left out on purpose
    page_kind: str = "content"


def _filter(result: PageConcepts, page_text: str) -> PageExtraction:
    kind = (result.page_kind or "content").strip().lower()
    if kind in NON_TEACHING_PAGES or looks_like_recap_page(page_text):
        # the heading is more reliable than the model about WHICH kind of non-teaching page this is
        shown = heading_page_kind(page_text) or (kind if kind in NON_TEACHING_PAGES else "recap")
        return PageExtraction([], len(result.concepts), shown)
    kept = [
        c for c in result.concepts
        if (c.kind or "idea").strip().lower() not in DROPPED_KINDS and not looks_like_activity(c.name)
    ]
    return PageExtraction(kept, len(result.concepts) - len(kept), normalize_page_kind(kind))


def extract_page_concepts(provider, page_text: str) -> list[ExtractedConcept]:
    return extract_page(provider, page_text).concepts


def extract_page(provider, page_text: str) -> PageExtraction:
    """Raises ConceptExtractionError after MAX_RETRIES failed corrections. Never returns a silent [] on failure.
    Activities, exercises and the concepts of recap/exercise pages are filtered out (counted in `dropped`)."""
    if not page_text.strip():
        return PageExtraction()
    user = f"PAGE TEXT:\n{page_text[: settings.concept_max_chars]}"
    last_error = ""
    for attempt in range(MAX_RETRIES + 1):
        prompt = user
        if attempt:
            prompt += f"\n\nYour previous reply was invalid: {last_error}\nReturn valid JSON only, matching the schema exactly."
        raw = provider.complete_json(SYSTEM, prompt)
        try:
            return _filter(PageConcepts.model_validate_json(_strip_fences(raw)), page_text)
        except ValidationError as exc:
            last_error = "; ".join(e["msg"] for e in exc.errors())[:300]
    raise ConceptExtractionError("Couldn't build the concept map for a page. Please retry, or re-upload a clearer file.")
</file>

<file path="backend/app/pipeline/crosslink.py">
"""Cross-chapter prerequisites: which concepts of EARLIER chapters of the same book a chapter's concepts need.

How it works (cheap layers first, LLM last):
  1. For every canonical concept of the chapter, the nearest canonical concepts of earlier READY chapters of the
     same book are found by the stored embeddings (PostgreSQL's copy; no embedding calls). Weak matches are dropped.
  2. ONE LLM call per batch sees only numbered concepts and numbered candidates and answers with numbers, so it
     cannot invent anything; a prerequisite outside a concept's own candidate list fails validation and is retried.
  3. The result replaces the chapter's rows in `cross_chapter_edges`. Edges only ever point from a lower chapter
     number to a higher one, so the book-wide graph cannot gain a cycle.
If the candidate set is unchanged since the last run the LLM is not asked again (`signature`). Everything here runs
AFTER the chapter is committed and can never fail it; the outcome is recorded in `chapter.graph_report["cross_chapter"]`.
Only the same book is ever searched, so nothing crosses teachers."""
import hashlib
import json
import logging
import re
import uuid

import numpy as np
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import ProcessingError
from app.models.content import Chapter, ChapterStatus, Concept, ContentEmbedding, CrossChapterEdge, Page
from app.embeddings.vectors import from_bytes

logger = logging.getLogger(__name__)
MAX_RETRIES = 2

SYSTEM = (
    "You are a curriculum analyst. You get NEW concepts of one textbook chapter and, for each, a short list of "
    "candidate concepts from EARLIER chapters of the same book. Pick a candidate ONLY if a student could not "
    "understand the new concept without first knowing that candidate: a direct, necessary prerequisite, not a "
    "related topic, not the same general subject, not background that merely helps. Most concepts have none, and "
    "choosing nothing is the normal, correct answer; when unsure, choose nothing. At most 2 per concept. Use only "
    "the given numbers, and for each concept only numbers from its own candidates list. Reply with JSON only, "
    'shaped exactly as: {"links":[{"concept":<number>,"prerequisites":[<number>,...]}]}. Omit concepts with no '
    "prerequisites."
)


class CrossLinkError(ProcessingError):
    pass


class _Item(BaseModel):
    concept: int
    prerequisites: list[int] = Field(default_factory=list)


class _Result(BaseModel):
    links: list[_Item]


def _clip(text: str, limit: int) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _usable(row: ContentEmbedding) -> bool:
    from app.pipeline.indexing import _usable as usable  # same rule as the graph copy: no placeholder/odd-size vectors
    return usable(row)


def _canonical(db: Session, chapter_ids: list) -> list[tuple[Concept, Chapter]]:
    rows = db.execute(
        select(Concept, Chapter).join(Page, Page.id == Concept.page_id).join(Chapter, Chapter.id == Page.chapter_id)
        .where(Chapter.id.in_(chapter_ids), Concept.is_canonical.is_(True))
        .order_by(Chapter.sequence_num, Page.page_number, Concept.position)
    ).all()
    return [(c, ch) for c, ch in rows]


def _vectors(db: Session, chapter_ids: list) -> dict:
    out = {}
    for row in db.scalars(select(ContentEmbedding).where(ContentEmbedding.chapter_id.in_(chapter_ids), ContentEmbedding.concept_id.is_not(None))):
        if _usable(row):
            out[row.concept_id] = (row.model, np.asarray(from_bytes(row.vector), dtype=float))
    return out


def earlier_chapters(db: Session, chapter: Chapter) -> list[Chapter]:
    if chapter.sequence_num is None:
        return []
    return list(db.scalars(
        select(Chapter).where(
            Chapter.book_id == chapter.book_id, Chapter.status == ChapterStatus.READY,
            Chapter.sequence_num < chapter.sequence_num, Chapter.id != chapter.id,
        ).order_by(Chapter.sequence_num)
    ))


def find_candidates(db: Session, chapter: Chapter) -> dict:
    """{concept: [(earlier concept, earlier chapter, similarity), ...]} nearest first, only above the floor."""
    earlier = earlier_chapters(db, chapter)
    if not earlier:
        return {}
    new = _canonical(db, [chapter.id])
    old = _canonical(db, [c.id for c in earlier])
    vectors = _vectors(db, [chapter.id, *[c.id for c in earlier]])
    old = [(c, ch) for c, ch in old if c.id in vectors]
    if not old:
        return {}
    matrix = np.vstack([vectors[c.id][1] / (np.linalg.norm(vectors[c.id][1]) or 1.0) for c, _ in old])
    models = [vectors[c.id][0] for c, _ in old]
    found = {}
    for concept, _ in new:
        if concept.id not in vectors:
            continue
        model, vec = vectors[concept.id]
        norm = np.linalg.norm(vec) or 1.0
        sims = matrix @ (vec / norm)
        order = np.argsort(-sims)
        picks = [
            (old[i][0], old[i][1], float(sims[i])) for i in order
            if models[i] == model and sims[i] >= settings.crosslink_min_similarity
        ][: settings.crosslink_candidates]
        if picks:
            found[concept] = picks
    return found


def _signature(candidates: dict, model: str) -> str:
    rows = sorted((str(c.id), sorted(str(p.id) for p, _, _ in picks)) for c, picks in candidates.items())
    return hashlib.sha256(json.dumps([model, settings.crosslink_max_per_concept, settings.crosslink_keep_similarity, rows]).encode()).hexdigest()


def _ask(provider, batch: list, chapter: Chapter) -> dict:
    """batch: [(concept, picks)] -> {concept id: [(prerequisite concept, similarity)]}. Validated, retried."""
    olds: dict = {}
    for _, picks in batch:
        for p, ch, _ in picks:
            olds.setdefault(p.id, (len(olds) + 1, p, ch))
    lines = [f"NEW CONCEPTS (chapter: {_clip(chapter.title, 80)})"]
    for i, (concept, picks) in enumerate(batch, 1):
        lines.append(f"{i}. {_clip(concept.name, 80)} - {_clip(concept.description, 120)}")
        lines.append("   candidates: " + ", ".join(str(olds[p.id][0]) for p, _, _ in picks))
    lines.append("EARLIER CONCEPTS")
    for number, p, ch in sorted(olds.values(), key=lambda t: t[0]):
        lines.append(f"{number}. [{_clip(ch.title, 50)}] {_clip(p.name, 80)} - {_clip(p.description, 120)}")
    user = "CROSS-CHAPTER\n" + "\n".join(lines)
    by_number = {number: p for number, p, _ in olds.values()}
    allowed = [{olds[p.id][0] for p, _, _ in picks} for _, picks in batch]
    sims = [{p.id: s for p, _, s in picks} for _, picks in batch]
    last = ""
    for attempt in range(MAX_RETRIES + 1):
        prompt = user if not attempt else f"{user}\n\nYour previous reply was invalid: {last}\nReturn valid JSON only, matching the schema exactly."
        raw = provider.complete_json(SYSTEM, prompt)
        try:
            text = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())
            result = _Result.model_validate_json(text)
        except ValidationError as exc:
            last = "; ".join(e["msg"] for e in exc.errors())[:300]
            continue
        bad = next(
            (f"concept {it.concept} / prerequisite {n} is not allowed" for it in result.links for n in it.prerequisites
             if not 1 <= it.concept <= len(batch) or n not in allowed[it.concept - 1]),
            "",
        )
        if bad:
            last = bad
            continue
        out: dict = {}
        for it in result.links:
            concept = batch[it.concept - 1][0]
            chosen = list(dict.fromkeys(it.prerequisites))[: settings.crosslink_max_per_concept]
            out.setdefault(concept.id, [])
            out[concept.id] += [(by_number[n], sims[it.concept - 1][by_number[n].id]) for n in chosen if by_number[n] not in [x for x, _ in out[concept.id]]]
        return out
    raise CrossLinkError("Couldn't link this chapter's concepts to earlier chapters.")


def crosslink_chapter(db: Session, chapter: Chapter, provider) -> dict:
    """Recomputes this chapter's cross-chapter edges. Commits nothing. Returns the report (also stored on the chapter)."""
    report: dict = {"status": "done", "model": getattr(provider, "model_name", "unknown")}
    old_report = (chapter.graph_report or {}).get("cross_chapter") or {}

    def finish(rep: dict) -> dict:
        chapter.graph_report = {**(chapter.graph_report or {}), "cross_chapter": rep}
        db.flush()
        return rep

    if not settings.crosslink_enabled:
        return finish({"status": "disabled"})
    new_count = len(_canonical(db, [chapter.id]))
    if new_count > settings.crosslink_max_concepts:
        return finish({"status": "skipped_too_many_concepts"})
    candidates = find_candidates(db, chapter)
    if not candidates:
        db.execute(delete(CrossChapterEdge).where(CrossChapterEdge.chapter_id == chapter.id))
        return finish({"status": "no_candidates", "edges": 0, "earlier_chapters": len(earlier_chapters(db, chapter))})

    signature = _signature(candidates, report["model"])
    have = len(db.scalars(select(CrossChapterEdge.id).where(CrossChapterEdge.chapter_id == chapter.id)).all())
    if old_report.get("signature") == signature and old_report.get("edges") == have:
        return finish({**old_report, "status": "unchanged"})

    items = list(candidates.items())
    found: dict = {}
    for start in range(0, len(items), settings.crosslink_batch):
        for cid, picks in _ask(provider, items[start:start + settings.crosslink_batch], chapter).items():
            found.setdefault(cid, []).extend(picks)

    db.execute(delete(CrossChapterEdge).where(CrossChapterEdge.chapter_id == chapter.id))
    edges = dropped_weak = 0
    for cid, picks in found.items():
        for prereq, similarity in picks:
            if similarity < settings.crosslink_keep_similarity:  # the model chose it, but the match is too thin to trust
                dropped_weak += 1
                continue
            db.add(CrossChapterEdge(chapter_id=chapter.id, concept_id=cid, prerequisite_id=prereq.id, similarity=round(similarity, 3)))
            edges += 1
    return finish({**report, "edges": edges, "dropped_weak": dropped_weak, "concepts_with_candidates": len(candidates),
                   "signature": signature, "earlier_chapters": len(earlier_chapters(db, chapter))})


def explain_chapter(db: Session, chapter: Chapter, provider) -> list[str]:
    """Dry run for judging the settings on real data: for every concept with candidates, prints the candidates (nearest
    first, with similarity) and what the model chose (kept / dropped as too weak). Asks the model, writes nothing."""
    candidates = find_candidates(db, chapter)
    if not candidates:
        return [f"{chapter.title}: no candidates ({len(earlier_chapters(db, chapter))} earlier chapters)"]
    items = list(candidates.items())
    chosen: dict = {}
    for start in range(0, len(items), settings.crosslink_batch):
        chosen.update(_ask(provider, items[start:start + settings.crosslink_batch], chapter))
    lines = [f"{chapter.title}: {len(candidates)} concepts with candidates "
             f"(offer floor {settings.crosslink_min_similarity}, keep floor {settings.crosslink_keep_similarity})"]
    for concept, picks in items:
        picked = {p.id for p, _ in chosen.get(concept.id, [])}
        lines.append(f"  {concept.name}")
        for p, ch, sim in picks:
            if p.id in picked:
                mark = "CHOSEN, kept" if sim >= settings.crosslink_keep_similarity else "CHOSEN, dropped (weak)"
            else:
                mark = "-"
            lines.append(f"      {sim:.3f}  {p.name}  [{_clip(ch.title, 40)}]  {mark}")
    return lines


def crosslink_after(session_factory, chapter_id, provider=None) -> list[str]:
    """After a chapter is ready and embedded: link it, then re-link the later chapters of the same book (their
    candidates may have changed, and links INTO a re-processed chapter were deleted with its old concepts).
    NEVER raises. Returns one line per chapter for logs / scripts."""
    lines: list[str] = []
    db = session_factory()
    try:
        chapter = db.get(Chapter, chapter_id)
        if chapter is None or chapter.status != ChapterStatus.READY or not settings.crosslink_enabled:
            return lines
        if provider is None:
            from app.llm import get_llm_provider
            provider = get_llm_provider()
        later = list(db.scalars(
            select(Chapter).where(
                Chapter.book_id == chapter.book_id, Chapter.status == ChapterStatus.READY,
                Chapter.sequence_num > (chapter.sequence_num or 0),
            ).order_by(Chapter.sequence_num).limit(settings.crosslink_max_relinks)
        )) if chapter.sequence_num is not None else []
        book_id = chapter.book_id
        for target_id in [chapter.id, *[c.id for c in later]]:
            try:
                target = db.get(Chapter, target_id)
                rep = crosslink_chapter(db, target, provider)
                db.commit()
                lines.append(f"{target.title}: {rep.get('status')} ({rep.get('edges', 0)} cross-chapter edges)")
            except Exception as exc:
                db.rollback()
                logger.exception("Cross-chapter linking of chapter %s failed", target_id)
                lines.append(f"FAILED {target_id}: {type(exc).__name__}")
                try:
                    target = db.get(Chapter, target_id)
                    target.graph_report = {**(target.graph_report or {}), "cross_chapter": {"status": "failed"}}
                    db.commit()
                except Exception:
                    db.rollback()
        from app.pipeline.indexing import sync_cross_edges
        sync_cross_edges(db, book_id)
    except Exception:
        logger.exception("Cross-chapter linking crashed for chapter %s", chapter_id)
    finally:
        db.close()
    return lines
</file>

<file path="backend/app/pipeline/embedmatch.py">
"""Layer 4: embeddings as a SECOND similarity signal for 'this chapter looks like a chapter of a book I can see'.

The fingerprint (3-word shingles) is exact about reused text but blind when a book was re-typeset, lightly
reworded or re-scanned badly. Page embeddings catch similar meaning. This runs after the chapter is `ready`
and embedded, uses only the vectors PostgreSQL already holds (no embedding calls, no LLM), and only ever
adds SUGGESTIONS (`signal: "embedding"`) for books the fingerprint did not already suggest. It never reuses
concepts or sets anything by itself: the teacher still confirms `variant_of`.

Privacy: the same rule as the fingerprint suggestions. A teacher's chapter is compared with official books and
with that teacher's own other books only; an official chapter only with other official books. Nothing here
can name another teacher's book. The outcome is recorded in `chapter.match_report["embedding_match"]`."""
import logging
from collections import defaultdict

import numpy as np
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.embeddings.vectors import from_bytes
from app.models.content import Book, Chapter, ChapterStatus, ContentEmbedding

logger = logging.getLogger(__name__)
MAX_SUGGESTIONS = 3


def _usable(row: ContentEmbedding) -> bool:
    from app.pipeline.indexing import _usable as usable  # no placeholder / odd-size vectors, same rule as the graph copy
    return usable(row)


def _unit(row: ContentEmbedding) -> np.ndarray:
    vec = np.asarray(from_bytes(row.vector), dtype=float)
    return vec / (np.linalg.norm(vec) or 1.0)


def compute(db: Session, chapter: Chapter) -> tuple[list[dict], dict]:
    """(suggestions, info). `info` has the status and, for tuning, the closest books even below the threshold."""
    mine = [r for r in db.scalars(select(ContentEmbedding).where(
        ContentEmbedding.chapter_id == chapter.id, ContentEmbedding.page_id.is_not(None))) if _usable(r)]
    if not mine:
        return [], {"status": "no_vectors"}
    book = db.get(Book, chapter.book_id)
    visible = Book.is_reference.is_(True)
    if book.owner_teacher_id is not None:
        visible = or_(visible, and_(Book.is_reference.is_(False), Book.owner_teacher_id == book.owner_teacher_id))
    rows = db.execute(
        select(ContentEmbedding, Chapter, Book)
        .join(Chapter, Chapter.id == ContentEmbedding.chapter_id).join(Book, Book.id == Chapter.book_id)
        .where(ContentEmbedding.page_id.is_not(None), Chapter.status == ChapterStatus.READY, Book.id != book.id, visible)
    ).all()
    model = mine[0].model
    others = [(e, ch, b) for e, ch, b in rows if e.model == model and _usable(e)]
    if not others:
        return [], {"status": "no_candidates", "pages_compared": len(mine)}
    if len(others) > settings.embed_match_max_pages:
        return [], {"status": "skipped_too_many_pages"}

    matrix = np.vstack([_unit(e) for e, _, _ in others])
    per_book: dict = defaultdict(list)  # book id -> [(similarity, chapter)] for each of my pages that matched it
    for row in mine:
        sims = matrix @ _unit(row)
        best: dict = {}
        for i in np.argsort(-sims)[: 50]:
            b = others[i][2]
            if sims[i] >= settings.embed_match_similarity and b.id not in best:
                best[b.id] = (float(sims[i]), others[i][1])
        for bid, hit in best.items():
            per_book[bid].append(hit)

    books = {str(b.id): b for _, _, b in others}
    scored = []
    for bid, hits in per_book.items():
        chapters: dict = defaultdict(lambda: [0, None])
        for _, ch in hits:
            chapters[ch.id][0] += 1
            chapters[ch.id][1] = ch.title
        top_id, (_, top_title) = max(chapters.items(), key=lambda kv: kv[1][0])
        scored.append({
            "book_id": str(bid), "chapter_id": str(top_id), "chapter_title": top_title, "kind": "variant",
            "matched_pages": len(hits), "pages_checked": len(mine),
            "avg_similarity": round(sum(s for s, _ in hits) / len(hits), 3), "signal": "embedding",
        })
    scored.sort(key=lambda s: (s["matched_pages"], s["avg_similarity"]), reverse=True)
    suggestions = [s for s in scored if s["matched_pages"] / len(mine) >= settings.variant_min_coverage]
    closest = [
        {"book": " ".join(str(x) for x in (books[s["book_id"]].publisher, books[s["book_id"]].subject, books[s["book_id"]].class_name)),
         "chapter": s["chapter_title"], "matched_pages": s["matched_pages"], "pages_checked": len(mine),
         "avg_similarity": s["avg_similarity"]}
        for s in scored[:3]
    ]
    return suggestions, {"status": "done", "model": model, "pages_compared": len(mine), "closest": closest}


def embedmatch_chapter(db: Session, chapter: Chapter) -> dict:
    """Recomputes this chapter's embedding suggestions and merges them into `match_report`. Commits nothing.
    Fingerprint suggestions stay first and untouched; an embedding one is added only for a book the
    fingerprint did not already suggest, and only while there is room (at most 3 in all)."""
    report = dict(chapter.match_report or {})
    if not settings.embed_match_enabled:
        return {"status": "disabled"}
    found, info = compute(db, chapter)
    base = [s for s in (report.get("suggestions") or []) if s.get("signal") != "embedding"]
    known = {s["book_id"] for s in base}
    extra = [s for s in found if s["book_id"] not in known][: max(0, MAX_SUGGESTIONS - len(base))]
    stored = {k: v for k, v in info.items() if k != "closest"}
    stored["added"] = len(extra)
    chapter.match_report = {**report, "suggestions": base + extra, "embedding_match": stored}
    db.flush()
    return {**info, "added": len(extra)}


def embedmatch_after(session_factory, chapter_id) -> str:
    """After a chapter is ready and embedded. NEVER raises. Returns a one-line outcome for logs."""
    db = session_factory()
    try:
        chapter = db.get(Chapter, chapter_id)
        if chapter is None or chapter.status != ChapterStatus.READY or not settings.embed_match_enabled:
            return "skipped"
        rep = embedmatch_chapter(db, chapter)
        db.commit()
        return f"{rep.get('status')} (+{rep.get('added', 0)} suggestions)"
    except Exception:
        db.rollback()
        logger.exception("Embedding match crashed for chapter %s", chapter_id)
        return "failed"
    finally:
        db.close()
</file>

<file path="backend/app/pipeline/embedprobe.py">
"""Layer 4 calibration on REAL data, without needing a second edition of a book.

For a sample of pages of the official books: (1) the real LLM rewords the page in different words, the real embedding
model embeds the rewording, and it is compared with the page's stored vector -> how similar 'the same content, other
words' really is; (2) the same page's vector is compared with pages of OTHER chapters -> how similar 'different
content, same subject' gets. A page-similarity threshold is only trustworthy if it sits between the two groups.
Reads PostgreSQL, makes LLM + embedding calls (about `pages` of each), writes nothing."""
import json
import re
import statistics

import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.embeddings.vectors import from_bytes
from app.models.content import Book, Chapter, ChapterStatus, ContentEmbedding, Page
from app.pipeline.embedmatch import _usable

SYSTEM = (
    "You rewrite one textbook page. Reply with JSON only: {\"text\": \"<the rewritten page>\"}. Reword EVERY sentence "
    "in different words and a different sentence structure. Keep every fact, term, number and the same length. "
    "Do not copy any run of four or more words from the original."
)


def _unit(vec) -> np.ndarray:
    v = np.asarray(vec, dtype=float)
    return v / (np.linalg.norm(v) or 1.0)


def _words(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def kept_phrases(original: str, reworded: str) -> float:
    """Share of the original's 4-word runs that survive in the rewording (0 = fully reworded)."""
    def grams(text):
        w = _words(text)
        return {tuple(w[i:i + 4]) for i in range(len(w) - 3)}
    a = grams(original)
    return len(a & grams(reworded)) / len(a) if a else 0.0


def reword(llm, text: str) -> str | None:
    try:
        raw = llm.complete_json(SYSTEM, "PAGE:\n" + text)
        out = json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())).get("text")
        return out.strip()[: settings.embedding_max_chars] if isinstance(out, str) and out.strip() else None
    except Exception:
        return None


def probe(db: Session, llm, embedder, pages: int = 10) -> dict:
    from app.pipeline.indexing import page_text
    rows = db.execute(
        select(ContentEmbedding, Page, Chapter)
        .join(Page, Page.id == ContentEmbedding.page_id).join(Chapter, Chapter.id == ContentEmbedding.chapter_id)
        .join(Book, Book.id == Chapter.book_id)
        .where(ContentEmbedding.page_id.is_not(None), Chapter.status == ChapterStatus.READY, Book.is_reference.is_(True))
    ).all()
    usable = [(e, p, c) for e, p, c in rows
              if _usable(e) and e.model == embedder.model_name and e.dim == embedder.dim and page_text(p)]
    usable.sort(key=lambda t: (str(t[2].book_id), t[2].sequence_num, t[1].page_number))
    if len(usable) < 4:
        return {"status": "not_enough_pages", "pages_available": len(usable)}
    idx = sorted({int(i) for i in np.linspace(0, len(usable) - 1, min(pages, len(usable)))})
    matrix = np.vstack([_unit(from_bytes(e.vector)) for e, _, _ in usable])
    chapter_ids = [c.id for _, _, c in usable]
    several_chapters = len(set(chapter_ids)) > 1

    texts, picked, kept = [], [], []
    for i in idx:
        original = page_text(usable[i][1])
        new = reword(llm, original)
        if new:
            texts.append(new)
            picked.append(i)
            kept.append(kept_phrases(original, new))
    if len(texts) < 3:
        return {"status": "rewording_failed", "rewritten": len(texts), "asked": len(idx)}

    vectors = embedder.embed(texts)
    same = [float(matrix[i] @ _unit(v)) for i, v in zip(picked, vectors)]
    other = []
    for i in picked:
        sims = matrix @ matrix[i]
        mask = np.array([(cid != chapter_ids[i]) if several_chapters else (j != i) for j, cid in enumerate(chapter_ids)])
        other.append(float(sims[mask].max()))

    thr = settings.embed_match_similarity
    lo, hi = min(same), max(other)
    recall = sum(1 for s in same if s >= thr) / len(same)
    false_rate = sum(1 for s in other if s >= thr) / len(other)
    return {
        "status": "done", "pages": len(same), "several_chapters": several_chapters,
        "same_min": lo, "same_median": statistics.median(same), "other_max": hi, "other_median": statistics.median(other),
        "kept_phrases_median": statistics.median(kept), "threshold": thr, "recall": recall, "false_rate": false_rate,
        "separable": lo > hi, "recommended": round((lo + hi) / 2, 2) if lo > hi else None,
        "pass": recall >= 0.9 and false_rate == 0,
    }
</file>

<file path="backend/app/pipeline/fingerprint.py">
"""Page fingerprints: 3-word-shingle MinHash + LSH band keys.

Why shingles of 3 words: a bag of single words says two pages are identical if they use the same words
in any order; 3-word shingles only match when the actual phrasing matches. Normalization is Unicode-aware
(the old ASCII-only version turned Hindi/Telugu pages into empty text)."""
import hashlib
import re
import unicodedata
from typing import Optional

import numpy as np
from datasketch import MinHash

from app.core.config import settings

NUM_PERM = 128
SHINGLE_SIZE = 3
BANDS = 32  # 32 bands x 4 rows: ~99% recall at Jaccard 0.6, ~5% false candidates at 0.2
ROWS = NUM_PERM // BANDS


def tokenize(text: str) -> list[str]:
    s = unicodedata.normalize("NFKC", text or "").casefold()
    return re.sub(r"[^\w\s]|_", " ", s).split()


def compute_minhash(text: str, min_words: Optional[int] = None) -> Optional[bytes]:
    """512-byte signature, or None when the page is too short to match reliably (covers, blanks)."""
    tokens = tokenize(text)
    if len(tokens) < max(min_words if min_words is not None else settings.fingerprint_min_words, SHINGLE_SIZE):
        return None
    m = MinHash(num_perm=NUM_PERM, seed=1)
    for i in range(len(tokens) - SHINGLE_SIZE + 1):
        m.update(" ".join(tokens[i:i + SHINGLE_SIZE]).encode("utf8"))
    return np.asarray(m.hashvalues, dtype=">u4").tobytes()


def compute_jaccard_similarity(sig_a: Optional[bytes], sig_b: Optional[bytes]) -> float:
    """Estimated Jaccard similarity of the two pages' shingle sets (0.0 if either has no signature)."""
    if not sig_a or not sig_b or len(sig_a) != len(sig_b):
        return 0.0
    a, b = np.frombuffer(sig_a, dtype=">u4"), np.frombuffer(sig_b, dtype=">u4")
    return float(np.mean(a == b))


def band_keys(signature: bytes) -> list[int]:
    """One 63-bit key per band; two pages sharing any key become match candidates."""
    values = np.frombuffer(signature, dtype=">u4")
    keys = []
    for band in range(BANDS):
        chunk = bytes([band]) + values[band * ROWS:(band + 1) * ROWS].tobytes()
        keys.append(int.from_bytes(hashlib.blake2b(chunk, digest_size=8).digest(), "big") & 0x7FFFFFFFFFFFFFFF)
    return keys


def apply_fingerprint(page, text: str) -> Optional[bytes]:
    """Sets the page's signature and LSH index rows (no-op for too-short pages)."""
    from app.models.content import PageBand  # local import: models import nothing from pipeline

    signature = compute_minhash(text)
    page.fingerprint = signature
    page.bands = [PageBand(key=k) for k in band_keys(signature)] if signature else []
    return signature
</file>

<file path="backend/app/pipeline/front_matter.py">
"""Layer 1: read the cover + publisher/edition pages and propose the Book's metadata.
The teacher always confirms or edits the result before a Book exists (Rules.md: never auto-create)."""
import json
import re
from typing import Optional

from pydantic import BaseModel, Field, ValidationError, field_validator

from app.content_library.publishers import board_is_really_a_publisher

from app.core.errors import ProcessingError

MAX_RETRIES = 2

SYSTEM = (
    "You read the cover and the publisher/edition pages of a school textbook and report what they state. "
    "Reply with JSON only, shaped exactly as: "
    '{"board":str|null,"class_name":str|null,"subject":str|null,"publisher":str|null,"edition":str|null,'
    '"is_customized":bool,"school":str|null}. '
    "Use null for anything the pages do not state; never guess. 'board' is the exam board or authority "
    "(e.g. CBSE, ICSE, a state board). 'class_name' looks like 'Class 9'. 'edition' is the edition/year line. "
    "'is_customized' is true only if the pages say the book was made for a specific school, and 'school' is then its name. "
    "Write class_name as 'Class N' even if the pages say 'Grade 9', 'Std. IX' or 'Standard 9'. 'publisher' is the body that "
    "publishes the book (for example NCERT for the National Council of Educational Research and Training). "
    "'board' is the EXAMINATION board (CBSE, ICSE, a state board...). NCERT, SCERT and other publishers are NOT boards: use null "
    "when the pages name no examination board. If the pages give the publisher's short name (NCERT next to 'National Council of "
    "Educational Research and Training'), use the short name. "
    "Return null only for what the text really does not state."
)


class FrontMatterError(ProcessingError):
    pass


class BookMetadata(BaseModel):
    board: Optional[str] = Field(default=None, max_length=80)
    class_name: Optional[str] = Field(default=None, max_length=40)
    subject: Optional[str] = Field(default=None, max_length=80)
    publisher: Optional[str] = Field(default=None, max_length=120)
    edition: Optional[str] = Field(default=None, max_length=120)
    is_customized: bool = False
    school: Optional[str] = Field(default=None, max_length=120)

    @field_validator("board", "class_name", "subject", "publisher", "edition", "school", mode="before")
    @classmethod
    def _blank_to_none(cls, v):
        if isinstance(v, str):
            v = " ".join(v.split())
            return v or None
        return v


FIELDS = ("board", "class_name", "subject", "publisher", "edition", "school")
_ALIASES = {"class": "class_name", "classname": "class_name", "class_name": "class_name", "grade": "class_name", "standard": "class_name",
            "std": "class_name", "exam_board": "board", "publisher_name": "publisher", "publishers": "publisher"}


def is_empty(m: "BookMetadata") -> bool:
    """True when nothing at all was read (the teacher then fills the form by hand)."""
    return not any(getattr(m, f) for f in FIELDS)


def _clean_keys(obj) -> dict:
    """Models sometimes answer {"Board": ...}, {"class": ...} or wrap everything in {"metadata": {...}}; accept those."""
    if not isinstance(obj, dict):
        return {}
    keys = {re.sub(r"[^a-z0-9]+", "_", str(k).lower()).strip("_"): v for k, v in obj.items()}
    keys = {_ALIASES.get(k, k): v for k, v in keys.items()}
    if not any(f in keys for f in FIELDS):
        for v in keys.values():
            if isinstance(v, dict):
                inner = _clean_keys(v)
                if any(f in inner for f in FIELDS):
                    return inner
    return {k: v for k, v in keys.items() if k in FIELDS or k == "is_customized"}


def parse_reply(raw: str) -> "BookMetadata":
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`").removeprefix("json").strip()
    try:
        data = json.loads(raw)
    except ValueError as exc:
        raise ValidationError.from_exception_data("BookMetadata", [{"type": "value_error", "loc": (), "input": raw, "ctx": {"error": exc}}]) from exc
    meta = BookMetadata.model_validate(_clean_keys(data))
    if board_is_really_a_publisher(meta.board, meta.publisher):
        meta.board = None  # models often put 'NCERT' here; it is the publisher
    return meta


def extract_book_metadata(provider, text: str) -> BookMetadata:
    user = f"FRONT PAGES TEXT:\n{text[:6000]}"
    last_error = ""
    result: Optional[BookMetadata] = None
    for attempt in range(MAX_RETRIES + 1):
        prompt = user if not attempt else (
            f"{user}\n\nYour previous reply was unusable: {last_error}\nRead the text again and return valid JSON only, matching the schema exactly."
        )
        raw = provider.complete_json(SYSTEM, prompt)
        try:
            result = parse_reply(raw)
        except ValidationError as exc:
            last_error = "; ".join(e["msg"] for e in exc.errors())[:300]
            continue
        if not is_empty(result):
            return result
        last_error = "every field was null, but the text may state some of them (class, subject, publisher...)"
    if result is not None:  # parsed fine but nothing was found, even after a second look: let the teacher fill it in
        return result
    raise FrontMatterError("Couldn't read the book's details from these pages. You can enter them by hand instead.")
</file>

<file path="backend/app/pipeline/graph.py">
"""Builds the chapter's prerequisite graph from its page-level concepts.

1. Concepts with the same normalized name inside a chapter are ONE concept: the first occurrence
   (lowest page, then position) is canonical; only canonical concepts get edges.
2. Candidate edges come from (a) page-level prerequisite names that match a canonical concept in this
   chapter and (b) one LLM linking call per chapter (pipeline/linking.py).
   Near-duplicate names ("Cell as the Basic Unit of Life" / "Cell as Basic Unit of Life") merge too: first by
   a stop-word-free key, then (when an embedder is given) by name embedding similarity.
3. An edge whose prerequisite first appears on a LATER page than its dependent is dropped (a recap page must
   not make an early concept depend on a late one). Cycles are broken deterministically: edges are added
   most-plausible first, and any edge that would close a cycle is dropped and listed in the report.
The stored graph is therefore always a DAG. Nothing is committed here; the caller commits."""
import logging
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.embeddings.vectors import cosine
from app.models.content import Chapter, Concept, ConceptEdge, Page
from app.pipeline.linking import propose_links

logger = logging.getLogger(__name__)
MAX_REPORTED = 50
_STOP = {"the", "a", "an", "of", "in", "on", "and", "as", "to", "for", "its", "their", "is", "are", "by", "with"}


def normalize_name(name: str) -> str:
    s = unicodedata.normalize("NFKC", name or "").casefold()
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return re.sub(r"^(the|a|an) ", "", s)


def _singular(word: str) -> str:
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 3 and word.endswith("s") and not word.endswith(("ss", "us", "is")):
        return word[:-1]
    return word


def loose_key(name: str) -> str:
    """normalize_name without stop words, plurals, parenthetical asides and word order:
    'Cell as the Basic Unit of Life' == 'Basic unit of the cell life'; 'Prokaryotic cells' == 'Prokaryotic cell';
    'DNA (Deoxyribonucleic acid)' == 'DNA'."""
    bare = re.sub(r"\([^)]*\)", " ", name or "")
    words = [_singular(w) for w in normalize_name(bare).split() if w not in _STOP]
    return " ".join(sorted(words)) or normalize_name(name)


def _numbers(key: str) -> frozenset:
    return frozenset(re.findall(r"\d+", key))


NEAR_MISS_FLOOR = 0.80  # similar pairs between this and the merge threshold are reported, so the threshold can be tuned


def merge_by_embedding(keys: list[str], names: dict[str, str], embedder, threshold: float, near_misses=None) -> dict[str, str]:
    """keys in chapter order -> {key: representative key}. A key joins the first earlier representative whose
    name vector is >= threshold similar (names with different numbers never merge). Raises if the embedder fails.
    near_misses (a list) receives {"a", "b", "similarity"} for pairs of representatives just under the threshold."""
    if len(keys) < 2:
        return {k: k for k in keys}
    vectors = embedder([names[k] for k in keys])
    reps: list[str] = []
    alias: dict[str, str] = {}
    vec = dict(zip(keys, vectors))
    for key in keys:
        target = next(
            (r for r in reps if _numbers(r) == _numbers(key) and cosine(vec[r], vec[key]) >= threshold), None
        )
        alias[key] = target or key
        if target is None:
            if near_misses is not None:
                for r in reps:
                    sim = cosine(vec[r], vec[key])
                    if NEAR_MISS_FLOOR <= sim < threshold and _numbers(r) == _numbers(key):
                        near_misses.append({"a": names[r], "b": names[key], "similarity": round(sim, 3)})
            reps.append(key)
    return alias


@dataclass
class _Candidate:
    prerequisite: Concept
    concept: Concept
    source: str  # "page" | "llm"


def _creates_cycle(dependents: dict, prerequisite_id, concept_id) -> bool:
    """Adding prerequisite -> concept makes a cycle iff concept can already reach prerequisite."""
    stack, seen = [concept_id], set()
    while stack:
        node = stack.pop()
        if node == prerequisite_id:
            return True
        if node in seen:
            continue
        seen.add(node)
        stack.extend(dependents.get(node, ()))
    return False


def build_chapter_graph(db: Session, chapter: Chapter, llm, embedder=None) -> dict:
    """(Re)builds concept identity + edges for one chapter and returns the report (also stored on the chapter).
    embedder: optional callable list[str] -> list[vector] used only to merge near-duplicate names; if it fails
    the chapter is built without that merge (reported as merge_by_embedding='failed')."""
    db.execute(delete(ConceptEdge).where(ConceptEdge.chapter_id == chapter.id))

    rows = db.execute(
        select(Concept, Page.page_number)
        .join(Page, Page.id == Concept.page_id)
        .where(Page.chapter_id == chapter.id)
        .order_by(Page.page_number, Concept.position)
    ).all()

    # --- 1. identity: merge same-named concepts, first occurrence wins
    loose: dict[str, str] = {}  # loose key -> first display name
    for concept, _ in rows:
        loose.setdefault(loose_key(concept.name) or str(concept.id), concept.name)
    alias = {k: k for k in loose}
    embed_status = "off"
    near_misses: list[dict] = []
    if embedder is not None:
        try:
            alias = merge_by_embedding(list(loose), loose, embedder, settings.concept_merge_similarity, near_misses)
            embed_status = "done"
        except Exception:  # never fail a chapter over an optional merge; details are not user-facing
            logger.warning("Embedding-based concept merge failed; continuing without it", exc_info=True)
            embed_status = "failed"

    def key_of(name: str, fallback: str = "") -> str:
        k = loose_key(name) or fallback
        return alias.get(k, k)

    canon: dict[str, Concept] = {}
    page_of: dict = {}
    keyed: list[tuple[Concept, str]] = []
    for concept, page_number in rows:
        key = key_of(concept.name, str(concept.id))
        concept.name_key = key
        concept.is_canonical = key not in canon
        canon.setdefault(key, concept)
        page_of[concept.id] = page_number
        keyed.append((concept, key))
    ordered = list(canon.values())  # chapter order

    # --- 2a. candidates from prerequisite names the page-level LLM wrote
    candidates: list[_Candidate] = []
    unresolved: list[dict] = []
    seen_unresolved: set[tuple[str, str]] = set()
    for concept, key in keyed:
        target = canon[key]
        for raw in concept.prerequisites or []:
            pkey = key_of(raw)
            if not pkey or pkey == key:
                continue
            if pkey in canon:
                candidates.append(_Candidate(canon[pkey], target, "page"))
            elif (key, pkey) not in seen_unresolved:
                seen_unresolved.add((key, pkey))
                unresolved.append({"concept": target.name, "prerequisite": raw})

    # --- 2b. candidates from the chapter-level LLM pass
    llm_status = "skipped_too_few_concepts"
    if len(ordered) >= 2:
        if len(ordered) > settings.link_max_concepts:
            llm_status = "skipped_too_many_concepts"
        else:
            pairs = propose_links(llm, [(c.name, c.description or "") for c in ordered])
            candidates += [_Candidate(ordered[p], ordered[c], "llm") for c, p in pairs]
            llm_status = "done"

    # --- 3. add plausible edges first; drop whatever would close a cycle
    def rank(c: _Candidate):
        return (c.source != "page", page_of[c.concept.id], page_of[c.prerequisite.id])

    dependents: dict = defaultdict(set)
    accepted: dict[tuple, str] = {}
    dropped: list[dict] = []
    backward: list[dict] = []
    for cand in sorted(candidates, key=rank):
        pair = (cand.prerequisite.id, cand.concept.id)
        if pair in accepted:
            continue
        if page_of[cand.prerequisite.id] > page_of[cand.concept.id]:
            if {"prerequisite": cand.prerequisite.name, "concept": cand.concept.name} not in backward:
                backward.append({"prerequisite": cand.prerequisite.name, "concept": cand.concept.name})
            continue
        if _creates_cycle(dependents, cand.prerequisite.id, cand.concept.id):
            dropped.append({"prerequisite": cand.prerequisite.name, "concept": cand.concept.name})
            continue
        accepted[pair] = cand.source
        dependents[cand.prerequisite.id].add(cand.concept.id)

    for (prereq_id, concept_id), source in accepted.items():
        db.add(ConceptEdge(chapter_id=chapter.id, concept_id=concept_id, prerequisite_id=prereq_id, source=source))

    report = {
        "concepts": len(ordered),
        "duplicate_names_merged": len(rows) - len(ordered),
        "edges": len(accepted),
        "llm_linking": llm_status,
        "model": getattr(llm, "model_name", "unknown"),  # 'fake' = placeholder concepts, not real extraction
        "merge_by_embedding": embed_status,
        "near_duplicates_not_merged": sorted(near_misses, key=lambda m: -m["similarity"])[:MAX_REPORTED],
        "dropped_backward_edges": backward[:MAX_REPORTED],
        "unresolved_prerequisites": unresolved[:MAX_REPORTED],
        "dropped_cycle_edges": dropped[:MAX_REPORTED],
    }
    chapter.graph_report = report
    db.flush()
    return report


def copy_chapter_graph(db: Session, chapter: Chapter, source: Chapter, concept_map: dict) -> dict:
    """Same pages, same concepts -> same graph: copy the source chapter's edges and identity instead of asking
    the LLM again (a second run would give a different set of edges). concept_map: source concept id -> new Concept.
    Returns the new report; raises KeyError if an edge refers to a concept that was not copied (caller falls back)."""
    db.execute(delete(ConceptEdge).where(ConceptEdge.chapter_id == chapter.id))
    for old_id, new in concept_map.items():
        old = db.get(Concept, old_id)
        new.name_key, new.is_canonical = old.name_key, old.is_canonical
    edges = db.scalars(select(ConceptEdge).where(ConceptEdge.chapter_id == source.id)).all()
    for e in edges:
        db.add(ConceptEdge(
            chapter_id=chapter.id, concept_id=concept_map[e.concept_id].id,
            prerequisite_id=concept_map[e.prerequisite_id].id, source=e.source,
        ))
    report = {**(source.graph_report or {}), "edges": len(edges), "edges_copied": True}
    report.pop("cross_chapter", None)  # the source's links point at the source's concepts; this chapter gets its own
    chapter.graph_report = report
    db.flush()
    return report
</file>

<file path="backend/app/pipeline/indexing.py">
"""Derived data for a chapter that is already `ready`: embeddings (PostgreSQL) and the Memgraph copy.

Runs AFTER the chapter's all-or-nothing commit, never inside it: an outage of the embedding service or of
Memgraph must not make a good chapter `failed`. Students use the graph in PostgreSQL either way; this stage
only feeds search. Each stage records its state on the chapter (`embedding_status`, `graph_sync_status`,
`index_error`), and `python -m app.db.sync_graph` retries whatever is pending or failed.

  1. embeddings: one vector per page (its text) and per canonical concept (name + description), stored in
     `content_embeddings`. Unchanged text keeps its vector; identical text anywhere reuses one; so a
     reprocess or an identical re-upload costs few or no embedding calls.
  2. graph store: the chapter's pages, concepts, prerequisite edges and vectors are written to Memgraph from
     what PostgreSQL holds (stored vectors included, so no embedding calls are needed to rebuild it).
"""
import hashlib
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import FAKE_EMBEDDING_MODEL, settings
from app.embeddings import EmbeddingError, get_embedding_provider
from app.embeddings.vectors import from_bytes, to_bytes
from app.graph_store import GraphStoreError, get_graph_store
from app.graph_store.base import ChapterGraph, ConceptNode, EdgeRow, PageNode
from app.models.content import Book, Chapter, ChapterStatus, Concept, ConceptEdge, ContentEmbedding, CrossChapterEdge, IndexStatus, Page
from app.pipeline.fingerprint import tokenize

logger = logging.getLogger(__name__)

GENERIC_EMBEDDING_ERROR = "Embeddings could not be created. See the server log, then run python -m app.db.sync_graph."
GENERIC_GRAPH_ERROR = "The graph store could not be updated. See the server log, then run python -m app.db.sync_graph."


@dataclass
class IndexReport:
    chapter_id: str = ""
    embedding: str = ""          # status after this run (done / skipped / failed / unchanged)
    graph: str = ""              # same for the graph store
    embedded: int = 0            # vectors created with a call to the embedding service
    reused: int = 0              # vectors copied from identical text elsewhere (no call)
    kept: int = 0                # vectors already up to date
    removed: int = 0             # vectors of concepts/pages that no longer exist as such
    graph_pages: int = 0
    graph_concepts: int = 0
    graph_edges: int = 0
    without_vectors: int = 0     # nodes written to the graph store with no vector
    errors: list[str] = field(default_factory=list)  # detailed messages for the operator (the DB keeps a generic one)


# ---- what gets embedded -------------------------------------------------------------------------
@dataclass
class _Item:
    kind: str       # "page" | "concept"
    id: object      # page/concept id
    text: str

    @property
    def sha(self) -> str:
        return hashlib.sha256(self.text.encode("utf8")).hexdigest()


def concept_text(concept: Concept) -> str:
    return f"{concept.name}. {concept.description or ''}".strip()[: settings.embedding_max_chars]


def page_text(page: Page) -> Optional[str]:
    """None for covers/blank pages (the same 'too short to matter' rule the fingerprints use)."""
    text = (page.content_text or "").strip()
    if len(tokenize(text)) < settings.fingerprint_min_words:
        return None
    return text[: settings.embedding_max_chars]


def _chapter_pages(db: Session, chapter: Chapter) -> list[Page]:
    return list(db.scalars(select(Page).where(Page.chapter_id == chapter.id).order_by(Page.page_number)))


def _canonical_concepts(db: Session, chapter: Chapter) -> list[Concept]:
    return list(db.scalars(
        select(Concept).join(Page, Page.id == Concept.page_id)
        .where(Page.chapter_id == chapter.id, Concept.is_canonical.is_(True))
        .order_by(Page.page_number, Concept.position)
    ))


def chapter_items(db: Session, chapter: Chapter) -> list[_Item]:
    items = [_Item("concept", c.id, concept_text(c)) for c in _canonical_concepts(db, chapter)]
    for page in _chapter_pages(db, chapter):
        text = page_text(page)
        if text:
            items.append(_Item("page", page.id, text))
    return items


# ---- stage 1: embeddings ------------------------------------------------------------------------
def embed_chapter(db: Session, chapter: Chapter, provider) -> IndexReport:
    """Brings the chapter's `content_embeddings` up to date. Nothing is committed (the caller commits)."""
    report = IndexReport(chapter_id=str(chapter.id))
    existing = {}
    for row in db.scalars(select(ContentEmbedding).where(ContentEmbedding.chapter_id == chapter.id)):
        existing[("page", row.page_id) if row.page_id else ("concept", row.concept_id)] = row

    wanted: set = set()
    todo: list[tuple[_Item, str, Optional[bytes]]] = []  # (item, sha, vector bytes when found in the cache)
    for item in chapter_items(db, chapter):
        key = (item.kind, item.id)
        wanted.add(key)
        sha = item.sha
        row = existing.get(key)
        if row and row.model == provider.model_name and row.dim == provider.dim and row.text_sha256 == sha:
            report.kept += 1
            continue
        cached = db.scalar(
            select(ContentEmbedding).where(
                ContentEmbedding.model == provider.model_name, ContentEmbedding.dim == provider.dim,
                ContentEmbedding.text_sha256 == sha,
            ).limit(1)
        )
        todo.append((item, sha, cached.vector if cached else None))

    fresh_texts = {sha: item.text for item, sha, vec in todo if vec is None}
    fresh: dict[str, bytes] = {}
    if fresh_texts:
        shas = list(fresh_texts)
        vectors = provider.embed([fresh_texts[s] for s in shas])
        if len(vectors) != len(shas):
            raise EmbeddingError(f"Asked for {len(shas)} embeddings, got {len(vectors)}.")
        fresh = {sha: to_bytes(vec) for sha, vec in zip(shas, vectors)}

    for item, sha, cached_vector in todo:
        vector = cached_vector if cached_vector is not None else fresh[sha]
        if cached_vector is not None:
            report.reused += 1
        else:
            report.embedded += 1
        row = existing.get((item.kind, item.id))
        if row is None:
            row = ContentEmbedding(chapter_id=chapter.id)
            if item.kind == "page":
                row.page_id = item.id
            else:
                row.concept_id = item.id
            db.add(row)
        row.model, row.dim, row.text_sha256, row.vector = provider.model_name, provider.dim, sha, vector
        row.created_at = datetime.now(timezone.utc)

    for key, row in existing.items():  # e.g. a concept that stopped being the canonical one
        if key not in wanted:
            db.delete(row)
            report.removed += 1
    db.flush()
    return report


# ---- stage 2: the graph store copy --------------------------------------------------------------
def _usable(row: ContentEmbedding) -> bool:
    """Placeholder (fake) vectors never go into a real store; vectors of the wrong size can't be indexed."""
    if row.dim != settings.embedding_dim:
        return False
    return row.model != FAKE_EMBEDDING_MODEL or settings.embedding_provider.lower() == "fake"


def build_chapter_payload(db: Session, chapter: Chapter) -> ChapterGraph:
    """Everything the graph store needs, read from PostgreSQL. No page text: ids, numbers, names, vectors."""
    book = db.get(Book, chapter.book_id)
    vectors: dict[tuple[str, object], tuple[str, list[float]]] = {}
    for row in db.scalars(select(ContentEmbedding).where(ContentEmbedding.chapter_id == chapter.id)):
        if _usable(row):
            key = ("page", row.page_id) if row.page_id else ("concept", row.concept_id)
            vectors[key] = (row.model, from_bytes(row.vector))

    pages = _chapter_pages(db, chapter)
    rows = db.execute(
        select(Concept, Page.id).join(Page, Page.id == Concept.page_id)
        .where(Page.chapter_id == chapter.id).order_by(Page.page_number, Concept.position)
    ).all()
    pages_by_key: dict[str, list[str]] = defaultdict(list)
    for concept, page_id in rows:
        if str(page_id) not in pages_by_key[concept.name_key]:
            pages_by_key[concept.name_key].append(str(page_id))
    canonical = [c for c, _ in rows if c.is_canonical]

    models = {m for m, _ in vectors.values()}
    graph = ChapterGraph(
        book_id=str(book.id), chapter_id=str(chapter.id), title=chapter.title or "", sequence_num=chapter.sequence_num or 0,
        is_reference=bool(book.is_reference), owner_teacher_id=str(book.owner_teacher_id) if book.owner_teacher_id else None,
        embedding_model=models.pop() if len(models) == 1 else None,
    )
    graph.pages = [
        PageNode(str(p.id), p.page_number or 0, vectors.get(("page", p.id), (None, None))[1]) for p in pages
    ]
    graph.concepts = [
        ConceptNode(str(c.id), c.name, c.description or "", c.position or 0, vectors.get(("concept", c.id), (None, None))[1])
        for c in canonical
    ]
    for c in canonical:
        graph.concept_pages += [(str(c.id), page_id) for page_id in pages_by_key.get(c.name_key, [])]
    graph.edges = [
        EdgeRow(str(e.concept_id), str(e.prerequisite_id), e.source)
        for e in db.scalars(select(ConceptEdge).where(ConceptEdge.chapter_id == chapter.id))
    ]
    return graph


def sync_cross_edges(db: Session, book_id) -> bool:
    """Copy the book's cross-chapter prerequisite edges (PostgreSQL) into the graph store. Best effort: a store
    outage is logged and the next chapter write / `sync_graph` repeats it. Returns True when written."""
    try:
        store = get_graph_store()
        if store is None:
            return False
        rows = db.execute(
            select(CrossChapterEdge.concept_id, CrossChapterEdge.prerequisite_id)
            .join(Chapter, Chapter.id == CrossChapterEdge.chapter_id).where(Chapter.book_id == book_id)
        ).all()
        store.ensure_schema()
        store.replace_cross_edges(str(book_id), [EdgeRow(str(c), str(p), "book") for c, p in rows])
        return True
    except Exception:
        logger.warning("Cross-chapter edge sync for book %s failed", book_id, exc_info=True)
        return False


# ---- orchestration ------------------------------------------------------------------------------
def _fail(db: Session, chapter_id, field_name: str, message: str) -> None:
    """Record a failed stage on a fresh view of the chapter (the failed transaction was rolled back)."""
    chapter = db.get(Chapter, chapter_id)
    setattr(chapter, field_name, IndexStatus.FAILED)
    chapter.index_error = message[:500]
    db.commit()


def index_chapter(session_factory, chapter_id, *, embed: bool = True) -> IndexReport:
    """Both stages for one ready chapter, with its own session. NEVER raises (it runs in the background and
    after the chapter is already committed). `embed=False` skips stage 1: that is what a rebuild of the graph
    store uses, so it works from the stored vectors without calling the embedding service."""
    report = IndexReport(chapter_id=str(chapter_id))
    db = session_factory()
    try:
        chapter = db.get(Chapter, chapter_id)
        if chapter is None or chapter.status != ChapterStatus.READY:
            report.errors.append("chapter is not ready")
            return report

        if embed:
            try:
                provider = get_embedding_provider()
            except RuntimeError as exc:  # misconfigured settings; the text names the settings, never a secret
                provider = False
                report.embedding = IndexStatus.FAILED
                report.errors.append(str(exc))
                _fail(db, chapter_id, "embedding_status", str(exc))
            if provider is None:
                chapter.embedding_status = IndexStatus.SKIPPED
                report.embedding = IndexStatus.SKIPPED
                db.commit()
            elif provider is not False:
                try:
                    done = embed_chapter(db, chapter, provider)
                    chapter.embedding_status = IndexStatus.DONE
                    db.commit()
                    report.embedding = IndexStatus.DONE
                    report.embedded, report.reused, report.kept, report.removed = done.embedded, done.reused, done.kept, done.removed
                except Exception as exc:
                    db.rollback()
                    logger.exception("Embedding chapter %s failed", chapter_id)
                    report.embedding = IndexStatus.FAILED
                    report.errors.append(f"{type(exc).__name__}: {str(exc)[:200]}")
                    _fail(db, chapter_id, "embedding_status", GENERIC_EMBEDDING_ERROR)
            if report.embedding == IndexStatus.FAILED:
                return report  # nothing worth sending to the graph store yet: the retry does both stages

        chapter = db.get(Chapter, chapter_id)
        try:
            store = get_graph_store()
        except Exception as exc:
            store = False
            report.graph = IndexStatus.FAILED
            report.errors.append(f"{type(exc).__name__}: {str(exc)[:200]}")
            _fail(db, chapter_id, "graph_sync_status", GENERIC_GRAPH_ERROR)
        if store is None:
            chapter.graph_sync_status = IndexStatus.SKIPPED
            report.graph = IndexStatus.SKIPPED
            db.commit()
        elif store is not False:
            try:
                payload = build_chapter_payload(db, chapter)
                store.ensure_schema()
                store.replace_chapter(payload)
                chapter.graph_sync_status = IndexStatus.DONE
                report.graph = IndexStatus.DONE
                report.graph_pages, report.graph_concepts, report.graph_edges = len(payload.pages), len(payload.concepts), len(payload.edges)
                report.without_vectors = sum(1 for n in [*payload.pages, *payload.concepts] if n.embedding is None)
                db.commit()
                sync_cross_edges(db, chapter.book_id)  # replacing the chapter dropped its edges to other chapters
            except Exception as exc:
                db.rollback()
                logger.exception("Graph sync of chapter %s failed", chapter_id)
                report.graph = IndexStatus.FAILED
                report.errors.append(f"{type(exc).__name__}: {str(exc)[:300]}")
                _fail(db, chapter_id, "graph_sync_status", GENERIC_GRAPH_ERROR)

        chapter = db.get(Chapter, chapter_id)
        if (chapter.embedding_status in (IndexStatus.DONE, IndexStatus.SKIPPED)
                and chapter.graph_sync_status in (IndexStatus.DONE, IndexStatus.SKIPPED)):
            chapter.index_error = None
            chapter.indexed_at = datetime.now(timezone.utc)
            db.commit()
    except Exception as exc:  # last resort: indexing must never take the caller down
        logger.exception("Indexing chapter %s crashed", chapter_id)
        report.errors.append(f"{type(exc).__name__}: {str(exc)[:200]}")
        try:
            db.rollback()
        except Exception:
            pass
    finally:
        db.close()
    return report


def chapters_needing_index(db: Session, book_id=None, chapter_id=None) -> list[Chapter]:
    query = select(Chapter).where(Chapter.status == ChapterStatus.READY).order_by(Chapter.book_id, Chapter.sequence_num)
    if chapter_id is not None:
        query = query.where(Chapter.id == chapter_id)
    elif book_id is not None:
        query = query.where(Chapter.book_id == book_id)
    embeddings_on = settings.embedding_provider.lower() != "none"
    graph_on = settings.graph_store_provider.lower() != "none"

    def needs_work(status: str, switched_on: bool) -> bool:
        # 'skipped' means "that stage was off when the chapter was processed": once it is switched on, do it now
        return status in (IndexStatus.PENDING, IndexStatus.FAILED) or (status == IndexStatus.SKIPPED and switched_on)

    return [
        c for c in db.scalars(query)
        if chapter_id is not None or needs_work(c.embedding_status, embeddings_on) or needs_work(c.graph_sync_status, graph_on)
    ]
</file>

<file path="backend/app/pipeline/jobs.py">
"""Background job: process one chapter's stored upload and record the outcome on the chapter."""
import logging
import uuid
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.errors import ProcessingError
from app.content_library.link_requests import fulfill_requests_for_chapter
from app.core.storage import read_file
from app.models.content import Chapter, ChapterStatus, IndexStatus
from app.pipeline.crosslink import crosslink_after
from app.pipeline.embedmatch import embedmatch_after
from app.pipeline.indexing import index_chapter
from app.pipeline.orchestrator import PipelineOrchestrator

logger = logging.getLogger(__name__)

GENERIC_ERROR = "Something went wrong while processing this chapter. Please try again."


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def is_actively_processing(chapter: Chapter) -> bool:
    """True while a job is running. A 'processing' chapter older than the timeout is treated as stuck
    (e.g. the server restarted mid-job), so the teacher can re-upload or retry instead of waiting forever."""
    if chapter.status != ChapterStatus.PROCESSING:
        return False
    started = chapter.processing_started_at
    if started is None:
        return False
    if started.tzinfo is None:  # SQLite returns naive datetimes
        started = started.replace(tzinfo=timezone.utc)
    return utcnow() - started < timedelta(minutes=settings.chapter_processing_timeout_min)


def mark_processing(chapter: Chapter) -> None:
    chapter.status = ChapterStatus.PROCESSING
    chapter.error_message = None
    chapter.processing_started_at = utcnow()
    # The old pages (and their vectors) are replaced by this run, so the derived copies are out of date again.
    chapter.embedding_status = IndexStatus.PENDING
    chapter.graph_sync_status = IndexStatus.PENDING
    chapter.index_error = None


def run_chapter_job(chapter_id: uuid.UUID, user_id: uuid.UUID, session_factory, fresh: bool = False) -> None:
    """Runs after the HTTP response, with its OWN session (the request's session is closed by then).
    Pages and the 'ready' status are committed together, so a failure never leaves half a chapter."""
    db = session_factory()
    committed_ready = False
    try:
        chapter = db.get(Chapter, chapter_id)
        if chapter is None or chapter.status != ChapterStatus.PROCESSING or not chapter.source_file:
            return
        ext = chapter.source_file.rsplit(".", 1)[-1]
        try:
            data = read_file(chapter.source_file)
            PipelineOrchestrator(db, reuse_concepts=not fresh).process_chapter_file(chapter, data, ext, user_id)
            chapter.status = ChapterStatus.READY
            chapter.error_message = None
            fulfill_requests_for_chapter(db, chapter)  # students who asked for this chapter get closure
            db.commit()
            committed_ready = True
        except Exception as exc:
            db.rollback()
            logger.exception("Chapter %s processing failed", chapter_id)
            # Only ProcessingError text is written for humans; anything else could leak internals.
            message = str(exc) if isinstance(exc, ProcessingError) else GENERIC_ERROR
            chapter = db.get(Chapter, chapter_id)
            chapter.status = ChapterStatus.FAILED
            chapter.error_message = message[:500]
            db.commit()
    finally:
        db.close()
    if committed_ready:
        # Embeddings + the graph-store copy come AFTER the commit and can never fail the chapter (see
        # pipeline/indexing.py). Their outcome is recorded on the chapter; sync_graph retries failures.
        index_chapter(session_factory, chapter_id)
        embedmatch_after(session_factory, chapter_id)  # Layer 4: needs the page vectors; never raises
        crosslink_after(session_factory, chapter_id)  # needs the vectors the line above just made; never raises
</file>

<file path="backend/app/pipeline/linking.py">
"""Chapter-level LLM linking pass: which concepts of one chapter are prerequisites of which.

The model only ever sees and returns NUMBERS from the list we give it, so it cannot invent concepts
or misspell names; anything out of range fails validation and is retried (Rules.md §3)."""
from pydantic import BaseModel, Field, ValidationError

from app.core.errors import ProcessingError

MAX_RETRIES = 2

SYSTEM = (
    "You are a curriculum analyst. You get the numbered concepts of ONE textbook chapter, in the order they "
    "appear. For each concept, decide which OTHER listed concepts a student must understand first. "
    "Use only the given numbers. Include only direct, genuinely necessary prerequisites (usually 0-3 per "
    "concept); never list a concept as its own prerequisite. Reply with JSON only, shaped exactly as: "
    '{"edges":[{"concept":<number>,"prerequisites":[<number>,...]}]}. Omit concepts with no prerequisites.'
)


class LinkingError(ProcessingError):
    pass


class LinkItem(BaseModel):
    concept: int
    prerequisites: list[int] = Field(default_factory=list)


class LinkResult(BaseModel):
    edges: list[LinkItem]  # required: a reply without it is invalid, not "no edges"


def _clip(text: str, limit: int) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _check_ranges(result: LinkResult, n: int) -> str:
    for item in result.edges:
        for number in [item.concept, *item.prerequisites]:
            if not 1 <= number <= n:
                return f"number {number} is not in the list (valid numbers are 1 to {n})"
    return ""


def propose_links(provider, concepts: list[tuple[str, str]]) -> list[tuple[int, int]]:
    """concepts: [(name, description)] in chapter order. Returns 0-based (concept_index, prerequisite_index)
    pairs, de-duplicated, with self-links dropped. Raises LinkingError after MAX_RETRIES failed corrections."""
    n = len(concepts)
    listing = "\n".join(f"{i}. {_clip(name, 80)} - {_clip(desc, 120)}" for i, (name, desc) in enumerate(concepts, 1))
    user = f"CONCEPTS:\n{listing}"
    last_error = ""
    for attempt in range(MAX_RETRIES + 1):
        prompt = user
        if attempt:
            prompt += f"\n\nYour previous reply was invalid: {last_error}\nReturn valid JSON only, matching the schema exactly."
        raw = provider.complete_json(SYSTEM, prompt)
        try:
            text = raw.strip()
            if text.startswith("```"):
                text = text.strip("`").removeprefix("json").strip()
            result = LinkResult.model_validate_json(text)
        except ValidationError as exc:
            last_error = "; ".join(e["msg"] for e in exc.errors())[:300]
            continue
        problem = _check_ranges(result, n)
        if problem:
            last_error = problem
            continue
        pairs: list[tuple[int, int]] = []
        seen: set[tuple[int, int]] = set()
        for item in result.edges:
            for prereq in item.prerequisites:
                pair = (item.concept - 1, prereq - 1)
                if pair[0] != pair[1] and pair not in seen:
                    seen.add(pair)
                    pairs.append(pair)
        return pairs
    raise LinkingError("Couldn't work out how the concepts in this chapter depend on each other. Please retry.")
</file>

<file path="backend/app/pipeline/matching.py">
"""Find known pages similar to a new page, and turn page matches into book-level suggestions.

Thresholds (settings): >= reuse_similarity is the same page (reuse its concepts, no LLM call);
variant_min_similarity..reuse_similarity is a page from a variant/edition of a known book.

Privacy: concept reuse may use any book's page (the uploader already holds near-identical text, so nothing
new is revealed). Book SUGGESTIONS are limited to books the uploading teacher can already see."""
import uuid
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.content import Book, Chapter, Page, PageBand
from app.pipeline.fingerprint import compute_jaccard_similarity

MAX_CANDIDATES = 30


@dataclass
class PageMatch:
    page_id: uuid.UUID
    score: float
    book_id: uuid.UUID
    is_reference: bool
    owner_teacher_id: Optional[uuid.UUID]
    chapter_id: Optional[uuid.UUID] = None
    chapter_title: Optional[str] = None


def find_matches(db: Session, signature: bytes, keys: Iterable[int]) -> list[PageMatch]:
    """Pages with similarity >= variant_min_similarity, best first. Looks up the LSH keys, then scores only
    the few candidates that share one, never the whole table."""
    shared = db.execute(
        select(PageBand.page_id, func.count().label("shared"))
        .where(PageBand.key.in_(list(keys)))
        .group_by(PageBand.page_id)
        .order_by(func.count().desc())
        .limit(MAX_CANDIDATES)
    ).all()
    if not shared:
        return []
    rows = db.execute(
        select(Page.id, Page.fingerprint, Book.id, Book.is_reference, Book.owner_teacher_id, Chapter.id, Chapter.title)
        .join(Chapter, Chapter.id == Page.chapter_id)
        .join(Book, Book.id == Chapter.book_id)
        .where(Page.id.in_([r.page_id for r in shared]))
    ).all()
    matches = []
    for page_id, fingerprint, book_id, is_reference, owner_id, chapter_id, chapter_title in rows:
        score = compute_jaccard_similarity(signature, fingerprint)
        if score >= settings.variant_min_similarity:
            matches.append(PageMatch(page_id, score, book_id, is_reference, owner_id, chapter_id, chapter_title))
    return sorted(matches, key=lambda m: m.score, reverse=True)


def summarize_book_matches(
    per_page: list[list[PageMatch]], pages_checked: int, own_book_id: uuid.UUID, teacher_id: uuid.UUID
) -> list[dict]:
    """Matches for ONE chapter: books (visible to the teacher, other than this one) with at least
    variant_min_coverage of the chapter's fingerprinted pages matching, each with the chapter of that book
    that matches best. kind='same' if the matched pages are near-identical, else 'variant'."""
    if pages_checked == 0:
        return []
    best: dict[uuid.UUID, list[PageMatch]] = defaultdict(list)  # book -> best match for each page that matched it
    for matches in per_page:
        page_best: dict[uuid.UUID, PageMatch] = {}
        for m in matches:
            visible = m.is_reference or m.owner_teacher_id == teacher_id
            if visible and m.book_id != own_book_id and (m.book_id not in page_best or m.score > page_best[m.book_id].score):
                page_best[m.book_id] = m
        for book_id, m in page_best.items():
            best[book_id].append(m)

    suggestions = []
    for book_id, found in best.items():
        coverage = len(found) / pages_checked
        if coverage < settings.variant_min_coverage:
            continue
        average = sum(m.score for m in found) / len(found)
        chapters: dict = defaultdict(lambda: [0, None])  # which chapter of that book do the matched pages sit in?
        for m in found:
            chapters[m.chapter_id][0] += 1
            chapters[m.chapter_id][1] = m.chapter_title
        top_id, (_, top_title) = max(chapters.items(), key=lambda kv: kv[1][0])
        suggestions.append({
            "book_id": str(book_id),
            "chapter_id": str(top_id) if top_id else None,
            "chapter_title": top_title,
            "kind": "same" if average >= settings.reuse_similarity else "variant",
            "matched_pages": len(found),
            "pages_checked": pages_checked,
            "avg_similarity": round(average, 3),
        })
    suggestions.sort(key=lambda s: (s["matched_pages"], s["avg_similarity"]), reverse=True)
    return suggestions[:3]
</file>

<file path="backend/app/pipeline/orchestrator.py">
import logging

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import ProcessingError
from app.llm import get_llm_provider
from app.models.content import Chapter, ChapterStatus, Concept, ConceptEdge, Page
from app.ocr import get_ocr_provider
from app.embeddings import get_embedding_provider
from app.pipeline.concepts import ConceptExtractionError, SUMMARY_TAIL_FROM, extract_page, heading_page_kind, looks_like_activity, looks_like_recap_page, looks_like_summary_page
from app.pipeline.fingerprint import apply_fingerprint, band_keys, compute_minhash, tokenize
from app.pipeline.graph import build_chapter_graph, copy_chapter_graph
from app.pipeline.matching import PageMatch, find_matches, summarize_book_matches

logger = logging.getLogger(__name__)

REVIEW_MIN_WORDS = 40  # a page this long that yields zero concepts is suspicious
MAX_REVIEW_REPORTED = 50


class PipelineOrchestrator:
    """Synchronous on purpose: OCR and LLM clients block, and this runs in a background thread
    (see pipeline/jobs.py). Providers come from the factories, so tests and keyless dev use the
    fake ones (OCR_PROVIDER / LLM_PROVIDER=fake).

    Cost layers, cheapest first:
      0. identical FILE already processed anywhere -> skip OCR (reuse its page text)
      1. identical/near-identical PAGE already known (>= reuse_similarity) -> reuse its concepts, no LLM call
      2. otherwise OCR text -> LLM concept extraction
    Pages that are only similar (a variant/edition) are still processed normally; they feed the
    book-level 'looks like a variant of X' suggestion instead."""

    def __init__(self, db: Session, ocr_provider=None, llm_provider=None, embedder=None, reuse_concepts: bool = True):
        self.db = db
        self._ocr = ocr_provider
        self.llm = llm_provider or get_llm_provider()
        self._embedder = embedder  # callable list[str] -> vectors; None -> built from settings (or off)
        self.reuse_concepts = reuse_concepts  # False ('reprocess --fresh'): extract every page again

    def _name_embedder(self):
        """Only a real embedding provider is used to merge near-duplicate concept names; never the fake one."""
        if self._embedder is not None:
            return self._embedder
        if settings.embedding_provider.lower() != "openai_compat":
            return None
        try:
            provider = get_embedding_provider()
        except Exception:
            logger.warning("Embedding provider is not usable; skipping name merge", exc_info=True)
            return None
        return provider.embed if provider else None

    @property
    def ocr(self):  # created lazily: an exact-duplicate upload never needs OCR (or Azure credentials)
        if self._ocr is None:
            self._ocr = get_ocr_provider()
        return self._ocr

    @property
    def model_name(self) -> str:
        return getattr(self.llm, "model_name", "unknown")

    def _reusable(self, source_page: Page) -> bool:
        """Concepts are reused only if we know which model made them, and never the fake model's placeholders
        for a real run (otherwise one dev run with LLM_PROVIDER=fake would poison every later upload)."""
        made_by = source_page.concepts_model
        return made_by is not None and (made_by != "fake" or self.model_name == "fake")

    def _cached_layout(self, chapter: Chapter):
        """Layer 0: the same file (by SHA-256) already processed into another chapter -> its page text."""
        if not chapter.source_sha256:
            return None
        source = self.db.scalar(
            select(Chapter).where(
                Chapter.source_sha256 == chapter.source_sha256,
                Chapter.status == ChapterStatus.READY,
                Chapter.id != chapter.id,
            ).limit(1)
        )
        if source is None:
            return None
        pages = self.db.scalars(select(Page).where(Page.chapter_id == source.id).order_by(Page.page_number)).all()
        if not pages:
            return None
        return {"pages": [{"page_number": p.page_number, "text": p.content_text, "lines": p.layout_data} for p in pages]}

    def process_chapter_file(self, chapter: Chapter, file_bytes: bytes, ext: str, user_id) -> list[Page]:
        """The chapter's previous pages are replaced, so re-running (retry / re-upload) never duplicates.
        Nothing is committed here: the caller commits once, so any failure rolls back to the previous state."""
        layout = self._cached_layout(chapter)
        ocr_reused = layout is not None
        if layout is None:
            layout = self.ocr.extract_layout(file_bytes, ext)  # slow, billable; done before touching the DB

        self.db.execute(delete(ConceptEdge).where(ConceptEdge.chapter_id == chapter.id))
        for old in list(chapter.pages):
            self.db.delete(old)
        self.db.flush()

        created: list[Page] = []
        per_page_matches: list[list[PageMatch]] = []
        pages_checked = pages_reused = 0
        review_pages: list[dict] = []
        dropped_concepts = recap_pages = 0
        reused_from: list[tuple[Page, Page, list[Concept]]] = []  # (new page, source page, its new concepts)
        uncovered = 0  # pages that were extracted/filtered, so the source chapter's edges cannot be copied
        short_empty_pages: list[int] = []
        summary_seen = False  # after a chapter-end summary, pages are exercises: no concepts, no LLM calls
        total_pages = len(layout["pages"])
        for index, p_data in enumerate(layout["pages"]):
            text, number = p_data["text"], p_data["page_number"]
            tail = summary_seen
            if looks_like_summary_page(text) and index >= SUMMARY_TAIL_FROM * total_pages:
                summary_seen = True

            matches: list[PageMatch] = []
            signature = compute_minhash(text)
            if signature:
                pages_checked += 1
                matches = find_matches(self.db, signature, band_keys(signature))
                per_page_matches.append(matches)
            best = matches[0] if matches and matches[0].score >= settings.reuse_similarity else None
            source_page = self.db.get(Page, best.page_id) if best else None
            if source_page is not None and (not self.reuse_concepts or not self._reusable(source_page)):
                logger.info("Not reusing concepts of page %s (made by %r)", source_page.id, source_page.concepts_model)
                best, source_page = None, None

            page = Page(
                chapter_id=chapter.id, page_number=number, content_text=text,
                layout_data=p_data.get("lines"), uploaded_by_id=user_id,
            )
            apply_fingerprint(page, text)
            self.db.add(page)
            self.db.flush()  # also makes this page's bands visible to the next page's lookup

            recap = looks_like_recap_page(text) or tail
            filtered = False
            if tail:
                best, source_page = None, None
                page.concepts_model = self.model_name
                page.page_kind = "exercise"  # after the chapter-end summary everything is exercise material
                concepts, filtered = [], True
            elif best:
                pages_reused += 1
                logger.info("Page %s matches %s (%.2f); reusing concepts", number, best.page_id, best.score)
                page.concepts_model = source_page.concepts_model
                page.page_kind = source_page.page_kind or "content"
                if recap and page.page_kind == "content":
                    page.page_kind = heading_page_kind(text) or "recap"
                concepts = [
                    (c.name, c.description, c.learning_objectives, c.prerequisites)
                    for c in sorted(source_page.concepts, key=lambda c: c.position)
                ]
                kept = [] if recap else [c for c in concepts if not looks_like_activity(c[0])]
                filtered = len(kept) != len(concepts)
                dropped_concepts += len(concepts) - len(kept)
                concepts = kept
            else:
                page.concepts_model = self.model_name
                try:
                    extraction = extract_page(self.llm, text)
                except ConceptExtractionError as exc:
                    raise ProcessingError(f"{exc} (page {number})") from exc
                dropped_concepts += extraction.dropped
                filtered = extraction.dropped > 0
                recap = recap or extraction.page_kind in ("recap", "exercise")
                page.page_kind = extraction.page_kind
                concepts = [(c.name, c.description, c.learning_objectives, c.prerequisites) for c in extraction.concepts]
            recap_pages += 1 if recap else 0

            if best and source_page.needs_review:  # a reused page keeps its source's verdict, never a fresh one
                page.needs_review, page.review_note = True, source_page.review_note
                review_pages.append({"page": number, "note": page.review_note})
            elif not best and not concepts and not filtered and not recap and len(tokenize(text)) >= REVIEW_MIN_WORDS:
                page.needs_review = True
                page.review_note = "No concepts were found on a page with a lot of text. It may be a bad scan."
                review_pages.append({"page": number, "note": page.review_note})

            new_concepts: list[Concept] = []
            for position, (name, description, objectives, prerequisites) in enumerate(concepts):
                concept = Concept(
                    page_id=page.id, name=name, description=description, position=position,
                    learning_objectives=objectives, prerequisites=prerequisites,
                )
                self.db.add(concept)
                new_concepts.append(concept)
            created.append(page)
            if best and not filtered:
                reused_from.append((page, source_page, new_concepts))
            elif tail or (not signature and not concepts):
                short_empty_pages.append(number)  # a page with no concepts by design is neutral for copying
            else:
                uncovered += 1

        chapter.match_report = {
            "ocr_reused": ocr_reused,
            "pages_checked": pages_checked,
            "pages_reused": pages_reused,
            "suggestions": summarize_book_matches(
                per_page_matches, pages_checked, chapter.book_id, user_id
            ),
        }

        # A chapter only becomes 'ready' (the caller's commit) once its concepts are linked into a graph.
        self.db.flush()
        report = self._copied_graph(chapter, reused_from, uncovered, short_empty_pages)
        if report is None:
            report = build_chapter_graph(self.db, chapter, self.llm, self._name_embedder())
        counters = {"dropped_concepts": dropped_concepts, "recap_pages": recap_pages}
        if report.get("edges_copied"):  # same pages as the source: its counters are the right ones
            counters = {k: report.get(k, v) for k, v in counters.items()}
        chapter.graph_report = {**report, "review_pages": review_pages[:MAX_REVIEW_REPORTED], **counters}
        return created

    def _copied_graph(self, chapter, reused_from, uncovered, short_empty_pages):
        """Every page reused unchanged from ONE finished chapter with the same concepts -> copy its graph, so a
        second run over the same content gives the same edges (and costs no LLM call). None = build normally."""
        if uncovered or not reused_from:
            return None
        source_ids = {src.chapter_id for _, src, _ in reused_from}
        if len(source_ids) != 1:
            return None
        source = self.db.get(Chapter, source_ids.pop())
        if (
            source is None or source.id == chapter.id or source.status != ChapterStatus.READY
            or (source.graph_report or {}).get("llm_linking") != "done"
        ):
            return None
        source_concepts = self.db.scalars(
            select(Concept).join(Page, Page.id == Concept.page_id).where(Page.chapter_id == source.id)
        ).all()
        by_page: dict = {}
        for c in source_concepts:
            by_page.setdefault(c.page_id, []).append(c)
        source_pages = {p.id: p.page_number for p in self.db.scalars(select(Page).where(Page.chapter_id == source.id))}
        if any(source_pages[pid] in short_empty_pages for pid in by_page):
            return None
        concept_map: dict = {}
        for _, src_page, new_concepts in reused_from:
            old = sorted(by_page.get(src_page.id, []), key=lambda c: c.position)
            if len(old) != len(new_concepts):
                return None
            concept_map.update({o.id: n for o, n in zip(old, new_concepts)})
        if set(concept_map) != {c.id for c in source_concepts}:
            return None  # the source has concepts on pages we did not reuse
        try:
            return copy_chapter_graph(self.db, chapter, source, concept_map)
        except KeyError:
            return None
</file>

<file path="backend/app/pipeline/structure.py">
"""Layer 3: the chapter-title sequence as a third way to say 'this book looks like an edition of that one'.

Pages can differ a lot between editions (re-typeset, reworded, bad scan) while the book keeps the same chapters
in the same order, often with slightly different titles ('Exploration and Entering' / 'Exploration: Entering the
World of Secondary Science'). So titles are compared by word overlap, and what counts is the longest run of
my chapters whose matches appear in the SAME ORDER in the other book. It needs no page text, so it also works
before a single chapter has been processed, and it only ever adds SUGGESTIONS (the teacher still confirms
`variant_of`). Exercise numbering, the other half of the original idea, is not used: it would need parsing page
text and is too fragile to trust.

Privacy: only official books and the teacher's own other books are compared, exactly like the page signals."""
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.content import Book, Chapter, ChapterStatus

STOP = {"a", "an", "the", "of", "and", "in", "to", "for", "on", "with", "our", "its", "is", "are", "at", "by", "from", "chapter", "unit", "lesson"}


def title_words(title: str) -> frozenset:
    """Lower-case words without filler and numbering ('Chapter 2: ...' -> the title only)."""
    return frozenset(w for w in re.findall(r"[a-z0-9]+", (title or "").lower()) if w not in STOP and not w.isdigit())


def title_overlap(a: frozenset, b: frozenset) -> float:
    """Share of the SHORTER title's words that the other title has. Empty titles never match."""
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


def ordered_matches(mine: list[str], other: list[str]) -> tuple[int, float]:
    """(how many of my chapters match chapters of `other` in the same order, their average overlap).
    Each of my chapters is paired with its best-matching title; the answer is the longest in-order run."""
    other_words = [title_words(t) for t in other]
    pairs: list[tuple[int, float]] = []  # per chapter of mine: (position in other, overlap) or (-1, 0)
    for title in mine:
        words = title_words(title)
        best = (-1, 0.0)
        for pos, ow in enumerate(other_words):
            score = title_overlap(words, ow)
            if score >= settings.structure_title_overlap and score > best[1]:
                best = (pos, score)
        pairs.append(best)
    # longest strictly increasing run of positions (small inputs, so the simple O(n^2) version)
    length = [0] * len(pairs)
    total = [0.0] * len(pairs)
    for i, (pos, score) in enumerate(pairs):
        if pos < 0:
            continue
        length[i], total[i] = 1, score
        for j in range(i):
            if pairs[j][0] >= 0 and pairs[j][0] < pos and length[j] + 1 > length[i]:
                length[i], total[i] = length[j] + 1, total[j] + score
    if not length or max(length) == 0:
        return 0, 0.0
    k = max(range(len(length)), key=lambda i: (length[i], total[i]))
    return length[k], total[k] / length[k]


def _titles(db: Session, book_id, ready_only: bool) -> list[str]:
    query = select(Chapter.title).where(Chapter.book_id == book_id).order_by(Chapter.sequence_num)
    if ready_only:
        query = query.where(Chapter.status == ChapterStatus.READY)
    return [t for (t,) in db.execute(query)]


def suggest(db: Session, book: Book, teacher_id, exclude=frozenset()) -> list[dict]:
    """Books (official, or the teacher's own) whose chapter titles follow the same order as `book`'s, best first.
    Needs >= structure_min_chapters in-order matches covering >= variant_min_coverage of this book's chapters.
    Only chapters that are already `ready` count on the OTHER side (an official book fills up over time)."""
    if not settings.structure_enabled:
        return []
    mine = _titles(db, book.id, ready_only=False)
    if len(mine) < settings.structure_min_chapters:
        return []
    candidates = db.scalars(select(Book).where(
        Book.id != book.id, (Book.is_reference.is_(True)) | (Book.owner_teacher_id == teacher_id)))
    found = []
    for other in candidates:
        if other.id in exclude:
            continue
        theirs = _titles(db, other.id, ready_only=True)
        matched, avg = ordered_matches(mine, theirs)
        if matched < settings.structure_min_chapters or matched / len(mine) < settings.variant_min_coverage:
            continue
        found.append({"book": other, "matched_chapters": matched, "chapters_checked": len(mine),
                      "coverage": round(matched / len(mine), 3), "avg_overlap": round(avg, 3),
                      "candidate_chapters_loaded": len(theirs)})
    return sorted(found, key=lambda h: (h["coverage"], h["avg_overlap"]), reverse=True)
</file>

<file path="backend/app/student/__init__.py">

</file>

<file path="backend/app/student/request_routes.py">
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import require_student
from app.content_library import access, link_requests
from app.db.session import get_db
from app.models import Book, ChapterRequest
from app.schemas import BookBrief, ChapterRequestCreate, ChapterRequestOut

router = APIRouter()


def _out(request: ChapterRequest, book: Book) -> ChapterRequestOut:
    return ChapterRequestOut(
        id=request.id, book=BookBrief.model_validate(book), chapter_hint=request.chapter_hint,
        chapter_id=request.chapter_id, status=request.status, created_at=request.created_at,
        resolved_at=request.resolved_at,
    )


@router.post("/books/{book_id}/chapter-requests", response_model=ChapterRequestOut, status_code=status.HTTP_201_CREATED)
def request_chapter(
    book_id: uuid.UUID, body: ChapterRequestCreate, response: Response,
    student=Depends(require_student), db: Session = Depends(get_db),
):
    """Ask the book's teacher to add a chapter that isn't available yet. Only for books you've linked."""
    book = access.get_linked_book(db, student, book_id)
    request, created = link_requests.create_request(db, student, book, body.chapter_hint, body.chapter_id)
    if not created:
        response.status_code = status.HTTP_200_OK
    return _out(request, book)


@router.get("/chapter-requests", response_model=list[ChapterRequestOut])
def my_requests(student=Depends(require_student), db: Session = Depends(get_db)):
    rows = db.execute(
        select(ChapterRequest, Book)
        .join(Book, Book.id == ChapterRequest.book_id)
        .where(ChapterRequest.student_id == student.id)
        .order_by(ChapterRequest.created_at.desc())
    ).all()
    return [_out(r, b) for r, b in rows]


@router.delete("/chapter-requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_request(request_id: uuid.UUID, student=Depends(require_student), db: Session = Depends(get_db)):
    request = db.get(ChapterRequest, request_id)
    if request is None or request.student_id != student.id:
        raise HTTPException(404, "Request not found")
    if request.status == "open":
        link_requests.resolve(db, request, "cancelled")
        db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
</file>

<file path="backend/app/student/routes.py">
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.dependencies import require_student
from app.content_library import access
from app.content_library.graph_view import chapter_graph
from app.core.config import settings
from app.core.ratelimit import limiter
from app.db.session import get_db
from app.models.content import Book, Chapter, ChapterStatus, Page, student_book
from app.models.room import Room, RoomMember
from app.schemas import BookOut, ChapterGraphOut, JoinRoomIn, PageOut, RoomOut

def _student_view(book: Book) -> BookOut:
    """Students only see chapters that finished processing."""
    out = BookOut.model_validate(book)
    out.chapters = [c for c in out.chapters if c.status == ChapterStatus.READY]
    return out


router = APIRouter(prefix="/student", tags=["student"], dependencies=[Depends(require_student)])


@router.get("/ping")
def ping(user=Depends(require_student)):
    return {"role": user.role}


# ---- rooms -----------------------------------------------------------------

@router.post("/rooms/join", response_model=RoomOut)
def join_room(body: JoinRoomIn, student=Depends(require_student), db: Session = Depends(get_db)):
    limiter.check("join-room", str(student.id), settings.rate_join_per_min, 60)
    room = db.scalar(select(Room).where(func.lower(Room.join_code) == body.join_code.lower()))
    if room is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invalid join code")

    already = db.scalar(select(RoomMember.id).where(RoomMember.room_id == room.id, RoomMember.user_id == student.id))
    if already:
        raise HTTPException(status.HTTP_409_CONFLICT, "You are already in this room")

    try:
        db.add(RoomMember(room_id=room.id, user_id=student.id))
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "You are already in this room")
    return room


@router.get("/rooms", response_model=list[RoomOut])
def my_rooms(student=Depends(require_student), db: Session = Depends(get_db)):
    return db.scalars(
        select(Room).join(RoomMember, RoomMember.room_id == Room.id)
        .where(RoomMember.user_id == student.id).order_by(RoomMember.joined_at.desc())
    ).all()


# ---- books -----------------------------------------------------------------

@router.get("/library", response_model=list[BookOut])
def library(student=Depends(require_student), db: Session = Depends(get_db)):
    """Books this student may link but hasn't yet: reference books + books of teachers whose room they joined."""
    linked = select(student_book.c.book_id).where(student_book.c.student_id == student.id)
    query = access.student_visible_books(student).where(Book.id.not_in(linked))
    books = db.scalars(query.order_by(Book.is_reference.desc(), Book.board, Book.class_name, Book.subject)).all()
    return [_student_view(b) for b in books]


@router.get("/books", response_model=list[BookOut])
def my_books(student=Depends(require_student), db: Session = Depends(get_db)):
    books = db.scalars(
        select(Book).join(student_book, student_book.c.book_id == Book.id)
        .where(student_book.c.student_id == student.id)
    ).all()
    return [_student_view(b) for b in books]


@router.get("/books/{book_id}", response_model=BookOut)
def get_book_details(book_id: uuid.UUID, student=Depends(require_student), db: Session = Depends(get_db)):
    return _student_view(access.get_book_visible_to_student(db, student, book_id))


@router.post("/books/{book_id}/link", status_code=status.HTTP_200_OK)
def link_book(book_id: uuid.UUID, student=Depends(require_student), db: Session = Depends(get_db)):
    book = access.get_book_visible_to_student(db, student, book_id)
    existing = db.execute(
        select(student_book).where(student_book.c.student_id == student.id, student_book.c.book_id == book.id)
    ).first()
    if existing:
        return {"status": "already_linked", "book_id": book.id}
    db.execute(student_book.insert().values(student_id=student.id, book_id=book.id))
    db.commit()
    return {"status": "linked", "book_id": book.id}


@router.delete("/books/{book_id}/link", status_code=status.HTTP_204_NO_CONTENT)
def unlink_book(book_id: uuid.UUID, student=Depends(require_student), db: Session = Depends(get_db)):
    db.execute(student_book.delete().where(student_book.c.student_id == student.id, student_book.c.book_id == book_id))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/books/{book_id}/chapters/{chapter_id}/pages", response_model=list[PageOut])
def get_chapter_pages(book_id: uuid.UUID, chapter_id: uuid.UUID, student=Depends(require_student), db: Session = Depends(get_db)):
    book = access.get_linked_book(db, student, book_id)  # page content only for books the student has linked
    chapter = db.scalar(
        select(Chapter).where(
            Chapter.id == chapter_id, Chapter.book_id == book.id, Chapter.status == ChapterStatus.READY
        )
    )
    if not chapter:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chapter not found")
    return db.scalars(select(Page).where(Page.chapter_id == chapter.id).order_by(Page.page_number)).all()


@router.get("/books/{book_id}/chapters/{chapter_id}/graph", response_model=ChapterGraphOut)
def get_chapter_graph(book_id: uuid.UUID, chapter_id: uuid.UUID, student=Depends(require_student), db: Session = Depends(get_db)):
    book = access.get_linked_book(db, student, book_id)
    chapter = db.scalar(
        select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book.id, Chapter.status == ChapterStatus.READY)
    )
    if not chapter:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chapter not found")
    return chapter_graph(db, chapter)


from app.student.request_routes import router as _request_router  # noqa: E402

router.include_router(_request_router)
</file>

<file path="backend/app/teacher/__init__.py">

</file>

<file path="backend/app/teacher/request_routes.py">
import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import require_teacher
from app.content_library import link_requests
from app.db.session import get_db
from app.models import Book, Chapter, ChapterRequest, ChapterStatus, User
from app.schemas import BookBrief, ChapterRequestOut, FulfillRequestIn

router = APIRouter()


def _out(request: ChapterRequest, book: Book, student: User) -> ChapterRequestOut:
    return ChapterRequestOut(
        id=request.id, book=BookBrief.model_validate(book), chapter_hint=request.chapter_hint,
        chapter_id=request.chapter_id, status=request.status, created_at=request.created_at,
        resolved_at=request.resolved_at, student_name=student.name,
    )


def _own_request(db: Session, teacher: User, request_id: uuid.UUID) -> ChapterRequest:
    request = db.get(ChapterRequest, request_id)
    if request is None or request.teacher_id != teacher.id:
        raise HTTPException(404, "Request not found")
    return request


@router.get("/chapter-requests", response_model=list[ChapterRequestOut])
def list_requests(
    status: Literal["open", "fulfilled", "dismissed", "cancelled", "all"] = "open",
    teacher=Depends(require_teacher), db: Session = Depends(get_db),
):
    query = (
        select(ChapterRequest, Book, User)
        .join(Book, Book.id == ChapterRequest.book_id)
        .join(User, User.id == ChapterRequest.student_id)
        .where(ChapterRequest.teacher_id == teacher.id)
        .order_by(ChapterRequest.created_at.desc())
    )
    if status != "all":
        query = query.where(ChapterRequest.status == status)
    return [_out(r, b, s) for r, b, s in db.execute(query).all()]


@router.post("/chapter-requests/{request_id}/dismiss", response_model=ChapterRequestOut)
def dismiss_request(request_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    request = _own_request(db, teacher, request_id)
    if request.status != "open":
        raise HTTPException(409, "This request is already closed")
    link_requests.resolve(db, request, "dismissed")
    db.commit()
    return _out(request, db.get(Book, request.book_id), db.get(User, request.student_id))


@router.post("/chapter-requests/{request_id}/fulfill", response_model=ChapterRequestOut)
def fulfill_request(request_id: uuid.UUID, body: FulfillRequestIn, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    """Mark a request done (optionally pointing at the chapter that now covers it). Requests are also closed
    automatically when a matching chapter finishes processing."""
    request = _own_request(db, teacher, request_id)
    if request.status != "open":
        raise HTTPException(409, "This request is already closed")
    if body.chapter_id is not None:
        chapter = db.scalar(select(Chapter).where(Chapter.id == body.chapter_id, Chapter.book_id == request.book_id))
        if chapter is None:
            raise HTTPException(404, "Chapter not found in that book")
        if chapter.status != ChapterStatus.READY:
            raise HTTPException(409, "That chapter hasn't finished processing yet")
        request.chapter_id = chapter.id
    link_requests.resolve(db, request, "fulfilled")
    db.commit()
    return _out(request, db.get(Book, request.book_id), db.get(User, request.student_id))
</file>

<file path="backend/app/teacher/rooms.py">
import uuid

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.codes import generate_unique_code
from app.models import Room, RoomMember, RoomType, User
from app.schemas import MemberOut, RoomOut


def create_room(db: Session, teacher: User, name: str, room_type: RoomType) -> Room:
    code = generate_unique_code(
        lambda c: db.scalar(select(Room.id).where(Room.join_code == c)) is not None, length=6
    )
    room = Room(teacher_id=teacher.id, name=name, room_type=room_type, join_code=code)
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


def list_rooms(db: Session, teacher: User) -> list[RoomOut]:
    rows = db.execute(
        select(Room, func.count(RoomMember.id))
        .outerjoin(RoomMember, RoomMember.room_id == Room.id)
        .where(Room.teacher_id == teacher.id)
        .group_by(Room.id)
        .order_by(Room.created_at.desc())
    ).all()
    return [RoomOut.model_validate(room).model_copy(update={"member_count": n}) for room, n in rows]


def get_owned_room(db: Session, teacher: User, room_id: uuid.UUID) -> Room:
    """Ownership check: another teacher's room looks like it doesn't exist."""
    room = db.scalar(select(Room).where(Room.id == room_id, Room.teacher_id == teacher.id))
    if room is None:
        raise HTTPException(404, "Room not found")
    return room


def list_members(db: Session, room: Room) -> list[MemberOut]:
    from app.schemas import MemberOut
    from app.models.user import User
    from app.models.room import RoomMember
    
    rows = db.execute(
        select(User.id, User.name, RoomMember.joined_at)
        .join(RoomMember, RoomMember.user_id == User.id)
        .where(RoomMember.room_id == room.id)
        .order_by(RoomMember.joined_at)
    ).all()
    
    # We now map the tuple (id, name, joined_at) directly to the schema
    return [MemberOut(id=row.id, name=row.name, joined_at=row.joined_at) for row in rows]
</file>

<file path="backend/app/teacher/routes.py">
import uuid
from typing import Literal, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Response, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.dependencies import require_teacher
from app.content_library import access
from app.content_library import deletion, feedback
from app.content_library import upload as uploads
from app.content_library.graph_view import chapter_graph
from app.content_library.search import search_books
from app.core.config import settings
from app.core.storage import save_by_hash
from app.db.session import get_db, get_session_factory
from app.models.content import Book, Chapter, ChapterStatus, MatchFeedback, Page, student_book
from app.models.room import RoomMember, RoomType
from app.pipeline import structure
from app.pipeline.jobs import is_actively_processing, mark_processing, run_chapter_job
from app.schemas import BulkLinkOut, ChapterMatchesOut, ChapterMatchOut, BookBrief, BookCreate, BookOut, ChapterCreate, ChapterGraphOut, ChapterOut, VariantOfIn, VariantSuggestionOut, MemberOut, PageOut, RoomCreate, RoomOut
from app.teacher import rooms as svc

router = APIRouter(prefix="/teacher", tags=["teacher"], dependencies=[Depends(require_teacher)])


@router.get("/ping")
def ping(user=Depends(require_teacher)):
    return {"role": user.role}


# ---- rooms -----------------------------------------------------------------

@router.post("/rooms", response_model=RoomOut, status_code=status.HTTP_201_CREATED)
def create_room(body: RoomCreate, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    return svc.create_room(db, teacher, body.name, body.room_type)


@router.get("/rooms", response_model=list[RoomOut])
def list_rooms(teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    return svc.list_rooms(db, teacher)


@router.get("/rooms/{room_id}/members", response_model=list[MemberOut])
def room_members(room_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    room = svc.get_owned_room(db, teacher, room_id)
    return svc.list_members(db, room)


@router.post("/rooms/{room_id}/books/{book_id}/link", response_model=BulkLinkOut)
def bulk_link_book(room_id: uuid.UUID, book_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    """Convenience: link a book to every student currently in a single-class room. The links stay per-student
    (the room itself holds no content), and students who join later still link for themselves."""
    room = svc.get_owned_room(db, teacher, room_id)
    if room.room_type != RoomType.single_class:
        raise HTTPException(409, "Bulk linking is for single-class rooms, where everyone uses the same book. "
                                 "In a mixed room, students link their own books.")
    book = access.get_book_visible_to_teacher(db, teacher, book_id)
    members = set(db.scalars(select(RoomMember.user_id).where(RoomMember.room_id == room.id)).all())
    already = set(db.scalars(
        select(student_book.c.student_id).where(student_book.c.book_id == book.id, student_book.c.student_id.in_(members))
    ).all()) if members else set()
    new = members - already
    if new:
        db.execute(student_book.insert(), [{"student_id": sid, "book_id": book.id} for sid in new])
        db.commit()
    return BulkLinkOut(linked=len(new), already_linked=len(already), total_students=len(members))


# ---- books (reference corpus + this teacher's own uploads only) ------------------

@router.post("/books", response_model=BookOut, status_code=status.HTTP_201_CREATED)
def create_book(body: BookCreate, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    if body.variant_of_id is not None:
        # A variant may only point at a book this teacher can already see (never someone else's private book).
        access.get_book_visible_to_teacher(db, teacher, body.variant_of_id)
    draft = None
    if body.draft_id is not None:
        draft = uploads.get_draft(db, teacher, body.draft_id, "front_pages")
    elif settings.require_front_pages:
        raise HTTPException(422, "Upload the book's cover and publisher/edition pages first")
    book = Book(
        board=body.board.strip(),
        class_name=body.class_name.strip(),
        subject=body.subject.strip(),
        publisher=body.publisher.strip(),
        edition=body.edition,
        is_customized=body.is_customized,
        school=body.school,
        variant_of_id=body.variant_of_id,
        is_reference=False,  # reference books are created only by the seed/ingest scripts
        owner_teacher_id=teacher.id,
        metadata_source="front_pages" if draft else "manual",
        extracted_metadata=(draft.payload or {}).get("metadata") if draft else None,
        front_pages_file=draft.source_file if draft else None,
    )
    db.add(book)
    if draft:
        db.delete(draft)  # consumed: the teacher has confirmed the metadata
    db.commit()
    db.refresh(book)
    return book


@router.get("/books", response_model=list[BookOut])
def list_books(
    scope: Literal["all", "mine", "reference"] = "all",
    q: Optional[str] = None,
    board: Optional[str] = None,
    class_name: Optional[str] = None,
    subject: Optional[str] = None,
    publisher: Optional[str] = None,
    teacher=Depends(require_teacher),
    db: Session = Depends(get_db),
):
    """Search the library: official books + your own. Filters are case-insensitive 'contains';
    `q` matches any of board/class/subject/publisher/edition/school; class 'IX' and 'Class 9' are the same."""
    query = search_books(db, teacher, q=q, board=board, class_name=class_name, subject=subject,
                         publisher=publisher, scope=scope)
    return db.scalars(query).all()


@router.get("/books/{book_id}", response_model=BookOut)
def get_book(book_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    return access.get_book_visible_to_teacher(db, teacher, book_id)


@router.post("/books/{book_id}/chapters", response_model=ChapterOut, status_code=status.HTTP_201_CREATED)
def create_chapter(book_id: uuid.UUID, body: ChapterCreate, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    book = access.get_owned_book(db, teacher, book_id)
    chapter = Chapter(book_id=book.id, title=body.title, sequence_num=body.sequence_num)
    db.add(chapter)
    db.commit()
    db.refresh(chapter)
    return chapter


@router.get("/books/{book_id}/chapters", response_model=list[ChapterOut])
def list_chapters(book_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    book = access.get_book_visible_to_teacher(db, teacher, book_id)
    return db.scalars(select(Chapter).where(Chapter.book_id == book.id).order_by(Chapter.sequence_num)).all()


def _owned_chapter(db: Session, teacher, book_id: uuid.UUID, chapter_id: uuid.UUID) -> Chapter:
    book = access.get_owned_book(db, teacher, book_id)
    chapter = db.scalar(select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book.id))
    if not chapter:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chapter not found in this book")
    return chapter


@router.post(
    "/books/{book_id}/chapters/{chapter_id}/pages/upload",
    response_model=ChapterOut,
    status_code=status.HTTP_202_ACCEPTED,
)
def teacher_upload_pages(
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    response: Response,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    teacher=Depends(require_teacher),
    db: Session = Depends(get_db),
    session_factory=Depends(get_session_factory),
):
    """Saves the file and starts processing in the background. Poll the chapter's `status`.
    Uploading again REPLACES the chapter's pages (one file per chapter)."""
    chapter = _owned_chapter(db, teacher, book_id, chapter_id)
    if is_actively_processing(chapter):
        raise HTTPException(status.HTTP_409_CONFLICT, "This chapter is still being processed. Please wait for it to finish.")

    upload = uploads.read_validated_upload(file, settings.max_upload_mb)
    data, ext, digest = upload.data, upload.ext, upload.sha256
    if chapter.status == ChapterStatus.READY and chapter.source_sha256 == digest:
        response.status_code = status.HTTP_200_OK  # same file as last time: nothing to redo
        return chapter

    chapter.source_file = save_by_hash(data, digest, ext)
    chapter.source_sha256 = digest
    mark_processing(chapter)
    db.commit()
    db.refresh(chapter)
    background_tasks.add_task(run_chapter_job, chapter.id, teacher.id, session_factory)
    return chapter


@router.post(
    "/books/{book_id}/chapters/{chapter_id}/retry",
    response_model=ChapterOut,
    status_code=status.HTTP_202_ACCEPTED,
)
def retry_chapter(
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    teacher=Depends(require_teacher),
    db: Session = Depends(get_db),
    session_factory=Depends(get_session_factory),
):
    """Re-runs processing on the file already uploaded, after a failure (or a stuck job)."""
    chapter = _owned_chapter(db, teacher, book_id, chapter_id)
    if is_actively_processing(chapter):
        raise HTTPException(status.HTTP_409_CONFLICT, "This chapter is still being processed.")
    if chapter.status not in (ChapterStatus.FAILED, ChapterStatus.PROCESSING) or not chapter.source_file:
        raise HTTPException(status.HTTP_409_CONFLICT, "Nothing to retry for this chapter")
    mark_processing(chapter)
    db.commit()
    db.refresh(chapter)
    background_tasks.add_task(run_chapter_job, chapter.id, teacher.id, session_factory)
    return chapter


@router.get("/books/{book_id}/chapters/{chapter_id}/pages", response_model=list[PageOut])
def list_chapter_pages(book_id: uuid.UUID, chapter_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    book = access.get_book_visible_to_teacher(db, teacher, book_id)
    chapter = db.scalar(select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book.id))
    if not chapter:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chapter not found in this book")
    return db.scalars(select(Page).where(Page.chapter_id == chapter.id).order_by(Page.page_number)).all()


@router.get("/books/{book_id}/chapters/{chapter_id}/graph", response_model=ChapterGraphOut)
def get_chapter_graph(book_id: uuid.UUID, chapter_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    book = access.get_book_visible_to_teacher(db, teacher, book_id)
    chapter = db.scalar(select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book.id))
    if not chapter:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chapter not found in this book")
    return chapter_graph(db, chapter)


# ---- variants: "this looks like an edition of book X" ---------------------------------------

def _chapter_matches(db: Session, teacher, book: Book) -> list[ChapterMatchesOut]:
    """Per finished chapter of this book: which chapters of OTHER books (official, or the teacher's own) it
    matches. Visibility is re-checked now, because the stored report may be old."""
    chapters = db.scalars(
        select(Chapter).where(Chapter.book_id == book.id, Chapter.status == ChapterStatus.READY).order_by(Chapter.sequence_num)
    ).all()
    visible: dict[str, Book | None] = {}
    out = []
    for chapter in chapters:
        matches = []
        for s in (chapter.match_report or {}).get("suggestions", []):
            if s["book_id"] not in visible:
                try:
                    visible[s["book_id"]] = access.get_book_visible_to_teacher(db, teacher, uuid.UUID(s["book_id"]))
                except HTTPException:
                    visible[s["book_id"]] = None
            base = visible[s["book_id"]]
            if base is None:
                continue
            matches.append(ChapterMatchOut(
                book=BookBrief.model_validate(base),
                chapter_id=uuid.UUID(s["chapter_id"]) if s.get("chapter_id") else None,
                chapter_title=s.get("chapter_title"),
                kind=s["kind"], matched_pages=s["matched_pages"], pages_checked=s["pages_checked"],
                avg_similarity=s["avg_similarity"], signal=s.get("signal", "fingerprint"),
            ))
        out.append(ChapterMatchesOut(chapter_id=chapter.id, chapter_title=chapter.title, matches=matches))
    return out


@router.get("/books/{book_id}/chapter-matches", response_model=list[ChapterMatchesOut])
def chapter_matches(book_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    """Chapter by chapter: 'your chapter X is identical to / an edition of chapter Y in book Z'.
    Never includes other teachers' private books."""
    return _chapter_matches(db, teacher, access.get_owned_book(db, teacher, book_id))


@router.get("/books/{book_id}/variant-suggestions", response_model=list[VariantSuggestionOut])
def variant_suggestions(book_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    """Books that look like the base of this one, judged CHAPTER by chapter: a book is suggested when at least
    half of your finished chapters each match a chapter of it. (Counting pages across the whole book would let
    one long chapter swamp the result, and a partly loaded official book would look like a poor match.)
    Suggestions the teacher dismissed are not offered again."""
    return _variant_suggestions(db, teacher, access.get_owned_book(db, teacher, book_id))


def _variant_suggestions(db: Session, teacher, book: Book) -> list[VariantSuggestionOut]:
    per_chapter = [c for c in _chapter_matches(db, teacher, book)]
    checked = [
        c for c in per_chapter
        if (db.get(Chapter, c.chapter_id).match_report or {}).get("pages_checked", 0) > 0
    ]
    pooled: dict[uuid.UUID, dict] = {}
    for chapter in checked:
        for m in chapter.matches:
            agg = pooled.setdefault(m.book.id, {"book": m.book, "chapters": 0, "pages": 0, "sim_sum": 0.0, "checked": 0})
            agg["chapters"] += 1
            agg["pages"] += m.matched_pages
            agg["sim_sum"] += m.avg_similarity * m.matched_pages
    pages_total = sum((db.get(Chapter, c.chapter_id).match_report or {}).get("pages_checked", 0) for c in checked)

    out = []
    for base_id, agg in pooled.items():
        coverage = agg["chapters"] / len(checked)
        if coverage < settings.variant_min_coverage or base_id == book.variant_of_id:
            continue
        avg = agg["sim_sum"] / agg["pages"]
        loaded = db.scalar(select(func.count()).select_from(Chapter).where(
            Chapter.book_id == base_id, Chapter.status == ChapterStatus.READY)) or 0
        out.append(VariantSuggestionOut(
            book=agg["book"], kind="same" if avg >= settings.reuse_similarity else "variant",
            coverage=round(coverage, 3), matched_chapters=agg["chapters"], chapters_checked=len(checked),
            candidate_chapters_loaded=loaded, avg_similarity=round(avg, 3),
            matched_pages=agg["pages"], pages_checked=pages_total,
        ))
    dismissed = feedback.dismissed_ids(db, book.id)
    out = sorted((v for v in out if v.book.id not in dismissed), key=lambda v: (v.coverage, v.avg_similarity), reverse=True)[:3]
    # Layer 3: books whose chapter titles follow the same order. Only for books the page evidence did not already
    # find, after it and only while there is room; works before a single page has been processed.
    seen = {v.book.id for v in out} | dismissed | ({book.variant_of_id} if book.variant_of_id else set())
    for hit in structure.suggest(db, book, teacher.id, exclude=seen)[: max(0, 3 - len(out))]:
        out.append(VariantSuggestionOut(
            book=BookBrief.model_validate(hit["book"]), kind="variant", coverage=hit["coverage"],
            matched_chapters=hit["matched_chapters"], chapters_checked=hit["chapters_checked"],
            candidate_chapters_loaded=hit["candidate_chapters_loaded"], avg_similarity=hit["avg_overlap"],
            matched_pages=0, pages_checked=0, signal="structure",
        ))
    return out


@router.post("/books/{book_id}/variant-of", response_model=BookOut)
def confirm_variant(book_id: uuid.UUID, body: VariantOfIn, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    """The teacher confirms 'my book is a variant of that one'."""
    book = access.get_owned_book(db, teacher, book_id)
    base = access.get_book_visible_to_teacher(db, teacher, body.base_book_id)
    if base.id == book.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "A book can't be a variant of itself")
    ancestor, hops = base, 0
    while ancestor is not None and hops < 50:  # refuse loops: base must not already descend from this book
        if ancestor.variant_of_id == book.id:
            raise HTTPException(status.HTTP_409_CONFLICT, "That book is already a variant of this one")
        ancestor = db.get(Book, ancestor.variant_of_id) if ancestor.variant_of_id else None
        hops += 1
    shown = next((v for v in _variant_suggestions(db, teacher, book) if v.book.id == base.id), None)  # what the teacher was shown
    if book.variant_of_id is not None and book.variant_of_id != base.id:
        feedback.record(db, book.id, book.variant_of_id, "retracted")  # switched to a different base
    feedback.record(db, book.id, base.id, "confirmed", shown.model_dump(mode="json", exclude={"book"}) if shown else None)
    book.variant_of_id = base.id
    db.commit()
    db.refresh(book)
    return book


@router.delete("/books/{book_id}/variant-of", status_code=status.HTTP_204_NO_CONTENT)
def clear_variant(book_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    book = access.get_owned_book(db, teacher, book_id)
    if book.variant_of_id is not None:
        feedback.record(db, book.id, book.variant_of_id, "retracted")  # a correction; the suggestion may be offered again
    book.variant_of_id = None
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_book(book_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    """Delete one of YOUR books with all its chapters. Students linked to it lose access to it."""
    deletion.delete_book(db, access.get_owned_book(db, teacher, book_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/books/{book_id}/chapters/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_chapter(book_id: uuid.UUID, chapter_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    """Delete one chapter of one of YOUR books."""
    book = access.get_owned_book(db, teacher, book_id)
    chapter = db.get(Chapter, chapter_id)
    if chapter is None or chapter.book_id != book.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chapter not found")
    deletion.delete_chapter(db, chapter)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/books/{book_id}/variant-suggestions/dismiss", status_code=status.HTTP_204_NO_CONTENT)
def dismiss_variant_suggestion(book_id: uuid.UUID, body: VariantOfIn, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    """'No, that is not the base of my book': the suggestion is not offered again for this book."""
    book = access.get_owned_book(db, teacher, book_id)
    base = access.get_book_visible_to_teacher(db, teacher, body.base_book_id)
    if base.id == book.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "A book can't be a variant of itself")
    if base.id == book.variant_of_id:
        raise HTTPException(status.HTTP_409_CONFLICT, "You confirmed this book as the base; clear that first")
    shown = next((v for v in _variant_suggestions(db, teacher, book) if v.book.id == base.id), None)
    feedback.record(db, book.id, base.id, "dismissed", shown.model_dump(mode="json", exclude={"book"}) if shown else None)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/books/{book_id}/variant-suggestions/dismiss/{base_book_id}", status_code=status.HTTP_204_NO_CONTENT)
def undo_dismiss(book_id: uuid.UUID, base_book_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    """Offer a dismissed suggestion again (idempotent)."""
    book = access.get_owned_book(db, teacher, book_id)
    row = db.scalar(select(MatchFeedback).where(
        MatchFeedback.book_id == book.id, MatchFeedback.base_book_id == base_book_id, MatchFeedback.decision == "dismissed"))
    if row is not None:
        db.delete(row)
        db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# front-pages drafts, whole-textbook upload, and student chapter requests live in their own modules
from app.teacher.request_routes import router as _request_router  # noqa: E402
from app.teacher.upload_routes import router as _upload_router  # noqa: E402

router.include_router(_upload_router)
router.include_router(_request_router)
</file>

<file path="backend/app/teacher/upload_routes.py">
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import require_teacher
from app.content_library import access
from app.content_library import upload as uploads
from app.core.config import settings
from app.core.ratelimit import limiter
from app.db.session import get_db, get_session_factory
from app.pipeline.jobs import run_chapter_job
from app.schemas import (
    BookBrief, BookMetadataOut, ChapterOut, FrontPagesDraftOut, WholeBookConfirmIn, WholeBookPlanOut,
)

from app.pipeline.front_matter import is_empty  # noqa: E402

router = APIRouter()  # included into the /teacher router (teacher guard + prefix come from there)


@router.post("/book-drafts/front-pages", response_model=FrontPagesDraftOut, status_code=status.HTTP_201_CREATED)
def upload_front_pages(file: UploadFile = File(...), teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    """Step 1 of adding a book: the cover + publisher/edition pages (a few pages, PDF or image).
    Returns the metadata the system read and any known books that already match it. Creates no Book:
    confirm by calling POST /teacher/books with the draft_id and the (edited) metadata."""
    limiter.check("front-pages", str(teacher.id), settings.rate_front_pages_per_hour, 3600)
    upload = uploads.read_validated_upload(file, settings.max_upload_mb)
    draft, metadata, matches = uploads.create_front_pages_draft(db, teacher, upload)
    warning = None
    if is_empty(metadata):
        chars = (draft.payload or {}).get("text_chars", 0)
        warning = (f"We read {chars} characters from these pages but could not find the book's details in them. "
                   "Upload the cover and the publisher/edition pages (clear scans), or fill the details in by hand.")
    return FrontPagesDraftOut(
        draft_id=draft.id, page_count=draft.page_count,
        metadata=BookMetadataOut(**metadata.model_dump()),
        matches=[BookBrief.model_validate(b) for b in matches],
        warning=warning,
    )


@router.post("/books/{book_id}/whole-book/plan", response_model=WholeBookPlanOut, status_code=status.HTTP_201_CREATED)
def plan_whole_book(book_id: uuid.UUID, file: UploadFile = File(...), teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    """Upload the entire textbook (PDF). Nothing is processed yet: the response proposes a chapter split
    (from the PDF's bookmarks, if any) for the teacher to review before confirming."""
    book = access.get_owned_book(db, teacher, book_id)
    limiter.check("whole-book-plan", str(teacher.id), settings.rate_whole_book_plan_per_hour, 3600)
    upload = uploads.read_validated_upload(file, settings.max_whole_book_mb, pdf_only=True)
    draft, proposed = uploads.create_whole_book_plan(db, teacher, book, upload)
    return WholeBookPlanOut(draft_id=draft.id, page_count=draft.page_count, proposed_chapters=proposed)


@router.post(
    "/books/{book_id}/whole-book/confirm", response_model=list[ChapterOut], status_code=status.HTTP_202_ACCEPTED
)
def confirm_whole_book(
    book_id: uuid.UUID,
    body: WholeBookConfirmIn,
    background_tasks: BackgroundTasks,
    teacher=Depends(require_teacher),
    db: Session = Depends(get_db),
    session_factory=Depends(get_session_factory),
):
    """Splits the uploaded PDF by the confirmed page ranges into new chapters and processes each in the background."""
    book = access.get_owned_book(db, teacher, book_id)
    draft = uploads.get_draft(db, teacher, body.draft_id, "whole_book", book.id)
    chapters = uploads.split_into_chapters(db, book, draft, body.chapters)
    db.delete(draft)
    db.commit()
    for chapter in chapters:
        db.refresh(chapter)
        background_tasks.add_task(run_chapter_job, chapter.id, teacher.id, session_factory)
    return chapters
</file>

<file path="backend/app/__init__.py">

</file>

<file path="backend/app/main.py">
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from supertokens_python import get_all_cors_headers
from supertokens_python.framework.fastapi import get_middleware

from app.admin.routes import router as admin_router
from app.auth.routes import router as auth_router
from app.auth.supertokens_config import init_supertokens
from app.core.config import settings
from app.core.errors import ProcessingError
from app.core.logging import setup_logging
from app.parent.routes import router as parent_router
from app.student.routes import router as student_router
from app.teacher.routes import router as teacher_router

setup_logging()
init_supertokens()

app = FastAPI(title="Tuition Companion API")

# get_middleware must be added before CORSMiddleware, so CORS ends up
# as the outer layer and handles preflight before SuperTokens sees the request.
app.add_middleware(get_middleware())
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type"] + get_all_cors_headers(),
)


@app.exception_handler(ProcessingError)
def processing_error_handler(request: Request, exc: ProcessingError):
    # ProcessingError messages are written to be safe to show to the teacher.
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(teacher_router)
app.include_router(admin_router)
app.include_router(student_router)
app.include_router(parent_router)
</file>

<file path="backend/app/schemas.py">
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.room import RoomType


# --- Auth & User Schemas ---
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    supertokens_user_id: str
    name: str
    username: str
    phone: str
    role: str
    link_code: Optional[str] = None
    created_at: datetime
    is_admin: bool = False  # may delete official books/chapters (see ADMIN_USERNAMES); only /auth/me fills it in


# --- Room Schemas ---
class RoomCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    room_type: RoomType = RoomType.single_class


class RoomOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    teacher_id: uuid.UUID
    name: str
    room_type: RoomType
    join_code: str
    created_at: datetime
    member_count: int = 0


class JoinRoomIn(BaseModel):
    join_code: str = Field(min_length=6, max_length=12)


# Replace the current MemberOut schema with this:
class MemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID        # This is the User ID
    name: str            # This is the User name
    joined_at: datetime  # When they joined the room
    


class RoomBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str


# --- Parent Schemas ---
class LinkStudentIn(BaseModel):
    link_code: str = Field(min_length=4, max_length=12)


class ChildOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    rooms: list[RoomBrief] = []


# --- Book, Chapter, Page, Concept Schemas ---
class ConceptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    learning_objectives: Optional[list[str]] = None
    prerequisites: Optional[list[str]] = None  # raw names from the page-level extraction
    is_canonical: bool = True
    prerequisite_ids: list[uuid.UUID] = []  # resolved links (only canonical concepts have any)


class GraphNodeOut(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    pages: list[int]  # every page where this concept appears


class GraphEdgeOut(BaseModel):
    prerequisite_id: uuid.UUID  # learn this first...
    concept_id: uuid.UUID  # ...before this
    source: str  # "page" (name match) or "llm" (chapter linking pass)


class CrossChapterEdgeOut(BaseModel):
    concept_id: uuid.UUID  # in THIS chapter
    prerequisite_id: uuid.UUID  # in an earlier chapter of the same book
    prerequisite_name: str
    prerequisite_chapter_id: uuid.UUID
    prerequisite_chapter_title: Optional[str] = None
    similarity: Optional[float] = None


class ChapterGraphOut(BaseModel):
    chapter_id: uuid.UUID
    status: str
    nodes: list[GraphNodeOut]
    edges: list[GraphEdgeOut]
    cross_chapter: list[CrossChapterEdgeOut] = []
    report: Optional[dict] = None


class ChapterMatchOut(BaseModel):
    """One of YOUR chapters matching a chapter of a book you can see."""
    book: "BookBrief"
    chapter_id: Optional[uuid.UUID] = None  # the matching chapter of that book
    chapter_title: Optional[str] = None
    kind: str  # "same" (near-identical pages) or "variant" (same content with edits)
    matched_pages: int
    pages_checked: int
    avg_similarity: float
    signal: str = "fingerprint"  # "fingerprint" (text overlap) or "embedding" (similar meaning; weaker evidence)


class ChapterMatchesOut(BaseModel):
    chapter_id: uuid.UUID
    chapter_title: str
    matches: list[ChapterMatchOut]


class VariantSuggestionOut(BaseModel):
    book: "BookBrief"
    kind: str  # "same" or "variant"
    coverage: float  # share of YOUR chapters that match a chapter of this book
    matched_chapters: int
    chapters_checked: int
    candidate_chapters_loaded: int  # how many finished chapters the suggested book has (official books fill up over time)
    avg_similarity: float
    matched_pages: int
    pages_checked: int
    signal: str = "pages"  # "pages" (text/meaning of the pages) or "structure" (same chapter titles in the same order; weaker evidence)


class BookBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    board: str
    class_name: str
    subject: str
    publisher: str
    edition: Optional[str] = None
    is_reference: bool = False


class VariantOfIn(BaseModel):
    base_book_id: uuid.UUID


class BookMetadataOut(BaseModel):
    board: Optional[str] = None
    class_name: Optional[str] = None
    subject: Optional[str] = None
    publisher: Optional[str] = None
    edition: Optional[str] = None
    is_customized: bool = False
    school: Optional[str] = None


class FrontPagesDraftOut(BaseModel):
    draft_id: uuid.UUID
    page_count: int
    metadata: BookMetadataOut  # what the system read; the teacher edits/confirms it
    matches: list["BookBrief"]  # known books (official first) that already match this metadata
    warning: Optional[str] = None  # set when nothing could be read from the pages, so the UI can say so


class ChapterRange(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    start_page: int = Field(ge=1)
    end_page: int = Field(ge=1)


class WholeBookPlanOut(BaseModel):
    draft_id: uuid.UUID
    page_count: int
    proposed_chapters: list[ChapterRange]  # from the PDF's bookmarks; empty if it has none


class WholeBookConfirmIn(BaseModel):
    draft_id: uuid.UUID
    chapters: list[ChapterRange]


class BulkLinkOut(BaseModel):
    linked: int
    already_linked: int
    total_students: int


class ChapterRequestCreate(BaseModel):
    chapter_hint: str = Field(min_length=3, max_length=200)
    chapter_id: Optional[uuid.UUID] = None


class ChapterRequestOut(BaseModel):
    id: uuid.UUID
    book: "BookBrief"
    chapter_hint: str
    chapter_id: Optional[uuid.UUID] = None
    status: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    student_name: Optional[str] = None  # only filled in for the teacher's view


class FulfillRequestIn(BaseModel):
    chapter_id: Optional[uuid.UUID] = None


class PageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    chapter_id: uuid.UUID
    page_number: int
    content_text: str
    needs_review: bool = False
    review_note: Optional[str] = None
    concepts: list[ConceptOut] = []


class ChapterCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    sequence_num: int = 1


class ChapterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    book_id: uuid.UUID
    title: str
    sequence_num: int
    status: str = "empty"
    error_message: Optional[str] = None


class BookCreate(BaseModel):
    board: str
    class_name: str
    subject: str
    publisher: str
    edition: Optional[str] = None
    is_customized: bool = False
    school: Optional[str] = None
    variant_of_id: Optional[uuid.UUID] = None
    draft_id: Optional[uuid.UUID] = None  # front-pages draft this Book is created from (see /teacher/book-drafts)


class BookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    board: str
    class_name: str
    subject: str
    publisher: str
    edition: Optional[str] = None
    is_customized: bool
    school: Optional[str] = None
    variant_of_id: Optional[uuid.UUID] = None
    is_reference: bool = False
    metadata_source: str = "manual"
    chapters: list[ChapterOut] = []
</file>

<file path="backend/tests/__init__.py">

</file>

<file path="backend/tests/conftest.py">
import os

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("SUPERTOKENS_CONNECTION_URI", "http://localhost:3567")

import pytest
from fastapi import HTTPException, Request, status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.dependencies import session_dependency
from app.db.session import get_db, get_session_factory
from app.main import app
from app.models import Base


class FakeSession:
    def __init__(self, user_id: str):
        self._user_id = user_id

    def get_user_id(self) -> str:
        return self._user_id


@pytest.fixture()
def session_factory():
    # Default: in-memory SQLite. Set TEST_DATABASE_URL (e.g. a throwaway local Postgres) to run the same
    # tests on the real database engine; tables are created and dropped around every test.
    url = os.environ.get("TEST_DATABASE_URL")
    if url:
        engine = create_engine(url)
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
    else:
        engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine, autoflush=False)
    if url:
        engine.dispose()


@pytest.fixture()
def client(session_factory):
    def override_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    def override_session(request: Request):
        # Stands in for a real session cookie: "Authorization: Bearer <supertokens_user_id>"
        auth = request.headers.get("authorization", "")
        if not auth.startswith("Bearer "):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
        return FakeSession(auth.removeprefix("Bearer "))

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[session_dependency] = override_session
    app.dependency_overrides[get_session_factory] = lambda: session_factory
    yield TestClient(app)
    app.dependency_overrides.clear()
    
@pytest.fixture(autouse=True)
def tmp_storage(tmp_path, monkeypatch):
    """Uploads go to a throwaway folder, never the real storage dir."""
    from app.core.config import settings

    monkeypatch.setattr(settings, "storage_dir", str(tmp_path / "storage"))


@pytest.fixture(autouse=True)
def fake_providers(monkeypatch):
    """Tests must never reach real Azure/LLM, even if a developer's .env sets
    OCR_PROVIDER=azure / LLM_PROVIDER=openai_compat (settings reads .env)."""
    from app.core.config import settings

    monkeypatch.setattr(settings, "ocr_provider", "fake")
    monkeypatch.setattr(settings, "llm_provider", "fake")
    # Same for embeddings and Memgraph: off unless a test switches them on (see the `indexing_on` fixture).
    monkeypatch.setattr(settings, "embedding_provider", "none")
    monkeypatch.setattr(settings, "graph_store_provider", "none")
    monkeypatch.setattr(settings, "embedding_dim", 64)


@pytest.fixture()
def indexing_on(monkeypatch):
    """Fake embeddings + the in-memory graph store, wired the way a configured deployment is."""
    from app.core.config import settings
    from app.graph_store import FAKE_STORE

    monkeypatch.setattr(settings, "embedding_provider", "fake")
    monkeypatch.setattr(settings, "graph_store_provider", "fake")
    FAKE_STORE.clear()
    FAKE_STORE.fail_with = None
    yield FAKE_STORE
    FAKE_STORE.clear()
    FAKE_STORE.fail_with = None


@pytest.fixture(autouse=True)
def fresh_rate_limits():
    """Rate-limit counters are process-wide; every test starts with a clean slate."""
    from app.core.ratelimit import limiter

    limiter.reset()
    yield
    limiter.reset()
</file>

<file path="backend/tests/test_book_access.py">
"""Content tenancy: who can see/change/link which Book (Rules.md §2 + §4)."""
import uuid

from app.models import Book, Role, User

FAKE_PDF = ("p.pdf", b"%PDF-1.4 fake", "application/pdf")


def make_user(session_factory, role: Role, tag: str):
    with session_factory() as db:
        user = User(
            supertokens_user_id=f"st-{tag}", name=tag, username=tag, phone="9" + tag[-3:], role=role,
            link_code=f"LNK{tag[-3:]}".upper()[:12] if role == Role.student else None,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        db.expunge(user)
    return user, {"Authorization": f"Bearer st-{tag}"}


def reference_book(session_factory) -> str:
    with session_factory() as db:
        book = Book(board="CBSE", class_name="Class 9", subject="Science", publisher="NCERT", is_reference=True)
        db.add(book)
        db.commit()
        return str(book.id)


def new_book(client, headers, **overrides) -> dict:
    body = {"board": "CBSE", "class_name": "Class 10", "subject": "Maths", "publisher": "Private Pub", **overrides}
    res = client.post("/teacher/books", json=body, headers=headers)
    assert res.status_code == 201, res.text
    return res.json()


def new_chapter(client, headers, book_id) -> str:
    res = client.post(f"/teacher/books/{book_id}/chapters", json={"title": "Ch 1", "sequence_num": 1}, headers=headers)
    assert res.status_code == 201, res.text
    return res.json()["id"]


def join_room_of(client, session_factory, teacher_headers, student_headers):
    room = client.post("/teacher/rooms", json={"name": "Room A", "room_type": "single_class"}, headers=teacher_headers).json()
    assert client.post("/student/rooms/join", json={"join_code": room["join_code"]}, headers=student_headers).status_code == 200


# ---- teacher side -----------------------------------------------------------

def test_created_book_is_owned_by_creator_and_never_reference(client, session_factory):
    a, ah = make_user(session_factory, Role.teacher, "teachera")
    book = new_book(client, ah, publisher="NCERT")  # even labelled "NCERT", a teacher's book is private
    assert book["is_reference"] is False
    with session_factory() as db:
        assert db.get(Book, uuid.UUID(book["id"])).owner_teacher_id == a.id


def test_teacher_cannot_see_or_modify_another_teachers_book(client, session_factory):
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    _, bh = make_user(session_factory, Role.teacher, "teacherb")
    book = new_book(client, ah)
    ch = new_chapter(client, ah, book["id"])

    assert book["id"] not in [b["id"] for b in client.get("/teacher/books", headers=bh).json()]
    assert client.get(f"/teacher/books/{book['id']}", headers=bh).status_code == 404
    assert client.get(f"/teacher/books/{book['id']}/chapters", headers=bh).status_code == 404
    assert client.get(f"/teacher/books/{book['id']}/chapters/{ch}/pages", headers=bh).status_code == 404
    assert client.post(f"/teacher/books/{book['id']}/chapters", json={"title": "X", "sequence_num": 2}, headers=bh).status_code == 404
    res = client.post(f"/teacher/books/{book['id']}/chapters/{ch}/pages/upload", files={"file": FAKE_PDF}, headers=bh)
    assert res.status_code == 404
    # owner still works
    assert client.get(f"/teacher/books/{book['id']}", headers=ah).status_code == 200


def test_reference_books_are_visible_to_teachers_but_read_only(client, session_factory):
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    ref_id = reference_book(session_factory)

    assert ref_id in [b["id"] for b in client.get("/teacher/books", headers=ah).json()]
    assert client.get(f"/teacher/books/{ref_id}", headers=ah).json()["is_reference"] is True
    assert client.post(f"/teacher/books/{ref_id}/chapters", json={"title": "X", "sequence_num": 1}, headers=ah).status_code == 403
    res = client.post(f"/teacher/books/{ref_id}/chapters/{uuid.uuid4()}/pages/upload", files={"file": FAKE_PDF}, headers=ah)
    assert res.status_code == 403


def test_list_scope_filter(client, session_factory):
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    _, bh = make_user(session_factory, Role.teacher, "teacherb")
    ref_id = reference_book(session_factory)
    mine = new_book(client, ah)
    new_book(client, bh)

    assert {b["id"] for b in client.get("/teacher/books?scope=mine", headers=ah).json()} == {mine["id"]}
    assert {b["id"] for b in client.get("/teacher/books?scope=reference", headers=ah).json()} == {ref_id}
    assert {b["id"] for b in client.get("/teacher/books", headers=ah).json()} == {mine["id"], ref_id}


def test_variant_of_must_point_at_a_visible_book(client, session_factory):
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    _, bh = make_user(session_factory, Role.teacher, "teacherb")
    ref_id = reference_book(session_factory)
    a_book = new_book(client, ah)

    body = {"board": "CBSE", "class_name": "Class 10", "subject": "Maths", "publisher": "P", "is_customized": True}
    assert client.post("/teacher/books", json={**body, "variant_of_id": a_book["id"]}, headers=bh).status_code == 404
    assert client.post("/teacher/books", json={**body, "variant_of_id": ref_id}, headers=bh).status_code == 201
    assert client.post("/teacher/books", json={**body, "variant_of_id": a_book["id"]}, headers=ah).status_code == 201


# ---- student side -----------------------------------------------------------

def test_student_can_only_link_reference_or_own_teachers_books(client, session_factory):
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    _, bh = make_user(session_factory, Role.teacher, "teacherb")
    _, sh = make_user(session_factory, Role.student, "student1")
    ref_id = reference_book(session_factory)
    a_book, b_book = new_book(client, ah), new_book(client, bh)

    # not in any room yet: reference only
    assert {b["id"] for b in client.get("/student/library", headers=sh).json()} == {ref_id}
    assert client.post(f"/student/books/{a_book['id']}/link", headers=sh).status_code == 404
    assert client.get(f"/student/books/{a_book['id']}", headers=sh).status_code == 404

    join_room_of(client, session_factory, ah, sh)

    assert {b["id"] for b in client.get("/student/library", headers=sh).json()} == {ref_id, a_book["id"]}
    assert client.post(f"/student/books/{a_book['id']}/link", headers=sh).json()["status"] == "linked"
    assert client.post(f"/student/books/{a_book['id']}/link", headers=sh).json()["status"] == "already_linked"
    assert client.post(f"/student/books/{ref_id}/link", headers=sh).status_code == 200
    assert client.post(f"/student/books/{b_book['id']}/link", headers=sh).status_code == 404  # other teacher's book

    assert client.get("/student/library", headers=sh).json() == []  # everything visible is now linked
    assert {b["id"] for b in client.get("/student/books", headers=sh).json()} == {a_book["id"], ref_id}


def test_student_reads_pages_only_of_linked_books_and_never_sees_fingerprints(client, session_factory):
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    _, sh = make_user(session_factory, Role.student, "student1")
    book = new_book(client, ah)
    ch = new_chapter(client, ah, book["id"])
    up = client.post(f"/teacher/books/{book['id']}/chapters/{ch}/pages/upload", files={"file": FAKE_PDF}, headers=ah)
    assert up.status_code == 202, up.text
    teacher_pages = client.get(f"/teacher/books/{book['id']}/chapters/{ch}/pages", headers=ah).json()
    assert teacher_pages and "fingerprint" not in teacher_pages[0]

    join_room_of(client, session_factory, ah, sh)
    url = f"/student/books/{book['id']}/chapters/{ch}/pages"
    assert client.get(url, headers=sh).status_code == 404  # in the room, but hasn't linked the book

    client.post(f"/student/books/{book['id']}/link", headers=sh)
    res = client.get(url, headers=sh)
    assert res.status_code == 200 and len(res.json()) == 1
    assert "fingerprint" not in res.json()[0]

    client.delete(f"/student/books/{book['id']}/link", headers=sh)
    assert client.get(url, headers=sh).status_code == 404  # unlink revokes access


def test_student_cannot_use_teacher_book_endpoints_and_parent_cannot_use_either(client, session_factory):
    _, sh = make_user(session_factory, Role.student, "student1")
    _, ph = make_user(session_factory, Role.parent, "parent1")
    assert client.get("/teacher/books", headers=sh).status_code == 403
    assert client.post("/teacher/books", json={"board": "b", "class_name": "c", "subject": "s", "publisher": "p"}, headers=sh).status_code == 403
    assert client.get("/student/library", headers=ph).status_code == 403
    assert client.post(f"/student/books/{uuid.uuid4()}/link", headers=ph).status_code == 403


def test_student_upload_and_verification_endpoints_are_gone(client, session_factory):
    _, th = make_user(session_factory, Role.teacher, "teachera")
    _, sh = make_user(session_factory, Role.student, "student1")
    assert client.post(f"/student/books/{uuid.uuid4()}/chapters/{uuid.uuid4()}/doubt-upload", files={"file": FAKE_PDF}, headers=sh).status_code == 404
    assert client.get("/teacher/pages/unverified", headers=th).status_code == 404
    assert client.post(f"/teacher/pages/{uuid.uuid4()}/verify", headers=th).status_code == 404
</file>

<file path="backend/tests/test_chapter_jobs.py">
"""Chapter processing lifecycle: background job, status, retry, upload validation (Rules.md §3)."""
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.config import settings
from app.models import Chapter, ChapterStatus, Page, Role
from tests.test_book_access import join_room_of, make_user, new_book, new_chapter
from tests.test_pipeline import CountingLLM, _text_pdf


def upload(client, headers, book_id, chapter_id, data, name="c.pdf"):
    return client.post(
        f"/teacher/books/{book_id}/chapters/{chapter_id}/pages/upload",
        files={"file": (name, data, "application/pdf")}, headers=headers,
    )


def chapter_status(client, headers, book_id, chapter_id) -> dict:
    chapters = client.get(f"/teacher/books/{book_id}/chapters", headers=headers).json()
    return next(c for c in chapters if c["id"] == chapter_id)


def page_count(session_factory, chapter_id) -> int:
    with session_factory() as db:
        return len(db.scalars(select(Page).where(Page.chapter_id == uuid.UUID(str(chapter_id)))).all())


def setup_chapter(client, session_factory, tag="teachera"):
    _, th = make_user(session_factory, Role.teacher, tag)
    book = new_book(client, th)
    return th, book["id"], new_chapter(client, th, book["id"])


class BrokenLLM:
    model_name = "broken"

    def complete_json(self, system, user):
        raise RuntimeError("secret-internal-detail: db password is hunter2")


def use_llm(monkeypatch, llm):
    monkeypatch.setattr("app.pipeline.orchestrator.get_llm_provider", lambda: llm)


# ---- lifecycle ----------------------------------------------------------------

def test_new_chapter_starts_empty_then_becomes_ready(client, session_factory):
    th, book_id, ch = setup_chapter(client, session_factory)
    assert chapter_status(client, th, book_id, ch)["status"] == "empty"

    res = upload(client, th, book_id, ch, _text_pdf("page one", "page two"))
    assert res.status_code == 202 and res.json()["status"] == "processing"

    done = chapter_status(client, th, book_id, ch)
    assert done["status"] == "ready" and done["error_message"] is None
    assert page_count(session_factory, ch) == 2


def test_failure_marks_chapter_failed_with_safe_message_and_keeps_no_pages(client, session_factory, monkeypatch):
    th, book_id, ch = setup_chapter(client, session_factory)
    use_llm(monkeypatch, BrokenLLM())

    assert upload(client, th, book_id, ch, _text_pdf("page one")).status_code == 202
    st = chapter_status(client, th, book_id, ch)
    assert st["status"] == "failed"
    assert "try again" in st["error_message"].lower()
    assert "hunter2" not in st["error_message"] and "secret" not in st["error_message"]  # no internals leak
    assert page_count(session_factory, ch) == 0


def test_retry_after_failure_uses_stored_file_and_succeeds(client, session_factory, monkeypatch):
    th, book_id, ch = setup_chapter(client, session_factory)
    use_llm(monkeypatch, CountingLLM(reply="not json"))
    upload(client, th, book_id, ch, _text_pdf("page one", "page two"))
    st = chapter_status(client, th, book_id, ch)
    assert st["status"] == "failed" and "page 1" in st["error_message"]

    use_llm(monkeypatch, CountingLLM())  # the LLM recovers
    res = client.post(f"/teacher/books/{book_id}/chapters/{ch}/retry", headers=th)
    assert res.status_code == 202
    assert chapter_status(client, th, book_id, ch)["status"] == "ready"
    assert page_count(session_factory, ch) == 2


def test_retry_is_rejected_when_there_is_nothing_to_retry(client, session_factory):
    th, book_id, ch = setup_chapter(client, session_factory)
    url = f"/teacher/books/{book_id}/chapters/{ch}/retry"
    assert client.post(url, headers=th).status_code == 409  # empty: no file yet
    upload(client, th, book_id, ch, _text_pdf("page one"))
    assert client.post(url, headers=th).status_code == 409  # already ready


def test_reuploading_identical_file_is_a_noop_and_different_file_replaces_pages(client, session_factory, monkeypatch):
    th, book_id, ch = setup_chapter(client, session_factory)
    llm = CountingLLM()
    use_llm(monkeypatch, llm)
    pdf = _text_pdf("alpha page one", "beta page two")

    assert upload(client, th, book_id, ch, pdf).status_code == 202
    calls = llm.calls
    again = upload(client, th, book_id, ch, pdf)
    assert again.status_code == 200 and again.json()["status"] == "ready"
    assert llm.calls == calls  # nothing reprocessed

    assert upload(client, th, book_id, ch, _text_pdf("only one new page")).status_code == 202
    assert page_count(session_factory, ch) == 1  # replaced, not appended


def test_failed_reupload_leaves_previous_pages_untouched(client, session_factory, monkeypatch):
    th, book_id, ch = setup_chapter(client, session_factory)
    upload(client, th, book_id, ch, _text_pdf("good page one", "good page two"))
    use_llm(monkeypatch, BrokenLLM())
    upload(client, th, book_id, ch, _text_pdf("a bad new upload"))
    assert chapter_status(client, th, book_id, ch)["status"] == "failed"
    assert page_count(session_factory, ch) == 2  # rolled back to the old pages, not half-replaced


# ---- concurrency / stuck jobs -----------------------------------------------------

def set_processing(session_factory, chapter_id, started_ago_min):
    with session_factory() as db:
        ch = db.get(Chapter, uuid.UUID(chapter_id))
        ch.status = ChapterStatus.PROCESSING
        ch.source_file = ch.source_file or "xx/missing.pdf"
        ch.processing_started_at = datetime.now(timezone.utc) - timedelta(minutes=started_ago_min)
        db.commit()


def test_cannot_upload_or_retry_while_actively_processing(client, session_factory):
    th, book_id, ch = setup_chapter(client, session_factory)
    set_processing(session_factory, ch, started_ago_min=1)
    assert upload(client, th, book_id, ch, _text_pdf("x")).status_code == 409
    assert client.post(f"/teacher/books/{book_id}/chapters/{ch}/retry", headers=th).status_code == 409


def test_stuck_processing_chapter_can_be_replaced_after_timeout(client, session_factory):
    th, book_id, ch = setup_chapter(client, session_factory)
    set_processing(session_factory, ch, started_ago_min=settings.chapter_processing_timeout_min + 5)
    assert upload(client, th, book_id, ch, _text_pdf("fresh start")).status_code == 202
    assert chapter_status(client, th, book_id, ch)["status"] == "ready"


# ---- upload validation ------------------------------------------------------------

def test_upload_validation(client, session_factory, monkeypatch):
    th, book_id, ch = setup_chapter(client, session_factory)
    assert upload(client, th, book_id, ch, b"").status_code == 400
    assert upload(client, th, book_id, ch, b"just some text, not a pdf", name="fake.pdf").status_code == 415
    assert upload(client, th, book_id, ch, b"%PDF-1.4 x", name="notes.txt").status_code == 202  # content decides, not name
    monkeypatch.setattr(settings, "max_upload_mb", 0)
    th2, b2, c2 = setup_chapter(client, session_factory, tag="teacherb")
    assert upload(client, th2, b2, c2, b"%PDF-1.4 x").status_code == 413
    assert chapter_status(client, th2, b2, c2)["status"] == "empty"  # rejected uploads change nothing


def test_other_teacher_cannot_retry_or_replace_pages(client, session_factory):
    th, book_id, ch = setup_chapter(client, session_factory)
    _, other = make_user(session_factory, Role.teacher, "teacherb")
    assert client.post(f"/teacher/books/{book_id}/chapters/{ch}/retry", headers=other).status_code == 404
    assert upload(client, other, book_id, ch, _text_pdf("x")).status_code == 404


# ---- students only see finished chapters --------------------------------------------

def test_students_only_see_ready_chapters_and_their_pages(client, session_factory, monkeypatch):
    th, book_id, ready_ch = setup_chapter(client, session_factory)
    failed_ch = new_chapter(client, th, book_id)  # second chapter, same sequence is fine for this test
    _, sh = make_user(session_factory, Role.student, "student1")
    join_room_of(client, session_factory, th, sh)
    client.post(f"/student/books/{book_id}/link", headers=sh)

    upload(client, th, book_id, ready_ch, _text_pdf("good"))
    use_llm(monkeypatch, BrokenLLM())
    upload(client, th, book_id, failed_ch, _text_pdf("bad"))

    book = client.get(f"/student/books/{book_id}", headers=sh).json()
    assert [c["id"] for c in book["chapters"]] == [ready_ch]
    assert client.get(f"/student/books/{book_id}/chapters/{ready_ch}/pages", headers=sh).status_code == 200
    assert client.get(f"/student/books/{book_id}/chapters/{failed_ch}/pages", headers=sh).status_code == 404
    mine = client.get("/student/books", headers=sh).json()
    assert [c["id"] for c in mine[0]["chapters"]] == [ready_ch]
</file>

<file path="backend/tests/test_concept_graph.py">
"""Chapter concept graph: identity merging, name matching, LLM linking, cycle breaking (Rules.md §3)."""
import json
import uuid

import pytest
from sqlalchemy import select

from app.core.config import settings
from app.core.errors import ProcessingError
from app.models import Book, Chapter, Concept, ConceptEdge, Page, Role
from app.pipeline.graph import build_chapter_graph, normalize_name
from app.pipeline.linking import propose_links
from tests.test_book_access import join_room_of, make_user
from tests.test_chapter_jobs import chapter_status, page_count, setup_chapter, upload, use_llm
from tests.test_pipeline import CountingLLM, _text_pdf


class NoLinksLLM:
    """Links nothing, so a test sees only the deterministic name-matching edges."""
    model_name = "nolinks"
    calls = 0

    def complete_json(self, system, user):
        self.calls += 1
        return json.dumps({"edges": []})


class ScriptedLLM:
    def __init__(self, edges):
        self.edges, self.calls = edges, 0

    def complete_json(self, system, user):
        self.calls += 1
        return json.dumps({"edges": self.edges})


def make_chapter(db):
    book = Book(board="CBSE", class_name="9", subject="Sci", publisher="NCERT", is_reference=True)
    db.add(book)
    db.flush()
    ch = Chapter(book_id=book.id, title="Ch", sequence_num=1)
    db.add(ch)
    db.flush()
    return ch


def add_page(db, ch, number, *concepts):
    """concepts: (name, [raw prerequisite names]) tuples."""
    page = Page(chapter_id=ch.id, page_number=number, content_text=f"p{number}")
    db.add(page)
    db.flush()
    made = []
    for pos, (name, prereqs) in enumerate(concepts):
        c = Concept(page_id=page.id, name=name, description=f"about {name}", prerequisites=prereqs, position=pos)
        db.add(c)
        made.append(c)
    db.flush()
    return made


def edges_by_name(db, ch):
    names = {c.id: c.name for c in db.scalars(select(Concept)).all()}
    return {(names[e.prerequisite_id], names[e.concept_id], e.source) for e in db.scalars(select(ConceptEdge).where(ConceptEdge.chapter_id == ch.id))}


# ---- normalization -----------------------------------------------------------------

def test_normalize_name():
    assert normalize_name("  The Atom! ") == "atom"
    assert normalize_name("Law  of\tConservation") == "law of conservation"
    assert normalize_name("An Ion") == "ion"
    assert normalize_name("Atom") == normalize_name("atom.")
    assert normalize_name("Anode") == "anode"  # only a leading *word* 'a' is dropped


# ---- name matching + identity merging --------------------------------------------------

def test_prerequisite_names_resolve_to_concepts_and_unknown_ones_are_reported(session_factory):
    with session_factory() as db:
        ch = make_chapter(db)
        add_page(db, ch, 1, ("Atom", []))
        add_page(db, ch, 2, ("Molecule", ["the atom", "Nuclear physics"]))
        report = build_chapter_graph(db, ch, NoLinksLLM())
        db.commit()
        assert edges_by_name(db, ch) == {("Atom", "Molecule", "page")}
        assert report["edges"] == 1
        assert report["unresolved_prerequisites"] == [{"concept": "Molecule", "prerequisite": "Nuclear physics"}]


def test_same_named_concepts_merge_into_the_first_occurrence(session_factory):
    with session_factory() as db:
        ch = make_chapter(db)
        add_page(db, ch, 1, ("Matter", []))
        add_page(db, ch, 2, ("Atom", ["matter"]))
        add_page(db, ch, 3, ("matter.", ["Atom"]), ("Energy", ["Matter"]))  # 'matter.' is the same concept again
        report = build_chapter_graph(db, ch, NoLinksLLM())
        db.commit()
        concepts = db.execute(select(Concept, Page.page_number).join(Page).where(Page.chapter_id == ch.id)).all()
        canonical = {c.name: pn for c, pn in concepts if c.is_canonical}
        assert canonical == {"Matter": 1, "Atom": 2, "Energy": 3}
        assert report["duplicate_names_merged"] == 1
        # the page-3 duplicate's 'Atom' prerequisite would make canonical Matter (p1) need Atom (p2): backward, dropped
        assert edges_by_name(db, ch) == {("Matter", "Atom", "page"), ("Matter", "Energy", "page")}
        assert report["dropped_backward_edges"] == [{"prerequisite": "Atom", "concept": "Matter"}]
        assert report["dropped_cycle_edges"] == []
        assert all(e.concept_id != e.prerequisite_id for e in db.scalars(select(ConceptEdge)))


def test_self_prerequisite_is_ignored(session_factory):
    with session_factory() as db:
        ch = make_chapter(db)
        add_page(db, ch, 1, ("Atom", ["Atom", "the atom"]))
        report = build_chapter_graph(db, ch, NoLinksLLM())
        assert report["edges"] == 0 and report["dropped_cycle_edges"] == []


# ---- cycles ----------------------------------------------------------------------------

def test_two_cycle_keeps_the_forward_edge_and_drops_the_backward_one(session_factory):
    with session_factory() as db:
        ch = make_chapter(db)
        add_page(db, ch, 1, ("A", ["B"]))
        add_page(db, ch, 2, ("B", ["A"]))
        report = build_chapter_graph(db, ch, NoLinksLLM())
        # B (page 2) needing A (page 1) is the plausible direction; A needing B is the suspect one
        assert edges_by_name(db, ch) == {("A", "B", "page")}
        assert report["dropped_backward_edges"] == [{"prerequisite": "B", "concept": "A"}]
        assert report["dropped_cycle_edges"] == []


def test_same_page_two_cycle_is_broken_and_reported_as_a_cycle(session_factory):
    with session_factory() as db:
        ch = make_chapter(db)
        add_page(db, ch, 1, ("A", ["B"]), ("B", ["A"]))
        report = build_chapter_graph(db, ch, NoLinksLLM())
        assert len(edges_by_name(db, ch)) == 1
        assert len(report["dropped_cycle_edges"]) == 1 and report["dropped_backward_edges"] == []


def test_long_cycle_is_broken_and_result_is_acyclic(session_factory):
    with session_factory() as db:
        ch = make_chapter(db)
        add_page(db, ch, 1, ("A", ["C"]))
        add_page(db, ch, 2, ("B", ["A"]))
        add_page(db, ch, 3, ("C", ["B"]))
        report = build_chapter_graph(db, ch, NoLinksLLM())
        assert edges_by_name(db, ch) == {("A", "B", "page"), ("B", "C", "page")}
        assert len(report["dropped_backward_edges"]) == 1  # A (p1) needing C (p3)

        # independent acyclicity check on what is actually stored
        names = {c.id: c.name for c in db.scalars(select(Concept))}
        deps = {}
        for e in db.scalars(select(ConceptEdge)):
            deps.setdefault(e.prerequisite_id, []).append(e.concept_id)
        state = {}

        def visit(n):
            if state.get(n) == 1:
                raise AssertionError("cycle in stored graph")
            if state.get(n) == 2:
                return
            state[n] = 1
            for m in deps.get(n, []):
                visit(m)
            state[n] = 2
        for n in names:
            visit(n)


def test_only_forward_edges_survive(session_factory):
    """A needs B, B needs C, C needs A. Only C needing A (A on an earlier page) points forward; the other two
    would make an early concept depend on a later one and are dropped as backward edges."""
    with session_factory() as db:
        ch = make_chapter(db)
        add_page(db, ch, 1, ("A", ["B"]))
        add_page(db, ch, 2, ("B", ["C"]))
        add_page(db, ch, 3, ("C", ["A"]))
        report = build_chapter_graph(db, ch, NoLinksLLM())
        assert edges_by_name(db, ch) == {("A", "C", "page")}
        assert len(report["dropped_backward_edges"]) == 2 and report["dropped_cycle_edges"] == []


# ---- LLM linking pass ---------------------------------------------------------------------

def test_llm_edges_are_added_with_source_llm_and_never_override_name_matches(session_factory):
    with session_factory() as db:
        ch = make_chapter(db)
        add_page(db, ch, 1, ("Atom", []))
        add_page(db, ch, 2, ("Molecule", ["Atom"]))
        add_page(db, ch, 3, ("Compound", []))
        llm = ScriptedLLM([{"concept": 2, "prerequisites": [1]}, {"concept": 3, "prerequisites": [2, 3]}])
        report = build_chapter_graph(db, ch, llm)
        assert edges_by_name(db, ch) == {("Atom", "Molecule", "page"), ("Molecule", "Compound", "llm")}
        assert report["llm_linking"] == "done" and llm.calls == 1


def test_llm_linking_skipped_for_tiny_or_huge_chapters(session_factory, monkeypatch):
    with session_factory() as db:
        ch = make_chapter(db)
        add_page(db, ch, 1, ("Atom", []))
        llm = NoLinksLLM()
        assert build_chapter_graph(db, ch, llm)["llm_linking"] == "skipped_too_few_concepts"
        add_page(db, ch, 2, ("Molecule", []))
        monkeypatch.setattr(settings, "link_max_concepts", 1)
        assert build_chapter_graph(db, ch, llm)["llm_linking"] == "skipped_too_many_concepts"
        assert llm.calls == 0


def test_propose_links_validates_retries_and_gives_up():
    concepts = [("A", ""), ("B", ""), ("C", "")]
    bad = ScriptedLLM([{"concept": 9, "prerequisites": [1]}])  # 9 is not in the list
    with pytest.raises(ProcessingError):
        propose_links(bad, concepts)
    assert bad.calls == 3  # first try + 2 corrections

    class Garbage:
        calls = 0

        def complete_json(self, s, u):
            self.calls += 1
            return '{"concepts": []}'  # wrong shape: no 'edges'
    g = Garbage()
    with pytest.raises(ProcessingError):
        propose_links(g, concepts)
    assert g.calls == 3

    ok = ScriptedLLM([{"concept": 3, "prerequisites": [1, 1, 3, 2]}, {"concept": 2, "prerequisites": [1]}])
    assert propose_links(ok, concepts) == [(2, 0), (2, 1), (1, 0)]  # de-duplicated, self-link dropped


# ---- end to end through the API --------------------------------------------------------------

def test_upload_builds_graph_and_exposes_it_to_teacher_and_linked_students(client, session_factory):
    th, book_id, ch = setup_chapter(client, session_factory)
    _, sh = make_user(session_factory, Role.student, "student1")
    join_room_of(client, session_factory, th, sh)
    client.post(f"/student/books/{book_id}/link", headers=sh)

    assert upload(client, th, book_id, ch, _text_pdf("alpha idea", "beta idea", "gamma idea")).status_code == 202
    assert chapter_status(client, th, book_id, ch)["status"] == "ready"

    g = client.get(f"/teacher/books/{book_id}/chapters/{ch}/graph", headers=th).json()
    names = {n["id"]: n["name"] for n in g["nodes"]}
    assert sorted(names.values()) == ["alpha idea", "beta idea", "gamma idea"]
    # fake LLM chains each concept onto the previous one
    assert {(names[e["prerequisite_id"]], names[e["concept_id"]]) for e in g["edges"]} == {
        ("alpha idea", "beta idea"), ("beta idea", "gamma idea")}
    assert g["report"]["llm_linking"] == "done"

    assert client.get(f"/student/books/{book_id}/chapters/{ch}/graph", headers=sh).json()["edges"] == g["edges"]
    pages = client.get(f"/teacher/books/{book_id}/chapters/{ch}/pages", headers=th).json()
    linked = [c for p in pages for c in p["concepts"] if c["prerequisite_ids"]]
    assert len(linked) == 2


def test_graph_endpoints_enforce_access(client, session_factory):
    th, book_id, ch = setup_chapter(client, session_factory)
    upload(client, th, book_id, ch, _text_pdf("alpha idea", "beta idea"))
    _, other = make_user(session_factory, Role.teacher, "teacherb")
    _, sh = make_user(session_factory, Role.student, "student1")
    url_t, url_s = f"/teacher/books/{book_id}/chapters/{ch}/graph", f"/student/books/{book_id}/chapters/{ch}/graph"

    assert client.get(url_t, headers=other).status_code == 404  # someone else's private book
    assert client.get(url_s, headers=sh).status_code == 404  # student hasn't linked it
    join_room_of(client, session_factory, th, sh)
    client.post(f"/student/books/{book_id}/link", headers=sh)
    assert client.get(url_s, headers=sh).status_code == 200
    assert client.get(f"/student/books/{book_id}/chapters/{uuid.uuid4()}/graph", headers=sh).status_code == 404


def test_reupload_replaces_graph_without_stale_edges(client, session_factory):
    th, book_id, ch = setup_chapter(client, session_factory)
    upload(client, th, book_id, ch, _text_pdf("alpha idea", "beta idea", "gamma idea"))
    upload(client, th, book_id, ch, _text_pdf("delta idea", "epsilon idea"))
    g = client.get(f"/teacher/books/{book_id}/chapters/{ch}/graph", headers=th).json()
    assert sorted(n["name"] for n in g["nodes"]) == ["delta idea", "epsilon idea"]
    assert len(g["edges"]) == 1
    with session_factory() as db:
        concept_ids = {c.id for c in db.scalars(select(Concept))}
        edges = db.scalars(select(ConceptEdge)).all()
        assert len(edges) == 1
        assert all(e.concept_id in concept_ids and e.prerequisite_id in concept_ids for e in edges)


def test_linking_failure_fails_the_chapter_and_rolls_everything_back(client, session_factory, monkeypatch):
    th, book_id, ch = setup_chapter(client, session_factory)

    class PagesOkLinkingBroken:
        model_name = "x"

        def complete_json(self, system, user):
            if user.startswith("CONCEPTS:"):
                return "definitely not json"
            return CountingLLM().complete_json(system, user).replace("Matter", user.split("TEXT:\n")[-1][:12])

    use_llm(monkeypatch, PagesOkLinkingBroken())
    upload(client, th, book_id, ch, _text_pdf("first page text", "second page text"))
    st = chapter_status(client, th, book_id, ch)
    assert st["status"] == "failed" and "depend on each other" in st["error_message"]
    assert page_count(session_factory, ch) == 0
    with session_factory() as db:
        assert db.scalars(select(ConceptEdge)).all() == [] and db.scalars(select(Concept)).all() == []
</file>

<file path="backend/tests/test_concepts.py">
import uuid
import pytest
from sqlalchemy import select
from app.models.content import Book, Chapter, Page, Concept

def test_page_concept_hierarchy_and_prerequisites(session_factory):
    """Validate Phase 2 hierarchy: Book -> Chapter -> Page -> Concept"""
    with session_factory() as db:
        book = Book(board="CBSE", class_name="Class 10", subject="Science", publisher="NCERT", is_reference=True)
        db.add(book)
        db.flush()

        chapter = Chapter(book_id=book.id, title="Chemical Reactions", sequence_num=1)
        db.add(chapter)
        db.flush()

        page = Page(chapter_id=chapter.id, page_number=1, content_text="Equations.")
        db.add(page)
        db.flush()

        c1 = Concept(page_id=page.id, name="Chemical Equation", prerequisites=["Changes"])
        c2 = Concept(page_id=page.id, name="Law of Mass", prerequisites=["Chemical Equation"])
        db.add_all([c1, c2])
        db.commit()

        saved_page = db.scalar(select(Page).where(Page.id == page.id))
        assert saved_page is not None
        assert len(saved_page.concepts) == 2
        concept_names = [c.name for c in saved_page.concepts]
        assert "Chemical Equation" in concept_names


def test_concepts_cascade_delete_with_page(session_factory):
    """Deleting a page should cascade and delete its associated concepts."""
    with session_factory() as db:
        book = Book(board="ICSE", class_name="Class 9", subject="Math", publisher="Selina", is_reference=True)
        db.add(book)
        db.flush()

        chapter = Chapter(book_id=book.id, title="Algebra", sequence_num=1)
        db.add(chapter)
        db.flush()

        page = Page(chapter_id=chapter.id, page_number=5, content_text="Equations")
        db.add(page)
        db.flush()

        concept = Concept(page_id=page.id, name="Linear Equation")
        db.add(concept)
        db.commit()

        concept_id = concept.id

        # Delete page
        db.delete(page)
        db.commit()

        # Verify concept was deleted via cascade
        deleted_concept = db.scalar(select(Concept).where(Concept.id == concept_id))
        assert deleted_concept is None
</file>

<file path="backend/tests/test_library.py">
import uuid
import pytest
from sqlalchemy import select
from app.models.content import Book, Chapter, Page, student_book
from app.models.user import User, Role


def test_book_crud_and_student_link(session_factory):
    with session_factory() as db:
        # 1. Create a Book
        book = Book(board="CBSE", class_name="Class 10", subject="Mathematics", publisher="NCERT", is_reference=True)
        db.add(book)
        db.flush()

        # 2. Add Chapter
        chapter = Chapter(book_id=book.id, title="Real Numbers", sequence_num=1)
        db.add(chapter)
        db.flush()

        # 3. Create Student User
        student = User(
            supertokens_user_id=f"stu_{uuid.uuid4()}", 
            name="Test Student", 
            username=f"stu_{uuid.uuid4().hex[:8]}", 
            phone="1234567890", 
            role=Role.student
        )
        db.add(student)
        db.flush()

        # 4. Link Student to Book
        db.execute(student_book.insert().values(student_id=student.id, book_id=book.id))
        db.commit()

        # 5. Verify Linkage
        my_books = db.scalars(select(Book).join(student_book).where(student_book.c.student_id == student.id)).all()
        assert len(my_books) == 1
        assert my_books[0].id == book.id
</file>

<file path="backend/tests/test_matching.py">
"""Fingerprints, LSH lookup, Layer-0 file reuse, and book-level variant suggestions (Rules.md §3)."""
import uuid

import pytest
from sqlalchemy import select

from app.models import Book, Chapter, ChapterStatus, Page, PageBand, Role
from app.pipeline import matching
from app.pipeline.fingerprint import apply_fingerprint, band_keys, compute_jaccard_similarity, compute_minhash
from app.pipeline.orchestrator import PipelineOrchestrator
from app.ocr.fake_provider import FakeOCRProvider
from tests.test_book_access import make_user, new_book, new_chapter, reference_book
from tests.test_chapter_jobs import chapter_status, upload, use_llm
from tests.test_pipeline import CountingLLM, _text_pdf


def page_text(prefix: str, n: int = 100, alter_every: int = 0) -> str:
    """n distinct words; with alter_every=25, every 25th word is replaced (~0.8 similarity to the original)."""
    words = [f"{prefix}{i}" for i in range(n)]
    if alter_every:
        words = [f"alt{w}" if (i + 1) % alter_every == 0 else w for i, w in enumerate(words)]
    return " ".join(words)


# ---- fingerprints ---------------------------------------------------------------------

def test_identical_text_scores_one_and_unrelated_scores_near_zero():
    a, b = compute_minhash(page_text("alpha")), compute_minhash(page_text("beta"))
    assert compute_jaccard_similarity(a, compute_minhash(page_text("alpha"))) == 1.0
    assert compute_jaccard_similarity(a, b) < 0.1


def test_word_order_matters_unlike_a_bag_of_words():
    words = page_text("gamma").split()
    assert compute_jaccard_similarity(compute_minhash(" ".join(words)), compute_minhash(" ".join(reversed(words)))) < 0.2


def test_non_ascii_text_is_fingerprinted_not_erased():
    hindi_1 = "भारत एक विशाल देश है जिसकी संस्कृति बहुत प्राचीन और समृद्ध है और यहाँ अनेक भाषाएँ बोली जाती हैं तथा अनेक त्योहार मनाए जाते हैं"
    hindi_2 = "पदार्थ वह है जो स्थान घेरता है और जिसका द्रव्यमान होता है हमारे चारों ओर की हर वस्तु पदार्थ से बनी है जैसे हवा पानी और पत्थर"
    telugu = "భారతదేశం ఒక విశాలమైన దేశం దీని సంస్కృతి చాలా ప్రాచీనమైనది మరియు సంపన్నమైనది ఇక్కడ అనేక భాషలు మాట్లాడతారు మరియు అనేక పండుగలు జరుపుకుంటారు"
    f1, f2, ft = compute_minhash(hindi_1), compute_minhash(hindi_2), compute_minhash(telugu)
    assert f1 and f2 and ft
    assert compute_jaccard_similarity(f1, compute_minhash(hindi_1)) == 1.0
    assert compute_jaccard_similarity(f1, f2) < 0.1 and compute_jaccard_similarity(f1, ft) < 0.1


def test_short_pages_get_no_fingerprint():
    assert compute_minhash("Chapter 3") is None
    assert compute_minhash(page_text("x", 14)) is None
    assert compute_minhash(page_text("x", 15)) is not None
    assert compute_jaccard_similarity(None, compute_minhash(page_text("x"))) == 0.0


def test_similar_pages_share_band_keys_and_unrelated_pages_do_not():
    base = compute_minhash(page_text("delta"))
    variant = compute_minhash(page_text("delta", alter_every=25))
    other = compute_minhash(page_text("omega"))
    assert 0.6 < compute_jaccard_similarity(base, variant) < 0.95
    assert set(band_keys(base)) & set(band_keys(variant))
    assert not set(band_keys(base)) & set(band_keys(other))
    assert set(band_keys(base)) == set(band_keys(compute_minhash(page_text("delta"))))


# ---- the index replaces the full scan --------------------------------------------------------

def make_book_chapter(db, owner=None):
    book = Book(board="B", class_name="9", subject="S", publisher="P",
                is_reference=owner is None, owner_teacher_id=owner.id if owner else None)
    db.add(book)
    db.flush()
    ch = Chapter(book_id=book.id, title="C", sequence_num=1)
    db.add(ch)
    db.flush()
    return book, ch


def add_page(db, ch, number, text):
    page = Page(chapter_id=ch.id, page_number=number, content_text=text)
    apply_fingerprint(page, text)
    db.add(page)
    db.flush()
    return page


def test_lookup_only_scores_pages_that_share_a_band_key(session_factory, monkeypatch):
    with session_factory() as db:
        _, ch = make_book_chapter(db)
        for i in range(40):
            add_page(db, ch, i, page_text(f"filler{i}_"))
        target = add_page(db, ch, 99, page_text("delta"))
        calls = []
        real = matching.compute_jaccard_similarity
        monkeypatch.setattr(matching, "compute_jaccard_similarity", lambda a, b: calls.append(1) or real(a, b))

        sig = compute_minhash(page_text("delta", alter_every=25))
        found = matching.find_matches(db, sig, band_keys(sig))
        assert [m.page_id for m in found] == [target.id]
        assert len(calls) <= 3  # the target (and at most a stray collision), not all 41 pages


def test_rebuild_recomputes_fingerprints_and_index(session_factory):
    from app.db.rebuild_fingerprints import rebuild
    with session_factory() as db:
        _, ch = make_book_chapter(db)
        p = Page(chapter_id=ch.id, page_number=1, content_text=page_text("zeta"))
        short = Page(chapter_id=ch.id, page_number=2, content_text="Contents")
        db.add_all([p, short])
        db.flush()
        db.add(PageBand(page_id=p.id, key=12345))  # stale row from an older scheme
        db.commit()
        assert rebuild(db) == 1
        db.expire_all()
        assert p.fingerprint is not None and short.fingerprint is None
        keys = {b.key for b in db.scalars(select(PageBand).where(PageBand.page_id == p.id))}
        assert keys == set(band_keys(p.fingerprint)) and 12345 not in keys
        assert db.scalars(select(PageBand).where(PageBand.page_id == short.id)).all() == []


# ---- Layer 0: identical file anywhere -> no OCR -----------------------------------------------

class CountingOCR(FakeOCRProvider):
    calls = 0

    def extract_layout(self, data, ext):
        CountingOCR.calls += 1
        return super().extract_layout(data, ext)


def test_identical_file_skips_ocr_and_reuses_concepts_without_exposing_the_other_book(client, session_factory, monkeypatch):
    CountingOCR.calls = 0
    monkeypatch.setattr("app.pipeline.orchestrator.get_ocr_provider", lambda: CountingOCR())
    llm = CountingLLM()
    use_llm(monkeypatch, llm)
    pdf = _text_pdf(page_text("epsilon"), page_text("theta"))

    _, ah = make_user(session_factory, Role.teacher, "teachera")
    a_book = new_book(client, ah)
    a_ch = new_chapter(client, ah, a_book["id"])
    assert upload(client, ah, a_book["id"], a_ch, pdf).status_code == 202
    assert CountingOCR.calls == 1
    llm_calls_after_a = llm.calls

    _, bh = make_user(session_factory, Role.teacher, "teacherb")
    b_book = new_book(client, bh)
    b_ch = new_chapter(client, bh, b_book["id"])
    assert upload(client, bh, b_book["id"], b_ch, pdf).status_code == 202
    assert chapter_status(client, bh, b_book["id"], b_ch)["status"] == "ready"
    assert CountingOCR.calls == 1  # second upload never reached OCR
    assert llm.calls == llm_calls_after_a  # ...nor the per-page LLM: its pages matched A's at >= 0.95

    with session_factory() as db:
        report = db.get(Chapter, uuid.UUID(b_ch)).match_report
        assert report["ocr_reused"] is True and report["pages_reused"] == 2
        assert report["suggestions"] == []  # A's private book is invisible to B
        assert a_book["id"] not in str(report)
        pages = db.scalars(select(Page).join(Chapter).where(Chapter.id == uuid.UUID(b_ch))).all()
        assert sorted(p.content_text for p in pages) == sorted([page_text("epsilon"), page_text("theta")])


# ---- book-level variant suggestions --------------------------------------------------------------

def processed_reference_book(session_factory, texts, publisher="NCERT"):
    with session_factory() as db:
        book = Book(board="CBSE", class_name="Class 9", subject="Science", publisher=publisher, is_reference=True)
        db.add(book)
        db.flush()
        ch = Chapter(book_id=book.id, title="Ref ch", sequence_num=1)
        db.add(ch)
        db.flush()
        PipelineOrchestrator(db, llm_provider=CountingLLM()).process_chapter_file(ch, _text_pdf(*texts), "pdf", None)
        ch.status = ChapterStatus.READY
        db.commit()
        return str(book.id)


def suggestions(client, headers, book_id):
    res = client.get(f"/teacher/books/{book_id}/variant-suggestions", headers=headers)
    assert res.status_code == 200, res.text
    return res.json()


def test_edition_of_a_reference_book_is_suggested_as_a_variant(client, session_factory):
    ref_id = processed_reference_book(session_factory, [page_text("p1_"), page_text("p2_")])
    _, th = make_user(session_factory, Role.teacher, "teachera")
    book = new_book(client, th, publisher="School Press")
    ch = new_chapter(client, th, book["id"])
    upload(client, th, book["id"], ch, _text_pdf(page_text("p1_", alter_every=25), page_text("p2_", alter_every=25)))

    [s] = suggestions(client, th, book["id"])
    assert s["book"]["id"] == ref_id and s["book"]["publisher"] == "NCERT" and s["book"]["is_reference"] is True
    assert s["kind"] == "variant" and s["coverage"] == 1.0 and s["matched_pages"] == 2
    assert 0.6 < s["avg_similarity"] < 0.95

    # teacher confirms -> recorded, and no longer suggested
    res = client.post(f"/teacher/books/{book['id']}/variant-of", json={"base_book_id": ref_id}, headers=th)
    assert res.status_code == 200 and res.json()["variant_of_id"] == ref_id
    assert suggestions(client, th, book["id"]) == []
    assert client.delete(f"/teacher/books/{book['id']}/variant-of", headers=th).status_code == 204
    assert client.get(f"/teacher/books/{book['id']}", headers=th).json()["variant_of_id"] is None
    assert len(suggestions(client, th, book["id"])) == 1  # suggested again once cleared


def test_near_identical_pages_are_reported_as_the_same_book(client, session_factory):
    ref_id = processed_reference_book(session_factory, [page_text("q1_"), page_text("q2_")])
    _, th = make_user(session_factory, Role.teacher, "teachera")
    book = new_book(client, th)
    ch = new_chapter(client, th, book["id"])
    upload(client, th, book["id"], ch, _text_pdf(page_text("q1_"), page_text("q2_")))
    [s] = suggestions(client, th, book["id"])
    assert s["book"]["id"] == ref_id and s["kind"] == "same" and s["avg_similarity"] >= 0.95


def test_unrelated_or_barely_overlapping_uploads_get_no_suggestion(client, session_factory):
    processed_reference_book(session_factory, [page_text("r1_"), page_text("r2_"), page_text("r3_"), page_text("r4_")])
    _, th = make_user(session_factory, Role.teacher, "teachera")
    book = new_book(client, th)
    ch = new_chapter(client, th, book["id"])
    upload(client, th, book["id"], ch, _text_pdf(page_text("r1_", alter_every=25), page_text("n1_"), page_text("n2_"), page_text("n3_")))
    assert suggestions(client, th, book["id"]) == []  # only 1 of 4 pages matches: coverage 0.25 < 0.5


def test_suggestions_are_judged_chapter_by_chapter(client, session_factory):
    ref_id = processed_reference_book(session_factory, [page_text("s1_"), page_text("s2_"), page_text("s3_"), page_text("s4_")])
    _, th = make_user(session_factory, Role.teacher, "teachera")
    book = new_book(client, th)
    ch1 = new_chapter(client, th, book["id"])
    upload(client, th, book["id"], ch1, _text_pdf(page_text("s1_", alter_every=25), page_text("x1_")))
    [first] = suggestions(client, th, book["id"])
    assert (first["matched_chapters"], first["chapters_checked"]) == (1, 1) and first["matched_pages"] == 1 and first["pages_checked"] == 2
    ch2 = client.post(f"/teacher/books/{book['id']}/chapters", json={"title": "C2", "sequence_num": 2}, headers=th).json()["id"]
    upload(client, th, book["id"], ch2, _text_pdf(page_text("s2_", alter_every=25), page_text("s3_", alter_every=25)))
    [s] = suggestions(client, th, book["id"])
    assert s["book"]["id"] == ref_id and (s["matched_chapters"], s["chapters_checked"], s["coverage"]) == (2, 2, 1.0)
    assert s["matched_pages"] == 3 and s["pages_checked"] == 4


def chapter_matches(client, headers, book_id):
    res = client.get(f"/teacher/books/{book_id}/chapter-matches", headers=headers)
    assert res.status_code == 200, res.text
    return {c["chapter_title"]: c["matches"] for c in res.json()}


def test_a_partly_loaded_official_book_is_matched_by_chapter_not_by_page_count(client, session_factory):
    """The real-world case: the official book has only ONE chapter loaded so far, and the teacher's book has
    that chapter plus another. Counting pages over the whole book gave a confusing 25%; by chapter it is
    'your chapter 2 IS the official chapter', and the other chapter simply has no match yet."""
    ref_id = processed_reference_book(session_factory, [page_text("b1_"), page_text("b2_")])
    _, th = make_user(session_factory, Role.teacher, "teachera")
    book = new_book(client, th)
    c1 = new_chapter(client, th, book["id"])
    upload(client, th, book["id"], c1, _text_pdf(*[page_text(f"other{i}_") for i in range(6)]))  # long, unrelated
    c2 = client.post(f"/teacher/books/{book['id']}/chapters", json={"title": "The Building Block of Life", "sequence_num": 2}, headers=th).json()["id"]
    upload(client, th, book["id"], c2, _text_pdf(page_text("b1_"), page_text("b2_")))

    by_chapter = chapter_matches(client, th, book["id"])
    assert by_chapter["Ch 1"] == []
    [m] = by_chapter["The Building Block of Life"]
    assert m["book"]["id"] == ref_id and m["kind"] == "same" and m["chapter_title"] == "Ref ch"
    assert (m["matched_pages"], m["pages_checked"]) == (2, 2)  # judged within the chapter, not out of 8

    [s] = suggestions(client, th, book["id"])
    assert (s["matched_chapters"], s["chapters_checked"], s["coverage"]) == (1, 2, 0.5)
    assert s["candidate_chapters_loaded"] == 1 and s["kind"] == "same"
    assert (s["matched_pages"], s["pages_checked"]) == (2, 8)  # page totals stay available, but are not the criterion


def test_chapter_matches_survive_confirming_the_variant_and_respect_privacy(client, session_factory):
    ref_id = processed_reference_book(session_factory, [page_text("c1_"), page_text("c2_")])
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    _, bh = make_user(session_factory, Role.teacher, "teacherb")
    a_book = new_book(client, ah)
    a_ch = new_chapter(client, ah, a_book["id"])
    upload(client, ah, a_book["id"], a_ch, _text_pdf(page_text("c1_"), page_text("c2_")))
    b_book = new_book(client, bh)
    b_ch = new_chapter(client, bh, b_book["id"])
    upload(client, bh, b_book["id"], b_ch, _text_pdf(page_text("c1_", alter_every=25), page_text("c2_", alter_every=25)))

    client.post(f"/teacher/books/{a_book['id']}/variant-of", json={"base_book_id": ref_id}, headers=ah)
    assert suggestions(client, ah, a_book["id"]) == []  # already confirmed...
    assert [m["book"]["id"] for m in chapter_matches(client, ah, a_book["id"])["Ch 1"]] == [ref_id]  # ...but still shown per chapter

    # B sees the official chapter, never A's private book, though A's pages match B's too
    assert [m["book"]["id"] for m in chapter_matches(client, bh, b_book["id"])["Ch 1"]] == [ref_id]
    assert a_book["id"] not in client.get(f"/teacher/books/{b_book['id']}/chapter-matches", headers=bh).text

    assert client.get(f"/teacher/books/{a_book['id']}/chapter-matches", headers=bh).status_code == 404
    assert client.get(f"/teacher/books/{ref_id}/chapter-matches", headers=ah).status_code == 403


def test_other_teachers_private_books_are_never_suggested(client, session_factory):
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    _, bh = make_user(session_factory, Role.teacher, "teacherb")
    a_book = new_book(client, ah)
    a_ch = new_chapter(client, ah, a_book["id"])
    upload(client, ah, a_book["id"], a_ch, _text_pdf(page_text("u1_"), page_text("u2_")))

    b_book = new_book(client, bh)
    b_ch = new_chapter(client, bh, b_book["id"])
    upload(client, bh, b_book["id"], b_ch, _text_pdf(page_text("u1_", alter_every=25), page_text("u2_", alter_every=25)))
    assert suggestions(client, bh, b_book["id"]) == []

    # ...but a teacher's OWN other book is a valid base
    b_book2 = new_book(client, bh, subject="Other")
    ch2 = new_chapter(client, bh, b_book2["id"])
    upload(client, bh, b_book2["id"], ch2, _text_pdf(page_text("u1_", alter_every=25), page_text("u2_", alter_every=25)))
    [s] = suggestions(client, bh, b_book2["id"])
    assert s["book"]["id"] == b_book["id"] and s["kind"] == "same"


def test_suggestion_for_a_book_that_no_longer_exists_disappears(client, session_factory):
    ref_id = processed_reference_book(session_factory, [page_text("d1_"), page_text("d2_")])
    _, th = make_user(session_factory, Role.teacher, "teachera")
    book = new_book(client, th)
    ch = new_chapter(client, th, book["id"])
    upload(client, th, book["id"], ch, _text_pdf(page_text("d1_", alter_every=25), page_text("d2_", alter_every=25)))
    assert len(suggestions(client, th, book["id"])) == 1
    with session_factory() as db:  # the stored report still names it, but it is gone now
        db.delete(db.get(Book, uuid.UUID(ref_id)))
        db.commit()
    assert suggestions(client, th, book["id"]) == []


def _m(book_id, score, reference=True, owner=None):
    return matching.PageMatch(uuid.uuid4(), score, book_id, reference, owner)


def test_summarize_book_matches_rules():
    mine, ref, other_private, own_private = (uuid.uuid4() for _ in range(4))
    teacher, someone_else = uuid.uuid4(), uuid.uuid4()
    pages = [
        [_m(ref, 0.80), _m(other_private, 0.99, False, someone_else), _m(own_private, 0.70, False, teacher), _m(mine, 0.99, False, teacher)],
        [_m(ref, 0.70), _m(ref, 0.65)],  # one page matching a book twice counts once (best score)
        [],
        [_m(other_private, 0.99, False, someone_else)],
    ]
    out = matching.summarize_book_matches(pages, pages_checked=4, own_book_id=mine, teacher_id=teacher)
    assert [s["book_id"] for s in out] == [str(ref)]  # ref covers 2/4; own_private only 1/4; the rest filtered
    assert out[0]["matched_pages"] == 2 and out[0]["avg_similarity"] == 0.75 and out[0]["kind"] == "variant"
    assert matching.summarize_book_matches([[_m(ref, 0.97)]], 1, mine, teacher)[0]["kind"] == "same"
    assert matching.summarize_book_matches([[_m(ref, 0.97)]], 0, mine, teacher) == []
    assert matching.summarize_book_matches([[_m(ref, 0.97)], [], [], []], 4, mine, teacher) == []  # coverage 0.25


def test_variant_endpoints_enforce_access_and_reject_bad_links(client, session_factory):
    ref_id = reference_book(session_factory)
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    _, bh = make_user(session_factory, Role.teacher, "teacherb")
    _, sh = make_user(session_factory, Role.student, "student1")
    a1, a2 = new_book(client, ah), new_book(client, ah, subject="Two")
    b_book = new_book(client, bh)
    url = lambda b, p="variant-of": f"/teacher/books/{b}/{p}"

    assert client.get(url(a1["id"], "variant-suggestions"), headers=bh).status_code == 404  # not B's book
    assert client.get(url(ref_id, "variant-suggestions"), headers=ah).status_code == 403  # reference is read-only
    assert client.get(url(a1["id"], "variant-suggestions"), headers=sh).status_code == 403
    assert client.post(url(a1["id"]), json={"base_book_id": b_book["id"]}, headers=ah).status_code == 404  # B's private book
    assert client.post(url(a1["id"]), json={"base_book_id": a1["id"]}, headers=ah).status_code == 400
    assert client.post(url(a1["id"]), json={"base_book_id": str(uuid.uuid4())}, headers=ah).status_code == 404
    assert client.post(url(ref_id), json={"base_book_id": a1["id"]}, headers=ah).status_code == 403

    assert client.post(url(a1["id"]), json={"base_book_id": a2["id"]}, headers=ah).status_code == 200
    assert client.post(url(a2["id"]), json={"base_book_id": a1["id"]}, headers=ah).status_code == 409  # would be a loop
    assert client.post(url(a2["id"]), json={"base_book_id": ref_id}, headers=ah).status_code == 200


def test_a_stale_or_tampered_report_can_never_expose_a_private_book(client, session_factory):
    """Visibility is re-checked when matches are READ, so even a stored report that wrongly names someone else's
    private book (old data, a bug) cannot leak it."""
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    _, bh = make_user(session_factory, Role.teacher, "teacherb")
    b_book = new_book(client, bh, subject="Secret")
    a_book = new_book(client, ah)
    a_ch = new_chapter(client, ah, a_book["id"])
    upload(client, ah, a_book["id"], a_ch, _text_pdf(page_text("t1_"), page_text("t2_")))
    with session_factory() as db:
        chapter = db.get(Chapter, uuid.UUID(a_ch))
        chapter.match_report = {"pages_checked": 2, "suggestions": [{
            "book_id": b_book["id"], "chapter_id": None, "chapter_title": "leak?", "kind": "same",
            "matched_pages": 2, "pages_checked": 2, "avg_similarity": 1.0}]}
        db.commit()
    assert b_book["id"] not in client.get(f"/teacher/books/{a_book['id']}/chapter-matches", headers=ah).text
    assert suggestions(client, ah, a_book["id"]) == []
</file>

<file path="backend/tests/test_phase1_flow.py">
from app.models import Role, User

#update fixtures for username field
def make_user(session_factory, role: Role, phone: str, name="Test User"):
    with session_factory() as db:
        user = User(
            supertokens_user_id=f"st-{phone}",
            name=name,
            username=f"user{phone[-6:]}",
            phone=phone,
            role=role,
            link_code=f"LINK{phone[-4:]}" if role == Role.student else None,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        db.expunge(user)
    return user, {"Authorization": f"Bearer st-{phone}"}


def test_me_requires_auth(client):
    assert client.get("/auth/me").status_code == 401


def test_student_cannot_create_room(client, session_factory):
    _, sh = make_user(session_factory, Role.student, "+919000000002")
    res = client.post("/teacher/rooms", json={"name": "Maths 10", "room_type": "single_class"}, headers=sh)
    assert res.status_code == 403


def test_full_room_and_parent_flow(client, session_factory):
    _, th = make_user(session_factory, Role.teacher, "+919000000001")
    student, sh = make_user(session_factory, Role.student, "+919000000002")
    _, ph = make_user(session_factory, Role.parent, "+919000000003")
    _, other_th = make_user(session_factory, Role.teacher, "+919000000004")

    room = client.post("/teacher/rooms", json={"name": "Maths 10", "room_type": "mixed_class"}, headers=th).json()
    assert len(room["join_code"]) == 6

    res = client.post("/student/rooms/join", json={"join_code": room["join_code"].lower()}, headers=sh)
    assert res.status_code == 200
    res = client.post("/student/rooms/join", json={"join_code": room["join_code"]}, headers=sh)
    assert res.status_code == 409
    assert client.post("/student/rooms/join", json={"join_code": "ZZZZZZ"}, headers=sh).status_code == 404

    members = client.get(f"/teacher/rooms/{room['id']}/members", headers=th).json()
    assert [m["name"] for m in members] == ["Test User"]
    assert client.get("/teacher/rooms", headers=th).json()[0]["member_count"] == 1
    assert client.get(f"/teacher/rooms/{room['id']}/members", headers=other_th).status_code == 404

    res = client.post("/parent/link", json={"link_code": student.link_code}, headers=ph)
    assert res.status_code == 200
    kids = client.get("/parent/children", headers=ph).json()
    assert kids[0]["rooms"][0]["name"] == "Maths 10"
    assert "join_code" not in kids[0]["rooms"][0]

    assert client.post("/teacher/rooms", json={"name": "X1", "room_type": "single_class"}, headers=ph).status_code == 403
    assert client.post("/student/rooms/join", json={"join_code": room["join_code"]}, headers=ph).status_code == 403
</file>

<file path="backend/tests/test_phase3_settle.py">
"""Phase 3 groundwork: the pieces that settle the open decisions (page kind, exercise -> concepts, retrieval and its
cut-off, photographed doubts, the comprehension check). No Phase 3 route or table exists yet."""
import json
import uuid

import pytest
from sqlalchemy import select

from app.assessment.checks import (
    CheckQuestionError, Question, concept_scores, generate_question, grade, plan_check, question_count, shuffle_options, student_view,
)
from app.assignments.scope import chapter_concepts, propose_exercise_concepts, subject_concepts
from app.core.config import settings
from app.db import backfill_page_kind, check_probe, exercise_map, try_doubt_photo
from app.db.retrieval_probe import format_report
from app.doubts.calibration import probe, summarize
from app.doubts.query import DOUBT, PAGE, TOO_SHORT, classify_doubt_text
from app.doubts.retrieval import GROUNDED, NOT_IN_BOOK, OUTSIDE, UNAVAILABLE, Scope, retrieve, scope_for_concepts
from app.embeddings.fake_provider import FakeEmbeddingProvider
from app.graph_store.base import EdgeRow
from app.graph_store.fake_store import FakeGraphStore
from app.llm.fake_provider import FakeLLMProvider
from app.models import Book, Chapter, ChapterStatus, Concept, ConceptEdge, Page, PageKind
from app.pipeline.concepts import extract_page, heading_page_kind
from app.pipeline.indexing import build_chapter_payload, embed_chapter
from app.pipeline.orchestrator import PipelineOrchestrator
from tests.test_step10 import SENTENCES, ChapterLLM, StubOCR, make_ready

CELL = "The cell is the basic structural unit of all living organisms and every cell has a membrane and a nucleus and cytoplasm inside it"
TISSUE = "A tissue is a group of similar cells that work together to perform one function in plants and animals such as muscle tissue"
FORCE = "Force is a push or a pull on an object and a net force changes the speed or the direction of motion of that object"
EXERCISE = "Exercises 1. What is a cell and what is a membrane 2. Name the cell parts nucleus cytoplasm 3. Why does a cell have a membrane"


def words(tag: str, n: int = 20) -> str:
    return " ".join(f"{tag}{i}" for i in range(n))


@pytest.fixture()
def embedder():
    return FakeEmbeddingProvider(settings.embedding_dim)


def add_chapter(db, book, title, seq, pages, concepts=(), status=ChapterStatus.READY):
    """pages: [(number, text, kind)], concepts: [(page number, name, description)]. Returns the chapter."""
    ch = Chapter(book_id=book.id, title=title, sequence_num=seq, status=status)
    db.add(ch)
    db.flush()
    by_number = {}
    for number, text, kind in pages:
        page = Page(chapter_id=ch.id, page_number=number, content_text=text, page_kind=kind)
        db.add(page)
        by_number[number] = page
    db.flush()
    for position, (number, name, description) in enumerate(concepts):
        db.add(Concept(page_id=by_number[number].id, name=name, description=description, position=position))
    db.flush()
    return ch


def index(db, chapter, embedder, store=None):
    embed_chapter(db, chapter, embedder)
    db.flush()
    if store is not None:
        store.replace_chapter(build_chapter_payload(db, chapter))


def make_book(db, subject="Science", reference=True, owner=None):
    book = Book(board="CBSE", class_name="9", subject=subject, publisher="NCERT", is_reference=reference, owner_teacher_id=owner)
    db.add(book)
    db.flush()
    return book


def science_chapter(db, book, embedder, store=None):
    ch = add_chapter(db, book, "Cells", 1, [
        (1, CELL, "content"), (2, TISSUE, "content"), (3, EXERCISE, "exercise"),
    ], [(1, "Cell", "The cell is the basic structural unit of living organisms with a membrane nucleus and cytoplasm"),
        (2, "Tissue", "A tissue is a group of similar cells that perform one function")])
    index(db, ch, embedder, store)
    return ch


# ---- page kind ------------------------------------------------------------------------------------

def test_heading_decides_exercise_or_recap():
    assert heading_page_kind("Exercises\n1. What is a cell?") == "exercise"
    assert heading_page_kind("Review Questions\n1. Name") == "exercise"
    assert heading_page_kind("At a Glance\nThe cell is") == "recap"
    assert heading_page_kind("Cells divide. The summary of this process is long.") is None


def test_filter_reports_the_kind_of_non_teaching_page_from_the_heading_not_the_model():
    llm = FakeLLMProvider()
    llm.complete_json = lambda s, u: json.dumps({"page_kind": "recap", "concepts": []})
    assert extract_page(llm, "Exercises\n1. What is a cell?").page_kind == "exercise"
    assert extract_page(llm, "At a Glance\nCells are units").page_kind == "recap"


def test_the_pipeline_saves_page_kind(session_factory):
    pages = SENTENCES + ["At a Glance " + SENTENCES[0], "Exercises 1. What is an atom? " + SENTENCES[1]]
    with session_factory() as db:
        book = Book(board="CBSE", class_name="9", subject="Sci", publisher="NCERT", is_reference=True)
        db.add(book)
        db.flush()
        ch = make_ready(db, book, "A", 1)
        PipelineOrchestrator(db, ocr_provider=StubOCR(pages), llm_provider=ChapterLLM()).process_chapter_file(ch, b"x", "pdf", None)
        kinds = [p.page_kind for p in db.scalars(select(Page).where(Page.chapter_id == ch.id).order_by(Page.page_number))]
    assert kinds == ["content", "content", "content", "recap", "exercise"]


def test_backfill_labels_old_pages_once_and_only_touches_content_pages(session_factory):
    with session_factory() as db:
        book = make_book(db)
        add_chapter(db, book, "Old", 1, [
            (1, CELL, "content"), (2, TISSUE, "content"), (3, FORCE, "content"), (4, CELL + " again", "content"), (5, TISSUE + " again", "content"),
            (6, "At a Glance " + CELL, "content"), (7, "Some question text without any heading " + TISSUE, "content"), (8, "Exercises 1. what", "other"),
        ])
        db.commit()
    dry = backfill_page_kind.run(session_factory, yes=False)
    assert "dry run, would label" in dry[-1]
    with session_factory() as db:
        assert {p.page_kind for p in db.scalars(select(Page))} == {"content", "other"}  # dry run wrote nothing
    backfill_page_kind.run(session_factory, yes=True)
    with session_factory() as db:
        kinds = {p.page_number: p.page_kind for p in db.scalars(select(Page))}
    # 6 = summary heading in the last 40%; 7 comes after it = exercise; 8 was labelled `other` by someone: untouched
    assert kinds == {1: "content", 2: "content", 3: "content", 4: "content", 5: "content", 6: "recap", 7: "exercise", 8: "other"}
    assert "nothing" in backfill_page_kind.run(session_factory, yes=True)[-1]


# ---- scope: how each assignment level becomes concepts ---------------------------------------------

def test_chapter_and_subject_scope_use_canonical_concepts_of_ready_chapters(session_factory, embedder):
    with session_factory() as db:
        sci, maths = make_book(db), make_book(db, "Maths")
        c1 = science_chapter(db, sci, embedder)
        add_chapter(db, sci, "Draft", 2, [(1, FORCE, "content")], [(1, "Force", "push or pull")], status=ChapterStatus.PROCESSING)
        add_chapter(db, maths, "Sets", 1, [(1, FORCE, "content")], [(1, "Set", "a collection")])
        assert [c.name for c in chapter_concepts(db, c1.id)] == ["Cell", "Tissue"]
        assert [c.name for c in subject_concepts(db, [sci.id, maths.id], "science")] == ["Cell", "Tissue"]
        assert subject_concepts(db, [], "Science") == []


def test_exercise_pages_are_mapped_to_the_concepts_they_practise(session_factory, embedder):
    with session_factory() as db:
        book = make_book(db)
        ch = science_chapter(db, book, embedder)
        mapping = propose_exercise_concepts(db, ch, min_similarity=0.05)
        assert mapping.status == "ok" and mapping.exercise_pages == [3]
        assert mapping.proposed[0].name == "Cell"  # the exercise is about cells and membranes
        assert mapping.per_page[3][0][0] == "Cell"
        # a high floor proposes nothing rather than something arbitrary
        assert propose_exercise_concepts(db, ch, min_similarity=0.99).proposed == []
        # the teacher can point at pages explicitly (e.g. the pages of Ex.9.5) instead of the labelled ones
        assert propose_exercise_concepts(db, ch, [2], min_similarity=0.05).proposed[0].name == "Tissue"


def test_exercise_mapping_degrades_clearly(session_factory, embedder):
    with session_factory() as db:
        book = make_book(db)
        plain = add_chapter(db, book, "NoEx", 1, [(1, CELL, "content")], [(1, "Cell", "d")])
        assert propose_exercise_concepts(db, plain).status == "no_exercise_pages"
        unindexed = add_chapter(db, book, "NoVec", 2, [(1, CELL, "content"), (2, EXERCISE, "exercise")], [(1, "Cell", "d")])
        assert propose_exercise_concepts(db, unindexed).status == "no_vectors"
        capped = science_chapter(db, book, embedder)
        assert len(propose_exercise_concepts(db, capped, min_similarity=-1, max_concepts=1).proposed) == 1


def test_exercise_map_command_prints_the_evidence_and_writes_nothing(session_factory, embedder):
    with session_factory() as db:
        science_chapter(db, make_book(db), embedder)
        db.commit()
    text = "\n".join(exercise_map.run(session_factory, min_similarity=0.05))
    assert "page 3:" in text and "PROPOSED: Cell" in text and "Nothing was written" in text


# ---- retrieval ---------------------------------------------------------------------------------------

@pytest.fixture()
def world(session_factory, embedder, indexing_on):
    """Two books of two teachers in one store, like production: the student is linked only to `mine`."""
    store = FakeGraphStore()
    with session_factory() as db:
        mine, other = make_book(db), make_book(db, "Science", reference=True)
        cells = science_chapter(db, mine, embedder, store)
        force = add_chapter(db, mine, "Force", 2, [(1, FORCE, "content")], [(1, "Force", "Force is a push or a pull on an object")])
        index(db, force, embedder, store)
        db.add(ConceptEdge(chapter_id=cells.id, concept_id=chapter_concepts(db, cells.id)[1].id,
                           prerequisite_id=chapter_concepts(db, cells.id)[0].id, source="llm"))
        db.flush()
        store.replace_chapter(build_chapter_payload(db, cells))
        secret = add_chapter(db, other, "Secret", 1, [(1, "photosynthesis converts sunlight water and carbon dioxide into glucose and oxygen in the chloroplast of green leaves", "content")],
                             [(1, "Photosynthesis", "Plants make glucose from sunlight water and carbon dioxide")])
        index(db, secret, embedder, store)
        db.commit()
        yield {"db": db, "store": store, "mine": mine.id, "other": other.id, "cells": cells, "force": force, "secret": secret}


def ask(w, text, embedder, scope=None, books=None, threshold=0.2):
    books = [w["mine"]] if books is None else books
    return retrieve(w["db"], text, embedder=embedder, store=w["store"], book_ids=books, scope=scope, threshold=threshold)


def test_a_doubt_inside_the_book_is_grounded_with_page_text_and_a_prerequisite_refresher(world, embedder):
    r = ask(world, "what is a tissue group of similar cells", embedder, threshold=0.5)
    assert r.status == GROUNDED and r.confidence >= 0.5
    assert r.pages[0].text.startswith("A tissue is a group") and r.pages[0].chapter_title == "Cells"
    assert r.concepts[0].name == "Tissue"
    assert [p.name for p in r.prerequisites] == ["Cell"]  # Tissue needs Cell; never the hit itself


def test_a_doubt_with_no_support_in_the_books_is_not_in_book(world, embedder):
    r = ask(world, "zebra quantum jukebox harmonica", embedder, threshold=0.5)
    assert r.status == NOT_IN_BOOK and r.pages == [] and r.concepts == []


def test_retrieval_never_leaves_the_linked_books(world, embedder):
    q = "photosynthesis sunlight water carbon dioxide glucose chloroplast"
    assert ask(world, q, embedder, threshold=0.45).status == NOT_IN_BOOK                     # not linked: invisible
    r = ask(world, q, embedder, books=[world["other"]], threshold=0.45)
    assert r.status == GROUNDED and r.pages[0].book_id == str(world["other"])             # linked: found
    assert ask(world, q, embedder, books=[], threshold=0.0).status == NOT_IN_BOOK          # no books: never "everything"


def test_the_page_text_is_checked_in_postgres_not_taken_on_trust_from_the_store(world, embedder):
    world["db"].get(Chapter, world["cells"].id).status = ChapterStatus.PROCESSING  # e.g. re-uploaded since the sync
    world["db"].flush()
    r = ask(world, "what is a tissue group of similar cells", embedder)
    assert all(p.chapter_id != str(world["cells"].id) for p in r.pages)


def test_scoped_to_an_assignment_then_outside_assignment_when_the_books_cover_it_elsewhere(world, embedder):
    q = "what is a tissue group of similar cells"
    inside = ask(world, q, embedder, scope=Scope(chapter_ids={str(world["cells"].id)}))
    assert inside.status == GROUNDED
    outside = ask(world, q, embedder, scope=Scope(chapter_ids={str(world["force"].id)}), threshold=0.3)
    assert outside.status == OUTSIDE and outside.elsewhere[0].name == "Tissue" and outside.pages == []
    cell = next(c for c in chapter_concepts(world["db"], world["cells"].id) if c.name == "Cell")
    tissue = next(c for c in chapter_concepts(world["db"], world["cells"].id) if c.name == "Tissue")
    cell_only = ask(world, q, embedder, scope=scope_for_concepts(world["db"], [cell]), threshold=0.5)
    assert cell_only.status == OUTSIDE  # a concept-level assignment is narrower than its chapter: the tissue page is outside it
    assert ask(world, q, embedder, scope=scope_for_concepts(world["db"], [tissue]), threshold=0.5).status == GROUNDED


def test_service_failures_are_unavailable_not_a_guess(world, embedder):
    world["store"].fail_with = RuntimeError("down")
    assert ask(world, "what is a tissue", embedder).status == UNAVAILABLE

    class Broken:
        model_name, dim = "x", 4

        def embed(self, texts):
            from app.embeddings import EmbeddingError
            raise EmbeddingError("down")

    world["store"].fail_with = None
    assert retrieve(world["db"], "what is a tissue", embedder=Broken(), store=world["store"], book_ids=[world["mine"]]).status == UNAVAILABLE
    assert retrieve(world["db"], "x", embedder=None, store=None, book_ids=[world["mine"]]).status == UNAVAILABLE


# ---- photographed / typed doubts ------------------------------------------------------------------------

def test_photo_text_is_classified_by_length():
    assert classify_doubt_text("", from_photo=True).kind == TOO_SHORT
    assert classify_doubt_text("smudge ink", from_photo=True).kind == TOO_SHORT
    assert classify_doubt_text("cell", from_photo=False).kind == DOUBT  # one typed word is a legitimate doubt
    assert classify_doubt_text("why does the cell need a membrane at all", from_photo=True).kind == DOUBT
    page = classify_doubt_text(words("w", 80), from_photo=True)
    assert page.kind == PAGE and page.words == 80
    assert classify_doubt_text("   ", from_photo=False).kind == TOO_SHORT


def test_try_doubt_photo_command_covers_each_outcome(world, embedder):
    run = lambda text, photo=True, scope=None: "\n".join(try_doubt_photo.run(
        world["db"], text, photo, [world["mine"]], scope or [], embedder, world["store"]))
    assert "retake" in run("blur")
    assert "retrieval: grounded" in run("what is a tissue group of similar cells")
    page = run(CELL + " " + TISSUE + " " + words("filler", 30))
    assert "classified as: page" in page and "pick the concept" in page
    assert "ask your teacher" in run("zebra quantum jukebox harmonica harmonica quantum zebra jukebox", photo=True)


# ---- the comprehension check -------------------------------------------------------------------------------

def test_check_size_has_a_floor_and_a_ceiling():
    assert [question_count(n) for n in (0, 1, 2, 5, 10, 11, 60)] == [2, 2, 2, 5, 10, 10, 10]


def test_one_concept_still_gets_a_real_check_and_a_big_scope_is_capped_weak_first():
    assert plan_check(["a"]) == ["a", "a"]
    assert plan_check([]) == []
    ids = [f"c{i}" for i in range(15)]
    plan = plan_check(ids, priority_ids=["c13", "c14", "c9", "zzz"])
    assert len(plan) == 10 and {"c13", "c14", "c9"} <= set(plan) and plan == sorted(plan, key=ids.index)
    assert plan_check(ids[:4]) == ids[:4]  # in book order, one each


class Scripted:
    model_name = "scripted"

    def __init__(self, *replies):
        self.replies, self.calls, self.prompts = list(replies), 0, []

    def complete_json(self, system, user):
        self.prompts.append(user)
        self.calls += 1
        return self.replies.pop(0)


GOOD = json.dumps({"question": "Why does a cell have a membrane?", "options": ["To control what enters", "To store sunlight", "To make bones", "To pump blood"],
                   "correct_index": 0, "explanation": "The membrane controls entry."})


def test_a_valid_question_is_graded_by_code_and_the_student_view_has_no_key():
    q = generate_question(Scripted(GOOD), "c1", "Cell membrane", "d", "page text", seed="s")
    assert q.options[q.correct_index] == "To control what enters"
    view = student_view(q)
    assert set(view) == {"concept_id", "question", "options"} and "correct_index" not in json.dumps(view) and "explanation" not in view
    assert grade(q, q.correct_index).correct and not grade(q, (q.correct_index + 1) % 4).correct
    assert not grade(q, None).correct and not grade(q, True).correct and not grade(q, 9).correct
    assert grade(q, 0).explanation == "The membrane controls entry."


def test_options_are_shuffled_but_the_key_follows_the_right_answer():
    positions = set()
    for i in range(30):
        q = shuffle_options(Question("c", "Q?" * 5, ["right", "b", "c", "d"], 0, ""), seed=str(i))
        assert q.options[q.correct_index] == "right"
        positions.add(q.correct_index)
    assert len(positions) > 1
    again = [shuffle_options(Question("c", "Q?" * 5, ["right", "b", "c", "d"], 0, ""), seed="same") for _ in range(2)]
    assert again[0].options == again[1].options  # seeded: the same question looks the same on a reload


@pytest.mark.parametrize("bad", [
    "not json",
    json.dumps({"question": "Why does a cell have a membrane?", "options": ["a", "b", "c"], "correct_index": 0}),
    json.dumps({"question": "Why does a cell have a membrane?", "options": ["a", "a", "c", "d"], "correct_index": 0}),
    json.dumps({"question": "Why does a cell have a membrane?", "options": ["a", "b", "c", "All of the above"], "correct_index": 0}),
    json.dumps({"question": "Why does a cell have a membrane?", "options": ["a", "b", "c", "d"], "correct_index": 4}),
])
def test_invalid_questions_are_retried_with_a_correction_then_accepted(bad):
    llm = Scripted(bad, GOOD)
    q = generate_question(llm, "c1", "Cell", "d", "text")
    assert llm.calls == 2 and "previous reply was invalid" in llm.prompts[1] and q.question.startswith("Why does")


def test_three_invalid_replies_raise_a_safe_error():
    with pytest.raises(CheckQuestionError) as e:
        generate_question(Scripted("x", "y", "z"), "c1", "Cell", "d", "text")
    assert "try again" in str(e.value).lower()


def test_concept_scores_are_the_share_correct_per_concept():
    q = lambda c: Question(c, "Q?" * 5, ["a", "b", "c", "d"], 0, "")
    graded = [grade(q("a"), 0), grade(q("a"), 1), grade(q("b"), 0)]
    assert concept_scores(graded) == {"a": 0.5, "b": 1.0}


def test_check_probe_prints_the_question_and_the_key_separately(session_factory, embedder):
    with session_factory() as db:
        science_chapter(db, make_book(db), embedder)
        db.commit()
    text = "\n".join(check_probe.run(session_factory, FakeLLMProvider(), n=2))
    assert "Q: Which statement about" in text and "KEY (not shown to the student)" in text and "2/2 valid" in text
    sizes = "\n".join(check_probe.sizes(session_factory))
    assert "Cells: 2 concepts -> 2 questions" in sizes


# ---- calibrating "not in your book" ------------------------------------------------------------------

def test_summarize_finds_the_gap_between_in_book_and_off_topic():
    ok = summarize([0.62, 0.55, 0.7, 0.58, 0.66, 0.6, 0.64, 0.57, 0.61, 0.59], [0.2, 0.31, 0.25], [0.3], threshold=0.45)
    assert ok["separable"] and ok["recommended"] == pytest.approx((0.55 + 0.31) / 2, abs=0.01) and ok["pass"]
    overlap = summarize([0.3, 0.5, 0.6], [0.45, 0.2], [], threshold=0.4)
    assert not overlap["separable"] and overlap["recommended"] is None and not overlap["pass"]
    assert "OVERLAP" in "\n".join(format_report({**overlap, "status": "done", "doubts": 3, "off_topic_values": [0.2],
                                                 "in_book_values": [0.3], "right_chapter_top_hit": 1.0, "wrong_chapter_outside": None}))


def test_probe_runs_end_to_end_on_stored_chapters(session_factory, embedder, indexing_on):
    store = FakeGraphStore()
    with session_factory() as db:
        book = make_book(db)
        for i, (title, text) in enumerate([("Cells", CELL), ("Tissue", TISSUE), ("Force", FORCE)], 1):
            ch = add_chapter(db, book, title, i, [(1, text, "content"), (2, text + " more", "content")], [(1, title, text), (2, title + " two", text)])
            index(db, ch, embedder, store)
        db.commit()
        report = probe(db, FakeLLMProvider(), embedder, store, [book.id], pages=6)
    assert report["status"] == "done" and report["doubts"] >= 3 and 0 <= report["right_chapter_top_hit"] <= 1
    assert len(report["off_topic_values"]) == 10 and "in_book_p10" in report


def test_probe_says_when_there_is_too_little_to_judge(session_factory, embedder):
    with session_factory() as db:
        book = make_book(db)
        assert probe(db, FakeLLMProvider(), embedder, FakeGraphStore(), [book.id])["status"] == "not_enough_pages"
</file>

<file path="backend/tests/test_pipeline.py">
import uuid

import pytest
from sqlalchemy import select

from app.core.errors import ProcessingError
from app.models import Book, Chapter, Concept, Page, Role, User
from app.pipeline.orchestrator import PipelineOrchestrator


def _teacher(session_factory):
    with session_factory() as db:
        u = User(supertokens_user_id="st-t1", name="T", username="teach1", phone="1", role=Role.teacher)
        db.add(u)
        db.commit()
        db.refresh(u)
        db.expunge(u)
    return u, {"Authorization": "Bearer st-t1"}


def _book_and_chapter(db, owner=None):
    """Owned by `owner` (a teacher) if given, otherwise a reference book."""
    book = Book(board="CBSE", class_name="Class 9", subject="Science", publisher="Test",
                is_reference=owner is None, owner_teacher_id=owner.id if owner else None)
    db.add(book)
    db.flush()
    ch = Chapter(book_id=book.id, title="Matter", sequence_num=1)
    db.add(ch)
    db.commit()
    return book.id, ch.id


def _text_pdf(*page_texts: str) -> bytes:
    """Smallest valid-enough text PDF (pypdf rebuilds the xref table)."""
    objs = ["<< /Type /Catalog /Pages 2 0 R >>"]
    kids = " ".join(f"{3 + i * 2} 0 R" for i in range(len(page_texts)))
    objs.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(page_texts)} >>")
    for i, t in enumerate(page_texts):
        content_id = 4 + i * 2
        objs.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 200] /Contents {content_id} 0 R "
            f"/Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> >>"
        )
        stream = f"BT /F1 12 Tf 10 100 Td ({t}) Tj ET"
        objs.append(f"<< /Length {len(stream)} >>\nstream\n{stream}\nendstream")
    out = "%PDF-1.4\n" + "".join(f"{n + 1} 0 obj\n{o}\nendobj\n" for n, o in enumerate(objs))
    out += f"trailer\n<< /Root 1 0 R /Size {len(objs) + 1} >>\nstartxref\n0\n%%EOF"
    return out.encode()


class CountingLLM:
    model_name = "counting"

    def __init__(self, reply=None):
        self.calls = 0
        self.reply = reply

    def complete_json(self, system, user):
        self.calls += 1
        return self.reply or '{"concepts":[{"name":"Matter","description":"d","learning_objectives":[],"prerequisites":[]}]}'


def test_app_boots(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_teacher_upload_end_to_end_with_fake_providers(client, session_factory):
    teacher, th = _teacher(session_factory)
    with session_factory() as db:
        book_id, ch_id = _book_and_chapter(db, owner=teacher)
    res = client.post(
        f"/teacher/books/{book_id}/chapters/{ch_id}/pages/upload",
        files={"file": ("p.pdf", _text_pdf("Matter is anything with mass", "Particles of matter attract"), "application/pdf")},
        headers=th,
    )
    assert res.status_code == 202, res.text
    assert res.json()["status"] == "processing"  # the response returns before processing finishes

    # TestClient runs the background job before returning control, so by now it is done.
    pages = client.get(f"/teacher/books/{book_id}/chapters/{ch_id}/pages", headers=th).json()
    assert [p["page_number"] for p in pages] == [1, 2]
    assert all(p["concepts"] for p in pages)


def _chapter(db, book_id, n):
    ch = Chapter(book_id=book_id, title=f"Ch {n}", sequence_num=n)
    db.add(ch)
    db.commit()
    return ch


def test_identical_page_in_another_chapter_reuses_concepts_without_llm_call(session_factory):
    pdf = _text_pdf("Matter is anything that occupies space and has mass and we see matter all around us in our surroundings every single day")
    with session_factory() as db:
        book_id, ch1_id = _book_and_chapter(db)
        ch2 = _chapter(db, book_id, 2)
        llm = CountingLLM()
        orch = PipelineOrchestrator(db, llm_provider=llm)
        orch.process_chapter_file(db.get(Chapter, ch1_id), pdf, "pdf", None)
        db.commit()
        assert llm.calls == 1
        pages = orch.process_chapter_file(ch2, pdf, "pdf", None)
        db.commit()
        assert llm.calls == 1  # second chapter matched the first: zero LLM cost
        assert pages[0].concepts[0].name == "Matter"


def test_reprocessing_a_chapter_replaces_pages_instead_of_duplicating(session_factory):
    with session_factory() as db:
        _, ch_id = _book_and_chapter(db)
        orch = PipelineOrchestrator(db, llm_provider=CountingLLM())
        ch = db.get(Chapter, ch_id)
        orch.process_chapter_file(ch, _text_pdf("first version of page one", "and page two"), "pdf", None)
        db.commit()
        orch.process_chapter_file(ch, _text_pdf("a completely different single page"), "pdf", None)
        db.commit()
        pages = db.scalars(select(Page).where(Page.chapter_id == ch_id)).all()
        assert [p.page_number for p in pages] == [1]
        assert "different" in pages[0].content_text


def test_invalid_llm_json_fails_loudly_and_rolls_back(session_factory):
    pdf = _text_pdf("page one text here", "page two text here")
    with session_factory() as db:
        _, ch_id = _book_and_chapter(db)
        llm = CountingLLM(reply="not json at all")
        with pytest.raises(ProcessingError, match="page 1"):
            PipelineOrchestrator(db, llm_provider=llm).process_chapter_file(db.get(Chapter, ch_id), pdf, "pdf", None)
        assert llm.calls == 3  # first try + 2 correction retries
        db.rollback()  # what the job does on failure
        assert db.scalars(select(Page)).all() == []  # no half-processed chapter
</file>

<file path="backend/tests/test_processing.py">
import pytest
from app.pipeline.fingerprint import compute_minhash, compute_jaccard_similarity


def test_minhash_fingerprint_identical_and_near_duplicate():
    text1 = (
        "Matter in our surroundings: Everything in this universe is made of material "
        "which scientists have named matter. The air we breathe, the food we eat, stones, "
        "clouds, stars, plants and animals, even a drop of water."
    )
    text2 = (
        "Matter in our surroundings: Everything in this universe is made of material "
        "which scientists have named matter. The air we breathe, the food we eat, stones, "
        "clouds, stars, plants and animals, even a small drop of water."
    )
    unrelated_text = (
        "The French Revolution began in May 1789 when the Estates-General was convened "
        "by King Louis XVI to deal with the debt crisis of the monarchy."
    )

    fp1 = compute_minhash(text1)
    fp2 = compute_minhash(text2)
    fp_diff = compute_minhash(unrelated_text)

    # Identical/near-identical should produce a high similarity score
    sim_high = compute_jaccard_similarity(fp1, fp2)
    assert sim_high >= 0.85

    # Completely different subject matter should yield very low similarity
    sim_low = compute_jaccard_similarity(fp1, fp_diff)
    assert sim_low < 0.20
</file>

<file path="backend/tests/test_roles.py">
import pytest

from app.models import Role, User

#update fixtures for username field
def add_user(session_factory, role: Role):
    with session_factory() as db:
        db.add(User(
            supertokens_user_id=f"st-{role.value}",
            name="Test",
            username=f"{role.value}_user",
            phone="+919000000000",
            role=role,
        ))
        db.commit()


def test_no_session_is_401(client):
    assert client.get("/teacher/ping").status_code == 401


def test_unknown_session_user_is_401(client):
    res = client.get("/teacher/ping", headers={"Authorization": "Bearer st-ghost"})
    assert res.status_code == 401


@pytest.mark.parametrize("role", list(Role))
def test_each_role_only_reaches_its_own_routes(client, session_factory, role):
    add_user(session_factory, role)
    headers = {"Authorization": f"Bearer st-{role.value}"}
    for target in Role:
        res = client.get(f"/{target.value}/ping", headers=headers)
        assert res.status_code == (200 if target == role else 403)
</file>

<file path="backend/tests/test_step10.py">
"""Step 10: graph quality - near-duplicate merge, backward edges, activity/recap filtering, edge copy on full reuse."""
import json

import pytest
from sqlalchemy import select

from app.core.errors import ProcessingError
from app.models import Book, Chapter, ChapterStatus, Concept, ConceptEdge, Page
from app.pipeline.concepts import extract_page, looks_like_activity, looks_like_recap_page
from app.pipeline.graph import build_chapter_graph, loose_key
from app.pipeline.orchestrator import PipelineOrchestrator
from tests.test_concept_graph import NoLinksLLM, add_page, edges_by_name, make_chapter


# ---- 10d: near-duplicate names -----------------------------------------------------------------

def test_loose_key_ignores_stop_words_case_and_order():
    assert loose_key("Cell as the Basic Unit of Life") == loose_key("Cell as Basic Unit of Life")
    assert loose_key("Basic unit of life: the cell") == loose_key("Cell as Basic Unit of Life")
    assert loose_key("Cell membrane") != loose_key("Cell wall")
    assert loose_key("Prokaryotic cells") == loose_key("Prokaryotic cell")
    assert loose_key("Chloroplasts") == loose_key("chloroplast")
    assert loose_key("DNA (Deoxyribonucleic acid)") == loose_key("DNA")
    assert loose_key("Nucleus") != loose_key("Nucleolus") and loose_key("Mitosis") != loose_key("Meiosis")
    assert loose_key("Endoplasmic Reticulum (ER)") == loose_key("Endoplasmic reticulum")


def test_stop_word_variants_merge_and_prerequisites_resolve_to_the_merged_concept(session_factory):
    with session_factory() as db:
        ch = make_chapter(db)
        add_page(db, ch, 1, ("Cell as the Basic Unit of Life", []))
        add_page(db, ch, 2, ("Cell membrane", ["Cell as Basic Unit of Life"]))
        add_page(db, ch, 3, ("Cell as Basic Unit of Life", []))
        report = build_chapter_graph(db, ch, NoLinksLLM())
        assert report["duplicate_names_merged"] == 1
        assert edges_by_name(db, ch) == {("Cell as the Basic Unit of Life", "Cell membrane", "page")}


NAME_VECTORS = {
    "Plastids": [1.0, 0.0, 0.0],
    "Plastids in plant cells": [0.99, 0.1, 0.0],
    "Cell wall": [0.0, 1.0, 0.0],
    "Example 1.2 Speed": [0.0, 0.0, 1.0],
    "Example 1.3 Speed": [0.0, 0.0, 1.0],
}


def vectors(names):
    return [NAME_VECTORS[n] for n in names]


def test_embedding_similarity_merges_near_duplicates_but_not_different_ideas_or_numbers(session_factory):
    with session_factory() as db:
        ch = make_chapter(db)
        add_page(db, ch, 1, ("Plastids", []), ("Cell wall", []))
        add_page(db, ch, 2, ("Plastids in plant cells", []), ("Example 1.2 Speed", []))
        add_page(db, ch, 3, ("Example 1.3 Speed", []))
        report = build_chapter_graph(db, ch, NoLinksLLM(), embedder=vectors)
        assert report["merge_by_embedding"] == "done" and report["duplicate_names_merged"] == 1
        canonical = {c.name for c in db.scalars(select(Concept).where(Concept.is_canonical.is_(True)))}
        assert canonical == {"Plastids", "Cell wall", "Example 1.2 Speed", "Example 1.3 Speed"}


def test_embedder_failure_never_fails_the_chapter(session_factory):
    def broken(names):
        raise RuntimeError("secret-key-123 service down")

    with session_factory() as db:
        ch = make_chapter(db)
        add_page(db, ch, 1, ("Plastids", []))
        add_page(db, ch, 2, ("Plastids in plant cells", ["Plastids"]))
        report = build_chapter_graph(db, ch, NoLinksLLM(), embedder=broken)
        assert report["merge_by_embedding"] == "failed" and report["duplicate_names_merged"] == 0
        assert "secret" not in json.dumps(report)
        assert report["edges"] == 1


# ---- 10b/10c: recap pages and activities ------------------------------------------------------

def reply(page_kind="content", **concepts):
    items = [{"name": n, "kind": k, "description": "d"} for n, k in concepts.items()]
    return json.dumps({"page_kind": page_kind, "concepts": items})


class Scripted:
    model_name = "scripted"

    def __init__(self, text):
        self.text, self.calls = text, 0

    def complete_json(self, system, user):
        self.calls += 1
        return self.text


def test_activities_and_exercises_are_filtered_by_kind():
    out = extract_page(Scripted(reply(Osmosis="idea", Potato_demo="activity", Q3="exercise")), "Osmosis is the movement of water")
    assert [c.name for c in out.concepts] == ["Osmosis"] and out.dropped == 2


def test_activity_names_are_filtered_even_if_the_model_calls_them_ideas():
    out = extract_page(Scripted(json.dumps({"concepts": [
        {"name": "Osmosis experiment with potato pieces"}, {"name": "Onion Root Tip Experiment"},
        {"name": "Educational Activities on Cell Division"}, {"name": "Mitosis"}]})), "Mitosis divides a cell in two")
    assert [c.name for c in out.concepts] == ["Mitosis"] and out.dropped == 3
    assert looks_like_activity("Fig. 2.19 Meiosis") and not looks_like_activity("Cell membrane")


def test_recap_pages_keep_no_concepts_whether_flagged_by_the_model_or_the_heading():
    by_model = extract_page(Scripted(reply("recap", Cell="idea")), "The cell is the unit")
    assert by_model.concepts == [] and by_model.page_kind == "recap" and by_model.dropped == 1
    by_heading = extract_page(Scripted(reply("content", Cell="idea")), "At a Glance\n The cell is the unit of life")
    assert by_heading.concepts == []
    assert looks_like_recap_page("N 25 Cell\nExercises\n1. What is a cell?")
    assert not looks_like_recap_page("Cells divide. The summary of this process is long.\n" + "x " * 200)


def test_old_style_replies_without_kind_still_work():
    out = extract_page(Scripted('{"concepts":[{"name":"Matter","description":"d"}]}'), "Matter has mass")
    assert [c.name for c in out.concepts] == ["Matter"] and out.dropped == 0


# ---- pipeline level: recap pages are not flagged as bad scans; edges are copied -----------------

SENTENCES = [
    "Atoms are the smallest particles of an element that keep its chemical properties and they combine to form molecules in many ways.",
    "Molecules join together through chemical bonds and the shared electrons decide how strong each bond is within a compound.",
    "Compounds have properties very different from their elements because their atoms are arranged in fixed repeating patterns.",
]


class StubOCR:
    def __init__(self, pages):
        self.pages = pages

    def extract_layout(self, data, ext):
        return {"pages": [{"page_number": i + 1, "text": t, "lines": []} for i, t in enumerate(self.pages)]}


class ChapterLLM:
    """Page replies by text; every linking call returns a DIFFERENT edge set, like a real model would."""
    model_name = "scripted"

    def __init__(self):
        self.page_calls = self.link_calls = 0

    def complete_json(self, system, user):
        if user.startswith("CONCEPTS:\n"):
            self.link_calls += 1
            return json.dumps({"edges": [{"concept": 3, "prerequisites": [self.link_calls % 2 + 1]}]})
        self.page_calls += 1
        for i, s in enumerate(SENTENCES, 1):
            if s in user:
                return json.dumps({"concepts": [{"name": f"Concept {i}", "description": "d"}]})
        if "rivers" in user:
            return json.dumps({"concepts": [{"name": "Rivers", "description": "d"}]})
        return '{"concepts": []}'


def make_ready(db, owner_book, title, seq):
    ch = Chapter(book_id=owner_book.id, title=title, sequence_num=seq, status=ChapterStatus.PROCESSING)
    db.add(ch)
    db.flush()
    return ch


def run(db, chapter, llm, pages=SENTENCES):
    PipelineOrchestrator(db, ocr_provider=StubOCR(pages), llm_provider=llm).process_chapter_file(chapter, b"x", "pdf", None)
    chapter.status = ChapterStatus.READY
    db.flush()


def edge_names(db, chapter):
    return edges_by_name(db, chapter)


def test_identical_chapter_gets_a_copy_of_the_graph_not_a_new_llm_opinion(session_factory):
    llm = ChapterLLM()
    with session_factory() as db:
        book = Book(board="CBSE", class_name="9", subject="Sci", publisher="NCERT", is_reference=True)
        db.add(book)
        db.flush()
        first, second = make_ready(db, book, "A", 1), make_ready(db, book, "B", 2)
        run(db, first, llm)
        assert llm.link_calls == 1 and llm.page_calls == 3
        run(db, second, llm)
        assert llm.link_calls == 1 and llm.page_calls == 3  # no linking call, no page calls
        assert second.graph_report["edges_copied"] is True
        assert edge_names(db, second) == edge_names(db, first) and edge_names(db, first)
        new_ids = {c.id for c in db.scalars(select(Concept).join(Page).where(Page.chapter_id == second.id))}
        assert all(e.concept_id in new_ids and e.prerequisite_id in new_ids
                   for e in db.scalars(select(ConceptEdge).where(ConceptEdge.chapter_id == second.id)))


def test_a_changed_page_means_the_graph_is_built_again(session_factory):
    llm = ChapterLLM()
    with session_factory() as db:
        book = Book(board="CBSE", class_name="9", subject="Sci", publisher="NCERT", is_reference=True)
        db.add(book)
        db.flush()
        first, second = make_ready(db, book, "A", 1), make_ready(db, book, "B", 2)
        run(db, first, llm)
        run(db, second, llm, pages=[*SENTENCES[:2], "A completely different page about rivers, deltas and the sediment they carry to the sea over thousands of years."])
        assert llm.link_calls == 2 and not second.graph_report.get("edges_copied")


def test_fresh_run_ignores_stored_concepts(session_factory):
    llm = ChapterLLM()
    with session_factory() as db:
        book = Book(board="CBSE", class_name="9", subject="Sci", publisher="NCERT", is_reference=True)
        db.add(book)
        db.flush()
        first, second = make_ready(db, book, "A", 1), make_ready(db, book, "B", 2)
        run(db, first, llm)
        PipelineOrchestrator(db, ocr_provider=StubOCR(SENTENCES), llm_provider=llm, reuse_concepts=False) \
            .process_chapter_file(second, b"x", "pdf", None)
        assert llm.page_calls == 6 and not second.graph_report.get("edges_copied")


def test_recap_page_with_no_concepts_is_not_flagged_as_a_bad_scan(session_factory):
    llm = ChapterLLM()
    long_recap = "At a Glance\n" + " ".join(["The cell is the basic unit of life and it divides."] * 8)
    with session_factory() as db:
        book = Book(board="CBSE", class_name="9", subject="Sci", publisher="NCERT", is_reference=True)
        db.add(book)
        db.flush()
        ch = make_ready(db, book, "A", 1)
        run(db, ch, llm, pages=[SENTENCES[0], long_recap])
        assert ch.graph_report["review_pages"] == [] and ch.graph_report["recap_pages"] == 1


def test_sidebars_are_dropped_and_near_misses_are_reported(session_factory):
    out = extract_page(Scripted(reply(Mitosis="idea", Arun_Kumar_Sharma_and_Chromosome_Research="sidebar")), "Mitosis divides a cell")
    assert [c.name for c in out.concepts] == ["Mitosis"] and out.dropped == 1

    near = {"Cell membrane": [1.0, 0.0], "Cell membrane structure": [0.88, 0.475]}  # cosine ~0.88: close, not merged
    with session_factory() as db:
        ch = make_chapter(db)
        add_page(db, ch, 1, ("Cell membrane", []))
        add_page(db, ch, 2, ("Cell membrane structure", []))
        report = build_chapter_graph(db, ch, NoLinksLLM(), embedder=lambda names: [near[n] for n in names])
        assert report["duplicate_names_merged"] == 0
        assert report["near_duplicates_not_merged"] == [{"a": "Cell membrane", "b": "Cell membrane structure", "similarity": 0.88}]


def test_prerequisite_named_without_the_parenthetical_resolves(session_factory):
    with session_factory() as db:
        ch = make_chapter(db)
        add_page(db, ch, 1, ("DNA (Deoxyribonucleic acid)", []))
        add_page(db, ch, 2, ("Chromatin", ["DNA"]))
        report = build_chapter_graph(db, ch, NoLinksLLM())
        assert report["unresolved_prerequisites"] == [] and report["edges"] == 1


def test_pages_after_the_chapter_summary_are_exercises(session_factory):
    llm = ChapterLLM()
    summary = "At a Glance\n" + " ".join(["The cell is the basic unit of life and it divides."] * 6)
    pages = [SENTENCES[0], SENTENCES[1], SENTENCES[2], "rivers carry sediment to the sea " * 8, summary, *[SENTENCES[0] + f" Exercise {i}." for i in range(1)]]
    with session_factory() as db:
        book = Book(board="CBSE", class_name="9", subject="Sci", publisher="NCERT", is_reference=True)
        db.add(book)
        db.flush()
        ch = make_ready(db, book, "A", 1)
        calls_before = llm.page_calls
        run(db, ch, llm, pages=pages)
        names = {c.name for c in db.scalars(select(Concept).join(Page).where(Page.chapter_id == ch.id))}
        assert names == {"Concept 1", "Concept 2", "Concept 3", "Rivers"}  # nothing from the summary or the page after it
        assert ch.graph_report["recap_pages"] == 2 and ch.graph_report["review_pages"] == []
        assert llm.page_calls - calls_before == 5  # pages 1-5; the page after the summary cost no LLM call


def test_a_summary_heading_early_in_the_chapter_does_not_end_it(session_factory):
    llm = ChapterLLM()
    early = "Summary of the last lesson\n" + " ".join(["Atoms were covered earlier and we revise them."] * 6)
    with session_factory() as db:
        book = Book(board="CBSE", class_name="9", subject="Sci", publisher="NCERT", is_reference=True)
        db.add(book)
        db.flush()
        ch = make_ready(db, book, "A", 1)
        run(db, ch, llm, pages=[early, *SENTENCES, "rivers carry sediment to the sea " * 8])
        names = {c.name for c in db.scalars(select(Concept).join(Page).where(Page.chapter_id == ch.id))}
        assert {"Concept 1", "Concept 2", "Concept 3", "Rivers"} <= names


def test_copied_chapter_inherits_review_flags_and_counters_instead_of_inventing_new_ones(session_factory):
    llm = ChapterLLM()
    unreadable = "Exercise questions " + "nothing teachable here at all " * 12  # long page, model returns no concepts
    pages = [*SENTENCES, unreadable]
    with session_factory() as db:
        book = Book(board="CBSE", class_name="9", subject="Sci", publisher="NCERT", is_reference=True)
        db.add(book)
        db.flush()
        first, second = make_ready(db, book, "A", 1), make_ready(db, book, "B", 2)
        run(db, first, llm, pages=pages)
        # the model said nothing about page 4, but it was an exercise page: simulate the source NOT being flagged
        for p in db.scalars(select(Page).where(Page.chapter_id == first.id)):
            p.needs_review, p.review_note = False, None
        first.graph_report = {**first.graph_report, "review_pages": [], "recap_pages": 1, "dropped_concepts": 4}
        db.flush()
        run(db, second, llm, pages=pages)
        assert second.graph_report["edges_copied"] is True
        assert second.graph_report["review_pages"] == []
        assert second.graph_report["recap_pages"] == 1 and second.graph_report["dropped_concepts"] == 4


def test_copied_chapter_keeps_a_review_flag_the_source_had(session_factory):
    llm = ChapterLLM()
    with session_factory() as db:
        book = Book(board="CBSE", class_name="9", subject="Sci", publisher="NCERT", is_reference=True)
        db.add(book)
        db.flush()
        first, second = make_ready(db, book, "A", 1), make_ready(db, book, "B", 2)
        run(db, first, llm)
        page = db.scalar(select(Page).where(Page.chapter_id == first.id, Page.page_number == 2))
        page.needs_review, page.review_note = True, "teacher should check this scan"
        db.flush()
        run(db, second, llm)
        flagged = db.scalar(select(Page).where(Page.chapter_id == second.id, Page.page_number == 2))
        assert flagged.needs_review and flagged.review_note == "teacher should check this scan"
        assert [p["page"] for p in second.graph_report["review_pages"]] == [2]
</file>

<file path="backend/tests/test_step11.py">
"""Step 11: cross-chapter prerequisites (pipeline/crosslink.py)."""
import json

import pytest
from sqlalchemy import select, text

from app.content_library.graph_view import chapter_graph
from app.core.config import settings
from app.embeddings.vectors import to_bytes
from app.graph_store import FAKE_STORE
from app.llm.fake_provider import FakeLLMProvider
from app.models import Book, Chapter, ChapterStatus, Concept, ContentEmbedding, CrossChapterEdge, Page
from app.pipeline.crosslink import CrossLinkError, crosslink_after, crosslink_chapter, earlier_chapters, explain_chapter
from app.pipeline.indexing import sync_cross_edges

MODEL = "test-embedding"


@pytest.fixture(autouse=True)
def small_vectors(monkeypatch):
    monkeypatch.setattr(settings, "embedding_dim", 3)
    monkeypatch.setattr(settings, "embedding_provider", "openai_compat")  # so MODEL vectors count as usable (not fake)
    monkeypatch.setattr(settings, "crosslink_min_similarity", 0.4)
    FAKE_STORE.clear()


class Scripted:
    """Links every offered candidate list's FIRST number unless told otherwise; counts calls."""
    model_name = "scripted"

    def __init__(self, pick=None):
        self.calls, self.pick = 0, pick

    def complete_json(self, system, user):
        self.calls += 1
        if self.pick is not None:
            return json.dumps(self.pick(user))
        return FakeLLMProvider().complete_json(system, user)


def make_book(db, owner=None):
    book = Book(board="CBSE", class_name="9", subject="Sci", publisher="X", is_reference=owner is None)
    db.add(book)
    db.flush()
    return book


def add_chapter(db, book, seq, concepts, title=None):
    """concepts: [(name, vector)]; one page per concept, all canonical, READY, with stored vectors."""
    ch = Chapter(book_id=book.id, title=title or f"Chapter {seq}", sequence_num=seq, status=ChapterStatus.READY)
    db.add(ch)
    db.flush()
    made = {}
    for i, (name, vec) in enumerate(concepts, 1):
        page = Page(chapter_id=ch.id, page_number=i, content_text=name)
        db.add(page)
        db.flush()
        c = Concept(page_id=page.id, name=name, description=f"about {name}", position=0, name_key=name.lower(), is_canonical=True)
        db.add(c)
        db.flush()
        db.add(ContentEmbedding(chapter_id=ch.id, concept_id=c.id, model=MODEL, dim=3, text_sha256=name, vector=to_bytes(vec)))
        made[name] = c
    db.flush()
    return ch, made


def edges(db, chapter):
    names = {c.id: c.name for c in db.scalars(select(Concept))}
    return {(names[e.prerequisite_id], names[e.concept_id]) for e in db.scalars(select(CrossChapterEdge).where(CrossChapterEdge.chapter_id == chapter.id))}


def test_similar_earlier_concept_becomes_a_prerequisite_and_unrelated_ones_are_never_offered(session_factory):
    with session_factory() as db:
        book = make_book(db)
        ch1, _ = add_chapter(db, book, 1, [("Atom", [1, 0, 0]), ("River", [0, 1, 0])])
        ch2, _ = add_chapter(db, book, 2, [("Molecule", [0.9, 0.1, 0])])
        llm = Scripted()
        report = crosslink_chapter(db, ch2, llm)
        assert edges(db, ch2) == {("Atom", "Molecule")}  # River (similarity ~0.11) was not even a candidate
        assert report["status"] == "done" and report["edges"] == 1 and llm.calls == 1
        assert ch2.graph_report["cross_chapter"]["edges"] == 1


def test_nothing_points_forward_and_the_first_chapter_has_no_cross_links(session_factory):
    with session_factory() as db:
        book = make_book(db)
        ch1, _ = add_chapter(db, book, 1, [("Atom", [1, 0, 0])])
        ch2, _ = add_chapter(db, book, 2, [("Molecule", [1, 0.1, 0])])
        assert earlier_chapters(db, ch1) == [] and [c.id for c in earlier_chapters(db, ch2)] == [ch1.id]
        assert crosslink_chapter(db, ch1, Scripted())["status"] == "no_candidates"
        assert edges(db, ch1) == set()


def test_only_the_same_book_is_searched(session_factory):
    with session_factory() as db:
        a, b = make_book(db), make_book(db)
        add_chapter(db, b, 1, [("Atom", [1, 0, 0])])  # another book (could be another teacher's)
        ch2, _ = add_chapter(db, a, 2, [("Molecule", [1, 0, 0])])
        assert crosslink_chapter(db, ch2, Scripted())["status"] == "no_candidates"


def test_unchanged_candidates_do_not_ask_the_model_again(session_factory):
    with session_factory() as db:
        book = make_book(db)
        add_chapter(db, book, 1, [("Atom", [1, 0, 0])])
        ch2, _ = add_chapter(db, book, 2, [("Molecule", [1, 0.1, 0])])
        llm = Scripted()
        crosslink_chapter(db, ch2, llm)
        assert crosslink_chapter(db, ch2, llm)["status"] == "unchanged" and llm.calls == 1
        assert edges(db, ch2) == {("Atom", "Molecule")}


def test_model_may_not_pick_a_concept_it_was_not_offered_and_old_edges_survive_a_failed_run(session_factory):
    with session_factory() as db:
        book = make_book(db)
        add_chapter(db, book, 1, [("Atom", [1, 0, 0]), ("Ion", [0.95, 0.3, 0])])
        ch2, _ = add_chapter(db, book, 2, [("Molecule", [1, 0.1, 0])])
        crosslink_chapter(db, ch2, Scripted())
        before = edges(db, ch2)
        bad = Scripted(pick=lambda user: {"links": [{"concept": 1, "prerequisites": [99]}]})
        ch2.graph_report = {**ch2.graph_report, "cross_chapter": {}}  # force a re-ask
        with pytest.raises(CrossLinkError):
            crosslink_chapter(db, ch2, bad)
        assert bad.calls == 3 and edges(db, ch2) == before  # 1 try + 2 correction retries; nothing was replaced


def test_per_concept_cap(session_factory, monkeypatch):
    monkeypatch.setattr(settings, "crosslink_max_per_concept", 1)
    with session_factory() as db:
        book = make_book(db)
        add_chapter(db, book, 1, [("Atom", [1, 0, 0]), ("Ion", [0.95, 0.3, 0]), ("Electron", [0.9, 0.4, 0])])
        ch2, _ = add_chapter(db, book, 2, [("Molecule", [1, 0.1, 0])])
        crosslink_chapter(db, ch2, Scripted(pick=lambda u: {"links": [{"concept": 1, "prerequisites": [1, 2, 3]}]}))
        assert len(edges(db, ch2)) == 1


def test_edges_follow_their_concepts_when_an_earlier_chapter_is_processed_again(session_factory):
    with session_factory() as db:
        if db.bind.dialect.name == "sqlite":
            db.execute(text("PRAGMA foreign_keys=ON"))  # SQLite ignores ON DELETE CASCADE unless asked
        book = make_book(db)
        ch1, made = add_chapter(db, book, 1, [("Atom", [1, 0, 0])])
        ch2, _ = add_chapter(db, book, 2, [("Molecule", [1, 0.1, 0])])
        crosslink_chapter(db, ch2, Scripted())
        db.commit()
        db.delete(db.get(Concept, made["Atom"].id))  # what re-processing chapter 1 does to its old concepts
        db.commit()
        assert db.scalars(select(CrossChapterEdge)).all() == []


def test_chapter_processed_after_a_later_one_relinks_the_later_one(session_factory, monkeypatch):
    with session_factory() as db:
        book = make_book(db)
        ch2, _ = add_chapter(db, book, 2, [("Molecule", [1, 0.1, 0])])
        ch1, _ = add_chapter(db, book, 1, [("Atom", [1, 0, 0])])
        ids = (ch1.id, ch2.id)
        db.commit()
    lines = crosslink_after(session_factory, ids[0], Scripted())
    assert len(lines) == 2 and "done" in lines[1]  # chapter 1 itself, then chapter 2 gained its link
    with session_factory() as db:
        assert edges(db, db.get(Chapter, ids[1])) == {("Atom", "Molecule")}


def test_graph_view_lists_cross_chapter_links_and_hides_those_into_unready_chapters(session_factory):
    with session_factory() as db:
        book = make_book(db)
        ch1, _ = add_chapter(db, book, 1, [("Atom", [1, 0, 0])], title="Matter")
        ch2, _ = add_chapter(db, book, 2, [("Molecule", [1, 0.1, 0])])
        crosslink_chapter(db, ch2, Scripted())
        view = chapter_graph(db, ch2)
        assert [(x.prerequisite_name, x.prerequisite_chapter_title) for x in view.cross_chapter] == [("Atom", "Matter")]
        ch1.status = ChapterStatus.FAILED  # e.g. a failed re-upload: students must not see it, nor links into it
        db.flush()
        assert chapter_graph(db, ch2).cross_chapter == []


def test_graph_store_gets_the_cross_edges_and_traversal_follows_them(session_factory, monkeypatch):
    from app.graph_store.base import ChapterGraph, ConceptNode

    monkeypatch.setattr(settings, "graph_store_provider", "fake")
    with session_factory() as db:
        book = make_book(db)
        ch1, c1 = add_chapter(db, book, 1, [("Atom", [1, 0, 0])])
        ch2, c2 = add_chapter(db, book, 2, [("Molecule", [1, 0.1, 0])])
        crosslink_chapter(db, ch2, Scripted())
        db.commit()
        for ch, made in ((ch1, c1), (ch2, c2)):
            FAKE_STORE.replace_chapter(ChapterGraph(
                str(book.id), str(ch.id), ch.title, ch.sequence_num, True, None, MODEL,
                concepts=[ConceptNode(str(c.id), c.name, "", 0, [1, 0, 0]) for c in made.values()],
            ))
        assert sync_cross_edges(db, book.id) is True
        molecule, atom = str(c2["Molecule"].id), str(c1["Atom"].id)
        assert [(e.concept_id, e.prerequisite_id) for e in FAKE_STORE.cross_edges(str(book.id))] == [(molecule, atom)]
        assert [(r.name, r.depth) for r in FAKE_STORE.prerequisites(molecule, [str(book.id)])] == [("Atom", 1)]
        assert FAKE_STORE.prerequisites(molecule, ["some-other-book"]) == []  # tenant filter still applies


def test_disabled_switch(session_factory, monkeypatch):
    monkeypatch.setattr(settings, "crosslink_enabled", False)
    with session_factory() as db:
        book = make_book(db)
        add_chapter(db, book, 1, [("Atom", [1, 0, 0])])
        ch2, _ = add_chapter(db, book, 2, [("Molecule", [1, 0, 0])])
        assert crosslink_chapter(db, ch2, Scripted())["status"] == "disabled"


def test_only_the_nearest_few_candidates_are_offered(session_factory, monkeypatch):
    monkeypatch.setattr(settings, "crosslink_candidates", 1)
    seen = []

    def pick(user):
        seen.append(user)
        return {"links": []}

    with session_factory() as db:
        book = make_book(db)
        add_chapter(db, book, 1, [("Atom", [1, 0, 0]), ("Ion", [0.9, 0.4, 0])])
        ch2, _ = add_chapter(db, book, 2, [("Molecule", [1, 0.05, 0])])
        crosslink_chapter(db, ch2, Scripted(pick=pick))
    assert "Atom" in seen[0] and "Ion" not in seen[0]


WEAK = [0.45, 0.893, 0]  # cosine similarity ~0.45 with [1, 0, 0]: offered (floor 0.4) but below the keep floor (0.5)


def test_a_link_the_model_chose_is_dropped_when_the_match_is_too_weak(session_factory):
    with session_factory() as db:
        book = make_book(db)
        add_chapter(db, book, 1, [("Atom", [1, 0, 0]), ("Symbols", WEAK)])
        ch2, _ = add_chapter(db, book, 2, [("Molecule", [1, 0.05, 0])])
        llm = Scripted(pick=lambda u: {"links": [{"concept": 1, "prerequisites": [1, 2]}]})  # takes everything offered
        report = crosslink_chapter(db, ch2, llm)
        assert edges(db, ch2) == {("Atom", "Molecule")}  # the 0.45 one was offered and chosen, but not kept
        assert report["edges"] == 1 and report["dropped_weak"] == 1


def test_changing_the_keep_floor_asks_the_model_again(session_factory, monkeypatch):
    with session_factory() as db:
        book = make_book(db)
        add_chapter(db, book, 1, [("Atom", [1, 0, 0]), ("Symbols", WEAK)])
        ch2, _ = add_chapter(db, book, 2, [("Molecule", [1, 0.05, 0])])
        llm = Scripted(pick=lambda u: {"links": [{"concept": 1, "prerequisites": [1, 2]}]})
        crosslink_chapter(db, ch2, llm)
        monkeypatch.setattr(settings, "crosslink_keep_similarity", 0.4)
        assert crosslink_chapter(db, ch2, llm)["status"] == "done" and llm.calls == 2
        assert edges(db, ch2) == {("Atom", "Molecule"), ("Symbols", "Molecule")}


def test_explain_shows_candidates_and_writes_nothing(session_factory):
    with session_factory() as db:
        book = make_book(db)
        add_chapter(db, book, 1, [("Atom", [1, 0, 0]), ("Symbols", WEAK)])
        ch2, _ = add_chapter(db, book, 2, [("Molecule", [1, 0.05, 0])])
        llm = Scripted(pick=lambda u: {"links": [{"concept": 1, "prerequisites": [1, 2]}]})
        text_out = "\n".join(explain_chapter(db, ch2, llm))
        assert "Atom" in text_out and "CHOSEN, kept" in text_out and "CHOSEN, dropped (weak)" in text_out
        assert db.scalars(select(CrossChapterEdge)).all() == [] and "cross_chapter" not in (ch2.graph_report or {})
</file>

<file path="backend/tests/test_step12.py">
"""Layer 4: embeddings as a second similarity signal (pipeline/embedmatch.py)."""
import uuid

import pytest

from app.core.config import settings
from app.embeddings.vectors import to_bytes
from app.models import Book, Chapter, ChapterStatus, ContentEmbedding, Page
from app.models.user import Role, User
from app.pipeline.embedmatch import compute, embedmatch_after, embedmatch_chapter

MODEL = "test-embedding"
LONG = "word " * 40


@pytest.fixture(autouse=True)
def small_vectors(monkeypatch):
    monkeypatch.setattr(settings, "embedding_dim", 3)
    monkeypatch.setattr(settings, "embedding_provider", "openai_compat")
    monkeypatch.setattr(settings, "embed_match_similarity", 0.85)


def make_teacher(db, name):
    teacher = User(supertokens_user_id=f"st-{name}", name=name, username=name, phone="9" + name[-3:].rjust(3, "0"), role=Role.teacher)
    db.add(teacher)
    db.flush()
    return teacher


def make_book(db, owner=None, publisher="X"):
    book = Book(board="CBSE", class_name="9", subject="Sci", publisher=publisher,
                is_reference=owner is None, owner_teacher_id=owner.id if owner else None)
    db.add(book)
    db.flush()
    return book


def add_chapter(db, book, seq, vectors, model=MODEL, status=ChapterStatus.READY):
    ch = Chapter(book_id=book.id, title=f"Chapter {seq}", sequence_num=seq, status=status)
    db.add(ch)
    db.flush()
    for i, vec in enumerate(vectors, 1):
        page = Page(chapter_id=ch.id, page_number=i, content_text=LONG)
        db.add(page)
        db.flush()
        db.add(ContentEmbedding(chapter_id=ch.id, page_id=page.id, model=model, dim=3, text_sha256=str(uuid.uuid4()), vector=to_bytes(vec)))
    db.flush()
    return ch


A, B, C = [1, 0, 0], [0, 1, 0], [0, 0, 1]
A2 = [0.98, 0.1, 0]  # ~0.99 with A


def test_reworded_chapter_is_suggested_when_most_pages_are_close_in_meaning(session_factory):
    with session_factory() as db:
        official = make_book(db)
        add_chapter(db, official, 1, [A, B, C])
        teacher = make_teacher(db, "t1")
        mine = add_chapter(db, make_book(db, teacher), 1, [A2, B, [0.5, 0.5, 0.7]])
        found, info = compute(db, mine)
        assert len(found) == 1 and found[0]["signal"] == "embedding" and found[0]["kind"] == "variant"
        assert found[0]["matched_pages"] == 2 and found[0]["pages_checked"] == 3 and info["status"] == "done"


def test_too_few_matching_pages_is_no_suggestion_but_shows_up_as_closest(session_factory):
    with session_factory() as db:
        add_chapter(db, make_book(db), 1, [A, B, C])
        teacher = make_teacher(db, "t1")
        mine = add_chapter(db, make_book(db, teacher), 1, [A2, [0.5, 0.5, 0.7], [0.4, 0.4, 0.8]])
        found, info = compute(db, mine)
        assert found == [] and info["closest"][0]["matched_pages"] == 1


def test_another_teachers_private_book_is_never_searched(session_factory):
    with session_factory() as db:
        t1, t2 = make_teacher(db, "t1"), make_teacher(db, "t2")
        add_chapter(db, make_book(db, t2), 1, [A, B])  # t2's private upload
        mine = add_chapter(db, make_book(db, t1), 1, [A, B])
        found, info = compute(db, mine)
        assert found == [] and info["status"] == "no_candidates"


def test_the_teachers_own_other_book_is_searched(session_factory):
    with session_factory() as db:
        t1 = make_teacher(db, "t1")
        add_chapter(db, make_book(db, t1, "Old"), 1, [A, B])
        mine = add_chapter(db, make_book(db, t1, "New"), 1, [A2, B])
        assert len(compute(db, mine)[0]) == 1


def test_an_official_chapter_is_only_compared_with_official_books(session_factory):
    with session_factory() as db:
        t1 = make_teacher(db, "t1")
        add_chapter(db, make_book(db, t1), 1, [A, B])
        ref = add_chapter(db, make_book(db), 1, [A, B])
        assert compute(db, ref)[1]["status"] == "no_candidates"


def test_other_models_unready_chapters_and_the_same_book_are_ignored(session_factory):
    with session_factory() as db:
        official = make_book(db)
        add_chapter(db, official, 1, [A, B], model="other-model")
        add_chapter(db, official, 2, [A, B], status=ChapterStatus.FAILED)
        teacher = make_teacher(db, "t1")
        own = make_book(db, teacher)
        add_chapter(db, own, 1, [A, B])
        mine = add_chapter(db, own, 2, [A, B])
        assert compute(db, mine)[1]["status"] == "no_candidates"


def test_fingerprint_suggestions_stay_first_and_a_book_is_not_suggested_twice(session_factory):
    with session_factory() as db:
        official = make_book(db)
        other = make_book(db, publisher="Y")
        add_chapter(db, official, 1, [A, B])
        add_chapter(db, other, 1, [A, B])
        teacher = make_teacher(db, "t1")
        mine = add_chapter(db, make_book(db, teacher), 1, [A2, B])
        # the fingerprint already suggested `official`; only `other` is new (and visible: it is official too)
        mine.match_report = {"pages_checked": 2, "suggestions": [{"book_id": str(official.id), "chapter_id": None, "chapter_title": None,
                                                                    "kind": "same", "matched_pages": 2, "pages_checked": 2, "avg_similarity": 0.99}]}
        embedmatch_chapter(db, mine)
        ids = [s["book_id"] for s in mine.match_report["suggestions"]]
        assert ids == [str(official.id), str(other.id)] and mine.match_report["suggestions"][1]["signal"] == "embedding"
        embedmatch_chapter(db, mine)  # running again replaces its own suggestions, never doubles them
        assert [s["book_id"] for s in mine.match_report["suggestions"]] == ids
        assert mine.match_report["pages_checked"] == 2  # the rest of the report is untouched


def test_disabled_switch_and_missing_vectors(session_factory, monkeypatch):
    with session_factory() as db:
        add_chapter(db, make_book(db), 1, [A])
        teacher = make_teacher(db, "t1")
        mine = add_chapter(db, make_book(db, teacher), 1, [A])
        monkeypatch.setattr(settings, "embed_match_enabled", False)
        assert embedmatch_chapter(db, mine)["status"] == "disabled" and "embedding_match" not in (mine.match_report or {})
        monkeypatch.setattr(settings, "embed_match_enabled", True)
        empty = add_chapter(db, make_book(db, teacher), 1, [])
        assert compute(db, empty)[1]["status"] == "no_vectors"


def test_after_hook_saves_and_never_raises(session_factory, monkeypatch):
    with session_factory() as db:
        add_chapter(db, make_book(db), 1, [A, B])
        teacher = make_teacher(db, "t1")
        mine = add_chapter(db, make_book(db, teacher), 1, [A2, B])
        chapter_id = mine.id
        db.commit()
    assert "+1" in embedmatch_after(session_factory, chapter_id)
    with session_factory() as db:
        assert db.get(Chapter, chapter_id).match_report["suggestions"][0]["signal"] == "embedding"
    monkeypatch.setattr("app.pipeline.embedmatch.compute", lambda *a, **k: 1 / 0)
    assert embedmatch_after(session_factory, chapter_id) == "failed"


def test_teacher_route_exposes_the_signal(session_factory):
    from app.schemas import ChapterMatchOut
    assert ChapterMatchOut.model_fields["signal"].default == "fingerprint"


def test_a_suggestion_that_no_longer_holds_is_removed_on_the_next_run(session_factory):
    with session_factory() as db:
        add_chapter(db, make_book(db), 1, [A, B])
        teacher = make_teacher(db, "t1")
        mine = add_chapter(db, make_book(db, teacher), 1, [A2, B])
        embedmatch_chapter(db, mine)
        assert len(mine.match_report["suggestions"]) == 1
        for row in db.query(ContentEmbedding).filter(ContentEmbedding.chapter_id == mine.id):
            row.vector = to_bytes(C)  # e.g. the chapter was re-uploaded with different content
        db.flush()
        embedmatch_chapter(db, mine)
        assert mine.match_report["suggestions"] == [] and mine.match_report["embedding_match"]["added"] == 0
</file>

<file path="backend/tests/test_step13.py">
"""Layer 3: chapter-title sequence (pipeline/structure.py)."""
import pytest

from app.core.config import settings
from app.models import Book, Chapter, ChapterStatus, Role
from app.pipeline import structure
from app.pipeline.structure import ordered_matches, title_overlap, title_words
from tests.test_book_access import make_user, new_book

OFFICIAL = ["Exploration and Entering", "The Building Block of Life", "Matter in Our Surroundings", "Tissues"]


def titles_book(db, titles, owner_id=None, status=ChapterStatus.READY, subject="S"):
    book = Book(board="B", class_name="9", subject=subject, publisher="P", is_reference=owner_id is None, owner_teacher_id=owner_id)
    db.add(book)
    db.flush()
    for i, t in enumerate(titles, 1):
        db.add(Chapter(book_id=book.id, title=t, sequence_num=i, status=status))
    db.flush()
    return book


def test_title_words_drop_filler_and_numbering():
    assert title_words("Chapter 2: The Building Block of Life") == {"building", "block", "life"}
    assert title_words("Chapter 3") == frozenset() and title_overlap(title_words("Chapter 3"), title_words("Chapter 3")) == 0.0


def test_a_shorter_edition_title_matches_the_longer_one():
    a, b = title_words("Exploration: Entering the World of Secondary Science"), title_words("Exploration and Entering")
    assert title_overlap(a, b) == 1.0
    assert title_overlap(title_words("Tissues"), title_words("Atoms and Molecules")) == 0.0


def test_only_matches_in_the_same_order_count():
    assert ordered_matches(["Tissues", "Exploration and Entering"], OFFICIAL) == (1, 1.0)  # reversed: only one can be in order
    n, avg = ordered_matches(["Exploration: Entering the World", "Cells: The Building Block of Life", "Tissues"], OFFICIAL)
    assert n == 3 and avg == 1.0


def test_book_level_suggestion_by_titles_before_any_page_is_processed(session_factory):
    with session_factory() as db:
        titles_book(db, OFFICIAL)
        db.commit()
    t = make_user(session_factory, Role.teacher, "teachera")[0]
    with session_factory() as db:
        mine = titles_book(db, ["Exploration: Entering the World of Secondary Science", "The Building Block of Life", "Our own extra chapter"],
                           owner_id=t.id, status=ChapterStatus.EMPTY)  # nothing uploaded yet
        [hit] = structure.suggest(db, mine, t.id)
        assert hit["book"].id != mine.id and hit["matched_chapters"] == 2 and hit["chapters_checked"] == 3
        assert hit["coverage"] == 0.667 and hit["candidate_chapters_loaded"] == 4


def test_one_matching_title_or_a_low_share_is_not_enough(session_factory):
    t = make_user(session_factory, Role.teacher, "teachera")[0]
    with session_factory() as db:
        titles_book(db, OFFICIAL)
        one = titles_book(db, ["Tissues", "Something else", "Another"], owner_id=t.id)
        low = titles_book(db, ["Exploration and Entering", "The Building Block of Life", "X", "Y", "Z"], owner_id=t.id)
        half = titles_book(db, ["Tissues", "Unrelated topic"], owner_id=t.id)
        assert structure.suggest(db, half, t.id) == []  # 1 of 2 = 0.5 passes the share rule; only the 2-chapter minimum stops it
        assert structure.suggest(db, one, t.id) == []  # one match
        assert structure.suggest(db, low, t.id) == []  # 2 of 5 = 0.4 < 0.5


def test_other_teachers_books_are_not_compared_but_own_and_official_are(session_factory):
    a = make_user(session_factory, Role.teacher, "teachera")[0]
    b = make_user(session_factory, Role.teacher, "teacherb")[0]
    with session_factory() as db:
        a_book = titles_book(db, OFFICIAL, owner_id=a.id)
        b_book = titles_book(db, OFFICIAL, owner_id=b.id)
        assert structure.suggest(db, b_book, b.id) == []  # A's private copy is invisible to B
        mine2 = titles_book(db, OFFICIAL, owner_id=a.id, subject="Other")
        assert [h["book"].id for h in structure.suggest(db, mine2, a.id)] == [a_book.id]
        assert structure.suggest(db, mine2, a.id, exclude={a_book.id}) == []  # already found by the page evidence


def test_unprocessed_chapters_of_the_other_book_are_ignored_and_switch_off(session_factory, monkeypatch):
    t = make_user(session_factory, Role.teacher, "teachera")[0]
    with session_factory() as db:
        titles_book(db, OFFICIAL, status=ChapterStatus.PROCESSING)  # nothing finished yet
        mine = titles_book(db, OFFICIAL, owner_id=t.id)
        assert structure.suggest(db, mine, t.id) == []
        titles_book(db, OFFICIAL)
        assert len(structure.suggest(db, mine, t.id)) == 1
        monkeypatch.setattr(settings, "structure_enabled", False)
        assert structure.suggest(db, mine, t.id) == []


def test_route_returns_the_structure_suggestion_with_its_signal(client, session_factory):
    t, th = make_user(session_factory, Role.teacher, "teachera")
    with session_factory() as db:
        ref = titles_book(db, OFFICIAL)
        ref_id = str(ref.id)
        db.commit()
    book = new_book(client, th)
    with session_factory() as db:
        import uuid
        for i, title in enumerate(["Exploration: Entering the World of Secondary Science", "The Building Block of Life"], 1):
            db.add(Chapter(book_id=uuid.UUID(book["id"]), title=title, sequence_num=i))
        db.commit()
    res = client.get(f"/teacher/books/{book['id']}/variant-suggestions", headers=th)
    assert res.status_code == 200, res.text
    [s] = res.json()
    assert s["book"]["id"] == ref_id and s["signal"] == "structure" and s["matched_chapters"] == 2 and s["matched_pages"] == 0
    client.post(f"/teacher/books/{book['id']}/variant-of", json={"base_book_id": ref_id}, headers=th)
    assert client.get(f"/teacher/books/{book['id']}/variant-suggestions", headers=th).json() == []  # confirmed: no longer suggested
</file>

<file path="backend/tests/test_step14.py">
"""Layer 5: teacher decisions about variant suggestions feed back (content_library/feedback.py, match_feedback)."""
import uuid

from sqlalchemy import select

from app.db.match_feedback import summarize
from app.models import Book, Chapter, MatchFeedback, Role
from tests.test_book_access import make_user, new_book
from tests.test_step13 import OFFICIAL, titles_book


def setup(client, session_factory, tag="teachera"):
    """An official book plus a teacher book whose chapter titles follow it (so the structure signal suggests it)."""
    t, th = make_user(session_factory, Role.teacher, tag)
    with session_factory() as db:
        ref = titles_book(db, OFFICIAL)
        ref_id = str(ref.id)
        db.commit()
    book = new_book(client, th)
    with session_factory() as db:
        for i, title in enumerate(["Exploration: Entering the World of Secondary Science", "The Building Block of Life"], 1):
            db.add(Chapter(book_id=uuid.UUID(book["id"]), title=title, sequence_num=i))
        db.commit()
    return th, book["id"], ref_id


def rows(session_factory):
    with session_factory() as db:
        return list(db.scalars(select(MatchFeedback)))


def sugg(client, th, book_id):
    res = client.get(f"/teacher/books/{book_id}/variant-suggestions", headers=th)
    assert res.status_code == 200, res.text
    return res.json()


def test_confirming_records_what_the_suggestion_showed(client, session_factory):
    th, book_id, ref_id = setup(client, session_factory)
    assert client.post(f"/teacher/books/{book_id}/variant-of", json={"base_book_id": ref_id}, headers=th).status_code == 200
    [row] = rows(session_factory)
    assert row.decision == "confirmed" and str(row.base_book_id) == ref_id and str(row.book_id) == book_id
    assert row.evidence["signal"] == "structure" and row.evidence["coverage"] == 1.0 and "book" not in row.evidence


def test_confirming_a_book_nobody_suggested_is_recorded_as_a_miss(client, session_factory):
    th, book_id, _ = setup(client, session_factory)
    with session_factory() as db:
        other = titles_book(db, ["Gravitation", "Work and Energy"])
        other_id = str(other.id)
        db.commit()
    assert client.post(f"/teacher/books/{book_id}/variant-of", json={"base_book_id": other_id}, headers=th).status_code == 200
    [row] = rows(session_factory)
    assert row.decision == "confirmed" and row.evidence is None


def test_dismissing_hides_the_suggestion_and_undo_brings_it_back(client, session_factory):
    th, book_id, ref_id = setup(client, session_factory)
    assert [s["book"]["id"] for s in sugg(client, th, book_id)] == [ref_id]
    assert client.post(f"/teacher/books/{book_id}/variant-suggestions/dismiss", json={"base_book_id": ref_id}, headers=th).status_code == 204
    assert sugg(client, th, book_id) == []
    [row] = rows(session_factory)
    assert row.decision == "dismissed" and row.evidence["signal"] == "structure"
    assert client.delete(f"/teacher/books/{book_id}/variant-suggestions/dismiss/{ref_id}", headers=th).status_code == 204
    assert client.delete(f"/teacher/books/{book_id}/variant-suggestions/dismiss/{ref_id}", headers=th).status_code == 204  # idempotent
    assert [s["book"]["id"] for s in sugg(client, th, book_id)] == [ref_id] and rows(session_factory) == []


def test_a_dismissed_book_can_still_be_confirmed_by_hand(client, session_factory):
    th, book_id, ref_id = setup(client, session_factory)
    client.post(f"/teacher/books/{book_id}/variant-suggestions/dismiss", json={"base_book_id": ref_id}, headers=th)
    res = client.post(f"/teacher/books/{book_id}/variant-of", json={"base_book_id": ref_id}, headers=th)
    assert res.status_code == 200 and res.json()["variant_of_id"] == ref_id
    [row] = rows(session_factory)
    assert row.decision == "confirmed" and row.evidence["signal"] == "structure"  # evidence from the dismissal is kept


def test_clearing_retracts_but_does_not_hide_the_suggestion(client, session_factory):
    th, book_id, ref_id = setup(client, session_factory)
    client.post(f"/teacher/books/{book_id}/variant-of", json={"base_book_id": ref_id}, headers=th)
    assert client.delete(f"/teacher/books/{book_id}/variant-of", headers=th).status_code == 204
    [row] = rows(session_factory)
    assert row.decision == "retracted" and row.evidence["signal"] == "structure"
    assert [s["book"]["id"] for s in sugg(client, th, book_id)] == [ref_id]


def test_switching_to_another_base_retracts_the_old_one(client, session_factory):
    th, book_id, ref_id = setup(client, session_factory)
    with session_factory() as db:
        other_id = str(titles_book(db, ["Gravitation", "Work and Energy"]).id)
        db.commit()
    client.post(f"/teacher/books/{book_id}/variant-of", json={"base_book_id": ref_id}, headers=th)
    client.post(f"/teacher/books/{book_id}/variant-of", json={"base_book_id": other_id}, headers=th)
    decisions = {str(r.base_book_id): r.decision for r in rows(session_factory)}
    assert decisions == {ref_id: "retracted", other_id: "confirmed"}


def test_dismiss_guards(client, session_factory):
    th, book_id, ref_id = setup(client, session_factory)
    _, bh = make_user(session_factory, Role.teacher, "teacherb")
    url = f"/teacher/books/{book_id}/variant-suggestions/dismiss"
    assert client.post(url, json={"base_book_id": book_id}, headers=th).status_code == 400  # itself
    assert client.post(url, json={"base_book_id": str(uuid.uuid4())}, headers=th).status_code == 404
    assert client.post(url, json={"base_book_id": ref_id}, headers=bh).status_code == 404  # not B's book
    assert client.delete(f"{url}/{ref_id}", headers=bh).status_code == 404
    other = new_book(client, bh)  # B's private book is invisible to A
    assert client.post(url, json={"base_book_id": other["id"]}, headers=th).status_code == 404
    client.post(f"/teacher/books/{book_id}/variant-of", json={"base_book_id": ref_id}, headers=th)
    assert client.post(url, json={"base_book_id": ref_id}, headers=th).status_code == 409  # confirmed: clear it first
    assert rows(session_factory)[0].decision == "confirmed"


def test_report_counts_decisions_and_front_page_corrections(client, session_factory):
    th, book_id, ref_id = setup(client, session_factory)
    client.post(f"/teacher/books/{book_id}/variant-of", json={"base_book_id": ref_id}, headers=th)
    with session_factory() as db:
        book = db.get(Book, uuid.UUID(book_id))
        book.extracted_metadata = {"board": "CBSE", "class_name": "Class " + book.class_name, "publisher": "N C E R T", "subject": book.subject}
        db.commit()
        text = "\n".join(summarize(db))
        shown = "\n".join(summarize(db, show_changes=True))
    assert "1 teacher decisions" in text and "signal structure:" in text and "confirmed: 1" in text
    assert "confirmed without a suggestion (the system missed it): 0" in text
    assert "publisher: teacher changed 1 of 1" in text and "subject: teacher changed 0 of 1" in text
    assert "class_name: teacher changed 0 of 1" in text  # 'Class 9' read, '9' confirmed: the same class
    assert ref_id not in text and book_id not in text  # counts only, never ids
    assert "N C E R T" not in text and "'N C E R T' ->" in shown  # values only when asked for


def test_a_page_based_suggestion_can_be_dismissed_too(client, session_factory):
    t, th = make_user(session_factory, Role.teacher, "teachera")
    with session_factory() as db:
        ref_id = str(titles_book(db, OFFICIAL).id)
        db.commit()
    book = new_book(client, th)
    with session_factory() as db:  # a finished chapter whose page fingerprints matched the official book (titles differ: no structure signal)
        db.add(Chapter(book_id=uuid.UUID(book["id"]), title="Our own title", sequence_num=1, status="ready", match_report={
            "pages_checked": 2, "suggestions": [{"book_id": ref_id, "chapter_id": None, "chapter_title": "Tissues", "kind": "variant",
                                                 "matched_pages": 2, "pages_checked": 2, "avg_similarity": 0.8}]}))
        db.commit()
    [s] = sugg(client, th, book["id"])
    assert s["book"]["id"] == ref_id and s["signal"] == "pages"
    client.post(f"/teacher/books/{book['id']}/variant-suggestions/dismiss", json={"base_book_id": ref_id}, headers=th)
    assert sugg(client, th, book["id"]) == []
    [row] = rows(session_factory)
    assert row.evidence["signal"] == "pages" and row.evidence["coverage"] == 1.0
</file>

<file path="backend/tests/test_step15.py">
"""Phase 2 exit check, Layer 4 probe and chapter removal (db/phase2_check.py, pipeline/embedprobe.py, db/drop_chapter.py)."""
import json
import uuid

import pytest
from sqlalchemy import func, select

from app.core.config import settings
from app.db import drop_chapter, phase2_check as pc
from app.embeddings.vectors import to_bytes
from app.models import Book, Chapter, ChapterStatus, ContentEmbedding, CrossChapterEdge, Concept, MatchFeedback, Page, User
from app.pipeline.embedprobe import kept_phrases, probe

MODEL = "test-embedding"
TEXT = "the cell is the basic unit of life and every living thing is made of cells " * 3
OFFICIAL = ["Exploration and Entering", "The Building Block of Life", "Matter in Our Surroundings"]
GOOD = {"model": "gpt-x", "concepts": 12, "edges": 9, "unresolved_prerequisites": [], "llm_linking": "done", "review_pages": []}


@pytest.fixture(autouse=True)
def small_vectors(monkeypatch):
    monkeypatch.setattr(settings, "embedding_dim", 3)
    monkeypatch.setattr(settings, "embedding_provider", "openai_compat")
    monkeypatch.setattr(settings, "embed_match_similarity", 0.85)
    monkeypatch.setattr(settings, "graph_store_provider", "none")


def official_book(db, titles=OFFICIAL, report=None, status=ChapterStatus.READY, cross="done"):
    book = Book(board="CBSE", class_name="9", subject="Science", publisher="NCERT", is_reference=True)
    db.add(book)
    db.flush()
    for i, t in enumerate(titles, 1):
        rep = dict(GOOD if report is None else report)
        if i > 1 and cross:
            rep["cross_chapter"] = {"status": cross}
        ch = Chapter(book_id=book.id, title=t, sequence_num=i, status=status, graph_report=rep, embedding_status="done", graph_sync_status="done")
        db.add(ch)
        db.flush()
        db.add(Page(chapter_id=ch.id, page_number=1, content_text=TEXT))
    db.flush()
    return book


def with_vectors(db, book, vectors_by_chapter):
    chapters = list(db.scalars(select(Chapter).where(Chapter.book_id == book.id).order_by(Chapter.sequence_num)))
    for ch, vectors in zip(chapters, vectors_by_chapter):
        for n, vec in enumerate(vectors, 1):
            page = db.scalar(select(Page).where(Page.chapter_id == ch.id, Page.page_number == n))
            if page is None:
                page = Page(chapter_id=ch.id, page_number=n, content_text=TEXT)
                db.add(page)
                db.flush()
            db.add(ContentEmbedding(chapter_id=ch.id, page_id=page.id, model=MODEL, dim=3, text_sha256=str(uuid.uuid4()), vector=to_bytes(vec)))
    db.flush()


class Reworder:
    def complete_json(self, system, user):
        return json.dumps({"text": "a different wording of the page " + user[-20:]})


class Embedder:
    model_name, dim = MODEL, 3

    def __init__(self, vectors):
        self.vectors = vectors

    def embed(self, texts):
        return self.vectors[: len(texts)]


CH1 = [[1, 0, 0], [0.95, 0.05, 0], [0.9, 0.1, 0], [0.97, 0.02, 0]]
CH2 = [[0, 1, 0], [0.05, 0.95, 0], [0.1, 0.9, 0], [0.02, 0.97, 0]]


def test_probe_passes_when_reworded_pages_stay_close_and_different_pages_do_not(session_factory):
    with session_factory() as db:
        book = official_book(db, OFFICIAL[:2])
        with_vectors(db, book, [CH1, CH2])
        r = probe(db, Reworder(), Embedder([[1, 0.02, 0]] * 4 + [[0.02, 1, 0]] * 4), pages=8)
        assert r["status"] == "done" and r["pages"] == 8 and r["pass"] and r["separable"]
        assert r["same_min"] > 0.99 and r["other_max"] < 0.3 and r["recall"] == 1.0 and r["false_rate"] == 0


def test_probe_fails_with_a_recommendation_when_the_threshold_is_too_high(session_factory, monkeypatch):
    monkeypatch.setattr(settings, "embed_match_similarity", 0.995)
    with session_factory() as db:
        book = official_book(db, OFFICIAL[:2])
        with_vectors(db, book, [CH1, CH2])
        r = probe(db, Reworder(), Embedder([[1, 0.3, 0]] * 4 + [[0.3, 1, 0]] * 4), pages=8)
        assert not r["pass"] and r["separable"] and r["recall"] < 0.9 and 0.2 < r["recommended"] < 0.99


def test_probe_reports_when_embeddings_cannot_tell_the_pages_apart(session_factory):
    with session_factory() as db:
        book = official_book(db, OFFICIAL[:2])
        with_vectors(db, book, [CH1, CH2])
        r = probe(db, Reworder(), Embedder([[0, 0, 1]] * 8), pages=8)  # rewordings land somewhere unrelated
        assert not r["pass"] and not r["separable"] and r["recommended"] is None


def test_probe_needs_pages_and_working_rewording(session_factory):
    with session_factory() as db:
        book = official_book(db, OFFICIAL[:1])
        with_vectors(db, book, [[[1, 0, 0]]])
        assert probe(db, Reworder(), Embedder([]), 8)["status"] == "not_enough_pages"
        with_vectors(db, official_book(db, OFFICIAL[:2]), [CH1, CH2])

        class Broken:
            def complete_json(self, s, u):
                return "not json"
        assert probe(db, Broken(), Embedder([]), 8)["status"] == "rewording_failed"


def test_kept_phrases_measures_how_much_of_the_original_survives():
    a = "one two three four five six seven eight"
    assert kept_phrases(a, a) == 1.0 and kept_phrases(a, "completely different words in another order entirely") == 0.0


def test_official_books_check_passes_a_healthy_book_and_flags_a_test_leftover(session_factory):
    with session_factory() as db:
        official_book(db)
        res = pc.check_official_books(db)
        assert not [r for r in res if r[0] == "FAIL"] and res[0][0] == "PASS"
    with session_factory() as db:
        db.query(Chapter).delete()
        db.query(Book).delete()
        book = official_book(db, OFFICIAL[:2])
        leftover = Chapter(book_id=book.id, title="Matter in Our Surroundings", sequence_num=3, status=ChapterStatus.READY,
                           graph_report={**GOOD, "concepts": 2}, embedding_status="done", graph_sync_status="done")
        db.add(leftover)
        db.flush()
        fails = [m for s, t, m in pc.check_official_books(db) if s == "FAIL"]
        assert any("only 2 concepts" in m and "drop_chapter" in m for m in fails)


def test_official_books_check_fails_on_too_few_chapters_pending_embeddings_and_fake_models(session_factory):
    with session_factory() as db:
        book = official_book(db, OFFICIAL[:2], report={**GOOD, "model": "fake"})
        db.query(Chapter).filter(Chapter.book_id == book.id, Chapter.sequence_num == 2).update({"embedding_status": "failed", "index_error": "boom"})
        fails = " | ".join(m for s, t, m in pc.check_official_books(db) if s == "FAIL")
        assert "need at least 3" in fails and "fake LLM" in fails and "embeddings failed (boom)" in fails


def test_cross_chapter_check_requires_the_step_and_lists_links_to_judge(session_factory):
    with session_factory() as db:
        official_book(db, cross=None)
        assert pc.check_cross_chapter(db)[0][0] == "FAIL"
    with session_factory() as db:
        db.query(Chapter).delete()
        db.query(Book).delete()
        book = official_book(db)
        assert [r[0] for r in pc.check_cross_chapter(db)] == ["PASS", "REVIEW"]  # done, zero links: someone must judge
        ch1, ch2 = [db.scalar(select(Chapter).where(Chapter.book_id == book.id, Chapter.sequence_num == n)) for n in (1, 2)]
        p1, p2 = [db.scalar(select(Page).where(Page.chapter_id == c.id)) for c in (ch1, ch2)]
        a, b = Concept(page_id=p1.id, name="Scientific units"), Concept(page_id=p2.id, name="Estimating cell size")
        db.add_all([a, b])
        db.flush()
        db.add(CrossChapterEdge(chapter_id=ch2.id, concept_id=b.id, prerequisite_id=a.id, similarity=0.61))
        db.flush()
        text = " ".join(m for s, t, m in pc.check_cross_chapter(db))
        assert "'Estimating cell size'" in text and "'Scientific units'" in text and "0.61" in text


def test_structure_check_uses_the_real_titles_and_leaves_nothing_behind(session_factory):
    with session_factory() as db:
        official_book(db)
        db.commit()
        before = (db.scalar(select(func.count()).select_from(Book)), db.scalar(select(func.count()).select_from(User)))
        res = pc.check_structure(db)
        assert [r[0] for r in res if r[1] in ("S1", "S2")] == ["PASS"] * 3
        db.rollback()
        assert (db.scalar(select(func.count()).select_from(Book)), db.scalar(select(func.count()).select_from(User))) == before
    with session_factory() as db:
        db.query(Chapter).delete()
        db.query(Book).delete()
        official_book(db, OFFICIAL[:1])
        assert pc.check_structure(db)[0][0] == "FAIL"


def test_feedback_round_trip_passes_and_leaves_nothing_behind(session_factory):
    with session_factory() as db:
        official_book(db)
        res = pc.check_feedback(db)
        assert [r[0] for r in res if r[1] == "F1"] == ["PASS"] * 3, res
        db.rollback()
        assert db.scalar(select(func.count()).select_from(MatchFeedback)) == 0 and db.scalar(select(func.count()).select_from(User)) == 0


def test_embedding_check_refuses_fake_providers_and_can_be_skipped(session_factory, monkeypatch):
    with session_factory() as db:
        assert pc.check_embedding(db, skip_probe=True)[0][0] == "REVIEW"
        monkeypatch.setattr(settings, "llm_provider", "fake")
        assert pc.check_embedding(db, skip_probe=False)[0][0] == "FAIL"


def test_front_pages_check(session_factory):
    with session_factory() as db:
        assert pc.check_front_pages(db)[0][0] == "FAIL"  # nothing ever confirmed from front pages
        db.add(Book(board="CBSE", class_name="9", subject="Science", publisher="NCERT", is_reference=True, extracted_metadata={"board": "CBSE", "class_name": "Class 9", "subject": "Science", "publisher": "N C E R T"}))
        db.flush()
        res = pc.check_front_pages(db)
        reviews = [m for s, t, m in res if s == "REVIEW"]
        assert res[0][0] == "PASS" and len(reviews) == 1 and "'publisher': read 'N C E R T', teacher confirmed 'NCERT'" in reviews[0]
        assert not any("class_name" in m for s, t, m in res)  # 'Class 9' and '9' are the same class


def test_run_prints_a_verdict_and_never_keeps_anything(session_factory):
    with session_factory() as db:
        official_book(db)
        db.commit()
    lines, fails = pc.run(session_factory, skip_probe=True)
    text = "\n".join(lines)
    assert "RESULT:" in text and fails >= 1 and "Phase 2 is NOT finished" in text  # at least: no migration table, no front-page book
    with session_factory() as db:
        assert db.scalar(select(func.count()).select_from(User)) == 0 and db.scalar(select(func.count()).select_from(MatchFeedback)) == 0


def test_drop_chapter_dry_run_refusals_and_real_delete(session_factory, monkeypatch):
    class Store:
        deleted = []

        def delete_chapter(self, cid):
            self.deleted.append(cid)
    store = Store()
    monkeypatch.setattr(drop_chapter, "get_graph_store", lambda: store)
    with session_factory() as db:
        book = official_book(db)
        teacher_book = Book(board="X", class_name="9", subject="S", publisher="P", is_reference=False, owner_teacher_id=pc._throwaway_teacher(db).id)
        db.add(teacher_book)
        db.flush()
        db.add(Chapter(book_id=teacher_book.id, title="Mine", sequence_num=1, status=ChapterStatus.READY))
        db.commit()
        book_id, teacher_id = book.id, teacher_book.id
    assert "dry run" in "\n".join(drop_chapter.run(session_factory, book_id, 3, confirm=False)) and store.deleted == []
    assert drop_chapter.run(session_factory, teacher_id, 1, True)[0].startswith("Refused")
    assert drop_chapter.run(session_factory, book_id, 9, True)[0].startswith("No chapter number 9")
    out = drop_chapter.run(session_factory, book_id, 3, confirm=True)
    assert out[0].startswith("deleted chapter 3") and "crosslink" in out[1] and len(store.deleted) == 1
    with session_factory() as db:
        assert [c.sequence_num for c in db.scalars(select(Chapter).where(Chapter.book_id == book_id).order_by(Chapter.sequence_num))] == [1, 2]
</file>

<file path="backend/tests/test_step16.py">
"""Delete books/chapters (teacher + admin), front-page reading that survives odd answers, drop_book, relaxed unresolved rule."""
import json
import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import func, select

from app.content_library import deletion
from app.core.config import settings
from app.db import drop_book, phase2_check as pc, try_front_pages
from app.models import Book, Chapter, ChapterStatus, Page, Role
from app.pipeline.front_matter import BookMetadata, extract_book_metadata, is_empty, parse_reply
from tests.test_book_access import make_user, new_book, new_chapter, reference_book
from tests.test_step6 import front_pdf, post_front, ref_book
from tests.test_step15 import GOOD, TEXT, official_book


class FakeStore:
    def __init__(self, fail=False):
        self.deleted, self.fail = [], fail

    def delete_chapter(self, cid):
        if self.fail:
            raise RuntimeError("graph store down")
        self.deleted.append(cid)


@pytest.fixture
def store(monkeypatch):
    s = FakeStore()
    monkeypatch.setattr(deletion, "get_graph_store", lambda: s)
    return s


def add_chapter_row(session_factory, book_id, title="Ch", seq=1, status=ChapterStatus.READY, started=None):
    with session_factory() as db:
        ch = Chapter(book_id=uuid.UUID(book_id), title=title, sequence_num=seq, status=status, processing_started_at=started)
        db.add(ch)
        db.flush()
        db.add(Page(chapter_id=ch.id, page_number=1, content_text=TEXT))
        db.commit()
        return str(ch.id)


def count(session_factory, model):
    with session_factory() as db:
        return db.scalar(select(func.count()).select_from(model))


# ---------------- teachers delete their own books and chapters ----------------

def test_teacher_deletes_own_book_with_its_chapters_and_graph_copy(client, session_factory, store):
    _, th = make_user(session_factory, Role.teacher, "teachera")
    book = new_book(client, th)
    ch_id = add_chapter_row(session_factory, book["id"])
    assert client.delete(f"/teacher/books/{book['id']}", headers=th).status_code == 204
    assert count(session_factory, Book) == 0 and count(session_factory, Chapter) == 0 and count(session_factory, Page) == 0
    assert store.deleted == [uuid.UUID(ch_id)] or store.deleted == [ch_id]
    assert client.delete(f"/teacher/books/{book['id']}", headers=th).status_code == 404


def test_nobody_else_can_delete_my_book_and_official_books_are_not_deletable_here(client, session_factory, store):
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    _, bh = make_user(session_factory, Role.teacher, "teacherb")
    book = new_book(client, ah)
    assert client.delete(f"/teacher/books/{book['id']}", headers=bh).status_code == 404
    ref = ref_book(session_factory)
    assert client.delete(f"/teacher/books/{ref}", headers=ah).status_code == 403
    assert count(session_factory, Book) == 2


def test_deleting_a_book_unmarks_books_that_were_variants_of_it(client, session_factory, store):
    _, th = make_user(session_factory, Role.teacher, "teachera")
    base, variant = new_book(client, th), new_book(client, th, subject="Other")
    assert client.post(f"/teacher/books/{variant['id']}/variant-of", json={"base_book_id": base["id"]}, headers=th).status_code == 200
    assert client.delete(f"/teacher/books/{base['id']}", headers=th).status_code == 204
    with session_factory() as db:
        assert db.get(Book, uuid.UUID(variant["id"])).variant_of_id is None


def test_a_chapter_being_processed_cannot_be_deleted_but_a_stuck_one_can(client, session_factory, store):
    _, th = make_user(session_factory, Role.teacher, "teachera")
    book = new_book(client, th)
    busy = add_chapter_row(session_factory, book["id"], "Busy", 1, ChapterStatus.PROCESSING, datetime.now(timezone.utc))
    assert client.delete(f"/teacher/books/{book['id']}/chapters/{busy}", headers=th).status_code == 409
    assert client.delete(f"/teacher/books/{book['id']}", headers=th).status_code == 409
    stuck = add_chapter_row(session_factory, book["id"], "Stuck", 2, ChapterStatus.PROCESSING, datetime(2020, 1, 1, tzinfo=timezone.utc))
    assert client.delete(f"/teacher/books/{book['id']}/chapters/{stuck}", headers=th).status_code == 204


def test_delete_chapter_checks_it_belongs_to_that_book_and_book_survives(client, session_factory, store):
    _, th = make_user(session_factory, Role.teacher, "teachera")
    a, b = new_book(client, th), new_book(client, th, subject="Other")
    ch = add_chapter_row(session_factory, a["id"])
    assert client.delete(f"/teacher/books/{b['id']}/chapters/{ch}", headers=th).status_code == 404
    assert client.delete(f"/teacher/books/{a['id']}/chapters/{ch}", headers=th).status_code == 204
    assert count(session_factory, Book) == 2 and count(session_factory, Chapter) == 0


def test_graph_store_trouble_never_blocks_a_delete(client, session_factory, monkeypatch):
    monkeypatch.setattr(deletion, "get_graph_store", lambda: FakeStore(fail=True))
    _, th = make_user(session_factory, Role.teacher, "teachera")
    book = new_book(client, th)
    add_chapter_row(session_factory, book["id"])
    assert client.delete(f"/teacher/books/{book['id']}", headers=th).status_code == 204
    assert count(session_factory, Chapter) == 0


# ---------------- administrators delete official books ----------------

def test_only_listed_administrators_can_delete_official_books_and_chapters(client, session_factory, store, monkeypatch):
    _, ah = make_user(session_factory, Role.teacher, "adminuser")
    _, th = make_user(session_factory, Role.teacher, "teachera")
    ref = ref_book(session_factory)
    ch = add_chapter_row(session_factory, ref)
    mine = new_book(client, th)
    assert client.delete(f"/admin/books/{ref}", headers=ah).status_code == 403  # nobody is an administrator by default
    monkeypatch.setattr(settings, "admin_usernames", " AdminUser , someone ")
    assert client.delete(f"/admin/books/{ref}", headers=th).status_code == 403
    assert client.delete(f"/admin/books/{mine['id']}", headers=ah).status_code == 404  # not official: not an admin matter
    assert client.delete(f"/admin/books/{ref}/chapters/{uuid.uuid4()}", headers=ah).status_code == 404
    assert client.delete(f"/admin/books/{ref}/chapters/{ch}", headers=ah).status_code == 204
    assert client.delete(f"/admin/books/{ref}", headers=ah).status_code == 204
    assert count(session_factory, Book) == 1


def test_me_tells_the_ui_whether_the_user_is_an_administrator(client, session_factory, monkeypatch):
    _, ah = make_user(session_factory, Role.teacher, "adminuser")
    assert client.get("/auth/me", headers=ah).json()["is_admin"] is False
    monkeypatch.setattr(settings, "admin_usernames", "adminuser")
    assert client.get("/auth/me", headers=ah).json()["is_admin"] is True


def test_drop_book_tool(session_factory, store):
    with session_factory() as db:
        official = official_book(db)
        teacher_book_id = None
        db.commit()
        book_id = official.id
    out = drop_book.run(session_factory, book_id, confirm=False)
    assert "would delete" in out[0] and "3 chapters" in out[0] and count(session_factory, Book) == 1
    assert drop_book.run(session_factory, uuid.uuid4(), True) == ["Book not found."]
    assert drop_book.run(session_factory, book_id, True)[0].startswith("deleted") and count(session_factory, Book) == 0
    assert len(store.deleted) == 3


# ---------------- front pages ----------------

def test_reply_parsing_accepts_odd_but_clear_answers():
    assert parse_reply('{"Board": "CBSE", "Class": "Class 9", "Subject": "Science", "Publisher": "NCERT"}').publisher == "NCERT"
    nested = parse_reply('{"metadata": {"board": "CBSE", "grade": "Class 9", "publisher": "NCERT"}}')
    assert nested.class_name == "Class 9" and nested.board == "CBSE"
    assert parse_reply('```json\n{"board": "ICSE"}\n```').board == "ICSE"
    assert is_empty(parse_reply('{"unrelated": 1}'))


class Scripted:
    def __init__(self, *replies):
        self.replies, self.calls = list(replies), 0

    def complete_json(self, system, user):
        self.calls += 1
        return self.replies.pop(0) if len(self.replies) > 1 else self.replies[0]


def test_an_all_empty_answer_gets_a_second_look_and_never_crashes():
    good = '{"board": "CBSE", "class_name": "Class 9", "subject": "Science", "publisher": "NCERT"}'
    llm = Scripted('{"board": null, "class_name": null}', good)
    assert extract_book_metadata(llm, "Curiosity Grade 9 Science NCERT").publisher == "NCERT" and llm.calls == 2
    nothing = Scripted('{"board": null, "class_name": null, "subject": null, "publisher": null}')
    assert is_empty(extract_book_metadata(nothing, "some text")) and nothing.calls == 3  # asked three times, then the form stays empty
    junk_then_good = Scripted("not json at all", good)
    assert extract_book_metadata(junk_then_good, "text").board == "CBSE"


def test_the_draft_says_so_when_nothing_could_be_read(client, session_factory, monkeypatch):
    _, th = make_user(session_factory, Role.teacher, "teachera")
    with monkeypatch.context() as m:
        m.setattr("app.content_library.upload.extract_book_metadata", lambda provider, text: BookMetadata())
        body = post_front(client, th).json()
    assert body["warning"] and "characters" in body["warning"] and body["metadata"]["publisher"] is None
    assert post_front(client, th).json()["warning"] is None  # the normal fake-provider read fills the form


def test_try_front_pages_shows_what_the_reader_gets(tmp_path):
    pdf = tmp_path / "front.pdf"
    pdf.write_bytes(front_pdf())

    class Ocr:
        def extract_layout(self, data, ext):
            return {"pages": [{"text": "CURIOSITY Textbook of Science Grade 9 NCERT"}]}

    class Llm:
        def complete_json(self, system, user):
            return json.dumps({"board": None, "class_name": "Class 9", "subject": "Science", "publisher": "NCERT"})
    text = "\n".join(try_front_pages.run(str(pdf), Ocr(), Llm()))
    assert "43 characters" in text and "CURIOSITY" in text and "'publisher': 'NCERT'" in text and "would be filled" in text
    class Blank:
        def extract_layout(self, data, ext):
            return {"pages": [{"text": "   "}]}
    assert "No readable text" in "\n".join(try_front_pages.run(str(pdf), Blank(), Llm()))
    assert "Unsupported" in try_front_pages.run(str(tmp_path / "x.txt"))[0]


# ---------------- phase2_check: the two rules that were too blunt ----------------

def test_a_stray_unresolved_prerequisite_is_shown_for_review_not_failed(session_factory):
    with session_factory() as db:
        official_book(db, report={**GOOD, "concepts": 98, "unresolved_prerequisites": [{"concept": "A", "prerequisite": "Z"}]})
        res = pc.check_official_books(db)
        assert not [r for r in res if r[0] == "FAIL"]
        assert any(r[0] == "REVIEW" and "'A' needs 'Z'" in r[2] for r in res)
    with session_factory() as db:
        db.query(Chapter).delete()
        db.query(Book).delete()
        official_book(db, report={**GOOD, "concepts": 20, "unresolved_prerequisites": [{"concept": "A", "prerequisite": "Z"}] * 6})
        assert any(r[0] == "FAIL" and "unresolved" in r[2] for r in pc.check_official_books(db))


def test_an_empty_official_book_is_named_and_the_fix_is_given(session_factory):
    with session_factory() as db:
        official_book(db)
        empty = Book(board="CBSE", class_name="Class 9", subject="Science", publisher="NCERT", edition="2026", is_reference=True)
        db.add(empty)
        db.flush()
        fails = [r[2] for r in pc.check_official_books(db) if r[0] == "FAIL"]
        assert len(fails) == 1 and "no chapters at all" in fails[0] and f"drop_book --book {empty.id}" in fails[0] and "edition 2026" in fails[0]


# ---------------- what the real NCERT front pages produced (Oct 2026 run) ----------------
from app.content_library.publishers import acronym, board_is_really_a_publisher, same_publisher
from app.content_library.search import match_metadata

FULL = "National Council of Educational Research and Training"


def test_publisher_written_long_short_or_with_dots_is_one_publisher():
    assert acronym(FULL) == "ncert" and acronym("NCERT") == ""
    assert same_publisher(FULL, "NCERT") and same_publisher("N.C.E.R.T.", "NCERT") and same_publisher("N C E R T", FULL)
    assert not same_publisher("Oxford University Press", "NCERT") and not same_publisher("", "NCERT") and not same_publisher("Pearson", FULL)


def test_ncert_is_never_taken_as_the_board():
    assert board_is_really_a_publisher("NCERT") and board_is_really_a_publisher("N.C.E.R.T.") and board_is_really_a_publisher(FULL)
    assert board_is_really_a_publisher("Bharati Board", "Bharati Board") and not board_is_really_a_publisher("CBSE", "NCERT")
    m = parse_reply(json.dumps({"board": "NCERT", "class_name": "Class 10", "subject": "Science", "publisher": FULL, "edition": "Reprint 2026-27"}))
    assert m.board is None and m.publisher == FULL and m.class_name == "Class 10"


def test_the_real_reading_finds_the_official_book_it_is_a_copy_of(session_factory):
    with session_factory() as db:
        official = Book(board="CBSE", class_name="Class 9", subject="Science", publisher="NCERT", is_reference=True)
        other_class = Book(board="CBSE", class_name="Class 10", subject="Science", publisher="NCERT", is_reference=True)
        db.add_all([official, other_class])
        db.flush()
        seen = BookMetadata(board="NCERT", class_name="Class IX", subject="Science", publisher=FULL, edition="Reprint 2026-27")
        who = type("T", (), {"id": uuid.uuid4()})()
        assert [b.id for b in match_metadata(db, who, seen)] == [official.id]  # before the fix: board 'NCERT' and a long publisher name -> no match
        assert match_metadata(db, who, BookMetadata(class_name="Class 8", subject="Science", publisher=FULL)) == []  # another class is another book
        no_publisher = BookMetadata(board="NCERT", class_name="Class 9", subject="Science")  # the board slot held a publisher name
        assert [b.id for b in match_metadata(db, who, no_publisher)] == [official.id]


def test_try_front_pages_also_shows_the_library_match(tmp_path, session_factory):
    pdf = tmp_path / "front.pdf"
    pdf.write_bytes(front_pdf())
    with session_factory() as db:
        db.add(Book(board="CBSE", class_name="Class 9", subject="Science", publisher="NCERT", edition="2026", is_reference=True))
        db.commit()

    class Ocr:
        def extract_layout(self, data, ext):
            return {"pages": [{"text": "SCIENCE TEXTBOOK FOR CLASS IX NCERT National Council of Educational Research and Training"}]}

    class Llm:
        def complete_json(self, system, user):
            return json.dumps({"board": "NCERT", "class_name": "Class 9", "subject": "Science", "publisher": FULL})
    text = "\n".join(try_front_pages.run(str(pdf), Ocr(), Llm(), db_factory=session_factory))
    assert "'board': None" in text and "library match: NCERT Class 9 Science (edition 2026)" in text
</file>

<file path="backend/tests/test_step6.py">
"""Front-pages-first upload, library search, whole-textbook upload, bulk link, chapter requests."""
import io
import uuid

import pypdf
import pytest
from sqlalchemy import select

from app.core.config import settings
from app.models import Book, Chapter, ChapterRequest, Role, UploadDraft
from app.content_library.search import normalize_class
from tests.test_book_access import make_user, new_book, new_chapter, reference_book
from tests.test_chapter_jobs import chapter_status, page_count, upload
from tests.test_pipeline import _text_pdf

FRONT = ["Board: CBSE", "Class: IX", "Subject: Science", "Publisher: NCERT", "Edition: First edition 2025"]


def front_pdf(lines=FRONT):
    return _text_pdf(*lines)


def post_front(client, headers, data=None, name="front.pdf"):
    return client.post("/teacher/book-drafts/front-pages", files={"file": (name, data or front_pdf(), "application/pdf")}, headers=headers)


def ref_book(session_factory, **kw):
    fields = dict(board="CBSE", class_name="Class 9", subject="Science", publisher="NCERT", is_reference=True)
    fields.update(kw)
    with session_factory() as db:
        book = Book(**fields)
        db.add(book)
        db.commit()
        return str(book.id)


def pdf_with_outline(page_texts, outline):
    reader = pypdf.PdfReader(io.BytesIO(_text_pdf(*page_texts)))
    writer = pypdf.PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    for title, index in outline:
        writer.add_outline_item(title, index)
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


# ================= front pages =================================================================

def test_front_pages_return_metadata_and_matching_visible_books_only(client, session_factory):
    ref_id = ref_book(session_factory)
    ref_book(session_factory, subject="History")  # same board/class/publisher but another subject
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    _, bh = make_user(session_factory, Role.teacher, "teacherb")
    b_private = new_book(client, bh, board="CBSE", class_name="Class 9", subject="Science", publisher="NCERT")

    res = post_front(client, ah)
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["metadata"] == {"board": "CBSE", "class_name": "IX", "subject": "Science", "publisher": "NCERT",
                                "edition": "First edition 2025", "is_customized": False, "school": None}
    assert [m["id"] for m in body["matches"]] == [ref_id]  # 'IX' == 'Class 9'; History book and B's private book excluded

    mine = new_book(client, ah, board="CBSE", class_name="9", subject="Science", publisher="NCERT")
    again = post_front(client, ah).json()["matches"]
    assert [m["id"] for m in again] == [ref_id, mine["id"]] and b_private["id"] not in str(again)  # official first


def test_book_is_created_only_when_the_teacher_confirms_the_draft(client, session_factory):
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    _, bh = make_user(session_factory, Role.teacher, "teacherb")
    draft = post_front(client, ah).json()
    with session_factory() as db:
        assert db.scalars(select(Book)).all() == []  # nothing created yet

    body = {"board": "CBSE", "class_name": "Class 9", "subject": "Science", "publisher": "NCERT", "draft_id": draft["draft_id"]}
    assert client.post("/teacher/books", json=body, headers=bh).status_code == 404  # B can't use A's draft
    res = client.post("/teacher/books", json={**body, "edition": "edited by teacher"}, headers=ah)
    assert res.status_code == 201 and res.json()["metadata_source"] == "front_pages"
    with session_factory() as db:
        book = db.get(Book, uuid.UUID(res.json()["id"]))
        assert book.extracted_metadata["class_name"] == "IX"  # what was read, kept next to what was confirmed
        assert book.class_name == "Class 9" and book.front_pages_file
        assert db.scalars(select(UploadDraft)).all() == []
    assert client.post("/teacher/books", json=body, headers=ah).status_code == 404  # draft is single-use


def test_manual_entry_still_works_unless_front_pages_are_required(client, session_factory, monkeypatch):
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    body = {"board": "ICSE", "class_name": "Class 9", "subject": "Math", "publisher": "Selina"}
    assert client.post("/teacher/books", json=body, headers=ah).json()["metadata_source"] == "manual"
    monkeypatch.setattr(settings, "require_front_pages", True)
    assert client.post("/teacher/books", json=body, headers=ah).status_code == 422
    draft = post_front(client, ah).json()
    assert client.post("/teacher/books", json={**body, "draft_id": draft["draft_id"]}, headers=ah).status_code == 201


def test_front_pages_validation_and_failures_are_safe(client, session_factory, monkeypatch):
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    assert post_front(client, ah, _text_pdf(*[f"p{i}" for i in range(settings.front_pages_max_pages + 1)])).status_code == 422
    assert post_front(client, ah, b"not a pdf at all").status_code == 415
    assert post_front(client, ah, b"%PDF-1.4 corrupt").status_code in (201, 422)  # fake OCR tolerates; real files are checked

    class BlankOCR:
        def extract_layout(self, data, ext):
            return {"pages": [{"page_number": 1, "text": "  ", "lines": []}], "page_count": 1}

    class BrokenOCR:
        def extract_layout(self, data, ext):
            raise RuntimeError("azure key abc123 rejected")

    monkeypatch.setattr("app.content_library.upload.get_ocr_provider", lambda: BlankOCR())
    assert post_front(client, ah).status_code == 422
    monkeypatch.setattr("app.content_library.upload.get_ocr_provider", lambda: BrokenOCR())
    res = post_front(client, ah)
    assert res.status_code == 422 and "abc123" not in res.text and "try again" in res.text.lower()

    monkeypatch.undo()

    class GarbageLLM:
        def complete_json(self, system, user):
            return "nope"

    monkeypatch.setattr("app.content_library.upload.get_llm_provider", lambda: GarbageLLM())
    res = post_front(client, ah)
    assert res.status_code == 422 and "by hand" in res.text
    with session_factory() as db:
        assert db.scalars(select(UploadDraft)).all() == []  # failed attempts leave nothing behind


# ================= search ==================================================================================

def test_normalize_class():
    assert [normalize_class(x) for x in ("Class 9", "IX", "9th", "Grade 9", "class ix", "")] == ["9", "9", "9", "9", "9", ""]


def test_library_search(client, session_factory):
    ref_id = ref_book(session_factory)
    ref10 = ref_book(session_factory, class_name="Class 10", subject="Maths")
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    _, bh = make_user(session_factory, Role.teacher, "teacherb")
    mine = new_book(client, ah, subject="Science", publisher="Oxford", board="ICSE", class_name="Class 9")
    new_book(client, bh, subject="Science", publisher="Hidden Press")

    def ids(**params):
        return {b["id"] for b in client.get("/teacher/books", params=params, headers=ah).json()}

    assert ids(class_name="IX", subject="science") == {ref_id, mine["id"]}
    assert ids(publisher="ncer") == {ref_id, ref10}
    assert ids(q="oxford icse") == {mine["id"]}
    assert ids(q="science", scope="reference") == {ref_id}
    assert ids(q="hidden") == set()  # other teacher's private book
    assert ids(q="%") == set() and ids(subject="_") == set()  # LIKE wildcards are not wildcards here


# ================= whole textbook =============================================================================

TEXTS = [f"page {i} of the textbook about topic {i}" for i in range(1, 7)]


def plan(client, headers, book_id, data, name="book.pdf"):
    return client.post(f"/teacher/books/{book_id}/whole-book/plan", files={"file": (name, data, "application/pdf")}, headers=headers)


def confirm(client, headers, book_id, draft_id, chapters):
    return client.post(f"/teacher/books/{book_id}/whole-book/confirm", json={"draft_id": draft_id, "chapters": chapters}, headers=headers)


def test_whole_book_is_split_by_bookmarks_and_processed_per_chapter(client, session_factory):
    _, th = make_user(session_factory, Role.teacher, "teachera")
    book = new_book(client, th)
    existing = new_chapter(client, th, book["id"])  # sequence 1 already used

    res = plan(client, th, book["id"], pdf_with_outline(TEXTS, [("Matter", 0), ("Atoms", 2), ("Energy", 5)]))
    assert res.status_code == 201, res.text
    p = res.json()
    assert p["page_count"] == 6
    assert p["proposed_chapters"] == [
        {"title": "Matter", "start_page": 1, "end_page": 2},
        {"title": "Atoms", "start_page": 3, "end_page": 5},
        {"title": "Energy", "start_page": 6, "end_page": 6},
    ]
    with session_factory() as db:
        assert db.scalars(select(Chapter).where(Chapter.title == "Matter")).all() == []  # not created before confirm

    edited = [{"title": "Matter and Atoms", "start_page": 1, "end_page": 4}, {"title": "Energy", "start_page": 5, "end_page": 6}]
    res = confirm(client, th, book["id"], p["draft_id"], edited)
    assert res.status_code == 202, res.text
    assert [(c["title"], c["sequence_num"]) for c in res.json()] == [("Matter and Atoms", 2), ("Energy", 3)]
    chapters = {c["title"]: c for c in client.get(f"/teacher/books/{book['id']}/chapters", headers=th).json()}
    assert chapters["Matter and Atoms"]["status"] == chapters["Energy"]["status"] == "ready"  # background jobs ran
    assert chapters[existing and "Ch 1"]["status"] == "empty"
    assert page_count(session_factory, chapters["Matter and Atoms"]["id"]) == 4 and page_count(session_factory, chapters["Energy"]["id"]) == 2

    texts = [pg["content_text"] for pg in client.get(
        f"/teacher/books/{book['id']}/chapters/{chapters['Energy']['id']}/pages", headers=th).json()]
    assert texts == [TEXTS[4], TEXTS[5]]  # the right slice of the PDF
    assert confirm(client, th, book["id"], p["draft_id"], edited).status_code == 404  # draft is single-use


def test_whole_book_without_bookmarks_proposes_nothing_and_accepts_manual_ranges(client, session_factory):
    _, th = make_user(session_factory, Role.teacher, "teachera")
    book = new_book(client, th)
    p = plan(client, th, book["id"], _text_pdf(*TEXTS)).json()
    assert p["proposed_chapters"] == [] and p["page_count"] == 6
    res = confirm(client, th, book["id"], p["draft_id"], [{"title": "All of it", "start_page": 1, "end_page": 6}])
    assert res.status_code == 202 and res.json()[0]["sequence_num"] == 1


@pytest.mark.parametrize("chapters,message", [
    ([], "at least one"),
    ([{"title": "A", "start_page": 1, "end_page": 3}, {"title": "B", "start_page": 3, "end_page": 5}], "overlaps"),
    ([{"title": "A", "start_page": 4, "end_page": 2}], "before the first"),
    ([{"title": "A", "start_page": 1, "end_page": 9}], "only has 6 pages"),
])
def test_whole_book_range_validation(client, session_factory, chapters, message):
    _, th = make_user(session_factory, Role.teacher, "teachera")
    book = new_book(client, th)
    p = plan(client, th, book["id"], _text_pdf(*TEXTS)).json()
    res = confirm(client, th, book["id"], p["draft_id"], chapters)
    assert res.status_code == 422 and message in res.text
    with session_factory() as db:
        assert db.scalars(select(Chapter)).all() == []  # nothing half-created


def test_whole_book_chapter_count_limit(client, session_factory, monkeypatch):
    monkeypatch.setattr(settings, "max_whole_book_chapters", 2)
    _, th = make_user(session_factory, Role.teacher, "teachera")
    book = new_book(client, th)
    p = plan(client, th, book["id"], _text_pdf(*TEXTS)).json()
    three = [{"title": f"C{i}", "start_page": i, "end_page": i} for i in (1, 2, 3)]
    assert confirm(client, th, book["id"], p["draft_id"], three).status_code == 422


def test_whole_book_access_and_file_checks(client, session_factory):
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    _, bh = make_user(session_factory, Role.teacher, "teacherb")
    _, sh = make_user(session_factory, Role.student, "student1")
    book, other = new_book(client, ah), new_book(client, ah, subject="Other")
    ref = reference_book(session_factory)
    pdf = _text_pdf(*TEXTS)

    assert plan(client, bh, book["id"], pdf).status_code == 404  # not B's book
    assert plan(client, ah, ref, pdf).status_code == 403  # reference is read-only
    assert plan(client, sh, book["id"], pdf).status_code == 403
    png = b"\x89PNG\r\n\x1a\n" + b"0" * 20
    assert plan(client, ah, book["id"], png).status_code == 415  # whole book must be a PDF
    assert plan(client, ah, book["id"], b"%PDF-1.4 this is junk").status_code == 422  # unreadable PDF
    assert plan(client, ah, book["id"], b"").status_code == 400

    p = plan(client, ah, book["id"], pdf).json()
    one = [{"title": "A", "start_page": 1, "end_page": 2}]
    assert confirm(client, bh, book["id"], p["draft_id"], one).status_code == 404  # B can't confirm A's draft
    assert confirm(client, ah, other["id"], p["draft_id"], one).status_code == 404  # draft belongs to a different book
    assert confirm(client, ah, book["id"], str(uuid.uuid4()), one).status_code == 404


# ================= bulk link ====================================================================================

def make_room(client, headers, room_type="single_class"):
    return client.post("/teacher/rooms", json={"name": "Class 9A", "room_type": room_type}, headers=headers).json()


def join(client, room, headers):
    assert client.post("/student/rooms/join", json={"join_code": room["join_code"]}, headers=headers).status_code == 200


def test_bulk_link_a_book_to_every_student_in_a_single_class_room(client, session_factory):
    _, th = make_user(session_factory, Role.teacher, "teachera")
    students = [make_user(session_factory, Role.student, f"student{i}")[1] for i in (1, 2, 3)]
    room = make_room(client, th)
    for h in students[:2]:
        join(client, room, h)
    ref_id, mine = reference_book(session_factory), new_book(client, th)

    url = lambda book: f"/teacher/rooms/{room['id']}/books/{book}/link"
    assert client.post(url(ref_id), headers=th).json() == {"linked": 2, "already_linked": 0, "total_students": 2}
    assert client.post(url(ref_id), headers=th).json() == {"linked": 0, "already_linked": 2, "total_students": 2}
    assert client.post(url(mine["id"]), headers=th).json()["linked"] == 2
    assert {b["id"] for b in client.get("/student/books", headers=students[0]).json()} == {ref_id, mine["id"]}
    assert client.get("/student/books", headers=students[2]).json() == []  # not in the room: untouched

    join(client, room, students[2])  # joins later: not auto-linked (links stay per-student)
    assert client.get("/student/books", headers=students[2]).json() == []
    assert client.post(url(ref_id), headers=th).json() == {"linked": 1, "already_linked": 2, "total_students": 3}


def test_bulk_link_rules(client, session_factory):
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    _, bh = make_user(session_factory, Role.teacher, "teacherb")
    _, sh = make_user(session_factory, Role.student, "student1")
    single, mixed = make_room(client, ah), make_room(client, ah, "mixed_class")
    a_book, b_book = new_book(client, ah), new_book(client, bh)

    assert client.post(f"/teacher/rooms/{mixed['id']}/books/{a_book['id']}/link", headers=ah).status_code == 409
    assert client.post(f"/teacher/rooms/{single['id']}/books/{a_book['id']}/link", headers=bh).status_code == 404  # not B's room
    assert client.post(f"/teacher/rooms/{single['id']}/books/{b_book['id']}/link", headers=ah).status_code == 404  # B's private book
    assert client.post(f"/teacher/rooms/{single['id']}/books/{a_book['id']}/link", headers=sh).status_code == 403
    empty = client.post(f"/teacher/rooms/{single['id']}/books/{a_book['id']}/link", headers=ah)
    assert empty.json() == {"linked": 0, "already_linked": 0, "total_students": 0}


# ================= chapter requests ===============================================================================

def setup_requests(client, session_factory):
    _, th = make_user(session_factory, Role.teacher, "teachera")
    _, sh = make_user(session_factory, Role.student, "student1")
    book = new_book(client, th)
    room = make_room(client, th)
    join(client, room, sh)
    client.post(f"/student/books/{book['id']}/link", headers=sh)
    return th, sh, book


def ask(client, headers, book_id, hint, chapter_id=None):
    body = {"chapter_hint": hint, **({"chapter_id": chapter_id} if chapter_id else {})}
    return client.post(f"/student/books/{book_id}/chapter-requests", json=body, headers=headers)


def test_student_requests_a_chapter_and_duplicates_are_merged(client, session_factory):
    th, sh, book = setup_requests(client, session_factory)
    first = ask(client, sh, book["id"], "Chapter 9:  Force and Laws of Motion")
    assert first.status_code == 201 and first.json()["status"] == "open"
    again = ask(client, sh, book["id"], "chapter 9 force and laws of motion!")
    assert again.status_code == 200 and again.json()["id"] == first.json()["id"]
    assert ask(client, sh, book["id"], "Gravitation").status_code == 201
    assert len(client.get("/student/chapter-requests", headers=sh).json()) == 2


def test_request_rules(client, session_factory, monkeypatch):
    th, sh, book = setup_requests(client, session_factory)
    _, other_student = make_user(session_factory, Role.student, "student2")
    ref = reference_book(session_factory)
    client.post(f"/student/books/{ref}/link", headers=sh)
    ready_ch = new_chapter(client, th, book["id"])
    upload(client, th, book["id"], ready_ch, _text_pdf("a page"))

    assert ask(client, other_student, book["id"], "Gravitation").status_code == 404  # hasn't linked the book
    assert ask(client, sh, ref, "Gravitation").status_code == 409  # official books have no teacher to ask
    assert ask(client, sh, book["id"], "!!").status_code == 422
    assert ask(client, sh, book["id"], "x" * 201).status_code == 422
    assert ask(client, sh, book["id"], "Chapter 1", chapter_id=ready_ch).status_code == 409  # already available
    assert ask(client, sh, book["id"], "Chapter 1", chapter_id=str(uuid.uuid4())).status_code == 404

    monkeypatch.setattr(settings, "open_requests_per_student", 2)
    assert ask(client, sh, book["id"], "Gravitation").status_code == 201
    assert ask(client, sh, book["id"], "Sound").status_code == 201
    assert ask(client, sh, book["id"], "Light").status_code == 429
    assert ask(client, sh, book["id"], "Sound").status_code == 200  # an existing one is still just returned


def test_teacher_sees_only_their_students_requests_and_can_close_them(client, session_factory):
    th, sh, book = setup_requests(client, session_factory)
    _, other_teacher = make_user(session_factory, Role.teacher, "teacherb")
    r1 = ask(client, sh, book["id"], "Gravitation").json()
    r2 = ask(client, sh, book["id"], "Sound").json()

    listed = client.get("/teacher/chapter-requests", headers=th).json()
    assert {r["chapter_hint"] for r in listed} == {"Gravitation", "Sound"}
    assert listed[0]["student_name"] == "student1" and listed[0]["book"]["id"] == book["id"]
    assert client.get("/teacher/chapter-requests", headers=other_teacher).json() == []
    assert client.post(f"/teacher/chapter-requests/{r1['id']}/dismiss", headers=other_teacher).status_code == 404

    assert client.post(f"/teacher/chapter-requests/{r1['id']}/dismiss", headers=th).json()["status"] == "dismissed"
    assert client.post(f"/teacher/chapter-requests/{r1['id']}/dismiss", headers=th).status_code == 409
    empty_ch = new_chapter(client, th, book["id"])
    assert client.post(f"/teacher/chapter-requests/{r2['id']}/fulfill", json={"chapter_id": empty_ch}, headers=th).status_code == 409  # not ready
    assert client.post(f"/teacher/chapter-requests/{r2['id']}/fulfill", json={}, headers=th).json()["status"] == "fulfilled"
    assert client.get("/teacher/chapter-requests", headers=th).json() == []
    assert len(client.get("/teacher/chapter-requests?status=all", headers=th).json()) == 2
    statuses = {r["chapter_hint"]: r["status"] for r in client.get("/student/chapter-requests", headers=sh).json()}
    assert statuses == {"Gravitation": "dismissed", "Sound": "fulfilled"}


def test_student_can_cancel_only_their_own_open_request(client, session_factory):
    th, sh, book = setup_requests(client, session_factory)
    _, other_student = make_user(session_factory, Role.student, "student2")
    r = ask(client, sh, book["id"], "Gravitation").json()
    assert client.delete(f"/student/chapter-requests/{r['id']}", headers=other_student).status_code == 404
    assert client.delete(f"/student/chapter-requests/{r['id']}", headers=sh).status_code == 204
    assert client.get("/teacher/chapter-requests", headers=th).json() == []
    assert client.get("/student/chapter-requests", headers=sh).json()[0]["status"] == "cancelled"
    assert client.get("/student/chapter-requests", headers=other_student).json() == []


def test_requests_close_themselves_when_the_chapter_becomes_ready(client, session_factory):
    th, sh, book = setup_requests(client, session_factory)
    other_book = new_book(client, th, subject="Other")
    chapter = client.post(f"/teacher/books/{book['id']}/chapters", json={"title": "Chapter 9: Force and Laws of Motion", "sequence_num": 9}, headers=th).json()["id"]
    pending = new_chapter(client, th, book["id"])

    by_title = ask(client, sh, book["id"], "force and laws of motion").json()
    by_id = ask(client, sh, book["id"], "the second one please", chapter_id=pending).json()
    unrelated = ask(client, sh, book["id"], "Gravitation").json()
    client.post(f"/student/books/{other_book['id']}/link", headers=sh)
    elsewhere = ask(client, sh, other_book["id"], "force and laws of motion").json()

    upload(client, th, book["id"], chapter, _text_pdf("some page text"))
    upload(client, th, book["id"], pending, _text_pdf("another page"))
    status_of = {r["id"]: r["status"] for r in client.get("/student/chapter-requests", headers=sh).json()}
    assert status_of[by_title["id"]] == "fulfilled" and status_of[by_id["id"]] == "fulfilled"
    assert status_of[unrelated["id"]] == "open" and status_of[elsewhere["id"]] == "open"  # other chapter / other book
    with session_factory() as db:
        assert db.get(ChapterRequest, uuid.UUID(by_id["id"])).resolved_at is not None
</file>

<file path="backend/tests/test_step7.py">
"""Rate limits, needs_review flags, draft cleanup, and the reference-corpus ingest script."""
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.core import ratelimit
from app.core.config import settings
from app.core.storage import read_file, save_by_hash, sha256_hex
from app.db.cleanup_drafts import cleanup
from app.db.ingest_reference import ingest, parse_ranges
from app.models import Book, Chapter, Page, Role, UploadDraft, User
from app.pipeline.orchestrator import PipelineOrchestrator
from tests.test_book_access import make_user, new_book, new_chapter
from tests.test_chapter_jobs import BrokenLLM, upload, use_llm
from tests.test_pipeline import CountingLLM, _text_pdf
from tests.test_step6 import TEXTS, make_room, pdf_with_outline, plan, post_front


# ---- rate limits --------------------------------------------------------------------------------

def test_limiter_blocks_after_limit_resets_after_window_and_separates_users(monkeypatch):
    clock = [1000.0]
    monkeypatch.setattr(ratelimit.time, "monotonic", lambda: clock[0])
    lim = ratelimit.RateLimiter()
    for _ in range(3):
        lim.check("b", "u1", 3, 60)
    with pytest.raises(Exception) as err:
        lim.check("b", "u1", 3, 60)
    assert err.value.status_code == 429 and int(err.value.headers["Retry-After"]) >= 1
    lim.check("b", "u2", 3, 60)  # other user unaffected
    lim.check("other-bucket", "u1", 3, 60)  # other action unaffected
    clock[0] += 61
    lim.check("b", "u1", 3, 60)  # window passed


def test_join_room_is_rate_limited_per_student(client, session_factory, monkeypatch):
    monkeypatch.setattr(settings, "rate_join_per_min", 3)
    _, s1 = make_user(session_factory, Role.student, "student1")
    _, s2 = make_user(session_factory, Role.student, "student2")
    for _ in range(3):
        assert client.post("/student/rooms/join", json={"join_code": "WRONG1"}, headers=s1).status_code == 404
    blocked = client.post("/student/rooms/join", json={"join_code": "WRONG1"}, headers=s1)
    assert blocked.status_code == 429 and "Retry-After" in blocked.headers
    assert client.post("/student/rooms/join", json={"join_code": "WRONG1"}, headers=s2).status_code == 404


def test_parent_link_is_rate_limited(client, session_factory, monkeypatch):
    monkeypatch.setattr(settings, "rate_parent_link_per_min", 2)
    _, ph = make_user(session_factory, Role.parent, "parent1")
    for _ in range(2):
        assert client.post("/parent/link", json={"link_code": "NOPE0000"}, headers=ph).status_code == 404
    assert client.post("/parent/link", json={"link_code": "NOPE0000"}, headers=ph).status_code == 429


def test_costly_upload_steps_are_rate_limited(client, session_factory, monkeypatch):
    monkeypatch.setattr(settings, "rate_front_pages_per_hour", 2)
    monkeypatch.setattr(settings, "rate_whole_book_plan_per_hour", 1)
    _, th = make_user(session_factory, Role.teacher, "teachera")
    assert post_front(client, th).status_code == 201 and post_front(client, th).status_code == 201
    assert post_front(client, th).status_code == 429
    book = new_book(client, th)
    assert plan(client, th, book["id"], _text_pdf(*TEXTS)).status_code == 201
    assert plan(client, th, book["id"], _text_pdf(*TEXTS)).status_code == 429


# ---- needs_review ------------------------------------------------------------------------------------

LONG = " ".join(f"word{i}" for i in range(60))


def test_long_page_without_concepts_is_flagged_for_review_and_reported(client, session_factory, monkeypatch):
    class OnlyEmptyForBlankPage(CountingLLM):
        def complete_json(self, system, user):
            self.calls += 1
            if "word0" in user:  # the long scan: the model found nothing
                return '{"concepts": []}'
            return '{"concepts":[{"name":"Matter","description":"d","learning_objectives":[],"prerequisites":[]}]}'

    use_llm(monkeypatch, OnlyEmptyForBlankPage())
    _, th = make_user(session_factory, Role.teacher, "teachera")
    book = new_book(client, th)
    ch = new_chapter(client, th, book["id"])
    assert upload(client, th, book["id"], ch, _text_pdf(LONG, "a short page about matter and nothing else here")).status_code == 202

    pages = client.get(f"/teacher/books/{book['id']}/chapters/{ch}/pages", headers=th).json()
    long_page, short_page = pages
    assert long_page["needs_review"] is True and "no concepts" in long_page["review_note"].lower()
    assert short_page["needs_review"] is False and short_page["review_note"] is None and short_page["concepts"]
    report = client.get(f"/teacher/books/{book['id']}/chapters/{ch}/graph", headers=th).json()["report"]
    assert [r["page"] for r in report["review_pages"]] == [1] and report["concepts"] == 1  # graph facts survive


def test_short_page_with_no_concepts_is_not_flagged(session_factory):
    class Empty(CountingLLM):
        def complete_json(self, system, user):
            return '{"concepts": []}'

    with session_factory() as db:
        book = Book(board="B", class_name="9", subject="S", publisher="P", is_reference=True)
        db.add(book)
        db.flush()
        ch = Chapter(book_id=book.id, title="C", sequence_num=1)
        db.add(ch)
        db.flush()
        pages = PipelineOrchestrator(db, llm_provider=Empty()).process_chapter_file(ch, _text_pdf("Contents page"), "pdf", None)
        assert pages[0].needs_review is False and ch.graph_report["review_pages"] == []


# ---- draft cleanup -----------------------------------------------------------------------------------

def stored(data: bytes) -> str:
    return save_by_hash(data, sha256_hex(data), "pdf")


def test_cleanup_removes_only_old_drafts_and_unreferenced_files(session_factory):
    old_time = datetime.now(timezone.utc) - timedelta(days=10)
    with session_factory() as db:
        teacher = User(supertokens_user_id="st-t", name="T", username="tt", phone="1", role=Role.teacher)
        db.add(teacher)
        db.flush()
        book = Book(board="B", class_name="9", subject="S", publisher="P", owner_teacher_id=teacher.id)
        db.add(book)
        db.flush()
        chapter = Chapter(book_id=book.id, title="C", sequence_num=1)
        db.add(chapter)

        orphan_file, shared_file, fresh_file = stored(b"%PDF-1.4 orphan"), stored(b"%PDF-1.4 shared"), stored(b"%PDF-1.4 fresh")
        chapter.source_file = shared_file  # a chapter still uses this file
        mk = lambda path, when: UploadDraft(teacher_id=teacher.id, kind="front_pages", source_file=path,
                                            source_sha256="0" * 64, page_count=1, created_at=when)
        db.add_all([mk(orphan_file, old_time), mk(shared_file, old_time), mk(fresh_file, datetime.now(timezone.utc))])
        db.commit()

        assert cleanup(db, older_than_days=7) == (2, 1)
        assert [d.source_file for d in db.scalars(select(UploadDraft))] == [fresh_file]
        with pytest.raises(FileNotFoundError):
            read_file(orphan_file)
        assert read_file(shared_file) and read_file(fresh_file)  # still there
        assert cleanup(db, older_than_days=7) == (0, 0)


# ---- reference corpus ingest ----------------------------------------------------------------------------

META = dict(board="CBSE", class_name="Class 9", subject="Science", publisher="NCERT", edition="2025")


def test_parse_ranges():
    r = parse_ranges("Matter in Our Surroundings: A:1-12, Atoms:13-30,Single:31")
    assert [(x.title, x.start_page, x.end_page) for x in r] == [
        ("Matter in Our Surroundings: A", 1, 12), ("Atoms", 13, 30), ("Single", 31, 31)]


def test_ingest_builds_a_public_read_only_reference_book_from_bookmarks(client, session_factory):
    pdf = pdf_with_outline(TEXTS, [("Matter", 0), ("Atoms", 3)])
    book_id, results = ingest(session_factory, pdf, **META, allow_fake=True)
    assert results == ["ok     Matter", "ok     Atoms"]

    with session_factory() as db:
        book = db.get(Book, uuid.UUID(book_id))
        assert book.is_reference and book.owner_teacher_id is None and book.edition == "2025"
        chapters = db.scalars(select(Chapter).where(Chapter.book_id == book.id).order_by(Chapter.sequence_num)).all()
        assert [(c.title, c.status) for c in chapters] == [("Matter", "ready"), ("Atoms", "ready")]
        assert [len(c.pages) for c in chapters] == [3, 3]
        assert all(c.graph_report and c.match_report for c in chapters)

    _, th = make_user(session_factory, Role.teacher, "teachera")
    _, sh = make_user(session_factory, Role.student, "student1")
    assert book_id in [b["id"] for b in client.get("/teacher/books?scope=reference", headers=th).json()]
    assert client.post(f"/teacher/books/{book_id}/chapters", json={"title": "x", "sequence_num": 9}, headers=th).status_code == 403
    assert client.post(f"/student/books/{book_id}/link", headers=sh).status_code == 200
    first_chapter = client.get(f"/student/books/{book_id}", headers=sh).json()["chapters"][0]["id"]
    assert client.get(f"/student/books/{book_id}/chapters/{first_chapter}/graph", headers=sh).status_code == 200


def test_ingest_with_explicit_ranges_refuses_duplicates_and_reports_failures(session_factory, monkeypatch):
    pdf = _text_pdf(*TEXTS)
    book_id, results = ingest(session_factory, pdf, ranges=parse_ranges("All:1-6"), **META, allow_fake=True)
    assert results == ["ok     All"]
    with pytest.raises(SystemExit, match="already exists"):
        ingest(session_factory, pdf, ranges=parse_ranges("All:1-6"), **META, allow_fake=True)

    use_llm(monkeypatch, BrokenLLM())
    _, results = ingest(session_factory, _text_pdf(*TEXTS), ranges=parse_ranges("Bad:1-2"), **{**META, "edition": "other"}, allow_fake=True)
    assert results[0].startswith("FAILED Bad: ") and "secret" not in results[0]


def test_ingest_rejects_a_pdf_without_chapters_or_with_bad_ranges(session_factory):
    from fastapi import HTTPException
    with pytest.raises(HTTPException):
        ingest(session_factory, _text_pdf(*TEXTS), **META, allow_fake=True)  # no bookmarks and no --chapters
    with pytest.raises(HTTPException):
        ingest(session_factory, _text_pdf(*TEXTS), ranges=parse_ranges("X:1-99"), **META, allow_fake=True)
    with session_factory() as db:
        assert db.scalars(select(Book)).all() == []  # nothing created on rejection


# ---- ingest: chapter-by-chapter into ONE reference book (NCERT ships one PDF per chapter) ---------------

def chapters_of(session_factory, book_id):
    with session_factory() as db:
        rows = db.scalars(select(Chapter).where(Chapter.book_id == uuid.UUID(book_id)).order_by(Chapter.sequence_num)).all()
        return [(c.sequence_num, c.title, c.status) for c in rows]


def test_ingest_append_adds_chapters_to_the_same_reference_book(session_factory):
    book_id, _ = ingest(session_factory, _text_pdf(*TEXTS[:3]), ranges=parse_ranges("Matter:1-3"), **META, allow_fake=True)
    again, results = ingest(session_factory, _text_pdf(*TEXTS[3:]), ranges=parse_ranges("Atoms:1-3"), append=True, **META, allow_fake=True)
    assert again == book_id and results == ["ok     Atoms"]
    third, _ = ingest(session_factory, _text_pdf(*TEXTS), ranges=parse_ranges("Energy:1-6"), append=True, first_number=9, **META, allow_fake=True)
    assert third == book_id
    assert chapters_of(session_factory, book_id) == [(1, "Matter", "ready"), (2, "Atoms", "ready"), (9, "Energy", "ready")]
    with session_factory() as db:
        assert len(db.scalars(select(Book).where(Book.is_reference.is_(True))).all()) == 1


def test_ingest_append_refuses_clashes_and_changes_nothing(session_factory):
    book_id, _ = ingest(session_factory, _text_pdf(*TEXTS), ranges=parse_ranges("Matter:1-6"), **META, allow_fake=True)
    with pytest.raises(SystemExit, match="--append"):
        ingest(session_factory, _text_pdf(*TEXTS), ranges=parse_ranges("Atoms:1-6"), **META, allow_fake=True)
    with pytest.raises(SystemExit, match="already has a chapter called 'matter'"):
        ingest(session_factory, _text_pdf(*TEXTS), ranges=parse_ranges("matter:1-6"), append=True, **META, allow_fake=True)
    with pytest.raises(SystemExit, match="chapter number 1"):
        ingest(session_factory, _text_pdf(*TEXTS), ranges=parse_ranges("Atoms:1-6"), append=True, first_number=1, **META, allow_fake=True)
    assert chapters_of(session_factory, book_id) == [(1, "Matter", "ready")]


def test_ingest_append_creates_the_book_when_it_does_not_exist_yet(session_factory):
    book_id, results = ingest(session_factory, _text_pdf(*TEXTS), ranges=parse_ranges("Matter:1-6"), append=True, first_number=3, **META, allow_fake=True)
    assert results == ["ok     Matter"] and chapters_of(session_factory, book_id) == [(3, "Matter", "ready")]


# ---- show_graph -----------------------------------------------------------------------------------------

def test_show_graph_renders_report_concepts_and_dependencies(session_factory):
    from app.db.show_graph import render_book
    book_id, _ = ingest(session_factory, _text_pdf("alpha idea", "beta idea", "gamma idea"), ranges=parse_ranges("Ideas:1-3"), **META, allow_fake=True)
    with session_factory() as db:
        text = render_book(db, uuid.UUID(book_id))
        assert "NCERT" in text and "[official]" in text and "== Chapter 1: Ideas  [ready]" in text
        assert "concepts=3  edges=2" in text and "llm_linking=done" in text
        assert "- beta idea" in text and "needs: alpha idea (llm)" in text
        assert "== Chapter 1" not in render_book(db, uuid.UUID(book_id), chapter_number=2)
        assert render_book(db, uuid.uuid4()) == "Book not found."


# ---- the fake LLM must never pass for real extraction -----------------------------------------------------

from app.llm.fake_provider import FakeLLMProvider  # noqa: E402

PAGE = " ".join(f"cell{i}" for i in range(40))


def process(db, chapter_id, llm, pdf):
    ch = db.get(Chapter, chapter_id)
    PipelineOrchestrator(db, llm_provider=llm).process_chapter_file(ch, pdf, "pdf", None)
    db.commit()
    return ch


def make_two_chapters(db):
    book = Book(board="B", class_name="9", subject="S", publisher="P", is_reference=True)
    db.add(book)
    db.flush()
    chapters = [Chapter(book_id=book.id, title=f"C{i}", sequence_num=i) for i in (1, 2)]
    db.add_all(chapters)
    db.commit()
    return [c.id for c in chapters]


def test_graph_report_and_pages_record_which_model_made_the_concepts(session_factory):
    with session_factory() as db:
        [c1, _] = make_two_chapters(db)
        ch = process(db, c1, FakeLLMProvider(), _text_pdf(PAGE))
        assert ch.graph_report["model"] == "fake" and {p.concepts_model for p in ch.pages} == {"fake"}


def test_placeholder_concepts_are_never_reused_by_a_real_model(session_factory):
    pdf = _text_pdf(PAGE)
    with session_factory() as db:
        [c1, c2] = make_two_chapters(db)
        process(db, c1, FakeLLMProvider(), pdf)
        real = CountingLLM()
        ch2 = process(db, c2, real, pdf)
        assert real.calls == 1  # extracted for real instead of copying the placeholder
        assert [c.name for p in ch2.pages for c in p.concepts] == ["Matter"] and ch2.pages[0].concepts_model == "counting"


def test_real_concepts_are_still_reused_and_fake_reuses_fake_but_unknown_origin_is_not_trusted(session_factory):
    pdf = _text_pdf(PAGE)
    with session_factory() as db:
        [c1, c2] = make_two_chapters(db)
        real = CountingLLM()
        process(db, c1, real, pdf)
        process(db, c2, real, pdf)
        assert real.calls == 1  # second chapter reused the real concepts
    with session_factory() as db:
        [c1, c2] = make_two_chapters(db)
        fake_a, fake_b = FakeLLMProvider(), FakeLLMProvider()
        process(db, c1, fake_a, pdf)
        ch = process(db, c2, fake_b, pdf)
        assert ch.match_report["pages_reused"] == 1  # placeholder -> placeholder is fine in tests
    with session_factory() as db:
        [c1, c2] = make_two_chapters(db)
        process(db, c1, CountingLLM(), pdf)
        for page in db.scalars(select(Page)):
            page.concepts_model = None  # pages from before models were recorded
        db.commit()
        llm = CountingLLM()
        process(db, c2, llm, pdf)
        assert llm.calls == 1  # origin unknown: not reused


def test_ingest_and_reprocess_refuse_the_fake_llm_unless_told_otherwise(session_factory, monkeypatch):
    from app.db.reprocess import reprocess
    pdf = _text_pdf(*TEXTS)
    with pytest.raises(SystemExit, match="PLACEHOLDER"):
        ingest(session_factory, pdf, ranges=parse_ranges("All:1-6"), **META)
    with session_factory() as db:
        assert db.scalars(select(Book)).all() == []
    book_id, _ = ingest(session_factory, pdf, ranges=parse_ranges("All:1-6"), **META, allow_fake=True)
    with pytest.raises(SystemExit, match="PLACEHOLDER"):
        reprocess(session_factory, uuid.UUID(book_id))


def test_reprocess_replaces_placeholder_concepts_with_real_ones_from_the_stored_file(session_factory, monkeypatch):
    from app.db.reprocess import reprocess
    from app.db.show_graph import render_book
    book_id, _ = ingest(session_factory, _text_pdf("alpha idea", "beta idea"), ranges=parse_ranges("Ideas:1-2"), **META, allow_fake=True)
    with session_factory() as db:
        assert "PLACEHOLDER" in render_book(db, uuid.UUID(book_id)) and "model=fake" in render_book(db, uuid.UUID(book_id))

    monkeypatch.setattr(settings, "llm_provider", "openai_compat")  # what fixing .env does
    monkeypatch.setattr("app.pipeline.orchestrator.get_llm_provider", lambda: CountingLLM())
    assert reprocess(session_factory, uuid.UUID(book_id)) == ["ok     Ideas"]
    with session_factory() as db:
        text = render_book(db, uuid.UUID(book_id))
        assert "PLACEHOLDER" not in text and "model=counting" in text and "- Matter" in text and "alpha idea" not in text
        assert reprocess(session_factory, uuid.UUID(book_id), chapter_number=7) == []  # no such chapter: nothing to do
</file>

<file path="backend/tests/test_step9.py">
"""Step 9: embeddings (durable copy in PostgreSQL) and the Memgraph copy of the concept graph.

Memgraph itself is not available in the test run: the store is exercised with the in-memory fake (same
behaviour contract) and the Memgraph client with a stub driver that records what it would send.
`python -m app.db.smoke_memgraph` is the real-server check."""
import uuid

import pytest
from sqlalchemy import select

from app.core.config import FAKE_EMBEDDING_MODEL, settings
from app.db import smoke_memgraph
from app.db.sync_graph import sync_all
from app.embeddings import EmbeddingError, get_embedding_provider
from app.embeddings.fake_provider import FakeEmbeddingProvider
from app.embeddings.openai_compat_provider import OpenAICompatEmbeddingProvider
from app.embeddings.vectors import cosine, from_bytes, to_bytes
from app.graph_store import FAKE_STORE, get_graph_store
from app.graph_store.base import ChapterGraph, ConceptNode, EdgeRow, GraphStoreError, PageNode
from app.graph_store.fake_store import FakeGraphStore
from app.graph_store.memgraph_store import CONCEPT_INDEX, PAGE_INDEX, MemgraphStore
from app.models import Book, Chapter, ChapterStatus, Concept, ConceptEdge, ContentEmbedding, IndexStatus, Page
from app.pipeline.indexing import build_chapter_payload, chapters_needing_index, embed_chapter, index_chapter
from app.pipeline.jobs import mark_processing
from tests.test_chapter_jobs import chapter_status, setup_chapter, upload
from tests.test_pipeline import _text_pdf


def words(tag: str, n: int = 20) -> str:
    """A page of n distinct words (>= 15 so it counts as a real page)."""
    return " ".join(f"{tag}{i}" for i in range(n))


class SharedProvider(FakeEmbeddingProvider):
    """One provider object for the whole test, so calls can be counted across the background job."""


@pytest.fixture()
def provider(monkeypatch, indexing_on):
    p = SharedProvider(settings.embedding_dim)
    monkeypatch.setattr("app.pipeline.indexing.get_embedding_provider", lambda: p)
    return p


def upload_ready(client, session_factory, *texts, tag="teachera"):
    th, book_id, ch = setup_chapter(client, session_factory, tag)
    assert upload(client, th, book_id, ch, _text_pdf(*texts)).status_code == 202
    assert chapter_status(client, th, book_id, ch)["status"] == "ready"
    return th, book_id, ch


def chapter_row(session_factory, ch) -> Chapter:
    with session_factory() as db:
        c = db.get(Chapter, uuid.UUID(str(ch)))
        db.expunge(c)
        return c


def embedding_rows(session_factory, ch):
    with session_factory() as db:
        return db.scalars(select(ContentEmbedding).where(ContentEmbedding.chapter_id == uuid.UUID(str(ch)))).all()


# ---- vectors and the fake provider ----------------------------------------------------------------

def test_vector_bytes_roundtrip_and_cosine():
    v = [0.5, -0.25, 1.0]
    assert from_bytes(to_bytes(v)) == pytest.approx(v)
    assert cosine([1, 0], [1, 0]) == pytest.approx(1.0)
    assert cosine([1, 0], [0, 1]) == pytest.approx(0.0)
    assert cosine([0, 0], [1, 0]) == 0.0


def test_fake_embeddings_are_deterministic_unit_length_and_reflect_shared_words():
    p = FakeEmbeddingProvider(128)
    a, b, c = p.embed(["the cell membrane controls what enters the cell", "the cell membrane controls entry", "volcanic rock formation in mountains"])
    assert p.embed(["the cell membrane controls what enters the cell"])[0] == a
    assert len(a) == 128 and cosine(a, a) == pytest.approx(1.0)
    assert cosine(a, b) > cosine(a, c) + 0.2
    assert p.model_name == FAKE_EMBEDDING_MODEL


# ---- the pipeline stage ---------------------------------------------------------------------------

def test_upload_embeds_concepts_and_pages_and_writes_the_graph_copy(client, session_factory, provider):
    th, book_id, ch = upload_ready(client, session_factory, words("alpha"), words("beta"))
    row = chapter_row(session_factory, ch)
    assert (row.embedding_status, row.graph_sync_status) == ("done", "done")
    assert row.index_error is None and row.indexed_at is not None

    with session_factory() as db:
        canonical = db.scalars(select(Concept).join(Page).where(Page.chapter_id == row.id, Concept.is_canonical.is_(True))).all()
        pages = db.scalars(select(Page).where(Page.chapter_id == row.id)).all()
        edges = db.scalars(select(ConceptEdge).where(ConceptEdge.chapter_id == row.id)).all()
        rows = db.scalars(select(ContentEmbedding).where(ContentEmbedding.chapter_id == row.id)).all()
        assert len(rows) == len(canonical) + len(pages)
        assert {r.model for r in rows} == {FAKE_EMBEDDING_MODEL} and {r.dim for r in rows} == {settings.embedding_dim}

        graph = FAKE_STORE.chapter(str(row.id))
        assert graph is not None and graph.book_id == book_id
        assert {c.id for c in graph.concepts} == {str(c.id) for c in canonical}
        assert {(e.concept_id, e.prerequisite_id, e.source) for e in graph.edges} == {
            (str(e.concept_id), str(e.prerequisite_id), e.source) for e in edges}
        assert all(c.embedding is not None for c in graph.concepts) and all(p.embedding is not None for p in graph.pages)
        # derived data only: the page TEXT never travels to the graph store (concept names are short extracts)
        assert words("alpha") not in repr(graph) and words("beta") not in repr(graph)
        assert all(not hasattr(p, "content_text") and not hasattr(p, "text") for p in graph.pages)


def test_short_pages_are_not_embedded_but_stay_in_the_graph(client, session_factory, provider):
    _, _, ch = upload_ready(client, session_factory, words("long"), "Cover page")
    with session_factory() as db:
        pages = {p.page_number: p for p in db.scalars(select(Page).where(Page.chapter_id == uuid.UUID(ch)))}
        assert pages[1].embedding is not None and pages[2].embedding is None
    graph = FAKE_STORE.chapter(ch)
    assert [p.embedding is not None for p in graph.pages] == [True, False]


def test_reprocessing_replaces_vectors_and_the_graph_copy(client, session_factory, provider):
    th, book_id, ch = upload_ready(client, session_factory, words("one"), words("two"))
    first_pages = {p.id for p in FAKE_STORE.chapter(ch).pages}
    assert upload(client, th, book_id, ch, _text_pdf(words("three"))).status_code == 202
    graph = FAKE_STORE.chapter(ch)
    assert len(graph.pages) == 1 and graph.pages[0].id not in first_pages
    with session_factory() as db:
        page_ids = {p.id for p in db.scalars(select(Page).where(Page.chapter_id == uuid.UUID(ch)))}
        assert {r.page_id for r in embedding_rows(session_factory, ch) if r.page_id} == page_ids  # old vectors are gone


def test_unchanged_chapter_is_not_embedded_again(client, session_factory, provider):
    _, _, ch = upload_ready(client, session_factory, words("same"))
    calls = provider.texts_embedded
    report = index_chapter(session_factory, uuid.UUID(ch))
    assert provider.texts_embedded == calls and report.embedded == 0 and report.kept > 0 and not report.errors


def test_identical_text_in_another_chapter_reuses_the_vector_without_a_call(client, session_factory, provider):
    upload_ready(client, session_factory, words("shared"), tag="teachera")
    calls = provider.texts_embedded
    upload_ready(client, session_factory, words("shared"), tag="teacherb")  # same text, other teacher
    assert provider.texts_embedded == calls
    assert len(embedding_rows(session_factory, FAKE_STORE.list_chapter_ids().pop())) > 0


def test_changing_the_embedding_model_re_embeds_everything(client, session_factory, provider):
    _, _, ch = upload_ready(client, session_factory, words("model"))
    before = len(embedding_rows(session_factory, ch))
    provider.model_name = "another-model"
    report = index_chapter(session_factory, uuid.UUID(ch))
    assert report.embedded == before and report.kept == 0
    assert {r.model for r in embedding_rows(session_factory, ch)} == {"another-model"}


def test_only_canonical_concepts_get_a_vector_and_stale_rows_are_removed(session_factory, provider):
    with session_factory() as db:
        book = Book(board="CBSE", class_name="9", subject="Sci", publisher="T", is_reference=True)
        db.add(book)
        db.flush()
        ch = Chapter(book_id=book.id, title="Ch", sequence_num=1, status=ChapterStatus.READY)
        db.add(ch)
        db.flush()
        p1 = Page(chapter_id=ch.id, page_number=1, content_text=words("a"))
        p2 = Page(chapter_id=ch.id, page_number=2, content_text=words("b"))
        db.add_all([p1, p2])
        db.flush()
        c1 = Concept(page_id=p1.id, name="Atom", description="d", position=0, name_key="atom", is_canonical=True)
        c2 = Concept(page_id=p2.id, name="atom", description="d2", position=0, name_key="atom", is_canonical=False)
        db.add_all([c1, c2])
        db.flush()
        embed_chapter(db, ch, provider)
        db.commit()
        concept_rows = db.scalars(select(ContentEmbedding).where(ContentEmbedding.concept_id.is_not(None))).all()
        assert [r.concept_id for r in concept_rows] == [c1.id]
        c1.is_canonical, c2.is_canonical = False, True  # identity changed (e.g. relink)
        db.flush()
        report = embed_chapter(db, ch, provider)
        db.commit()
        assert report.removed == 1
        assert [r.concept_id for r in db.scalars(select(ContentEmbedding).where(ContentEmbedding.concept_id.is_not(None)))] == [c2.id]


# ---- failures never fail the chapter ---------------------------------------------------------------

class DownProvider(FakeEmbeddingProvider):
    def embed(self, texts):
        raise EmbeddingError("secret-endpoint https://x.openai.azure.com key=hunter2")


def test_embedding_outage_keeps_the_chapter_ready_and_a_retry_completes_it(client, session_factory, indexing_on, monkeypatch):
    monkeypatch.setattr("app.pipeline.indexing.get_embedding_provider", lambda: DownProvider(settings.embedding_dim))
    th, book_id, ch = upload_ready(client, session_factory, words("down"))
    row = chapter_row(session_factory, ch)
    assert row.status == "ready"
    assert (row.embedding_status, row.graph_sync_status) == ("failed", "pending")
    assert "hunter2" not in row.index_error and "secret" not in row.index_error
    assert FAKE_STORE.chapter(ch) is None and embedding_rows(session_factory, ch) == []

    good = FakeEmbeddingProvider(settings.embedding_dim)
    monkeypatch.setattr("app.pipeline.indexing.get_embedding_provider", lambda: good)
    lines = sync_all(session_factory, allow_fake=True)
    assert not any(line == "!FAILED" for line in lines)
    row = chapter_row(session_factory, ch)
    assert (row.embedding_status, row.graph_sync_status, row.index_error) == ("done", "done", None)
    assert FAKE_STORE.chapter(ch) is not None


def test_graph_store_outage_keeps_the_chapter_ready_and_retry_does_not_re_embed(client, session_factory, provider):
    FAKE_STORE.fail_with = RuntimeError("bolt://secret-host:7687 refused")
    th, book_id, ch = upload_ready(client, session_factory, words("graph"))
    row = chapter_row(session_factory, ch)
    assert row.status == "ready" and (row.embedding_status, row.graph_sync_status) == ("done", "failed")
    assert "secret-host" not in row.index_error
    assert chapter_status(client, th, book_id, ch)["status"] == "ready"  # students/teacher see no difference

    FAKE_STORE.fail_with = None
    calls = provider.texts_embedded
    sync_all(session_factory, allow_fake=True)
    assert provider.texts_embedded == calls
    row = chapter_row(session_factory, ch)
    assert (row.graph_sync_status, row.index_error) == ("done", None) and FAKE_STORE.chapter(ch) is not None


def test_misconfigured_embeddings_are_recorded_not_raised(client, session_factory, monkeypatch, indexing_on):
    monkeypatch.setattr(settings, "embedding_provider", "openai_compat")
    monkeypatch.setattr(settings, "embedding_api_key", "")
    monkeypatch.setattr(settings, "llm_api_key", "")
    _, _, ch = upload_ready(client, session_factory, words("cfg"))
    row = chapter_row(session_factory, ch)
    assert row.status == "ready" and row.embedding_status == "failed" and "EMBEDDING_MODEL" in row.index_error


def test_with_everything_switched_off_both_stages_are_skipped(client, session_factory):
    _, _, ch = upload_ready(client, session_factory, words("off"))
    row = chapter_row(session_factory, ch)
    assert (row.embedding_status, row.graph_sync_status) == ("skipped", "skipped")
    assert embedding_rows(session_factory, ch) == []


def test_mark_processing_resets_the_derived_state():
    ch = Chapter(embedding_status="done", graph_sync_status="done", index_error="x")
    mark_processing(ch)
    assert (ch.embedding_status, ch.graph_sync_status, ch.index_error) == ("pending", "pending", None)


# ---- sync_graph ------------------------------------------------------------------------------------

def test_rebuild_restores_the_graph_copy_from_stored_vectors_without_embedding_calls(client, session_factory, provider, monkeypatch):
    _, _, ch = upload_ready(client, session_factory, words("r1"), words("r2"))
    before = FAKE_STORE.chapter(ch)
    FAKE_STORE.clear()
    monkeypatch.setattr("app.pipeline.indexing.get_embedding_provider", lambda: pytest.fail("the embedding service was called"))
    calls = provider.calls
    lines = sync_all(session_factory, rebuild=True, allow_fake=True)
    after = FAKE_STORE.chapter(ch)
    assert provider.calls == calls and after is not None
    assert [c.id for c in after.concepts] == [c.id for c in before.concepts]
    assert all(a.embedding == pytest.approx(b.embedding) for a, b in zip(after.concepts, before.concepts))
    assert all(a.embedding == pytest.approx(b.embedding) for a, b in zip(after.pages, before.pages) if b.embedding)
    assert any("graph store now holds" in line for line in lines)


def test_default_sync_only_touches_chapters_that_need_it(client, session_factory, provider):
    upload_ready(client, session_factory, words("done"))
    with session_factory() as db:
        assert chapters_needing_index(db) == []
    lines = sync_all(session_factory, allow_fake=True)
    assert "0 chapter(s) processed" in "\n".join(lines)


def test_prune_removes_graph_chapters_postgres_no_longer_has_as_ready(client, session_factory, provider):
    _, _, ch = upload_ready(client, session_factory, words("keep"))
    ghost = ChapterGraph(book_id=str(uuid.uuid4()), chapter_id=str(uuid.uuid4()), title="gone", sequence_num=1,
                         is_reference=True, owner_teacher_id=None, embedding_model=None)
    FAKE_STORE.replace_chapter(ghost)
    lines = sync_all(session_factory, prune=True, allow_fake=True)
    assert FAKE_STORE.list_chapter_ids() == {ch} and any("pruned 1" in line for line in lines)


def test_sync_refuses_placeholder_vectors_unless_allowed(session_factory, indexing_on):
    with pytest.raises(SystemExit, match="PLACEHOLDER"):
        sync_all(session_factory)
    sync_all(session_factory, allow_fake=True)


def test_placeholder_vectors_never_reach_a_real_store(client, session_factory, provider, monkeypatch):
    _, _, ch = upload_ready(client, session_factory, words("fk"))
    monkeypatch.setattr(settings, "embedding_provider", "none")  # i.e. a real deployment now
    with session_factory() as db:
        payload = build_chapter_payload(db, db.get(Chapter, uuid.UUID(ch)))
    assert all(n.embedding is None for n in [*payload.pages, *payload.concepts])
    monkeypatch.setattr(settings, "embedding_provider", "fake")
    with session_factory() as db:
        payload = build_chapter_payload(db, db.get(Chapter, uuid.UUID(ch)))
    assert all(n.embedding is not None for n in payload.concepts)


def test_vectors_of_the_wrong_size_are_not_indexed(client, session_factory, provider, monkeypatch):
    _, _, ch = upload_ready(client, session_factory, words("dim"))
    monkeypatch.setattr(settings, "embedding_dim", 128)
    with session_factory() as db:
        payload = build_chapter_payload(db, db.get(Chapter, uuid.UUID(ch)))
    assert all(n.embedding is None for n in [*payload.pages, *payload.concepts])


# ---- graph store contract (fake) --------------------------------------------------------------------

def test_smoke_checks_pass_on_the_in_memory_store():
    smoke_memgraph.results.clear()
    made: list[str] = []
    smoke_memgraph.run_store_checks(FakeGraphStore(), 96, made)
    assert smoke_memgraph.results and all(smoke_memgraph.results)


def test_search_only_sees_the_given_books():
    store = FakeGraphStore()
    mine, theirs = str(uuid.uuid4()), str(uuid.uuid4())
    for book, name in ((mine, "mine"), (theirs, "theirs")):
        store.replace_chapter(ChapterGraph(
            book_id=book, chapter_id=str(uuid.uuid4()), title="c", sequence_num=1, is_reference=False, owner_teacher_id=None,
            embedding_model="m", concepts=[ConceptNode(str(uuid.uuid4()), name, "", 0, [1.0, 0.0])],
            pages=[PageNode(str(uuid.uuid4()), 1, [1.0, 0.0])]))
    assert [h.name for h in store.search_concepts([1.0, 0.0], [mine], k=5)] == ["mine"]
    assert store.search_concepts([1.0, 0.0], [], k=5) == [] and store.search_pages([1.0, 0.0], [], k=5) == []
    assert {h.book_id for h in store.search_pages([1.0, 0.0], [mine, theirs], k=5)} == {mine, theirs}


# ---- the Memgraph client against a stub driver --------------------------------------------------------

class StubRecord:
    def __init__(self, row):
        self._row = row

    def data(self):
        return self._row


class StubResult:
    def __init__(self, rows=()):
        self.rows = list(rows)

    def consume(self):
        return None

    def data(self):
        return self.rows

    def __iter__(self):
        return iter(StubRecord(r) for r in self.rows)


class StubDriver:
    """Records every statement; `script(query, params)` returns the rows to answer with (or raises)."""

    def __init__(self, script=None):
        self.log: list[tuple[str, dict]] = []
        self.writes = self.reads = 0
        self.script = script or (lambda q, p: [])
        self.closed = False

    def _run(self, query, **params):
        self.log.append((query, params))
        return StubResult(self.script(query, params))

    def session(self):
        driver = self

        class Session:
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def run(self, statement, **params):
                return driver._run(statement, **params)

            def execute_write(self, fn):
                driver.writes += 1
                return fn(type("Tx", (), {"run": staticmethod(driver._run)}))

            def execute_read(self, fn):
                driver.reads += 1
                return fn(type("Tx", (), {"run": staticmethod(driver._run)}))

        return Session()

    def close(self):
        self.closed = True


def store_with(driver, **kw):
    return MemgraphStore("bolt://x", dim=4, driver=driver, **kw)


def sample_graph(n_concepts=3):
    concepts = [ConceptNode(str(uuid.uuid4()), f"c{i}", "d", i, [0.1] * 4) for i in range(n_concepts)]
    pages = [PageNode(str(uuid.uuid4()), 1, [0.2] * 4), PageNode(str(uuid.uuid4()), 2, None)]
    return ChapterGraph(
        book_id="B", chapter_id="CH", title="T", sequence_num=2, is_reference=True, owner_teacher_id=None, embedding_model="m",
        pages=pages, concepts=concepts, edges=[EdgeRow(concepts[1].id, concepts[0].id, "llm")],
        concept_pages=[(concepts[0].id, pages[0].id)],
    )


def test_ensure_schema_creates_label_and_vector_indexes_once():
    d = StubDriver()
    s = store_with(d, capacity=500, metric="cos")
    s.ensure_schema()
    s.ensure_schema()
    statements = [q for q, _ in d.log]
    assert sum(q.startswith("CREATE INDEX ON") for q in statements) == 5
    vector = [q for q in statements if q.startswith("CREATE VECTOR INDEX")]
    assert len(vector) == 2 and CONCEPT_INDEX in vector[0] and PAGE_INDEX in vector[1]
    assert '"dimension": 4' in vector[0] and '"capacity": 500' in vector[0] and '"metric": "cos"' in vector[0]
    assert statements.count("SHOW VECTOR INDEX INFO") == 1  # second call was a no-op


def test_ensure_schema_tolerates_existing_indexes_and_rejects_a_dimension_change():
    def exists(q, p):
        if q.startswith("CREATE"):
            raise RuntimeError("Index already exists")
        return [{"index_name": CONCEPT_INDEX, "dimension": 4}, {"index_name": PAGE_INDEX, "dimension": 4}]

    store_with(StubDriver(exists)).ensure_schema()

    def wrong(q, p):
        return [{"index_name": CONCEPT_INDEX, "dimension": 1536}] if q.startswith("SHOW") else []

    with pytest.raises(GraphStoreError, match="--rebuild"):
        store_with(StubDriver(wrong)).ensure_schema()


def test_replace_chapter_is_one_idempotent_transaction_with_no_page_text():
    d = StubDriver()
    s = store_with(d, batch=2)
    s.replace_chapter(sample_graph(5))
    assert d.writes == 1  # one transaction
    work = [(q, p) for q, p in d.log if not q.startswith(("CREATE INDEX", "CREATE VECTOR", "SHOW"))]
    assert all("DETACH DELETE" in q for q, _ in work[:3])  # starts by removing the chapter's old copy
    concept_batches = [p["rows"] for q, p in work if q.startswith("UNWIND $rows AS r CREATE (:Concept")]
    assert [len(b) for b in concept_batches] == [2, 2, 1]  # batched
    assert any("REQUIRES" in q for q, _ in work) and any("EXPLAINED_ON" in q for q, _ in work)
    page_rows = next(p["rows"] for q, p in work if ":Page {id: r.id" in q)
    assert page_rows[1]["embedding"] is None  # a page without a vector is still written
    assert "content_text" not in repr(d.log)


def test_every_search_is_filtered_by_book_and_widens_until_it_has_enough():
    seen = []

    def script(q, p):
        seen.append(p["limit"])
        return [] if p["limit"] < 500 else [{"id": "i", "name": "n", "description": None, "chapter_id": "c", "book_id": "B", "similarity": 0.9}]

    d = StubDriver(script)
    s = store_with(d, max_candidates=2000)
    hits = s.search_concepts([0.1] * 4, ["B", "B"], k=1)
    assert [h.name for h in hits] == [("n")] and hits[0].description == ""
    assert seen == [20, 80, 320, 1280]  # widened x4 until the window held one of this book's concepts
    query, params = d.log[0]
    assert "MATCH (node:Concept) WHERE id(node) = gid AND node.book_id IN $book_ids RETURN" in query  # the whole clause, nothing OR-ed in
    assert "node.book_id" not in query.split("MATCH (node:Concept)")[0]  # no property read on a raw hit (it may be a deleted node)
    assert params["book_ids"] == ["B"]
    d.log.clear()
    assert s.search_concepts([0.1] * 4, [], k=3) == [] and s.search_pages([0.1] * 4, [], k=3) == [] and d.log == []


def test_search_gives_up_at_the_ceiling():
    seen = []
    s = store_with(StubDriver(lambda q, p: seen.append(p["limit"]) or []), max_candidates=100)
    assert s.search_pages([0.1] * 4, ["B"], k=2) == [] and seen == [20, 80, 100]


def test_prerequisite_query_is_book_filtered_and_depth_is_bounded():
    d = StubDriver(lambda q, p: [{"id": "p", "name": "P", "depth": 1}])
    rows = store_with(d).prerequisites("c1", ["B"], max_depth=99)
    assert [(r.name, r.depth) for r in rows] == [("P", 1)]
    assert "c.book_id IN $book_ids" in d.log[0][0] and "*1..20" in d.log[0][0]
    assert store_with(StubDriver()).prerequisites("c1", []) == []


def test_driver_failures_become_graph_store_errors():
    def boom(q, p):
        raise ConnectionRefusedError("refused")

    with pytest.raises(GraphStoreError):
        store_with(StubDriver(boom)).replace_chapter(sample_graph())
    with pytest.raises(GraphStoreError):
        store_with(StubDriver(boom)).list_chapter_ids()


def test_unsafe_store_settings_are_rejected():
    with pytest.raises(ValueError):
        MemgraphStore("bolt://x", dim=4, metric='cos"} DROP')
    with pytest.raises(ValueError):
        MemgraphStore("bolt://x", dim=0)


# ---- providers and factories ---------------------------------------------------------------------------

class StubEmbeddingsClient:
    def __init__(self, dim=4, drop=0, fail=False):
        self.dim, self.drop, self.fail, self.calls = dim, drop, fail, []
        self.embeddings = self

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.fail:
            raise RuntimeError("401 key=hunter2")
        data = [type("D", (), {"index": i, "embedding": [float(i)] * self.dim}) for i in reversed(range(len(kwargs["input"]) - self.drop))]
        return type("R", (), {"data": data})


def test_openai_compat_embeddings_batch_keep_order_and_validate():
    client = StubEmbeddingsClient()
    p = OpenAICompatEmbeddingProvider("", "k", "dep", 4, batch_size=2, client=client)
    vectors = p.embed(["a", "b", "c", "d", "e"])
    assert [len(c["input"]) for c in client.calls] == [2, 2, 1] and all("dimensions" not in c for c in client.calls)
    assert vectors[0] == [0.0] * 4 and vectors[1] == [1.0] * 4  # sorted back into request order within a batch
    with_dims = StubEmbeddingsClient()
    OpenAICompatEmbeddingProvider("", "k", "dep", 4, send_dimensions=True, client=with_dims).embed(["a"])
    assert with_dims.calls[0]["dimensions"] == 4
    with pytest.raises(EmbeddingError, match="EMBEDDING_DIM"):
        OpenAICompatEmbeddingProvider("", "k", "dep", 8, client=StubEmbeddingsClient(dim=4)).embed(["a"])
    with pytest.raises(EmbeddingError, match="got 1"):
        OpenAICompatEmbeddingProvider("", "k", "dep", 4, client=StubEmbeddingsClient(drop=1)).embed(["a", "b"])
    with pytest.raises(EmbeddingError) as err:
        OpenAICompatEmbeddingProvider("", "k", "dep", 4, client=StubEmbeddingsClient(fail=True)).embed(["a"])
    assert "hunter2" not in str(err.value)


def test_embedding_provider_factory(monkeypatch):
    assert get_embedding_provider() is None  # "none" is the default under tests
    monkeypatch.setattr(settings, "embedding_provider", "fake")
    assert get_embedding_provider().model_name == FAKE_EMBEDDING_MODEL
    monkeypatch.setattr(settings, "embedding_provider", "openai_compat")
    monkeypatch.setattr(settings, "embedding_api_key", "")
    monkeypatch.setattr(settings, "llm_api_key", "")
    with pytest.raises(RuntimeError, match="EMBEDDING_MODEL"):
        get_embedding_provider()
    captured = {}

    class Capture:
        def __init__(self, base_url, api_key, model, dim, **kw):
            captured.update(base_url=base_url, api_key=api_key, model=model, dim=dim)

    monkeypatch.setattr("app.embeddings.openai_compat_provider.OpenAICompatEmbeddingProvider", Capture)
    monkeypatch.setattr(settings, "embedding_base_url", "")  # a real .env may set EMBEDDING_BASE_URL; test the blank fallback
    monkeypatch.setattr(settings, "llm_api_key", "llm-key")
    monkeypatch.setattr(settings, "llm_base_url", "https://res.openai.azure.com/openai/v1/")
    monkeypatch.setattr(settings, "embedding_model", "emb-deployment")
    get_embedding_provider()  # blank EMBEDDING_* falls back to the LLM resource
    assert captured == {"base_url": "https://res.openai.azure.com/openai/v1/", "api_key": "llm-key", "model": "emb-deployment", "dim": settings.embedding_dim}


def test_graph_store_factory(monkeypatch):
    assert get_graph_store() is None
    monkeypatch.setattr(settings, "graph_store_provider", "fake")
    assert get_graph_store() is FAKE_STORE
    monkeypatch.setattr(settings, "graph_store_provider", "memgraph")
    first = get_graph_store()
    assert isinstance(first, MemgraphStore) and get_graph_store() is first and first.dim == settings.embedding_dim


def test_stages_skipped_while_switched_off_are_done_once_switched_on(client, session_factory, monkeypatch, indexing_on):
    monkeypatch.setattr(settings, "embedding_provider", "none")
    monkeypatch.setattr(settings, "graph_store_provider", "none")
    _, _, ch = upload_ready(client, session_factory, words("late"))
    assert (chapter_row(session_factory, ch).embedding_status, chapter_row(session_factory, ch).graph_sync_status) == ("skipped", "skipped")
    with session_factory() as db:
        assert chapters_needing_index(db) == []  # nothing to do while both stay off
    monkeypatch.setattr(settings, "embedding_provider", "fake")
    monkeypatch.setattr(settings, "graph_store_provider", "fake")
    sync_all(session_factory, allow_fake=True)
    row = chapter_row(session_factory, ch)
    assert (row.embedding_status, row.graph_sync_status) == ("done", "done") and FAKE_STORE.chapter(ch) is not None
</file>

<file path="backend/.env.example">
ENV=dev
# Matches docker-compose.yml (host port 5434)
DATABASE_URL=postgresql+psycopg://postgres:Postgre21@localhost:5434/tuition
SUPERTOKENS_CONNECTION_URI=http://localhost:3567
SUPERTOKENS_API_KEY=
APP_NAME=Tuition Companion
API_DOMAIN=http://localhost:8000
WEBSITE_DOMAIN=http://localhost:5173
CORS_ORIGINS=http://localhost:5173

STORAGE_DIR=storage
MAX_UPLOAD_MB=20

# OCR: "fake" (no keys needed) or "azure"
OCR_PROVIDER=azure
AZURE_DOC_INTEL_ENDPOINT=https://<your-resource>.cognitiveservices.azure.com/
AZURE_DOC_INTEL_KEY=

# LLM: "fake" or "openai_compat" (OpenAI, or Azure OpenAI/Foundry via https://<res>.openai.azure.com/openai/v1/)
LLM_PROVIDER=openai_compat
LLM_BASE_URL=
LLM_API_KEY=
LLM_MODEL=gpt-4.1-mini   # on Azure: your DEPLOYMENT name

# Embeddings: "none" (skip), "fake" (placeholder vectors, tests only) or "openai_compat".
# Vectors are stored in PostgreSQL (the durable copy); Memgraph is rebuilt from them.
EMBEDDING_PROVIDER=openai_compat
EMBEDDING_MODEL=text-embedding-3-small   # on Azure: your embedding DEPLOYMENT name
EMBEDDING_DIM=1536
# Blank = reuse LLM_BASE_URL / LLM_API_KEY (the same Azure resource). Set them only if embeddings live elsewhere.
EMBEDDING_BASE_URL=
EMBEDDING_API_KEY=

# Graph store: "none" (skip), "memgraph" (docker compose service) or "fake" (in-memory, tests).
GRAPH_STORE_PROVIDER=memgraph
MEMGRAPH_URI=bolt://localhost:7687
MEMGRAPH_USER=
MEMGRAPH_PASSWORD=

# Teachers (by username, comma separated) who may delete OFFICIAL books and chapters. Empty = nobody.
ADMIN_USERNAMES=
</file>

<file path="backend/alembic.ini">
# A generic, single database configuration.

[alembic]
# path to migration scripts.
# this is typically a path given in POSIX (e.g. forward slashes)
# format, relative to the token %(here)s which refers to the location of this
# ini file
script_location = %(here)s/app/db/migrations

# template used to generate migration file names; The default value is %%(rev)s_%%(slug)s
# Uncomment the line below if you want the files to be prepended with date and time
# see https://alembic.sqlalchemy.org/en/latest/tutorial.html#editing-the-ini-file
# for all available tokens
# file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
# defaults to the current working directory.  for multiple paths, the path separator
# is defined by "path_separator" below.
prepend_sys_path = .


# timezone to use when rendering the date within the migration file
# as well as the filename.
# If specified, requires the tzdata library which can be installed by adding
# `alembic[tz]` to the pip requirements.
# string value is passed to ZoneInfo()
# leave blank for localtime
# timezone =

# max length of characters to apply to the "slug" field
# truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version location specification; This defaults
# to <script_location>/versions.  When using multiple version
# directories, initial revisions must be specified with --version-path.
# The path separator used here should be the separator specified by "path_separator"
# below.
# version_locations = %(here)s/bar:%(here)s/bat:%(here)s/alembic/versions

# path_separator; This indicates what character is used to split lists of file
# paths, including version_locations and prepend_sys_path within configparser
# files such as alembic.ini.
# The default rendered in new alembic.ini files is "os", which uses os.pathsep
# to provide os-dependent path splitting.
#
# Note that in order to support legacy alembic.ini files, this default does NOT
# take place if path_separator is not present in alembic.ini.  If this
# option is omitted entirely, fallback logic is as follows:
#
# 1. Parsing of the version_locations option falls back to using the legacy
#    "version_path_separator" key, which if absent then falls back to the legacy
#    behavior of splitting on spaces and/or commas.
# 2. Parsing of the prepend_sys_path option falls back to the legacy
#    behavior of splitting on spaces, commas, or colons.
#
# Valid values for path_separator are:
#
# path_separator = :
# path_separator = ;
# path_separator = space
# path_separator = newline
#
# Use os.pathsep. Default configuration used for new projects.
path_separator = os

# set to 'true' to search source files recursively
# in each "version_locations" directory
# new in Alembic version 1.10
# recursive_version_locations = false

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

# database URL.  This is consumed by the user-maintained env.py script only.
# other means of configuring database URLs may be customized within the env.py
# file.
sqlalchemy.url = driver://postgres:Postgre21@localhost/tuition


[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts.  See the documentation for further
# detail and examples

# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks = black
# black.type = console_scripts
# black.entrypoint = black
# black.options = -l 79 REVISION_SCRIPT_FILENAME

# lint with attempts to fix using "ruff" - use the module runner, against the "ruff" module
# hooks = ruff
# ruff.type = module
# ruff.module = ruff
# ruff.options = check --fix REVISION_SCRIPT_FILENAME

# Alternatively, use the exec runner to execute a binary found on your PATH
# hooks = ruff
# ruff.type = exec
# ruff.executable = ruff
# ruff.options = check --fix REVISION_SCRIPT_FILENAME

# Logging configuration.  This is also consumed by the user-maintained
# env.py script only.
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARNING
handlers = console
qualname =

[logger_sqlalchemy]
level = WARNING
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
</file>

<file path="backend/pytest.ini">
[pytest]
pythonpath = .
testpaths = tests
</file>

<file path="backend/requirements.txt">
fastapi
uvicorn[standard]
sqlalchemy>=2.0
psycopg[binary]
alembic
pydantic-settings
supertokens-python
pytest
httpx
python-multipart
pypdf
azure-ai-documentintelligence  # uncomment when OCR_PROVIDER=azure
openai
datasketch==1.5.9
numpy
neo4j>=5.20  # Bolt driver for Memgraph (GRAPH_STORE_PROVIDER=memgraph)
</file>

<file path="db-init/init-supertokens-db.sql">
CREATE DATABASE supertokens;
</file>

<file path="frontend/src/api/content.js">
const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    ...options,
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Request failed with status ${res.status}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

// --- Teacher Endpoints ---

export async function fetchBooks(params = {}) {
  const query = new URLSearchParams(params).toString();
  return request(`/teacher/books${query ? `?${query}` : ""}`);
}

export async function createBook(bookData) {
  return request("/teacher/books", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(bookData),
  });
}

export async function createChapter(bookId, chapterData) {
  return request(`/teacher/books/${bookId}/chapters`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(chapterData),
  });
}

export async function uploadChapterPages(bookId, chapterId, file) {
  const formData = new FormData();
  formData.append("file", file);

  return request(`/teacher/books/${bookId}/chapters/${chapterId}/pages/upload`, {
    method: "POST",
    body: formData,
  });
}

// --- Front pages first, whole-textbook upload, bulk link ---

// Step 1 of adding a book: cover + publisher/edition pages -> proposed metadata + matching known books.
export async function uploadFrontPages(file) {
  const formData = new FormData();
  formData.append("file", file);
  return request("/teacher/book-drafts/front-pages", { method: "POST", body: formData });
}

export async function planWholeBook(bookId, file) {
  const formData = new FormData();
  formData.append("file", file);
  return request(`/teacher/books/${bookId}/whole-book/plan`, { method: "POST", body: formData });
}

export async function confirmWholeBook(bookId, draftId, chapters) {
  return request(`/teacher/books/${bookId}/whole-book/confirm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ draft_id: draftId, chapters }),
  });
}

// Link a book to every student currently in a single-class room.
export async function bulkLinkBook(roomId, bookId) {
  return request(`/teacher/rooms/${roomId}/books/${bookId}/link`, { method: "POST" });
}

// --- Chapter requests (teacher inbox) ---

export async function fetchTeacherRequests(status = "open") {
  return request(`/teacher/chapter-requests?status=${status}`);
}

export async function dismissRequest(requestId) {
  return request(`/teacher/chapter-requests/${requestId}/dismiss`, { method: "POST" });
}

export async function fulfillRequest(requestId, chapterId = null) {
  return request(`/teacher/chapter-requests/${requestId}/fulfill`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(chapterId ? { chapter_id: chapterId } : {}),
  });
}

// Per chapter: "your chapter X is identical to / an edition of chapter Y in book Z".
export async function fetchChapterMatches(bookId) {
  return request(`/teacher/books/${bookId}/chapter-matches`);
}

// "This looks like an edition of book X": suggestions, confirm, clear.
export async function fetchVariantSuggestions(bookId) {
  return request(`/teacher/books/${bookId}/variant-suggestions`);
}

export async function confirmVariant(bookId, baseBookId) {
  return request(`/teacher/books/${bookId}/variant-of`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ base_book_id: baseBookId }),
  });
}

export async function clearVariant(bookId) {
  return request(`/teacher/books/${bookId}/variant-of`, { method: "DELETE" });
}

// The chapter's prerequisite graph: { nodes, edges, report }.
export async function fetchChapterGraph(bookId, chapterId) {
  return request(`/teacher/books/${bookId}/chapters/${chapterId}/graph`);
}

// Re-run processing on the already-uploaded file after a failure.
export async function retryChapter(bookId, chapterId) {
  return request(`/teacher/books/${bookId}/chapters/${chapterId}/retry`, {
    method: "POST",
  });
}

// --- Student Endpoints ---

export async function fetchMyLinkedBooks() {
  return request("/student/books");
}

// Books this student may link: reference books + books of teachers whose room they joined.
export async function fetchStudentLibrary() {
  return request("/student/library");
}

export async function linkBook(bookId) {
  return request(`/student/books/${bookId}/link`, {
    method: "POST",
  });
}

export async function unlinkBook(bookId) {
  return request(`/student/books/${bookId}/link`, {
    method: "DELETE",
  });
}

export async function fetchChapterPages(bookId, chapterId) {
  return request(`/student/books/${bookId}/chapters/${chapterId}/pages`);
}

// --- Student: ask the teacher to add a chapter ---

export async function requestChapter(bookId, chapterHint) {
  return request(`/student/books/${bookId}/chapter-requests`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ chapter_hint: chapterHint }),
  });
}

export async function fetchMyRequests() {
  return request("/student/chapter-requests");
}

export async function cancelRequest(requestId) {
  return request(`/student/chapter-requests/${requestId}`, { method: "DELETE" });
}

// --- Delete (own books/chapters for teachers; official ones only for administrators) ---

export async function fetchMe() {
  return request("/auth/me");
}

export async function deleteMyBook(bookId) {
  return request(`/teacher/books/${bookId}`, { method: "DELETE" });
}

export async function deleteMyChapter(bookId, chapterId) {
  return request(`/teacher/books/${bookId}/chapters/${chapterId}`, { method: "DELETE" });
}

export async function adminDeleteBook(bookId) {
  return request(`/admin/books/${bookId}`, { method: "DELETE" });
}

export async function adminDeleteChapter(bookId, chapterId) {
  return request(`/admin/books/${bookId}/chapters/${chapterId}`, { method: "DELETE" });
}

// "No, that is not the base of my book": the server remembers it and stops suggesting that book.
export async function dismissVariantSuggestion(bookId, baseBookId) {
  return request(`/teacher/books/${bookId}/variant-suggestions/dismiss`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ base_book_id: baseBookId }),
  });
}
</file>

<file path="frontend/src/auth/AuthContext.jsx">
import { createContext, useContext, useEffect, useState } from "react";
import { signIn, signUp } from "supertokens-web-js/recipe/emailpassword";
import {
  doesSessionExist,
  signOut as stSignOut,
} from "supertokens-web-js/recipe/session";
import "./supertokensInit";
import { api } from "../shared/api";
import { normalizePhone, normalizeUsername, usernameToEmail } from "./identity";

const AuthCtx = createContext(null);
export const useAuth = () => useContext(AuthCtx);

export function AuthProvider({ children }) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      if (await doesSessionExist()) {
        try {
          setProfile((await api("/auth/me")).data);
        } catch {
          setProfile(null);
        }
      }
      setLoading(false);
    })();
  }, []);

  async function login(username, password) {
    const response = await signIn({
      formFields: [
        { id: "email", value: usernameToEmail(normalizeUsername(username)) },
        { id: "password", value: password },
      ],
    });
    if (response.status !== "OK") {
      throw new Error("Invalid username or password"); // generic on purpose
    }
    const me = (await api("/auth/me")).data;
    setProfile(me);
    return me;
  }

  async function signup({ name, username, phone, password, role }) {
    const normalizedUsername = normalizeUsername(username);
    const response = await signUp({
      formFields: [
        { id: "email", value: usernameToEmail(normalizedUsername) },
        { id: "password", value: password },
        { id: "name", value: name },
        { id: "username", value: normalizedUsername },
        { id: "phone", value: normalizePhone(phone) },
        { id: "role", value: role },
      ],
    });
    if (response.status !== "OK") {
      const msg =
        response.status === "FIELD_ERROR"
          ? response.formFields[0]?.error
          : response.status === "GENERAL_ERROR"
            ? response.message
            : "Could not create account with these details";
      throw new Error(msg);
    }
    const me = (await api("/auth/me")).data;
    setProfile(me);
    return me;
  }

  async function logout() {
    await stSignOut();
    setProfile(null);
  }

  return (
    <AuthCtx.Provider value={{ user: profile, profile, loading, login, signup, logout }}>
      {children}
    </AuthCtx.Provider>
  );
}
</file>

<file path="frontend/src/auth/identity.js">
const USERNAME_RE = /^[a-z0-9_]{3,30}$/;
const PHONE_RE = /^\+?[0-9]{10,15}$/;

export function normalizeUsername(value) {
  const v = value.trim().toLowerCase();
  if (!USERNAME_RE.test(v)) {
    throw new Error("Username must be 3-30 characters: lowercase letters, numbers, underscore only");
  }
  return v;
}

export function usernameToEmail(username) {
  return `${username}@user.tuition-companion.app`;
}

export function normalizePhone(value) {
  const v = value.replace(/[\s\-()]/g, "");
  if (!PHONE_RE.test(v)) {
    throw new Error("Enter a valid phone number");
  }
  return v;
}
</file>

<file path="frontend/src/auth/LoginPage.jsx">
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "./AuthContext";

export default function LoginPage() {
  const { login } = useAuth();
  const nav = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function submit(e) {
    e.preventDefault();
    setError("");
    try {
      const me = await login(username, password);
      nav(`/${String(me.role).toLowerCase()}`, { replace: true });
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="container" style={{ maxWidth: 420 }}>
      <form className="card stack" onSubmit={submit}>
        <h2>Log in</h2>
        <div>
          <label htmlFor="username">Username</label>
          <input
            id="username"
            className="input"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="yourusername"
            required
          />
        </div>
        <div>
          <label htmlFor="pw">Password</label>
          <input
            id="pw"
            className="input"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        {error && <div className="error">{error}</div>}
        <button className="btn" type="submit">
          Log in
        </button>
        <span className="small">
          New here? <Link to="/signup">Create an account</Link>
        </span>
      </form>
    </div>
  );
}
</file>

<file path="frontend/src/auth/SignupPage.jsx">
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "./AuthContext";

export default function SignupPage() {
  const { signup } = useAuth();
  const nav = useNavigate();
  const [form, setForm] = useState({
    name: "",
    username: "",
    phone: "",
    password: "",
    role: "student",
  });
  const [error, setError] = useState("");
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setError("");
    try {
      const me = await signup(form);
      nav(`/${String(me.role).toLowerCase()}`, { replace: true });
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="container" style={{ maxWidth: 420 }}>
      <form className="card stack" onSubmit={submit}>
        <h2>Create your account</h2>
        <div>
          <label htmlFor="role">I am a…</label>
          <select
            id="role"
            className="input"
            value={form.role}
            onChange={set("role")}
          >
            <option value="teacher">Teacher</option>
            <option value="student">Student</option>
            <option value="parent">Parent</option>
          </select>
        </div>
        <div>
          <label htmlFor="name">Full name</label>
          <input
            id="name"
            className="input"
            value={form.name}
            onChange={set("name")}
            required
            minLength={2}
          />
        </div>
        <div>
          <label htmlFor="username">Username</label>
          <input
            id="username"
            className="input"
            value={form.username}
            onChange={set("username")}
            placeholder="lowercase, letters/numbers/_"
            required
            minLength={3}
            maxLength={30}
          />
          <span className="small">
            This is what you'll log in with. Each family member needs a
            different one, even if you share a phone.
          </span>
        </div>
        <div>
          <label htmlFor="phone">Phone number</label>
          <input
            id="phone"
            className="input"
            type="tel"
            value={form.phone}
            onChange={set("phone")}
            placeholder="+919876543210"
            required
          />
        </div>
        <div>
          <label htmlFor="pw">Password (min 8 characters)</label>
          <input
            id="pw"
            className="input"
            type="password"
            value={form.password}
            onChange={set("password")}
            required
            minLength={8}
          />
        </div>
        {error && <div className="error">{error}</div>}
        <button className="btn" type="submit">
          Sign up
        </button>
        <span className="small">
          Already have an account? <Link to="/login">Log in</Link>
        </span>
      </form>
    </div>
  );
}
</file>

<file path="frontend/src/auth/supertokensInit.js">
import SuperTokens from "supertokens-web-js";
import EmailPassword from "supertokens-web-js/recipe/emailpassword";
import Session from "supertokens-web-js/recipe/session";

SuperTokens.init({
  appInfo: {
    appName: "Tuition Companion",
    apiDomain: import.meta.env.VITE_API_URL,
    apiBasePath: "/auth",
  },
  recipeList: [Session.init(), EmailPassword.init()],
});
</file>

<file path="frontend/src/parent/ParentDashboard.jsx">
import { useEffect, useState } from "react";
import { api } from "../shared/api";
import Header from "../shared/Header";

export default function ParentDashboard() {
  const [children, setChildren] = useState(null);
  const [code, setCode] = useState("");
  const [error, setError] = useState("");

  const load = () =>
    api("/parent/children")
      .then(setChildren)
      .catch((e) => setError(e.message));
  useEffect(() => {
    load();
  }, []);

  async function link(e) {
    e.preventDefault();
    setError("");
    try {
      await api("/parent/link", { method: "POST", body: { link_code: code } });
      setCode("");
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="container stack">
      <Header title="My children" />

      <form className="card stack" onSubmit={link}>
        <h3>Link a student</h3>
        <label htmlFor="lc">Link code (from your child's dashboard)</label>
        <input
          id="lc"
          className="input"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          required
        />
        {error && <div className="error">{error}</div>}
        <button className="btn" type="submit">
          Link
        </button>
      </form>

      {children?.length === 0 && (
        <div className="card">
          <p className="small">No children linked yet.</p>
        </div>
      )}
      {children?.map((c) => (
        <div className="card" key={c.id}>
          <h3>{c.name}</h3>
          <p className="small">
            {c.rooms.length
              ? `In: ${c.rooms.map((r) => r.name).join(", ")}`
              : "Not in any room yet"}
          </p>
        </div>
      ))}
    </div>
  );
}
</file>

<file path="frontend/src/shared/api.js">
const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Callable function; always resolves to { data }
export async function api(path, options = {}) {
  const { headers, body, ...rest } = options;

  const isFormData = typeof FormData !== "undefined" && body instanceof FormData;
  const isPlainObject =
    body && typeof body === "object" && !isFormData && !(body instanceof Blob);

  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    ...rest,
    headers: {
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
      ...(headers || {}),
    },
    body: isPlainObject ? JSON.stringify(body) : body,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    const err = new Error(
      errorData.detail || `Request failed with status ${res.status}`,
    );
    err.status = res.status;
    err.data = errorData;
    throw err;
  }

  if (res.status === 204) return { data: null };

  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  return { data };
}

// Convenience methods
api.get = (path, options = {}) => api(path, { method: "GET", ...options });

api.post = (path, body, options = {}) =>
  api(path, { method: "POST", body: body || undefined, ...options });

api.delete = (path, options = {}) => api(path, { method: "DELETE", ...options });

export default api;
</file>

<file path="frontend/src/shared/Header.jsx">
import { useAuth } from "../auth/AuthContext";

export default function Header({ title }) {
  const { profile, logout } = useAuth();
  return (
    <div className="row" style={{ marginBottom: 16 }}>
      <div>
        <h1>{title}</h1>
        <span className="small">Signed in as {profile.name}</span>
      </div>
      <button className="btn secondary" onClick={logout}>
        Log out
      </button>
    </div>
  );
}
</file>

<file path="frontend/src/shared/Landing.jsx">
import React from "react";
import { Link, Navigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function Landing() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div style={{ padding: "2rem", textAlign: "center" }}>Loading...</div>
    );
  }

  // INTERCEPT: If the user is logged in, auto-redirect them to their specific dashboard
  if (user && user.role) {
    const role = user.role.toLowerCase();
    if (role === "teacher") return <Navigate to="/teacher" replace />;
    if (role === "student") return <Navigate to="/student" replace />;
    if (role === "parent") return <Navigate to="/parent" replace />;
  }

  return (
    <div
      style={{
        textAlign: "center",
        padding: "4rem 1rem",
        fontFamily: "sans-serif",
      }}
    >
      <h1 style={{ fontSize: "2.5rem", marginBottom: "1rem" }}>
        Welcome to Tuition Companion
      </h1>
      <p style={{ color: "#666", marginBottom: "2rem" }}>
        The complete platform for teachers, students, and parents.
      </p>

      <div style={{ display: "flex", gap: "1rem", justifyContent: "center" }}>
        <Link
          to="/login"
          style={{
            padding: "0.8rem 1.5rem",
            background: "#0070f3",
            color: "white",
            textDecoration: "none",
            borderRadius: "5px",
            fontWeight: "bold",
          }}
        >
          Login
        </Link>
        <Link
          to="/signup"
          style={{
            padding: "0.8rem 1.5rem",
            background: "#eaeaea",
            color: "black",
            textDecoration: "none",
            borderRadius: "5px",
            fontWeight: "bold",
          }}
        >
          Sign Up
        </Link>
      </div>
    </div>
  );
}
</file>

<file path="frontend/src/shared/ProtectedRoute.jsx">
import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function ProtectedRoute({ roles, children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div style={{ padding: "2rem", textAlign: "center" }}>
        Verifying access...
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Ensure case-insensitive role checking
  if (roles && roles.length > 0) {
    const userRole = user.role?.toLowerCase();
    const allowedRoles = roles.map((r) => r.toLowerCase());

    if (!allowedRoles.includes(userRole)) {
      // If a student tries to access /teacher, send them to / which will re-route them to /student
      return <Navigate to="/" replace />;
    }
  }

  return children;
}
</file>

<file path="frontend/src/shared/theme.css">
:root {
  --primary: #0f766e;
  --accent: #f59e0b;
  --success: #16a34a;
  --warn: #ea580c;
  --bg: #fafaf9;
  --surface: #ffffff;
  --text: #1c1917;
  --muted: #57534e;
  --border: #e7e5e4;
  --radius: 10px;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font: 400 16px/1.5 Inter, system-ui, sans-serif;
  font-variant-numeric: tabular-nums;
}

h1, h2, h3 { font-family: Poppins, Inter, sans-serif; margin: 0 0 8px; }
h1 { font-size: 30px; font-weight: 600; }
h2 { font-size: 23px; font-weight: 600; }
h3 { font-size: 18px; font-weight: 500; }

.small { font-size: 13px; color: var(--muted); }
.container { max-width: 960px; margin: 0 auto; padding: 24px 16px; }
.stack > * + * { margin-top: 12px; }
.row { display: flex; gap: 12px; align-items: center; justify-content: space-between; flex-wrap: wrap; }

.card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px; margin-bottom: 16px; }

label { display: block; font-size: 14px; font-weight: 500; margin-bottom: 4px; }
.input { width: 100%; min-height: 44px; padding: 8px 12px; border: 1px solid var(--border); border-radius: 8px; font: inherit; background: #fff; }

.btn { min-height: 44px; padding: 8px 16px; border: 0; border-radius: 8px; background: var(--primary); color: #fff; font: 500 14px Inter, sans-serif; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; justify-content: center; }
.btn.secondary { background: transparent; color: var(--primary); border: 1px solid var(--primary); }

.error { color: var(--warn); font-size: 14px; }
.code { display: inline-block; font: 600 22px/1 Poppins, monospace; letter-spacing: 0.15em; background: #f0fdfa; color: var(--primary); padding: 8px 12px; border-radius: 8px; }
.badge { background: var(--accent); color: #1c1917; font-size: 13px; padding: 2px 8px; border-radius: 999px; }

.table { width: 100%; border-collapse: collapse; }
.table th, .table td { text-align: left; padding: 8px; border-bottom: 1px solid var(--border); }

/* Status badges: always an icon + label, never color alone */
.status { display: inline-flex; align-items: center; gap: 4px; font-size: 13px; font-weight: 500; padding: 2px 10px; border-radius: 999px; border: 1px solid var(--border); background: #f5f5f4; color: var(--muted); }
.status.ready { background: #f0fdf4; color: var(--success); border-color: #bbf7d0; }
.status.processing { background: #fffbeb; color: #b45309; border-color: #fde68a; }
.status.failed { background: #fff7ed; color: var(--warn); border-color: #fed7aa; }

.back-link { display: inline-block; margin-bottom: 8px; color: var(--primary); font-size: 14px; text-decoration: none; }
.btn.small-btn { min-height: 36px; padding: 4px 12px; }
.btn.danger { background: transparent; color: var(--warn); border: 1px solid var(--warn); }
</file>

<file path="frontend/src/student/ChapterRequestPanel.jsx">
import React, { useEffect, useState } from "react";
import { requestChapter, fetchMyRequests, cancelRequest } from "../api/content";

const STATUS_TEXT = {
  open: "waiting for your teacher",
  fulfilled: "added - check your textbook",
  dismissed: "your teacher can't add this one",
  cancelled: "cancelled",
};

// "A chapter I need isn't in my teacher's book": ask the teacher to add it. Official books have no teacher
// to ask, so they're not offered here.
export default function ChapterRequestPanel({ linkedBooks }) {
  const privateBooks = linkedBooks.filter((b) => !b.is_reference);
  const [requests, setRequests] = useState([]);
  const [bookId, setBookId] = useState("");
  const [hint, setHint] = useState("");
  const [message, setMessage] = useState("");

  async function load() {
    try {
      setRequests(await fetchMyRequests());
    } catch (err) {
      console.error(err);
    }
  }

  useEffect(() => {
    load();
  }, [linkedBooks.length]);

  useEffect(() => {
    if (!bookId && privateBooks.length > 0) setBookId(privateBooks[0].id);
  }, [privateBooks.length]);

  if (privateBooks.length === 0 && requests.length === 0) return null;

  async function submit(e) {
    e.preventDefault();
    try {
      await requestChapter(bookId, hint);
      setHint("");
      setMessage("Sent to your teacher.");
      await load();
    } catch (err) {
      setMessage(err.message);
    }
  }

  async function cancel(id) {
    await cancelRequest(id);
    await load();
  }

  return (
    <div style={{ marginTop: "1.5rem" }}>
      {privateBooks.length > 0 && (
        <>
          <h3>Missing a chapter?</h3>
          <form onSubmit={submit} style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
            <select value={bookId} onChange={(e) => setBookId(e.target.value)}>
              {privateBooks.map((b) => (
                <option key={b.id} value={b.id}>{b.class_name} {b.subject}</option>
              ))}
            </select>
            <input
              placeholder="Which chapter? (e.g. Chapter 5 - Force)"
              value={hint}
              onChange={(e) => setHint(e.target.value)}
              required
              minLength={3}
              maxLength={200}
              style={{ flex: 1, minWidth: "12rem" }}
            />
            <button type="submit">Ask my teacher</button>
          </form>
          {message && <p style={{ color: "blue" }}>{message}</p>}
        </>
      )}
      {requests.length > 0 && (
        <>
          <h4>My requests</h4>
          <ul>
            {requests.map((r) => (
              <li key={r.id}>
                {r.chapter_hint} ({r.book.class_name} {r.book.subject}) - {STATUS_TEXT[r.status]}{" "}
                {r.status === "open" && <button onClick={() => cancel(r.id)}>Cancel</button>}
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
</file>

<file path="frontend/src/student/StudentDashboard.jsx">
import React, { useState, useEffect } from "react";
import { useAuth } from "../auth/AuthContext";
import api from "../shared/api";
import Header from "../shared/Header";
import ChapterRequestPanel from "./ChapterRequestPanel.jsx";
import {
  fetchMyLinkedBooks,
  fetchStudentLibrary,
  linkBook,
} from "../api/content";

export default function StudentDashboard() {
  const { user } = useAuth();
  const [rooms, setRooms] = useState([]);
  const [joinCode, setJoinCode] = useState("");
  const [linkedBooks, setLinkedBooks] = useState([]);
  const [availableBooks, setAvailableBooks] = useState([]);

  useEffect(() => {
    loadRooms();
    loadBooks();
  }, []);

  async function loadRooms() {
    try {
      const res = await api.get("/student/rooms");
      setRooms(res.data || []);
    } catch (err) {
      console.error("Failed to load rooms:", err);
    }
  }

  async function loadBooks() {
    try {
      const myBooks = await fetchMyLinkedBooks();
      setLinkedBooks(myBooks || []);
      setAvailableBooks((await fetchStudentLibrary()) || []);
    } catch (err) {
      console.error("Failed to load books:", err);
    }
  }

  async function joinRoom(e) {
    e.preventDefault();
    try {
      await api.post("/student/rooms/join", { join_code: joinCode });
      setJoinCode("");
      loadRooms();
    } catch (err) {
      alert("Failed to join room. Please verify the code.");
    }
  }

  async function handleLinkBook(e) {
    if (!e.target.value) return;
    try {
      await linkBook(e.target.value);
      await loadBooks();
    } catch (err) {
      alert("Failed to link book.");
    }
  }

  return (
    <div>
      <Header role="Student" />
      <div
        className="container"
        style={{ padding: "2rem", maxWidth: "800px", margin: "0 auto" }}
      >
        {/* Books & Doubts Section */}
        <div
          className="card"
          style={{
            padding: "1.5rem",
            border: "1px solid #ddd",
            borderRadius: "8px",
            marginBottom: "2rem",
          }}
        >
          <h2>My textbooks</h2>
          {linkedBooks.length === 0 ? (
            <p>
              You haven't linked any textbooks yet. Select a textbook below to
              get started.
            </p>
          ) : (
            <ul>
              {linkedBooks.map((b) => (
                <li key={b.id} style={{ margin: "0.5rem 0" }}>
                  <strong>
                    {b.class_name} {b.subject}
                  </strong>{" "}
                  ({b.publisher})
                </li>
              ))}
            </ul>
          )}

          <div style={{ marginTop: "1rem" }}>
            <select
              onChange={handleLinkBook}
              value=""
              style={{ padding: "0.5rem" }}
            >
              <option value="" disabled>
                Link a textbook...
              </option>
              {availableBooks.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.board} - {b.class_name} {b.subject} ({b.publisher})
                  {b.is_reference ? " - official" : ""}
                </option>
              ))}
            </select>
          </div>

          <ChapterRequestPanel linkedBooks={linkedBooks} />
        </div>

        {/* Room Section */}
        <div
          className="card"
          style={{
            padding: "1.5rem",
            border: "1px solid #ddd",
            borderRadius: "8px",
            marginBottom: "2rem",
          }}
        >
          <h2>Join a room</h2>
          <form
            onSubmit={joinRoom}
            style={{ display: "flex", gap: "0.5rem", marginTop: "1rem" }}
          >
            <input
              placeholder="Code from teacher"
              value={joinCode}
              onChange={(e) => setJoinCode(e.target.value)}
              required
              style={{ padding: "0.5rem", flex: 1 }}
            />
            <button type="submit" style={{ padding: "0.5rem 1rem" }}>
              Join
            </button>
          </form>
        </div>

        <div
          className="card"
          style={{
            padding: "1.5rem",
            border: "1px solid #ddd",
            borderRadius: "8px",
            marginBottom: "2rem",
          }}
        >
          <h2>My rooms</h2>
          {rooms.length === 0 ? (
            <p>No rooms joined yet.</p>
          ) : (
            <ul>
              {rooms.map((r) => (
                <li key={r.id} style={{ margin: "0.5rem 0" }}>
                  <strong>{r.name}</strong> ({r.room_type})
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Parent Link Code */}
        <div
          className="card"
          style={{
            padding: "1.5rem",
            border: "1px solid #ddd",
            borderRadius: "8px",
          }}
        >
          <h2>Parent link code</h2>
          <p style={{ color: "#666", fontSize: "0.9rem" }}>
            Give this code to your parent so they can follow your progress:
          </p>
          <div
            style={{
              fontSize: "1.5rem",
              letterSpacing: "3px",
              fontWeight: "bold",
              padding: "0.8rem 1.5rem",
              background: "#e0f2f1",
              display: "inline-block",
              borderRadius: "4px",
              marginTop: "0.5rem",
            }}
          >
            {user?.link_code || "N/A"}
          </div>
        </div>
      </div>
    </div>
  );
}
</file>

<file path="frontend/src/teacher/ChapterRequests.jsx">
import React, { useEffect, useState } from "react";
import { fetchTeacherRequests, dismissRequest, fulfillRequest } from "../api/content";

// Inbox of chapters students asked for. Requests also close themselves when a matching chapter finishes processing.
export default function ChapterRequests({ refreshKey }) {
  const [requests, setRequests] = useState([]);

  async function load() {
    try {
      setRequests(await fetchTeacherRequests("open"));
    } catch (err) {
      console.error(err);
    }
  }

  useEffect(() => {
    load();
  }, [refreshKey]);

  if (requests.length === 0) return null;

  async function act(fn, id) {
    try {
      await fn(id);
    } finally {
      await load();
    }
  }

  return (
    <section style={{ marginBottom: "2rem", border: "1px solid #e0b000", padding: "1rem", background: "#fffbea" }}>
      <h3>Chapter requests ({requests.length})</h3>
      <ul>
        {requests.map((r) => (
          <li key={r.id} style={{ margin: "0.4rem 0" }}>
            <b>{r.student_name}</b> asked for <i>{r.chapter_hint}</i> in {r.book.class_name} {r.book.subject}{" "}
            <button onClick={() => act(fulfillRequest, r.id)}>Mark done</button>{" "}
            <button onClick={() => act(dismissRequest, r.id)}>Dismiss</button>
          </li>
        ))}
      </ul>
    </section>
  );
}
</file>

<file path="frontend/src/teacher/NewBookWizard.jsx">
import React, { useState } from "react";
import { uploadFrontPages, createBook } from "../api/content";

const EMPTY = {
  board: "",
  class_name: "",
  subject: "",
  publisher: "",
  edition: "",
  school: "",
  is_customized: false,
};

const label = (b) =>
  `${b.board} ${b.class_name} ${b.subject} (${b.publisher}${b.edition ? `, ${b.edition}` : ""})`;

// Add a book: front pages first (cover + publisher/edition page) so the system can read the details
// and tell the teacher if an official book already matches. Manual entry stays as a fallback.
export default function NewBookWizard({ onCreated, onUseExisting }) {
  const [form, setForm] = useState(EMPTY);
  const [draft, setDraft] = useState(null); // { draft_id, matches }
  const [manual, setManual] = useState(false);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [warn, setWarn] = useState(false); // the message is a warning (nothing could be read), shown in orange

  const showForm = manual || draft;

  async function handleFront(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setBusy(true);
    setMessage("Reading the front pages...");
    try {
      const d = await uploadFrontPages(file);
      const m = d.metadata;
      setForm({
        board: m.board || "",
        class_name: m.class_name || "",
        subject: m.subject || "",
        publisher: m.publisher || "",
        edition: m.edition || "",
        school: m.school || "",
        is_customized: !!m.is_customized,
      });
      setDraft({ draft_id: d.draft_id, matches: d.matches });
      setWarn(!!d.warning);
      setMessage(
        d.warning
          ? `${d.warning} The form below is empty: fill it in by hand.`
          : d.matches.length
            ? "We found books that already match. Check them before creating a new one."
            : "Check the details below, fix anything that's wrong, then create the book.",
      );
    } catch (err) {
      setWarn(false);
      setMessage(err.message);
    } finally {
      setBusy(false);
      e.target.value = "";
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setBusy(true);
    try {
      const created = await createBook({
        ...form,
        edition: form.edition.trim() || null,
        school: form.school.trim() || null,
        draft_id: draft?.draft_id || null,
      });
      setForm(EMPTY);
      setDraft(null);
      setManual(false);
      setMessage("");
      await onCreated(created);
    } catch (err) {
      setMessage(`Error: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  function cancel() {
    setForm(EMPTY);
    setDraft(null);
    setManual(false);
    setMessage("");
  }

  const field = (key, placeholder, required = false) => (
    <input
      placeholder={placeholder}
      value={form[key]}
      onChange={(e) => setForm({ ...form, [key]: e.target.value })}
      required={required}
    />
  );

  return (
    <section style={{ marginBottom: "2rem", border: "1px solid #ccc", padding: "1rem" }}>
      <h3>Add a book</h3>
      <p style={{ fontSize: "0.85rem", color: "#666" }}>
        Official NCERT books are already in the library below; you can link them to your
        students without uploading anything. Add a book here only if it isn't listed (private
        publisher or school edition). It will be visible only to students in your rooms.
      </p>

      {!showForm && (
        <>
          <label>
            <b>1. Upload the cover and publisher/edition pages</b> (PDF or photo, a few pages)
            <br />
            <input type="file" accept="application/pdf,image/*" onChange={handleFront} disabled={busy} />
          </label>
          <p>
            <button type="button" onClick={() => setManual(true)}>
              I don't have these pages - enter the details by hand
            </button>
          </p>
        </>
      )}

      {message && <p style={{ color: warn ? "#b45f06" : "blue" }}>{message}</p>}

      {draft?.matches?.length > 0 && (
        <div style={{ background: "#eef6ff", padding: "0.5rem", marginBottom: "0.75rem" }}>
          <b>Already in the library:</b>
          <ul>
            {draft.matches.map((b) => (
              <li key={b.id}>
                {label(b)}
                {b.is_reference ? " - official" : " - yours"}{" "}
                <button type="button" onClick={() => { cancel(); onUseExisting(b); }}>
                  Use this one
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}

      {showForm && (
        <form onSubmit={handleSubmit} style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
          {field("board", "Board (e.g. ICSE)", true)}
          {field("class_name", "Class (e.g. Class 9)", true)}
          {field("subject", "Subject", true)}
          {field("publisher", "Publisher", true)}
          {field("edition", "Edition (optional)")}
          {field("school", "School (optional)")}
          <label>
            <input
              type="checkbox"
              checked={form.is_customized}
              onChange={(e) => setForm({ ...form, is_customized: e.target.checked })}
            />{" "}
            School-customized edition
          </label>
          <button type="submit" disabled={busy}>
            {draft ? "Looks right - create book" : "Create book"}
          </button>
          <button type="button" onClick={cancel}>
            Cancel
          </button>
        </form>
      )}
    </section>
  );
}
</file>

<file path="frontend/src/teacher/RoomDetail.jsx">
import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../shared/api";
import Header from "../shared/Header";

export default function RoomDetail() {
  const { roomId } = useParams();
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get(`/teacher/rooms/${roomId}/members`)
      .then((res) => {
        setMembers(res.data || []);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, [roomId]);

  return (
    <div>
      <Header role="Teacher" />
      <div
        className="container"
        style={{ padding: "2rem", maxWidth: "800px", margin: "0 auto" }}
      >
        <Link to="/teacher">← Back to rooms</Link>
        <h2 style={{ marginTop: "1rem" }}>Room Members</h2>
        <p style={{ color: "#666", marginBottom: "1.5rem" }}>
          Rooms only group students. Content is managed independently through
          the Content Library.
        </p>

        <div
          className="card"
          style={{
            padding: "1.5rem",
            border: "1px solid #ddd",
            borderRadius: "8px",
          }}
        >
          {loading ? (
            <p>Loading members...</p>
          ) : members.length === 0 ? (
            <p>No students have joined this room yet.</p>
          ) : (
            <table
              style={{
                width: "100%",
                textAlign: "left",
                borderCollapse: "collapse",
              }}
            >
              <thead>
                <tr style={{ borderBottom: "2px solid #ddd" }}>
                  <th style={{ padding: "0.5rem" }}>Student Name</th>
                  <th style={{ padding: "0.5rem" }}>Joined At</th>
                </tr>
              </thead>
              <tbody>
                {members.map((m) => (
                  <tr key={m.id} style={{ borderBottom: "1px solid #eee" }}>
                    <td style={{ padding: "0.5rem" }}>{m.name}</td>
                    <td style={{ padding: "0.5rem" }}>
                      {new Date(m.joined_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
</file>

<file path="frontend/src/teacher/TeacherDashboard.jsx">
import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import api from "../shared/api";
import Header from "../shared/Header";

export default function TeacherDashboard() {
  const [rooms, setRooms] = useState([]);
  const [name, setName] = useState("");
  const [type, setType] = useState("single_class");

  useEffect(() => {
    loadRooms();
  }, []);

  async function loadRooms() {
    try {
      const res = await api.get("/teacher/rooms");
      setRooms(res.data || []);
    } catch (err) {
      console.error("Failed to load rooms:", err);
    }
  }

  async function createRoom(e) {
    e.preventDefault();
    try {
      await api.post("/teacher/rooms", { name, room_type: type });
      setName("");
      loadRooms();
    } catch (err) {
      alert("Failed to create room.");
    }
  }

  return (
    <div>
      <Header role="Teacher" />
      <div
        className="container"
        style={{ padding: "2rem", maxWidth: "900px", margin: "0 auto" }}
      >
        <div style={{ display: "flex", gap: "1rem", marginBottom: "2rem" }}>
          <Link
            to="/teacher/library"
            style={{
              padding: "0.6rem 1.2rem",
              background: "#0070f3",
              color: "#fff",
              textDecoration: "none",
              borderRadius: "5px",
            }}
          >
            Content Library
          </Link>
        </div>

        <div
          className="card"
          style={{
            padding: "1.5rem",
            border: "1px solid #ddd",
            borderRadius: "8px",
            marginBottom: "2rem",
          }}
        >
          <h2>Create a room</h2>
          <form
            onSubmit={createRoom}
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "1rem",
              marginTop: "1rem",
            }}
          >
            <div>
              <label style={{ display: "block", marginBottom: "0.25rem" }}>
                Room name
              </label>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                style={{ padding: "0.5rem", width: "100%" }}
              />
            </div>
            <div>
              <label style={{ display: "block", marginBottom: "0.25rem" }}>
                Room type
              </label>
              <select
                value={type}
                onChange={(e) => setType(e.target.value)}
                style={{ padding: "0.5rem", width: "100%" }}
              >
                <option value="single_class">Single class</option>
                <option value="mixed_class">Mixed class</option>
              </select>
            </div>
            <button
              type="submit"
              style={{ padding: "0.6rem 1.2rem", alignSelf: "flex-start" }}
            >
              Create room
            </button>
          </form>
        </div>

        <div
          className="card"
          style={{
            padding: "1.5rem",
            border: "1px solid #ddd",
            borderRadius: "8px",
          }}
        >
          <h2>Your rooms</h2>
          {rooms.length === 0 ? (
            <p>No rooms created yet.</p>
          ) : (
            <table
              style={{
                width: "100%",
                textAlign: "left",
                borderCollapse: "collapse",
                marginTop: "1rem",
              }}
            >
              <thead>
                <tr style={{ borderBottom: "2px solid #ddd" }}>
                  <th style={{ padding: "0.5rem" }}>Room</th>
                  <th style={{ padding: "0.5rem" }}>Type</th>
                  <th style={{ padding: "0.5rem" }}>Join code</th>
                  <th style={{ padding: "0.5rem" }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {rooms.map((r) => (
                  <tr key={r.id} style={{ borderBottom: "1px solid #eee" }}>
                    <td style={{ padding: "0.5rem" }}>{r.name}</td>
                    <td style={{ padding: "0.5rem" }}>{r.room_type}</td>
                    <td style={{ padding: "0.5rem" }}>
                      <strong>{r.join_code}</strong>
                    </td>
                    <td style={{ padding: "0.5rem" }}>
                      <Link
                        to={`/teacher/rooms/${r.id}`}
                        style={{ color: "#0070f3" }}
                      >
                        View members
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
</file>

<file path="frontend/src/teacher/TeacherLibrary.jsx">
import React, { useState, useEffect } from "react";
import api from "../shared/api";
import NewBookWizard from "./NewBookWizard.jsx";
import WholeBookUpload from "./WholeBookUpload.jsx";
import ChapterRequests from "./ChapterRequests.jsx";
import {
  fetchBooks,
  bulkLinkBook,
  createChapter,
  uploadChapterPages,
  retryChapter,
  fetchChapterGraph,
  fetchVariantSuggestions,
  fetchChapterMatches,
  confirmVariant,
  clearVariant,
  fetchMe,
  deleteMyBook,
  deleteMyChapter,
  adminDeleteBook,
  adminDeleteChapter,
  dismissVariantSuggestion,
} from "../api/content";

// Convenience: link this book to every student in one of the teacher's single-class rooms.
function LinkToRoom({ book }) {
  const [rooms, setRooms] = useState([]);
  const [roomId, setRoomId] = useState("");
  const [note, setNote] = useState("");

  useEffect(() => {
    api
      .get("/teacher/rooms")
      .then((res) => setRooms((res.data || []).filter((r) => r.room_type === "single_class")))
      .catch(() => {});
  }, []);

  useEffect(() => setNote(""), [book.id]);

  if (rooms.length === 0) return null;

  async function link() {
    try {
      const r = await bulkLinkBook(roomId, book.id);
      setNote(
        `Linked for ${r.linked} student(s)` +
          (r.already_linked ? `, ${r.already_linked} already had it` : "") +
          `. Students who join later link it themselves.`,
      );
    } catch (err) {
      setNote(err.message);
    }
  }

  return (
    <p>
      <select value={roomId} onChange={(e) => setRoomId(e.target.value)}>
        <option value="">Link this book to all students in...</option>
        {rooms.map((r) => (
          <option key={r.id} value={r.id}>{r.name} ({r.member_count} students)</option>
        ))}
      </select>{" "}
      <button type="button" disabled={!roomId} onClick={link}>Link</button>{" "}
      <span style={{ color: "#444" }}>{note}</span>
    </p>
  );
}

function VariantBanner({ book, books, suggestions, onConfirm, onClear, onDismiss }) {
  const base = book.variant_of_id && books.find((b) => b.id === book.variant_of_id);
  const label = (b) => `${b.board} ${b.class_name} ${b.subject} (${b.publisher}${b.edition ? `, ${b.edition}` : ""})`;
  if (base) {
    return (
      <p style={{ background: "#eef6ff", padding: "0.5rem" }}>
        Marked as a customized version of <b>{label(base)}</b>.{" "}
        <button onClick={onClear}>Remove</button>
      </p>
    );
  }
  const s = suggestions[0];
  if (!s) return null;
  const of = `${s.matched_chapters} of your ${s.chapters_checked} chapter${s.chapters_checked === 1 ? "" : "s"}`;
  const partial =
    s.book.is_reference && s.candidate_chapters_loaded < 40
      ? ` (the official book has ${s.candidate_chapters_loaded} chapter${s.candidate_chapters_loaded === 1 ? "" : "s"} loaded so far)`
      : "";
  return (
    <div style={{ background: "#fff8e6", padding: "0.5rem", marginBottom: "1rem" }}>
      {s.kind === "same" ? (
        <p>
          {of} {s.matched_chapters === 1 && s.chapters_checked > 1 ? "is" : "are"} identical to chapters of{" "}
          <b>{label(s.book)}</b>
          {s.book.is_reference ? " (official)" : ""}{partial}. Students can use that book for those chapters.
          Is your book the same book?
        </p>
      ) : (
        <p>
          {of} match chapters of <b>{label(s.book)}</b>
          {s.book.is_reference ? " (official)" : ""}{partial}, with edits. Is this a customized version of it?
        </p>
      )}
      <button onClick={() => onConfirm(s.book.id)}>Yes, it's based on it</button>{" "}
      <button onClick={() => onDismiss(s.book.id)}>Not now</button>
    </div>
  );
}

function ConceptMap({ graph }) {
  const nameById = Object.fromEntries(graph.nodes.map((n) => [n.id, n.name]));
  const report = graph.report || {};
  const dropped = report.dropped_cycle_edges?.length || 0;
  const unresolved = report.unresolved_prerequisites?.length || 0;
  const review = report.review_pages || [];
  const placeholder = report.model === "fake";
  return (
    <div style={{ marginTop: "1rem" }}>
      <h4>Concept map ({graph.nodes.length} concepts)</h4>
      {placeholder && (
        <p style={{ color: "crimson", fontWeight: "bold" }}>
          These are PLACEHOLDER concepts from the fake test model, not real extraction. Set LLM_PROVIDER in
          backend/.env, then run python -m app.db.reprocess for this book.
        </p>
      )}
      {graph.nodes.length === 0 ? (
        <p style={{ color: "#666" }}>No concepts were found in this chapter.</p>
      ) : (
        <ul>
          {graph.nodes.map((n) => {
            const needs = graph.edges
              .filter((e) => e.concept_id === n.id)
              .map((e) => nameById[e.prerequisite_id]);
            return (
              <li key={n.id}>
                {n.name}{" "}
                <small style={{ color: "#666" }}>(p. {n.pages.join(", ")})</small>
                {needs.length > 0 && (
                  <div style={{ fontSize: "0.85rem", color: "#444" }}>
                    needs: {needs.join(", ")}
                  </div>
                )}
              </li>
            );
          })}
        </ul>
      )}
      {review.length > 0 && (
        <p style={{ fontSize: "0.85rem", color: "crimson" }}>
          {review.length === 1 ? "1 page looks" : `${review.length} pages look`} incomplete (page{" "}
          {review.map((r) => r.page).join(", ")}): the text was long but no concepts were found. A clearer
          scan may help - upload the chapter again.
        </p>
      )}
      {(dropped > 0 || unresolved > 0) && (
        <p style={{ fontSize: "0.85rem", color: "#a60" }}>
          {dropped > 0 && `${dropped} link(s) were skipped because they formed a loop. `}
          {unresolved > 0 &&
            `${unresolved} prerequisite(s) mentioned in the text don't match any concept in this chapter.`}
        </p>
      )}
    </div>
  );
}

export default function TeacherLibrary() {
  const [books, setBooks] = useState([]);
  const [selectedBookId, setSelectedBookId] = useState(null);
  const [selectedChapterId, setSelectedChapterId] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const [search, setSearch] = useState("");
  const [newChapterTitle, setNewChapterTitle] = useState("");
  const [graph, setGraph] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [chapterMatches, setChapterMatches] = useState({}); // my chapter id -> matches in other books
  const [dismissed, setDismissed] = useState([]); // base book ids hidden right away (the server remembers them too)
  const [isAdmin, setIsAdmin] = useState(false); // may also delete official books and chapters

  useEffect(() => {
    fetchMe().then((me) => setIsAdmin(!!me.is_admin)).catch(() => {});
  }, []);

  const selectedBook = books.find((b) => b.id === selectedBookId) || null;
  const selectedChapter =
    selectedBook?.chapters?.find((c) => c.id === selectedChapterId) || null;
  const anyProcessing = !!selectedBook?.chapters?.some(
    (c) => c.status === "processing",
  );
  const referenceBooks = books.filter((b) => b.is_reference);
  const myBooks = books.filter((b) => !b.is_reference);

  useEffect(() => {
    const timer = setTimeout(loadBooks, search ? 250 : 0);
    return () => clearTimeout(timer);
  }, [search]);

  // Variant suggestions for the selected book (own books only), refreshed as chapters finish.
  const readyChapters = selectedBook?.chapters?.filter((c) => c.status === "ready").length || 0;
  useEffect(() => {
    setSuggestions([]);
    setChapterMatches({});
    if (!selectedBook || selectedBook.is_reference || readyChapters === 0) return undefined;
    let cancelled = false;
    fetchChapterMatches(selectedBook.id)
      .then((list) => !cancelled && setChapterMatches(Object.fromEntries(list.map((c) => [c.chapter_id, c.matches]))))
      .catch(() => {});
    fetchVariantSuggestions(selectedBook.id)
      .then((list) => !cancelled && setSuggestions(list.filter((s) => !dismissed.includes(s.book.id))))
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [selectedBook?.id, selectedBook?.variant_of_id, readyChapters, dismissed]);

  async function handleConfirmVariant(baseId) {
    try {
      await confirmVariant(selectedBook.id, baseId);
      await loadBooks();
      setStatusMessage("Saved. This book is now marked as a variant.");
    } catch (err) {
      setStatusMessage(`Error: ${err.message}`);
    }
  }

  async function handleDismissVariant(baseId) {
    setDismissed((d) => [...d, baseId]);
    try {
      await dismissVariantSuggestion(selectedBook.id, baseId);
    } catch (err) {
      setStatusMessage(`Error: ${err.message}`);
    }
  }

  const canDelete = (book) => !book.is_reference || isAdmin;

  async function handleDeleteBook() {
    const book = selectedBook;
    const what = book.is_reference ? "this OFFICIAL book" : "this book";
    if (!window.confirm(`Delete ${what} (${book.subject}) with all its chapters? Students linked to it will lose access. This cannot be undone.`)) return;
    try {
      await (book.is_reference ? adminDeleteBook(book.id) : deleteMyBook(book.id));
      setSelectedBookId(null);
      setSelectedChapterId(null);
      await loadBooks();
      setStatusMessage("Book deleted.");
    } catch (err) {
      setStatusMessage(`Couldn't delete the book: ${err.message}`);
    }
  }

  async function handleDeleteChapter(ch) {
    if (!window.confirm(`Delete chapter ${ch.sequence_num}: ${ch.title}? This cannot be undone.`)) return;
    try {
      await (selectedBook.is_reference
        ? adminDeleteChapter(selectedBook.id, ch.id)
        : deleteMyChapter(selectedBook.id, ch.id));
      if (selectedChapterId === ch.id) setSelectedChapterId(null);
      await loadBooks();
      setStatusMessage("Chapter deleted.");
    } catch (err) {
      setStatusMessage(`Couldn't delete the chapter: ${err.message}`);
    }
  }

  async function handleClearVariant() {
    try {
      await clearVariant(selectedBook.id);
      await loadBooks();
    } catch (err) {
      setStatusMessage(`Error: ${err.message}`);
    }
  }

  // Load the concept map whenever a finished chapter is selected.
  useEffect(() => {
    setGraph(null);
    if (!selectedBook || !selectedChapter || selectedChapter.status !== "ready") {
      return undefined;
    }
    let cancelled = false;
    fetchChapterGraph(selectedBook.id, selectedChapter.id)
      .then((g) => !cancelled && setGraph(g))
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [selectedBook?.id, selectedChapter?.id, selectedChapter?.status]);

  // While a chapter is processing in the background, refresh every few seconds.
  useEffect(() => {
    if (!anyProcessing) return undefined;
    const timer = setInterval(loadBooks, 3000);
    return () => clearInterval(timer);
  }, [anyProcessing]);

  async function loadBooks() {
    try {
      setBooks(await fetchBooks(search.trim() ? { q: search.trim() } : {}));
    } catch (err) {
      setStatusMessage(`Couldn't load books: ${err.message}`);
    }
  }

  function selectBook(book) {
    setSelectedBookId(book.id);
    setSelectedChapterId(null);
  }

  async function handleBookCreated(created) {
    setSearch("");
    setBooks(await fetchBooks());
    setSelectedBookId(created.id);
    setSelectedChapterId(null);
    setStatusMessage("Book created. Upload the whole textbook, or add chapters one by one.");
  }

  function handleUseExisting(book) {
    setSearch("");
    setSelectedBookId(book.id);
    setSelectedChapterId(null);
    setStatusMessage("This book is already in the library. Link it to your students below - no upload needed.");
  }

  async function handleCreateChapter(e) {
    e.preventDefault();
    if (!selectedBook || !newChapterTitle.trim()) return;
    try {
      await createChapter(selectedBook.id, {
        title: newChapterTitle.trim(),
        sequence_num: (selectedBook.chapters?.length || 0) + 1,
      });
      await loadBooks(); // refetch so the chapter list stays correct when switching books
      setNewChapterTitle("");
      setStatusMessage("Chapter added.");
    } catch (err) {
      setStatusMessage(`Error: ${err.message}`);
    }
  }

  async function handleFileUpload(e) {
    const file = e.target.files?.[0];
    if (!file || !selectedBook || !selectedChapter) return;
    setUploading(true);
    setStatusMessage("Uploading...");
    try {
      const chapter = await uploadChapterPages(
        selectedBook.id,
        selectedChapter.id,
        file,
      );
      setStatusMessage(
        chapter.status === "ready"
          ? "This is the same file as before, so nothing needed to be redone."
          : "Upload received. Processing in the background - you can keep working.",
      );
      await loadBooks();
    } catch (err) {
      setStatusMessage(`Upload failed: ${err.message}`);
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  async function handleRetry(chapter) {
    try {
      await retryChapter(selectedBook.id, chapter.id);
      setStatusMessage("Retrying...");
      await loadBooks();
    } catch (err) {
      setStatusMessage(`Retry failed: ${err.message}`);
    }
  }

  const statusLabel = (ch) => {
    if (ch.status === "processing") return " - processing...";
    if (ch.status === "ready") return " - ready";
    if (ch.status === "failed") return " - failed";
    return " - no file yet";
  };

  const bookItem = (b) => (
    <li
      key={b.id}
      onClick={() => selectBook(b)}
      style={{
        cursor: "pointer",
        fontWeight: selectedBookId === b.id ? "bold" : "normal",
      }}
    >
      {b.board} - {b.class_name} - {b.subject} ({b.publisher}
      {b.edition ? `, ${b.edition}` : ""})
    </li>
  );

  return (
    <div style={{ padding: "1.5rem" }}>
      <h2>Content Library</h2>
      {statusMessage && <p style={{ color: "blue" }}>{statusMessage}</p>}

      <ChapterRequests refreshKey={books.length} />

      <NewBookWizard onCreated={handleBookCreated} onUseExisting={handleUseExisting} />

      <input
        placeholder="Search the library (e.g. 'class 9 science ncert')"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        style={{ width: "100%", maxWidth: "28rem", marginBottom: "1rem" }}
      />

      <div style={{ display: "flex", gap: "2rem" }}>
        <div style={{ width: "40%" }}>
          <h3>Official (reference) books</h3>
          {referenceBooks.length === 0 ? (
            <p style={{ color: "#666" }}>{search ? "No official books match." : "None loaded yet."}</p>
          ) : (
            <ul>{referenceBooks.map(bookItem)}</ul>
          )}
          <h3>My books</h3>
          {myBooks.length === 0 ? (
            <p style={{ color: "#666" }}>You haven't added any books.</p>
          ) : (
            <ul>{myBooks.map(bookItem)}</ul>
          )}
        </div>

        {selectedBook && (
          <div style={{ width: "60%" }}>
            <h3>
              Chapters for {selectedBook.subject}
              {selectedBook.is_reference ? (isAdmin ? " (official)" : " (official, read-only)") : ""}
            </h3>
            {canDelete(selectedBook) && (
              <p>
                <button type="button" onClick={handleDeleteBook} style={{ color: "crimson" }}>
                  Delete this book
                </button>
              </p>
            )}
            {!selectedBook.is_reference && (
              <VariantBanner
                book={selectedBook}
                books={books}
                suggestions={suggestions}
                onConfirm={handleConfirmVariant}
                onClear={handleClearVariant}
                onDismiss={handleDismissVariant}
              />
            )}
            <LinkToRoom book={selectedBook} />
            <ul>
              {selectedBook.chapters?.map((ch) => (
                <li
                  key={ch.id}
                  onClick={() => setSelectedChapterId(ch.id)}
                  style={{
                    cursor: selectedBook.is_reference ? "default" : "pointer",
                    fontWeight: selectedChapter?.id === ch.id ? "bold" : "normal",
                  }}
                >
                  Ch {ch.sequence_num}: {ch.title}
                  <span style={{ color: ch.status === "failed" ? "crimson" : "#666" }}>
                    {statusLabel(ch)}
                  </span>
                  {(chapterMatches[ch.id] || []).slice(0, 1).map((m) => (
                    <div key={m.book.id} style={{ fontSize: "0.85rem", color: "#245" }}>
                      {m.kind === "same" ? "Identical to" : "An edition of"}{" "}
                      {m.chapter_title ? `"${m.chapter_title}"` : "a chapter"} in {m.book.class_name}{" "}
                      {m.book.subject} ({m.book.publisher}){m.book.is_reference ? ", official" : ""}
                    </div>
                  ))}
                  {canDelete(selectedBook) && ch.status !== "processing" && (
                    <button
                      type="button"
                      style={{ marginLeft: "0.5rem", color: "crimson" }}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteChapter(ch);
                      }}
                    >
                      Delete
                    </button>
                  )}
                  {ch.status === "failed" && (
                    <>
                      <div style={{ color: "crimson", fontSize: "0.85rem" }}>
                        {ch.error_message}
                      </div>
                      {!selectedBook.is_reference && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleRetry(ch);
                          }}
                        >
                          Retry
                        </button>
                      )}
                    </>
                  )}
                </li>
              ))}
            </ul>

            {graph && <ConceptMap graph={graph} />}

            {!selectedBook.is_reference && (
              <>
                <WholeBookUpload book={selectedBook} onDone={loadBooks} />
                <p style={{ marginTop: "1rem" }}>Or add a chapter at a time:</p>
                <form onSubmit={handleCreateChapter} style={{ marginTop: "1rem" }}>
                  <input
                    placeholder="New chapter title"
                    value={newChapterTitle}
                    onChange={(e) => setNewChapterTitle(e.target.value)}
                    required
                  />
                  <button type="submit">Add Chapter</button>
                </form>

                {selectedChapter && (
                  <div
                    style={{
                      marginTop: "1.5rem",
                      padding: "1rem",
                      backgroundColor: "#f9f9f9",
                    }}
                  >
                    <h4>Upload pages for {selectedChapter.title}</h4>
                    <input
                      type="file"
                      accept="application/pdf,image/*"
                      onChange={handleFileUpload}
                      disabled={uploading || selectedChapter.status === "processing"}
                    />
                    {selectedChapter.status === "processing" && (
                      <p>Processing OCR & concepts... this page refreshes by itself.</p>
                    )}
                    {selectedChapter.status === "ready" && (
                      <p style={{ color: "#666" }}>
                        Uploading a different file replaces this chapter's pages.
                      </p>
                    )}
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
</file>

<file path="frontend/src/teacher/WholeBookUpload.jsx">
import React, { useState } from "react";
import { planWholeBook, confirmWholeBook } from "../api/content";

// Upload the whole textbook as one PDF, review the chapter split, then confirm. Nothing is
// processed until the teacher confirms.
export default function WholeBookUpload({ book, onDone }) {
  const [plan, setPlan] = useState(null); // { draft_id, page_count }
  const [rows, setRows] = useState([]);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");

  async function handleFile(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setBusy(true);
    setMessage("Reading the PDF...");
    try {
      const p = await planWholeBook(book.id, file);
      setPlan(p);
      setRows(p.proposed_chapters);
      setMessage(
        p.proposed_chapters.length
          ? `The PDF has ${p.page_count} pages. We split it using its bookmarks - check the page ranges.`
          : `The PDF has ${p.page_count} pages and no bookmarks. Add each chapter with its page range.`,
      );
    } catch (err) {
      setMessage(err.message);
    } finally {
      setBusy(false);
      e.target.value = "";
    }
  }

  const update = (i, key, value) =>
    setRows(rows.map((r, j) => (j === i ? { ...r, [key]: value } : r)));

  async function handleConfirm() {
    setBusy(true);
    try {
      const chapters = rows.map((r) => ({
        title: r.title,
        start_page: Number(r.start_page),
        end_page: Number(r.end_page),
      }));
      const created = await confirmWholeBook(book.id, plan.draft_id, chapters);
      setPlan(null);
      setRows([]);
      setMessage(`Started processing ${created.length} chapter(s). Their status updates below.`);
      await onDone();
    } catch (err) {
      setMessage(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={{ marginTop: "1.5rem", padding: "1rem", backgroundColor: "#f4f9f4" }}>
      <h4>Upload the whole textbook</h4>
      {!plan && (
        <input type="file" accept="application/pdf" onChange={handleFile} disabled={busy} />
      )}
      {message && <p style={{ color: "blue" }}>{message}</p>}
      {plan && (
        <>
          <table>
            <thead>
              <tr><th>Chapter title</th><th>From page</th><th>To page</th><th /></tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={i}>
                  <td><input value={r.title} onChange={(e) => update(i, "title", e.target.value)} /></td>
                  <td><input type="number" min="1" max={plan.page_count} value={r.start_page}
                    onChange={(e) => update(i, "start_page", e.target.value)} style={{ width: "5rem" }} /></td>
                  <td><input type="number" min="1" max={plan.page_count} value={r.end_page}
                    onChange={(e) => update(i, "end_page", e.target.value)} style={{ width: "5rem" }} /></td>
                  <td><button type="button" onClick={() => setRows(rows.filter((_, j) => j !== i))}>Remove</button></td>
                </tr>
              ))}
            </tbody>
          </table>
          <p>
            <button type="button" onClick={() => setRows([...rows, { title: "", start_page: 1, end_page: 1 }])}>
              Add chapter
            </button>{" "}
            <button type="button" onClick={handleConfirm} disabled={busy || rows.length === 0}>
              Confirm and process {rows.length} chapter(s)
            </button>{" "}
            <button type="button" onClick={() => { setPlan(null); setMessage(""); }}>Cancel</button>
          </p>
        </>
      )}
    </div>
  );
}
</file>

<file path="frontend/src/App.jsx">
import { Navigate, Route, Routes } from "react-router-dom";
import LoginPage from "./auth/LoginPage.jsx";
import SignupPage from "./auth/SignupPage.jsx";
import ParentDashboard from "./parent/ParentDashboard.jsx";
import ProtectedRoute from "./shared/ProtectedRoute.jsx";
import Landing from "./shared/Landing.jsx";
import StudentDashboard from "./student/StudentDashboard.jsx";
import TeacherDashboard from "./teacher/TeacherDashboard.jsx";
import RoomDetail from "./teacher/RoomDetail.jsx";

// Phase 2 content library
import TeacherLibrary from "./teacher/TeacherLibrary.jsx";

const guard = (role, el) => (
  <ProtectedRoute roles={[role]}>{el}</ProtectedRoute>
);

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />

      {/* Teacher Routes */}
      <Route path="/teacher" element={guard("teacher", <TeacherDashboard />)} />
      <Route
        path="/teacher/rooms/:roomId"
        element={guard("teacher", <RoomDetail />)}
      />
      <Route
        path="/teacher/library"
        element={guard("teacher", <TeacherLibrary />)}
      />

      {/* Student Routes */}
      <Route path="/student" element={guard("student", <StudentDashboard />)} />

      {/* Parent Routes */}
      <Route path="/parent" element={guard("parent", <ParentDashboard />)} />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
</file>

<file path="frontend/src/main.jsx">
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.jsx";
import "./shared/theme.css";
import { AuthProvider } from "./auth/AuthContext.jsx";
ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>,
);
</file>

<file path="frontend/.env.example">
VITE_API_URL=http://localhost:8000
</file>

<file path="frontend/.gitignore">
# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

node_modules
dist
dist-ssr
*.local

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
.DS_Store
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?
</file>

<file path="frontend/eslint.config.js">
import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import { defineConfig, globalIgnores } from 'eslint/config'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{js,jsx}'],
    extends: [
      js.configs.recommended,
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      globals: globals.browser,
      parserOptions: { ecmaFeatures: { jsx: true } },
    },
  },
])
</file>

<file path="frontend/index.html">
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>frontend</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Poppins:wght@500;600&display=swap"
      rel="stylesheet"
    />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
</file>

<file path="frontend/package.json">
{
  "name": "frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "lint": "eslint .",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^19.2.8",
    "react-dom": "^19.2.8",
    "react-router-dom": "^7.18.4",
    "supertokens-web-js": "^0.16.0"
  },
  "devDependencies": {
    "@eslint/js": "^10.0.1",
    "@types/react": "^19.2.18",
    "@types/react-dom": "^19.2.7",
    "@vitejs/plugin-react": "^6.1.1",
    "eslint": "^10.10.0",
    "eslint-plugin-react-hooks": "^7.1.1",
    "eslint-plugin-react-refresh": "^0.5.6",
    "globals": "^17.12.0",
    "vite": "^8.3.0"
  }
}
</file>

<file path="frontend/vite.config.js">
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
})
</file>

<file path=".gitignore">
.env
*.env.local
venv/
.venv/
__pycache__/
.pytest_cache/
node_modules/
dist/
firebase-service-account.json
*.sqlite
backend/storage/
</file>

</files>
