"""Grade calculation (Criteria for Mastery) across all levels (3 levels × 4 exercises = 12 points total).

| Grade | Condition                                                   |
|-------|-------------------------------------------------------------|
| A     | all levels passed, 0 hints and 0 incorrect attempts         |
| B+    | 1-5 hints  (or 0 hints but at least one incorrect attempt)  |
| B     | 6-9 hints                                                   |
| C     | 10-12 hints                                                 |
| D     | 13+ hints, or any exercise ended with the solution revealed |
"""

FINISHED = {"passed", "failed_revealed"}


def _int(value, lo=0, hi=None):
    try:
        v = max(lo, int(value))
    except (TypeError, ValueError):
        v = lo
    return min(v, hi) if hi is not None else v


def _level_points(data, ex_count):
    """Compute (earned_points, revealed_exercise) for a level."""
    exercises = data.get("exercises") if isinstance(data.get("exercises"), dict) else None
    if exercises is not None:
        pts = 0
        revealed_ex = False
        for i in range(1, ex_count + 1):
            st = (exercises.get(str(i)) or {}).get("status")
            if st == "passed":
                pts += 1
            elif st == "failed_revealed":
                revealed_ex = True
        return pts, revealed_ex
    # Legacy fallback when only level status is sent
    status = data.get("status")
    if status == "passed":
        return ex_count, False
    if status == "failed_revealed":
        return 0, True
    return 0, False


def compute_grade(levels, level_numbers, max_hints=3, ex_counts=None):
    """``levels``: {"1": {"status": str, "wrong": int, "hints": int, "exercises": {...}}, ...}."""
    ex_counts = ex_counts or {}
    rows, total_hints, total_wrong, revealed, complete = [], 0, 0, [], True
    total_points, max_points = 0, 0

    for n in level_numbers:
        ex_count = ex_counts.get(n, 4)
        max_points += ex_count
        data = levels.get(str(n)) or {}
        status = data.get("status") or "locked"
        hints = _int(data.get("hints"), 0, max_hints)
        wrong = _int(data.get("wrong"))
        pts, rev_ex = _level_points(data, ex_count)
        total_points += pts
        total_hints += hints
        total_wrong += wrong
        if status == "failed_revealed" or rev_ex:
            revealed.append(n)
        if status not in FINISHED:
            complete = False
        rows.append({
            "level": n,
            "status": status,
            "hints": hints,
            "wrong": wrong,
            "points": pts,
            "max_points": ex_count,
        })

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
        grade, reason = "D", f"{total_hints} hints used (13+)."

    return {
        "grade": grade,
        "reason": reason,
        "complete": complete,
        "total_hints": total_hints,
        "total_wrong": total_wrong,
        "total_points": total_points,
        "max_points": max_points,
        "revealed_levels": revealed,
        "levels": rows,
    }
