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
