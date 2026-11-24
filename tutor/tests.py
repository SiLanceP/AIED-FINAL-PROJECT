import json
from django.test import TestCase

from ai.providers import AIUnavailable, resolve_config
from lessons.models import Exercise, Level
from tutor.checker import evaluate
from tutor.grading import compute_grade
from tutor.views import _leaks_solution


class TutorTests(TestCase):
    def test_seed_and_reference_solutions_pass(self):
        self.assertEqual(Level.objects.count(), 3)
        self.assertEqual(Exercise.objects.count(), 12)
        for level in Level.objects.prefetch_related("exercises"):
            self.assertEqual(level.exercises.count(), 4)
        for ex in Exercise.objects.select_related("level"):
            res = evaluate(ex, ex.solution_lines)
            self.assertTrue(
                res["correct"],
                f"Level {ex.level.number} Exercise {ex.number} failed: {res}",
            )
            # Every exercise must have 3 static hints and none should leak the exact solution line
            self.assertEqual(len(ex.static_hints), 3, f"Expected 3 static hints for {ex}")
            for i, hint in enumerate(ex.static_hints, 1):
                self.assertTrue(hint.strip(), f"Empty static hint {i} for {ex}")
                self.assertFalse(
                    _leaks_solution(hint, ex),
                    f"Static hint {i} for {ex} leaks the full solution: {hint}",
                )

    def test_all_twelve_exercises_error_handling_and_valid_variants(self):
        """Verify valid variants pass AND common beginner mistakes are rejected for all 12 exercises."""
        cases = [
            # (level, ex, valid_variants, invalid_cases_with_expected_kind)
            (
                1, 1,
                [
                    ['print("Hello, Python!")'],
                    ["print('hello python')"],  # lenient capitalization/punctuation
                ],
                [
                    (["print(Hello)"], "constraint"),
                    (['Print("Hello, Python!")'], "constraint"),
                    (['print("Hello, Python!"'], "syntax"),
                    (['print("Hi")'], "output"),
                    ([""], "incomplete"),
                ],
            ),
            (
                1, 2,
                [
                    ['print("Hello, World!")', 'print("I am coding in Python.")'],
                    ['print("hello world")', 'print("i am coding in python")'],
                ],
                [
                    (['print("Hello, World!")', ""], "incomplete"),
                    (['print("Hello, World!")', "print(123)"], "constraint"),
                    (['print("Hello, World!")', 'print("wrong")'], "output"),
                ],
            ),
            (
                1, 3,
                [
                    ['print("2026")'],
                    ["print('2026')"],
                ],
                [
                    (["print(2026)"], "constraint"),  # missing quotes around 2026 MUST fail
                    (['print("2025")'], "output"),
                    (["2026"], "constraint"),
                ],
            ),
            (
                1, 4,
                [
                    ['print("Level:", 1)'],
                    ['print("level", 1)'],
                ],
                [
                    (['print("Level: 1")'], "constraint"),  # single string instead of str + int
                    (['print("Level:", "1")'], "constraint"),  # "1" is str, must be int 1
                    (['print("Level:", 2)'], "output"),
                ],
            ),
            (
                2, 1,
                [
                    ['city = "Manila"'],
                    ["city = 'manila'"],
                ],
                [
                    (["city = Manila"], "runtime"),
                    (['town = "Manila"'], "constraint"),
                    (["city = 123"], "constraint"),
                    (['city = "Cebu"'], "output"),
                ],
            ),
            (
                2, 2,
                [
                    ["age = 17", "is_student = True"],
                ],
                [
                    (['age = "17"', "is_student = True"], "constraint"),   # string instead of int
                    (["age = 17", 'is_student = "True"'], "constraint"),   # string instead of bool
                    (["age = 17", "is_student = true"], "runtime"),        # lowercase true
                    (["age = 18", "is_student = True"], "output"),
                ],
            ),
            (
                2, 3,
                [
                    ['print("Order:", food)', 'print("Pesos:", price)'],
                    ['print("order", food)', 'print("pesos", price)'],
                ],
                [
                    (['print("Order: Adobo")', 'print("Pesos: 120")'], "constraint"),  # hardcoded
                    (['print("Order:", "food")', 'print("Pesos:", "price")'], "constraint"),
                ],
            ),
            (
                2, 4,
                [
                    ["total = burger + drink"],
                    ["total = drink + burger"],
                ],
                [
                    (["total = 115"], "constraint"),            # hardcoded instead of burger + drink
                    (["total = 85 + 30"], "constraint"),        # didn't use variable names
                    (["total = burger - drink"], "constraint"), # wrong operator
                ],
            ),
            (
                3, 1,
                [
                    ["name = input()"],
                    ['name = input("Your name: ")'],
                ],
                [
                    (['name = "Ana"'], "constraint"),  # hardcoded without input()
                    (["input()"], "constraint"),       # forgot to assign to name
                ],
            ),
            (
                3, 2,
                [
                    ["color = input()"],
                    ['color = input("Color: ")'],
                ],
                [
                    (['color = "blue"'], "constraint"),
                    (["fav = input()"], "constraint"),
                ],
            ),
            (
                3, 3,
                [
                    ["age = int(age_text)"],
                ],
                [
                    (["age = age_text"], "constraint"),   # forgot int()
                    (["age = int(17)"], "constraint"),    # hardcoded instead of age_text
                    (["age = 17"], "constraint"),
                ],
            ),
            (
                3, 4,
                [
                    ["birth_year = int(input())"],
                    ['birth_year = int(input("Birth year: "))'],
                ],
                [
                    (["birth_year = input()"], "constraint"),  # forgot int()
                    (["birth_year = 2008"], "constraint"),     # hardcoded
                ],
            ),
        ]

        for lvl, ex_num, valids, invalids in cases:
            ex = Exercise.objects.get(level__number=lvl, number=ex_num)
            for ans in valids:
                res = evaluate(ex, ans)
                self.assertTrue(res["correct"], f"L{lvl}E{ex_num} valid {ans} failed: {res}")
            for ans, exp_kind in invalids:
                res = evaluate(ex, ans)
                self.assertFalse(res["correct"], f"L{lvl}E{ex_num} invalid {ans} unexpectedly passed!")
                self.assertEqual(
                    res["kind"], exp_kind,
                    f"L{lvl}E{ex_num} invalid {ans}: expected kind={exp_kind}, got {res}",
                )

    def test_checker_safety(self):
        ex1_2 = Exercise.objects.get(level__number=1, number=2)
        self.assertEqual(evaluate(ex1_2, ["import os", 'print("x")'])["kind"], "forbidden")
        self.assertEqual(evaluate(ex1_2, ['eval("1")', 'print("x")'])["kind"], "forbidden")

    def test_hints_and_reveal_across_all_twelve_exercises(self):
        """Verify all 3 hints + solution reveal work cleanly via HTTP API on every exercise."""
        for ex in Exercise.objects.select_related("level"):
            wrong_answers = ["x = 1"] * ex.blank_count
            for hint_idx in range(3):
                h = self.client.post(
                    f"/api/hint/{ex.level.number}/",
                    json.dumps({
                        "exercise": ex.number,
                        "answers": wrong_answers,
                        "hints": hint_idx,
                        "ai": {"provider": "none"},
                    }),
                    content_type="application/json",
                ).json()
                self.assertTrue(h["consumed"], f"Hint {hint_idx+1} not consumed for {ex}")
                self.assertEqual(h["hint_number"], hint_idx + 1)
                self.assertEqual(h["hint"], ex.static_hints[hint_idx])

            # 4th hint must be rejected
            self.assertEqual(
                self.client.post(
                    f"/api/hint/{ex.level.number}/",
                    json.dumps({
                        "exercise": ex.number,
                        "answers": wrong_answers,
                        "hints": 3,
                        "ai": {"provider": "none"},
                    }),
                    content_type="application/json",
                ).status_code,
                400,
            )

            # Reveal at 3 hints returns exact solution lines that pass evaluation
            rev = self.client.post(
                f"/api/reveal/{ex.level.number}/",
                json.dumps({
                    "exercise": ex.number,
                    "answers": wrong_answers,
                    "hints": 3,
                    "ai": {"provider": "none"},
                }),
                content_type="application/json",
            ).json()
            self.assertEqual(rev["solution_lines"], ex.solution_lines)
            self.assertTrue(evaluate(ex, rev["solution_lines"])["correct"])

    def test_tutor_flow_actions(self):
        # 1st wrong -> retry; 2nd wrong -> suggest_hint; wrong after 3 hints -> automatic reveal
        r1 = self.client.post(
            "/api/check/1/",
            json.dumps({"exercise": 2, "answers": ["x = 1", "y = 2"], "wrong": 0, "hints": 0}),
            content_type="application/json",
        ).json()
        self.assertEqual(r1["action"], "retry")
        r2 = self.client.post(
            "/api/check/1/",
            json.dumps({"exercise": 2, "answers": ["x = 1", "y = 2"], "wrong": 1, "hints": 0}),
            content_type="application/json",
        ).json()
        self.assertEqual(r2["action"], "suggest_hint")
        r3 = self.client.post(
            "/api/check/1/",
            json.dumps({"exercise": 2, "answers": ["x = 1", "y = 2"], "wrong": 2, "hints": 3}),
            content_type="application/json",
        ).json()
        self.assertEqual(r3["action"], "reveal")

        # Reveal is blocked before 3 hints
        self.assertEqual(
            self.client.post(
                "/api/reveal/1/",
                json.dumps({"exercise": 2, "hints": 2}),
                content_type="application/json",
            ).status_code,
            400,
        )

    def test_grading_rules_and_points(self):
        nums = [1, 2, 3]

        def mk(hints_per_level, wrong=0, reveals_count=0):
            out = {}
            rem_rev = reveals_count
            for n, total_h in zip(nums, hints_per_level):
                rem_h = total_h
                exs = {}
                lv_rev = 0
                for i in range(1, 5):
                    h = min(3, rem_h)
                    rem_h -= h
                    if rem_rev > 0:
                        st = "failed_revealed"
                        rem_rev -= 1
                        lv_rev += 1
                    else:
                        st = "passed"
                    exs[str(i)] = {"status": st, "hints": h}
                out[str(n)] = {
                    "status": "failed_revealed" if lv_rev else "passed",
                    "hints": total_h,
                    "wrong": wrong,
                    "exercises": exs,
                }
            return out

        info_a = compute_grade(mk([0, 0, 0], wrong=0), nums)
        self.assertEqual(info_a["grade"], "A")
        self.assertEqual(info_a["total_points"], 12)
        self.assertEqual(info_a["max_points"], 12)
        self.assertEqual(info_a["max_total_hints"], 36)

        self.assertEqual(compute_grade(mk([0, 0, 0], wrong=2), nums)["grade"], "B+")
        self.assertEqual(compute_grade(mk([1, 0, 0]), nums)["grade"], "B+")   # 1
        self.assertEqual(compute_grade(mk([4, 4, 4]), nums)["grade"], "B+")   # 12
        self.assertEqual(compute_grade(mk([5, 4, 4]), nums)["grade"], "B")    # 13
        self.assertEqual(compute_grade(mk([7, 7, 7]), nums)["grade"], "B")    # 21
        self.assertEqual(compute_grade(mk([8, 7, 7]), nums)["grade"], "C")    # 22
        self.assertEqual(compute_grade(mk([10, 10, 9]), nums)["grade"], "C")  # 29
        self.assertEqual(compute_grade(mk([10, 10, 10]), nums)["grade"], "D") # 30
        self.assertEqual(compute_grade(mk([12, 12, 12]), nums)["grade"], "D") # 36

        info_d = compute_grade(mk([3, 0, 0], reveals_count=1), nums)
        self.assertEqual(info_d["grade"], "D")
        self.assertEqual(info_d["total_points"], 11)
        self.assertEqual(info_d["total_hints"], 3)

    def test_ai_local_url_restriction(self):
        with self.assertRaises(AIUnavailable):
            resolve_config({"provider": "ollama", "base_url": "https://evil.example.com/v1"})
        cfg = resolve_config({"provider": "auto"})
        self.assertEqual(cfg.kind, "auto")
        cfg_keyless = resolve_config({"provider": "pollinations"})
        self.assertEqual(cfg_keyless.kind, "cloud")
        self.assertEqual(cfg_keyless.api_key, "anonymous")

    def test_pages_render(self):
        for url in ["/", "/level/1/", "/level/2/", "/level/3/", "/settings/", "/report/"]:
            self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(self.client.get("/level/4/").status_code, 404)
        self.assertEqual(self.client.get("/level/5/").status_code, 404)

    def test_unlock_all_flag_in_template(self):
        self.assertContains(self.client.get("/"), "window.UNLOCK_ALL = false;")
        with self.settings(UNLOCK_ALL=True):
            self.assertContains(self.client.get("/"), "window.UNLOCK_ALL = true;")

    def test_interactive_terminal_and_post_pass_explanations(self):
        # Level 3 enables interactive terminal; Levels 1 and 2 keep standard output
        self.assertContains(self.client.get("/level/1/"), "interactiveTerminal: false,")
        self.assertContains(self.client.get("/level/2/"), "interactiveTerminal: false,")
        self.assertContains(self.client.get("/level/3/"), "interactiveTerminal: true,")

        # Interactive harness pauses cleanly when input() needs user input, then completes once provided
        import importlib.util
        from django.conf import settings
        spec = importlib.util.spec_from_file_location("harness", settings.HARNESS_PATH)
        harness = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(harness)

        code = 'name = input("Name: ")\ncolor = input()\nprint(name, "likes", color)\n'
        r1 = harness.run_code(code, "", echo=True, interactive=True)
        self.assertTrue(r1["need_input"])
        self.assertEqual(r1["prompt"], "Name: ")
        self.assertIsNone(r1["error"])

        r2 = harness.run_code(code, "Lance", echo=True, interactive=True)
        self.assertTrue(r2["need_input"])
        self.assertEqual(r2["output"], "Name: Lance\n")
        self.assertEqual(r2["prompt"], "")

        r3 = harness.run_code(code, "Lance\nblue", echo=True, interactive=True)
        self.assertFalse(r3["need_input"])
        self.assertIsNone(r3["error"])
        self.assertIn("Lance likes blue", r3["output"])

        # Every exercise returns a post-pass explanation on /api/check/ and /api/explain/
        for ex in Exercise.objects.select_related("level"):
            self.assertTrue(ex.pass_explanation.strip(), f"Missing pass_explanation for {ex}")
            chk = self.client.post(
                f"/api/check/{ex.level.number}/",
                json.dumps({"exercise": ex.number, "answers": ex.solution_lines, "wrong": 0, "hints": 0}),
                content_type="application/json",
            ).json()
            self.assertTrue(chk["correct"])
            self.assertEqual(chk["explanation"], ex.pass_explanation)

            exp = self.client.post(
                f"/api/explain/{ex.level.number}/",
                json.dumps({"exercise": ex.number, "answers": ex.solution_lines, "ai": {"provider": "none"}}),
                content_type="application/json",
            ).json()
            self.assertEqual(exp["explanation"], ex.pass_explanation)
            self.assertEqual(exp["source"], "builtin")
