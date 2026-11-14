#!/usr/bin/env python3
"""
Unit tests for Cycle 4 TaskContext features:
1. S1 Invalidate-and-recompute
2. S7 Cadence and Hard-Reset
3. S8 Pre-done Triplet Critique
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
from harness import TaskContext

class TestHarnessV2Features(unittest.TestCase):

    def test_s1_invalidate_and_recompute(self):
        ctx = TaskContext(task_id="test_recompute")
        ctx.working_memory = [
            {"key": "raw_length_mm", "val": 7315.2, "turn": 1},
            {"key": "span_ft", "val": 24.0, "depends_on": ["raw_length_mm"], "turn": 2},
            {"key": "wind_force_lbs", "val": 12000.0, "depends_on": ["span_ft"], "turn": 2},
            {"key": "unrelated_var", "val": 42.0, "turn": 1}
        ]
        
        # When S1 trips on raw_length_mm, all dependent variables must be purged
        purged = ctx.invalidate_and_recompute("raw_length_mm")
        self.assertIn("raw_length_mm", purged)
        self.assertIn("span_ft", purged)
        self.assertIn("wind_force_lbs", purged)
        
        # Only unrelated_var should remain
        remaining_keys = [m["key"] for m in ctx.working_memory]
        self.assertIn("unrelated_var", remaining_keys)
        self.assertNotIn("span_ft", remaining_keys)
        self.assertNotIn("wind_force_lbs", remaining_keys)

    def test_s7_cadence_and_hard_reset(self):
        ctx = TaskContext(task_id="test_s7")
        ctx.constraints = {"building": "A2", "risk_category": "III", "velocity_mph": 115}
        ctx.compute_constraint_hash()
        
        # Turn 1: normal
        ctx.step_turn()
        self.assertEqual(ctx.turns, 1)
        
        # Turn 2: normal
        ctx.step_turn()
        self.assertEqual(ctx.turns, 2)
        
        # Tamper constraints during turn 2
        ctx.constraints["risk_category"] = "I"  # Contamination / drift!
        
        # Turn 3: S7 check triggers automatically and performs hard-reset
        msg = ctx.step_turn()
        self.assertEqual(ctx.turns, 3)
        self.assertIsNotNone(msg)
        self.assertIn("S7 Hard-Reset performed", msg)
        
        # Verify constraints were restored to pristine initial state
        self.assertEqual(ctx.constraints["risk_category"], "III")
        self.assertTrue(ctx.verify_constraint_integrity())

    def test_s8_pre_done_critique(self):
        ctx = TaskContext(task_id="test_s8")
        prompt = "Provide an engineering memo and an Excel takeoff schedule for chilled water piping."
        
        # Only memo provided -> incomplete
        files = ["piping_memo.md"]
        ok, missing = ctx.pre_done_judge_critique(prompt, files)
        self.assertFalse(ok)
        self.assertTrue(any("Schedule" in m for m in missing))
        
        # Both provided -> complete
        files = ["piping_memo.md", "pipe_schedule.xlsx"]
        ok, missing = ctx.pre_done_judge_critique(prompt, files)
        self.assertTrue(ok)
        self.assertEqual(len(missing), 0)

if __name__ == "__main__":
    unittest.main()
