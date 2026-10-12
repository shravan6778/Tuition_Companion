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
