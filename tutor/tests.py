import json
from django.test import TestCase

from ai.providers import AIUnavailable, resolve_config
from lessons.models import Exercise, Level
from tutor.checker import evaluate
from tutor.grading import compute_grade


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

    def test_alternative_correct_answers_pass(self):
        # Level 1 Exercise 2: single quotes, lowercase, and missing punctuation should all pass
        ex1_2 = Exercise.objects.get(level__number=1, number=2)
        self.assertTrue(
            evaluate(ex1_2, ["print('Hello, World!')", "print('I am coding in Python.')"])["correct"]
        )
        self.assertTrue(
            evaluate(ex1_2, ['print("hello world")', 'print("i am coding in python")'])["correct"]
        )
        # Level 1 Exercise 4: missing colon should still pass
        ex1_4 = Exercise.objects.get(level__number=1, number=4)
        self.assertTrue(evaluate(ex1_4, ['print("level", 1)'])["correct"])
        # Wrong words or wrong numbers must still fail
        self.assertFalse(evaluate(ex1_4, ['print("level", 2)'])["correct"])
        # Level 3 Exercise 4: prompt inside input() should still pass
        ex3_4 = Exercise.objects.get(level__number=3, number=4)
        self.assertTrue(
            evaluate(ex3_4, ['birth_year = int(input("Birth year: "))'])["correct"]
        )

    def test_checker_constraints_and_safety(self):
        ex1_2 = Exercise.objects.get(level__number=1, number=2)
        self.assertEqual(evaluate(ex1_2, ["", 'print("x")'])["kind"], "incomplete")
        self.assertEqual(evaluate(ex1_2, ["print(", 'print("x")'])["kind"], "syntax")
        self.assertEqual(evaluate(ex1_2, ["import os", 'print("x")'])["kind"], "forbidden")
        self.assertEqual(evaluate(ex1_2, ['eval("1")', 'print("x")'])["kind"], "forbidden")

        ex3_4 = Exercise.objects.get(level__number=3, number=4)
        # Hard-coding 2008 without input() violates must_call: input
        res = evaluate(ex3_4, ["birth_year = 2008"])
        self.assertFalse(res["correct"])
        self.assertEqual(res["kind"], "constraint")

    def test_tutor_flow_actions_and_fallback_hints(self):
        # 1st wrong -> retry; 2nd wrong -> suggest_hint; wrong after 3 hints -> reveal
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

        # Hint falls back to static hint when AI is turned off
        h = self.client.post(
            "/api/hint/1/",
            json.dumps({
                "exercise": 2,
                "answers": ["x = 1", "y = 2"],
                "hints": 0,
                "ai": {"provider": "none"},
            }),
            content_type="application/json",
        ).json()
        self.assertTrue(h["consumed"])
        self.assertEqual(h["source"], "builtin")
        self.assertEqual(h["hint_number"], 1)

        # Reveal is blocked before 3 hints, allowed at 3 hints
        self.assertEqual(
            self.client.post(
                "/api/reveal/1/",
                json.dumps({"exercise": 2, "hints": 2}),
                content_type="application/json",
            ).status_code,
            400,
        )
        rev = self.client.post(
            "/api/reveal/1/",
            json.dumps({
                "exercise": 2,
                "answers": ["x = 1", "y = 2"],
                "hints": 3,
                "ai": {"provider": "none"},
            }),
            content_type="application/json",
        ).json()
        self.assertEqual(len(rev["solution_lines"]), 2)

    def test_grading_rules_and_points(self):
        nums = [1, 2, 3]
        all_passed_ex = {str(i): {"status": "passed"} for i in range(1, 5)}
        mk = lambda hints_per_level, wrong=0, status="passed": {
            str(n): {"status": status, "hints": h, "wrong": wrong, "exercises": dict(all_passed_ex)}
            for n, h in zip(nums, hints_per_level)
        }
        info_a = compute_grade(mk([0, 0, 0], wrong=0), nums)
        self.assertEqual(info_a["grade"], "A")
        self.assertEqual(info_a["total_points"], 12)
        self.assertEqual(info_a["max_points"], 12)

        self.assertEqual(compute_grade(mk([0, 0, 0], wrong=2), nums)["grade"], "B+")
        self.assertEqual(compute_grade(mk([2, 2, 1]), nums)["grade"], "B+")  # 5
        self.assertEqual(compute_grade(mk([2, 2, 2]), nums)["grade"], "B")   # 6
        self.assertEqual(compute_grade(mk([3, 3, 3]), nums)["grade"], "B")   # 9
        self.assertEqual(compute_grade(mk([4, 3, 3]), nums, max_hints=5)["grade"], "C")  # 10
        self.assertEqual(compute_grade(mk([4, 4, 4]), nums, max_hints=5)["grade"], "C")  # 12
        self.assertEqual(compute_grade(mk([5, 4, 4]), nums, max_hints=5)["grade"], "D")  # 13

        lvs = mk([0, 0, 0])
        lvs["2"]["status"] = "failed_revealed"
        lvs["2"]["exercises"]["4"] = {"status": "failed_revealed"}
        info_d = compute_grade(lvs, nums)
        self.assertEqual(info_d["grade"], "D")
        self.assertEqual(info_d["total_points"], 11)

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
