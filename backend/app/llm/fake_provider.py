import json

class FakeLLMProvider:
    """Deterministic stand-in for tests and keyless local dev."""

    model_name = "fake"

    def complete_json(self, system: str, user: str) -> str:
        text = user.split("CHAPTER TEXT:\n", 1)[-1]
        lines = []
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
                "summary": f"Key idea from the chapter: {name}",
                "prerequisites": [lines[i - 1]] if i else [],
            }
            for i, name in enumerate(lines)
        ]
        return json.dumps({"concepts": concepts})