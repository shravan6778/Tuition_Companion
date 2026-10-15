import json
import re


class FakeLLMProvider:
    """Deterministic stand-in for tests and keyless local dev.
    Builds up to 3 chained concepts from the first lines of the text after the 'TEXT:' marker."""

    model_name = "fake"

    def complete_json(self, system: str, user: str) -> str:
        if user.startswith("PERSONALIZATION BRIEFING"):
            return self._briefing(user)
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
        if user.startswith("TUTOR DOUBT\n"):  # an explanation built from the first shown page
            m = re.search(r"\[P1\][^\n]*\n(.+?)(?:\n\n\[P|\nKEY CONCEPTS|\nREFRESHER|\Z)", user, flags=re.DOTALL)
            if not m:
                return json.dumps({"answer": "", "refresher": None, "used_sources": [], "cannot_answer": True})
            words = m.group(1).split()[:30]
            refresher = "Earlier idea: " + user.split("REFRESHER", 1)[1].split("\n- ", 1)[1].split(":", 1)[0] if "REFRESHER" in user else None
            return json.dumps({"answer": "The page explains it like this: " + " ".join(words), "refresher": refresher,
                               "used_sources": ["P1"], "cannot_answer": False})
        if user.startswith("QUIZ QUESTION (MCQ)"):
            return self._quiz_mcq(user)
        if user.startswith("QUIZ QUESTION (SHORT_ANSWER)"):
            return self._quiz_short_answer(user)
        if user.startswith("SHORT ANSWER GRADING\n"):
            return self._grade_short_answer(user)
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

    def _briefing(self, user_prompt: str) -> str:
        session_lines = re.findall(r"- \[(\d{4}-\d{2}-\d{2})\] ([^\n]+)", user_prompt)
        weak_lines = re.findall(r"- WEAK: ([^(\n]+?)\s*\(([^)]+)\)", user_prompt)
        risk_lines = re.findall(r"- AT_RISK: ([^(\n]+?)\s*\(([^)]+)\)", user_prompt)
        allowed = re.findall(r"ALLOWED_CONCEPT: ([^\n]+)", user_prompt)

        if session_lines:
            dt, note = session_lines[0]
            last_cov = f"In the most recent session ({dt}), the student worked on: {note[:160]}"
        else:
            last_cov = "No prior teacher session logs have been recorded yet; recent activity comes from checks and quizzes."

        weak_parts = []
        focus_concepts = []
        for name, reason in weak_lines[:3]:
            clean_name = name.strip()
            weak_parts.append(f"{clean_name} ({reason.strip()})")
            if clean_name in allowed and clean_name not in focus_concepts:
                focus_concepts.append(clean_name)
        for name, reason in risk_lines[:2]:
            clean_name = name.strip()
            weak_parts.append(f"{clean_name} is at risk ({reason.strip()})")
            if clean_name in allowed and len(focus_concepts) < 3 and clean_name not in focus_concepts:
                focus_concepts.append(clean_name)

        if not weak_parts:
            weak_summary = "No concepts are currently flagged as weak or at risk."
        else:
            weak_summary = "Current areas needing attention: " + "; ".join(weak_parts) + "."

        if not focus_concepts and allowed:
            focus_concepts = [allowed[0].strip()]

        if focus_concepts:
            suggested = (
                f"Focus today's session on {', '.join(focus_concepts)} to reinforce foundational understanding "
                "before moving to dependent topics."
            )
        else:
            suggested = "Begin with a diagnostic check on the student's current chapter to establish baseline mastery."

        return json.dumps({
            "last_covered": last_cov,
            "weak_areas": weak_summary,
            "suggested_focus": suggested,
            "focus_concepts": focus_concepts,
        })

    def _quiz_mcq(self, user: str) -> str:
        qtype = (re.search(r"^QUESTION TYPE:\s*(.+)$", user, re.M) or [None, "RECALL"])[1].strip().lower()
        name = (re.search(r"^PRIMARY CONCEPT:\s*(.+)$", user, re.M) or [None, "this concept"])[1].strip()
        desc = (re.search(r"^PRIMARY DESCRIPTION:\s*(.+)$", user, re.M) or [None, ""])[1].strip()
        rel = (re.search(r"^RELATED CONCEPT:\s*(.+)$", user, re.M) or [None, ""])[1].strip()
        page = user.partition("PRIMARY PAGE")[2].partition("\n")[2].partition("\n\n")[0].strip()
        asked = len(re.findall(r"^- ", user.partition("QUESTIONS ALREADY ASKED:\n")[2], re.M))
        right = (desc or " ".join(page.split()[:12]) or f"The textbook idea of {name}")[:180]
        if qtype == "cross_concept" and rel:
            stem = f"How does {name} connect with {rel} according to the page?" if not asked else f"Which statement links {name} and {rel}?"
        elif qtype == "application":
            stem = f"In a practical example from the page, how is {name} applied?" if not asked else f"Which situation best illustrates {name}?"
        else:
            stem = f"According to the page, which statement best describes {name}?" if not asked else f"What key fact does the page state about {name}?"
        return json.dumps({
            "question": stem,
            "options": [
                right,
                f"{name} is unrelated to the chapter topic",
                f"{name} only applies outside this subject",
                f"The page states the opposite of {name}",
            ],
            "correct_index": 0,
            "explanation": f"The page explains {name} as: {right}.",
        })

    def _quiz_short_answer(self, user: str) -> str:
        qtype = (re.search(r"^QUESTION TYPE:\s*(.+)$", user, re.M) or [None, "CROSS_CONCEPT"])[1].strip().lower()
        name = (re.search(r"^PRIMARY CONCEPT:\s*(.+)$", user, re.M) or [None, "this concept"])[1].strip()
        desc = (re.search(r"^PRIMARY DESCRIPTION:\s*(.+)$", user, re.M) or [None, ""])[1].strip()
        rel = (re.search(r"^RELATED CONCEPT:\s*(.+)$", user, re.M) or [None, ""])[1].strip()
        rel_desc = (re.search(r"^RELATED DESCRIPTION:\s*(.+)$", user, re.M) or [None, ""])[1].strip()
        if qtype == "cross_concept" and rel:
            q = f"Explain how {name} and {rel} are related based on the textbook pages."
            expected = f"{name} ({desc or 'primary concept'}) connects to {rel} ({rel_desc or 'related concept'}) as described on the pages."
        else:
            q = f"Explain how {name} works using an example or principle from the page."
            expected = desc or f"{name} operates according to the principles stated on the textbook page."
        return json.dumps({
            "question": q[:450],
            "expected_answer": expected[:550],
            "explanation": f"Grounded in the textbook section on {name}" + (f" and {rel}." if rel else "."),
        })

    def _grade_short_answer(self, user: str) -> str:
        expected = (re.search(r"^EXPECTED ANSWER:\s*(.+)$", user, re.M) or [None, ""])[1].strip().lower()
        student = (re.search(r"^STUDENT ANSWER:\s*(.+)$", user, re.M) or [None, ""])[1].strip().lower()
        exp_words = {w for w in re.findall(r"[a-z0-9]+", expected) if len(w) > 3}
        stu_words = {w for w in re.findall(r"[a-z0-9]+", student) if len(w) > 3}
        if not stu_words or "wrong" in student or "idk" in student or "do not know" in student or "unrelated" in student:
            return json.dumps({
                "score": 0.0,
                "feedback": "The response does not state the key concept described in the textbook.",
            })
        overlap = len(exp_words & stu_words) / max(1, min(len(exp_words), 4))
        score = round(min(1.0, max(0.85 if overlap >= 0.4 else 0.3, overlap)), 2)
        feedback = (
            "Good explanation covering the key textbook points."
            if score >= 0.8
            else "Partially mentions the topic but misses key details from the expected answer."
        )
        return json.dumps({"score": score, "feedback": feedback})