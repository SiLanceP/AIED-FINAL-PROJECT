"""Grade calculation (Criteria for Mastery) across all 3 levels (12 exercises, 3 hints each = 36 hints max).

| Grade | Condition                                                      |
|-------|----------------------------------------------------------------|
| A     | All 12 exercises passed, 0 hints and 0 incorrect attempts      |
| B+    | 1-12 hints (or 0 hints but at least one incorrect attempt)     |
| B     | 13-21 hints                                                    |
| C     | 22-29 hints                                                    |
| D     | 30-36 hints, or any exercise ended with the solution revealed  |
"""

FINISHED = {"passed", "failed_revealed"}


def _int(value, lo=0, hi=None):
    try:
        v = max(lo, int(value))
    except (TypeError, ValueError):
        v = lo
    return min(v, hi) if hi is not None else v


def _level_totals(data, ex_count, max_hints_per_ex):
    """Compute (earned_points, level_hints, revealed_exercise_count) for a level."""
    exercises = data.get("exercises") if isinstance(data.get("exercises"), dict) else None
    max_level_hints = ex_count * max_hints_per_ex
    if exercises is not None:
        pts = 0
        hints_sum = 0
        has_ex_hints = False
        revealed_count = 0
        for i in range(1, ex_count + 1):
            ex_data = exercises.get(str(i)) or {}
            st = ex_data.get("status")
            if st == "passed":
                pts += 1
            elif st == "failed_revealed":
                revealed_count += 1
            if "hints" in ex_data:
                has_ex_hints = True
                hints_sum += _int(ex_data.get("hints"), 0, max_hints_per_ex)
            elif isinstance(ex_data.get("hintLog"), list) and ex_data["hintLog"]:
                has_ex_hints = True
                hints_sum += min(len(ex_data["hintLog"]), max_hints_per_ex)
        level_hints = hints_sum if has_ex_hints else _int(data.get("hints"), 0, max_level_hints)
        return pts, level_hints, revealed_count

    # Legacy fallback when only level-level stats are sent
    status = data.get("status")
    level_hints = _int(data.get("hints"), 0, max_level_hints)
    if status == "passed":
        return ex_count, level_hints, 0
    if status == "failed_revealed":
        return 0, level_hints, ex_count
    return 0, level_hints, 0


def compute_grade(levels, level_numbers, max_hints=3, ex_counts=None):
    """``levels``: {"1": {"status": str, "wrong": int, "hints": int, "exercises": {...}}, ...}.

    ``max_hints`` is the maximum hints allowed per EXERCISE (default 3 -> 12 per level, 36 total).
    """
    ex_counts = ex_counts or {}
    rows, total_hints, total_wrong, revealed_levels, complete = [], 0, 0, [], True
    total_points, max_points, max_total_hints, total_reveals = 0, 0, 0, 0

    for n in level_numbers:
        ex_count = ex_counts.get(n, 4)
        max_level_hints = ex_count * max_hints
        max_points += ex_count
        max_total_hints += max_level_hints

        data = levels.get(str(n)) or {}
        status = data.get("status") or "locked"
        wrong = _int(data.get("wrong"))
        pts, level_hints, rev_count = _level_totals(data, ex_count, max_hints)

        total_points += pts
        total_hints += level_hints
        total_wrong += wrong
        total_reveals += rev_count
        if rev_count > 0 or status == "failed_revealed":
            revealed_levels.append(n)
        if status not in FINISHED:
            complete = False
        rows.append({
            "level": n,
            "status": status,
            "hints": level_hints,
            "max_hints": max_level_hints,
            "wrong": wrong,
            "points": pts,
            "max_points": ex_count,
            "reveals": rev_count,
        })

    if not complete:
        grade, reason = None, "Finish all levels to receive a grade."
    elif revealed_levels:
        grade, reason = "D", f"The solution was revealed on level(s) {', '.join(map(str, revealed_levels))}."
    elif total_hints == 0 and total_wrong == 0:
        grade, reason = "A", "Perfect! All 12 exercises passed with no hints and no incorrect attempts."
    elif total_hints == 0:
        grade, reason = "B+", f"No hints used, but {total_wrong} incorrect attempt(s)."
    elif total_hints <= 12:
        grade, reason = "B+", f"{total_hints} hint(s) used (1–12 out of {max_total_hints})."
    elif total_hints <= 21:
        grade, reason = "B", f"{total_hints} hints used (13–21 out of {max_total_hints})."
    elif total_hints <= 29:
        grade, reason = "C", f"{total_hints} hints used (22–29 out of {max_total_hints})."
    else:
        grade, reason = "D", f"{total_hints} hints used (30–{max_total_hints} out of {max_total_hints})."

    return {
        "grade": grade,
        "reason": reason,
        "complete": complete,
        "total_hints": total_hints,
        "max_total_hints": max_total_hints,
        "total_wrong": total_wrong,
        "total_points": total_points,
        "max_points": max_points,
        "total_reveals": total_reveals,
        "revealed_levels": revealed_levels,
        "levels": rows,
    }
