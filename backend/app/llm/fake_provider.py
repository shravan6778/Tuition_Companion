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
        if user.startswith("TUTOR DOUBT\n"):  # an explanation built from the first shown page
            m = re.search(r"\[P1\][^\n]*\n(.+?)(?:\n\n\[P|\nKEY CONCEPTS|\nREFRESHER|\Z)", user, flags=re.DOTALL)
            if not m:
                return json.dumps({"answer": "", "refresher": None, "used_sources": [], "cannot_answer": True})
            words = m.group(1).split()[:30]
            refresher = "Earlier idea: " + user.split("REFRESHER", 1)[1].split("\n- ", 1)[1].split(":", 1)[0] if "REFRESHER" in user else None
            return json.dumps({"answer": "The page explains it like this: " + " ".join(words), "refresher": refresher,
                               "used_sources": ["P1"], "cannot_answer": False})
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
