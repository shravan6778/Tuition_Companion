import json


class FakeLLMProvider:
    """Deterministic stand-in for tests and keyless local dev.
    Builds up to 3 chained concepts from the first lines of the text after the 'TEXT:' marker."""

    model_name = "fake"

    def complete_json(self, system: str, user: str) -> str:
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