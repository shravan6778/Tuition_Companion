"""Speech pilot: how many KEY TERMS does each language's speech-to-text get wrong?

    python -m app.db.stt_pilot speech-pilot.csv [--items ../frontend/src/speech/pilotItems.json] [--max-error-rate 0.15] [--show-misses]

The CSV comes from the pilot page (teacher menu -> /teacher/speech-pilot, see docs/SPEECH_PILOT.md): about 10 students each speak the same
five sentences in each language; columns participant, language, item, source (browser | server), reference, transcript.
A key term counts as WRONG when it is not found in the transcript. Terms are stems, compared after Unicode normalisation, lower-casing and
dropping punctuation and zero-width joiners, so Telugu and Hindi word endings do not count as errors. A miss is a miss even if the
transcript is a near-spelling, because the grader would not credit a term that is not there: read the misses (--show-misses) before deciding
whether a language is really bad or the recognizer is just spelling a loan word differently.

For each language and source it prints the error rate and a verdict against the threshold (PILOT_MAX_KEY_TERM_ERROR_RATE, default 0.15):
  * at or under it     : plain voice answers are fine (the student reviews the text anyway);
  * over it            : either make that language "confirm before grading" (SPEECH_HOLD_LANGUAGES=te-IN: the teacher confirms the transcript
                         before it is marked) or move it to server speech-to-text (SPEECH_PROVIDER=azure, SPEECH_SERVER_LANGUAGES=te-IN, Azure
                         free tier) and run the pilot again with source=server to see whether that is really better.
Nothing is written anywhere: no database, no files."""
import argparse
import csv
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

from app.core.config import settings

DEFAULT_ITEMS = Path(__file__).resolve().parents[3] / "frontend" / "src" / "speech" / "pilotItems.json"


def normalise(text: str) -> str:
    t = unicodedata.normalize("NFC", text or "").casefold().replace("\u200c", "").replace("\u200d", "")
    t = re.sub(r"[\s\.,;:!?\"'‘’“”()\[\]\-–—।॥]+", " ", t)
    return t.strip()


def term_hit(term: str, transcript: str) -> bool:
    return normalise(term) in normalise(transcript)


def analyse(rows: list[dict], items: dict, max_error_rate: float) -> dict:
    """items: {item id: {language: {"terms": [...]}}}. Returns {(language, source): stats}."""
    stats: dict = defaultdict(lambda: {"answers": 0, "terms": 0, "wrong": 0, "misses": [], "participants": set()})
    for r in rows:
        terms = (items.get(r["item"], {}).get(r["language"]) or {}).get("terms") or []
        if not terms:
            continue
        s = stats[(r["language"], r.get("source") or "browser")]
        s["answers"] += 1
        s["participants"].add(r["participant"])
        for t in terms:
            s["terms"] += 1
            if not term_hit(t, r.get("transcript", "")):
                s["wrong"] += 1
                s["misses"].append((r["participant"], r["item"], t, r.get("transcript", "")))
    for s in stats.values():
        s["rate"] = s["wrong"] / s["terms"] if s["terms"] else 0.0
        s["ok"] = s["rate"] <= max_error_rate
        s["participants"] = len(s["participants"])
    return dict(stats)


def advice(language: str, source: str, ok: bool, server_seen: bool) -> str:
    if ok:
        return "OK for plain voice answers (the student still reviews the text)."
    if source == "server":
        return "Still over the threshold on the server: keep typing as the main route and make this language 'confirm before grading'."
    options = [f"SPEECH_HOLD_LANGUAGES={language}  (teacher confirms the transcript before it is marked)",
               f"SPEECH_PROVIDER=azure and SPEECH_SERVER_LANGUAGES={language}  (server speech-to-text, Azure free tier)"]
    note = "" if server_seen else " Run the pilot again with source=server to see whether the server version is really better."
    return "NOT ready for plain voice. Choose one: " + "; or ".join(options) + "." + note


def load_items(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {i["id"]: i for i in data["items"]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Count wrong key terms in a speech pilot CSV")
    ap.add_argument("csv_path")
    ap.add_argument("--items", default=str(DEFAULT_ITEMS))
    ap.add_argument("--max-error-rate", type=float, default=settings.pilot_max_key_term_error_rate)
    ap.add_argument("--show-misses", action="store_true")
    args = ap.parse_args(argv)
    with open(args.csv_path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    result = analyse(rows, load_items(Path(args.items)), args.max_error_rate)
    if not result:
        print("No rows matched the pilot items. Check the CSV and --items.")
        return 1
    server_seen = any(src == "server" for _, src in result)
    print(f"Threshold: at most {args.max_error_rate:.0%} of key terms wrong\n")
    for (lang, src), s in sorted(result.items()):
        print(f"{lang}  [{src}]  {s['participants']} students, {s['answers']} answers, {s['wrong']} of {s['terms']} key terms wrong = {s['rate']:.1%}  ->  {'PASS' if s['ok'] else 'FAIL'}")
        print("   " + advice(lang, src, s["ok"], server_seen))
        if args.show_misses:
            for who, item, term, heard in s["misses"]:
                print(f"     miss: {who} / {item}: wanted '{term}', heard '{heard}'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
