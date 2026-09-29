from app.llm import get_llm_provider

if __name__ == "__main__":
    p = get_llm_provider()
    print("model:", p.model_name)
    print(p.complete_json("Reply with a JSON object only.", 'Return this JSON: {"ok": true}'))