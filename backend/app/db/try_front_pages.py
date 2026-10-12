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
