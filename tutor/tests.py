import json
from django.test import TestCase

from ai.providers import AIUnavailable, resolve_config
from lessons.models import Exercise, Level
from tutor.checker import evaluate
from tutor.grading import compute_grade


class TutorTests(TestCase):
    def test_seed_and_reference_solutions_pass(self):
        self.assertEqual(Level.objects.count(), 5)
        for ex in Exercise.objects.select_related("level"):
            res = evaluate(ex, ex.solution_lines)
            self.assertTrue(res["correct"], f"Level {ex.level.number} failed: {res}")

    def test_alternative_correct_answers_pass(self):
        # Level 1: single quotes instead of double quotes
        ex1 = Exercise.objects.get(level__number=1)
        self.assertTrue(evaluate(ex1, ["print('Hello, World!')", "print('I am learning Python.')"])["correct"])
        # Level 3: different prompt inside input() should still pass
        ex3 = Exercise.objects.get(level__number=3)
        self.assertTrue(evaluate(ex3, ["birth_year = int(input())"])["correct"])

    def test_checker_constraints_and_safety(self):
        ex1 = Exercise.objects.get(level__number=1)
        self.assertEqual(evaluate(ex1, ["", 'print("x")'])["kind"], "incomplete")
        self.assertEqual(evaluate(ex1, ["print(", 'print("x")'])["kind"], "syntax")
        self.assertEqual(evaluate(ex1, ["import os", 'print("x")'])["kind"], "forbidden")
        self.assertEqual(evaluate(ex1, ['eval("1")', 'print("x")'])["kind"], "forbidden")

        ex3 = Exercise.objects.get(level__number=3)
        # Hard-coding 2008 without input() violates must_call: input
        res = evaluate(ex3, ["birth_year = 2008"])
        self.assertFalse(res["correct"])
        self.assertEqual(res["kind"], "constraint")

    def test_tutor_flow_actions_and_fallback_hints(self):
        # 1st wrong -> retry; 2nd wrong -> suggest_hint; wrong after 3 hints -> reveal
        r1 = self.client.post("/api/check/1/", json.dumps({"answers": ["x = 1", "y = 2"], "wrong": 0, "hints": 0}),
                              content_type="application/json").json()
        self.assertEqual(r1["action"], "retry")
        r2 = self.client.post("/api/check/1/", json.dumps({"answers": ["x = 1", "y = 2"], "wrong": 1, "hints": 0}),
                              content_type="application/json").json()
        self.assertEqual(r2["action"], "suggest_hint")
        r3 = self.client.post("/api/check/1/", json.dumps({"answers": ["x = 1", "y = 2"], "wrong": 2, "hints": 3}),
                              content_type="application/json").json()
        self.assertEqual(r3["action"], "reveal")

        # Hint falls back to static hint when AI is turned off
        h = self.client.post("/api/hint/1/", json.dumps({
            "answers": ["x = 1", "y = 2"], "hints": 0, "ai": {"provider": "none"},
        }), content_type="application/json").json()
        self.assertTrue(h["consumed"])
        self.assertEqual(h["source"], "builtin")
        self.assertEqual(h["hint_number"], 1)

        # Reveal is blocked before 3 hints, allowed at 3 hints
        self.assertEqual(self.client.post("/api/reveal/1/", json.dumps({"hints": 2}),
                                          content_type="application/json").status_code, 400)
        rev = self.client.post("/api/reveal/1/", json.dumps({
            "answers": ["x = 1", "y = 2"], "hints": 3, "ai": {"provider": "none"},
        }), content_type="application/json").json()
        self.assertEqual(len(rev["solution_lines"]), 2)

    def test_grading_rules(self):
        nums = [1, 2, 3, 4, 5]
        mk = lambda hints_per_level, wrong=0, status="passed": {
            str(n): {"status": status, "hints": h, "wrong": wrong} for n, h in zip(nums, hints_per_level)
        }
        self.assertEqual(compute_grade(mk([0, 0, 0, 0, 0], wrong=0), nums)["grade"], "A")
        self.assertEqual(compute_grade(mk([0, 0, 0, 0, 0], wrong=2), nums)["grade"], "B+")
        self.assertEqual(compute_grade(mk([1, 1, 1, 1, 1]), nums)["grade"], "B+")  # 5
        self.assertEqual(compute_grade(mk([2, 2, 2, 0, 0]), nums)["grade"], "B")   # 6
        self.assertEqual(compute_grade(mk([3, 3, 3, 0, 0]), nums)["grade"], "B")   # 9
        self.assertEqual(compute_grade(mk([2, 2, 2, 2, 2]), nums)["grade"], "C")   # 10
        self.assertEqual(compute_grade(mk([3, 3, 3, 3, 0]), nums)["grade"], "C")   # 12
        self.assertEqual(compute_grade(mk([3, 3, 3, 3, 1]), nums)["grade"], "D")   # 13
        lvs = mk([0, 0, 0, 0, 0])
        lvs["3"]["status"] = "failed_revealed"
        self.assertEqual(compute_grade(lvs, nums)["grade"], "D")

    def test_ai_local_url_restriction(self):
        with self.assertRaises(AIUnavailable):
            resolve_config({"provider": "ollama", "base_url": "https://evil.example.com/v1"})
        cfg = resolve_config({"provider": "ollama"})
        self.assertEqual(cfg.kind, "local")

    def test_pages_render(self):
        for url in ["/", "/level/1/", "/level/5/", "/settings/", "/report/"]:
            self.assertEqual(self.client.get(url).status_code, 200)
