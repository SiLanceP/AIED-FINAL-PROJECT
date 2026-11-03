"""Grade calculation (Criteria for Mastery), based on totals across all 5 levels.

| Grade | Condition                                                   |
|-------|-------------------------------------------------------------|
| A     | all levels passed, 0 hints and 0 incorrect attempts         |
| B+    | 1-5 hints  (or 0 hints but at least one incorrect attempt)  |
| B     | 6-9 hints                                                   |
| C     | 10-12 hints                                                 |
| D     | 13-15 hints, or any level ended with the solution revealed  |
"""

FINISHED = {"passed", "failed_revealed"}


def _int(value, lo=0, hi=None):
    try:
        v = max(lo, int(value))
    except (TypeError, ValueError):
        v = lo
    return min(v, hi) if hi is not None else v


def compute_grade(levels, level_numbers, max_hints=3):
    """``levels``: {"1": {"status": str, "wrong": int, "hints": int}, ...} from localStorage."""
    rows, total_hints, total_wrong, revealed, complete = [], 0, 0, [], True
    for n in level_numbers:
        data = levels.get(str(n)) or {}
        status = data.get("status") or "locked"
        hints = _int(data.get("hints"), 0, max_hints)
        wrong = _int(data.get("wrong"))
        total_hints += hints
        total_wrong += wrong
        if status == "failed_revealed":
            revealed.append(n)
        if status not in FINISHED:
            complete = False
        rows.append({"level": n, "status": status, "hints": hints, "wrong": wrong})

    if not complete:
        grade, reason = None, "Finish all levels to receive a grade."
    elif revealed:
        grade, reason = "D", f"The solution was revealed on level(s) {', '.join(map(str, revealed))}."
    elif total_hints == 0 and total_wrong == 0:
        grade, reason = "A", "Perfect! All levels passed with no hints and no incorrect attempts."
    elif total_hints == 0:
        grade, reason = "B+", f"No hints used, but {total_wrong} incorrect attempt(s)."
    elif total_hints <= 5:
        grade, reason = "B+", f"{total_hints} hint(s) used (1-5)."
    elif total_hints <= 9:
        grade, reason = "B", f"{total_hints} hints used (6-9)."
    elif total_hints <= 12:
        grade, reason = "C", f"{total_hints} hints used (10-12)."
    else:
        grade, reason = "D", f"{total_hints} hints used (13-15)."

    return {
        "grade": grade,
        "reason": reason,
        "complete": complete,
        "total_hints": total_hints,
        "total_wrong": total_wrong,
        "revealed_levels": revealed,
        "levels": rows,
    }
