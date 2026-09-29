from typing import Protocol


class LLMProvider(Protocol):
    model_name: str

    def complete_json(self, system: str, user: str) -> str:
        """Return the model's raw reply, expected to be a JSON object."""
        ...