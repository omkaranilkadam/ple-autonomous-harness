#!/usr/bin/env python3
"""
tests/test_harness.py - Unit tests for PLEHarness
"""
import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from harness import PLEHarness, SilentFailureDetectors, ToolLayer, TaskContext


def test_s1_unit_drift():
    d = SilentFailureDetectors()
    assert d.s1_unit_drift(100, "mm", "mm").ok
    assert not d.s1_unit_drift(100, "mm", "m").ok
    assert not d.s1_unit_drift(100, "kN", "N").ok
    print("PASS: S1 unit drift")


def test_s2_callout_misread():
    d = SilentFailureDetectors()
    assert d.s2_callout_misread("2-#5", "2-#5").ok
    assert not d.s2_callout_misread("2-#5", "2-#4").ok
    print("PASS: S2 callout misread")


def test_s5_clash_clearance():
    d = SilentFailureDetectors()
    assert d.s5_clash_clearance(0.1).ok
    assert not d.s5_clash_clearance(-0.05).ok
    assert not d.s5_clash_clearance(0.005).ok  # within tolerance
    print("PASS: S5 clash clearance")


def test_s6_swallowed_error():
    d = SilentFailureDetectors()
    assert not d.s6_swallowed_error({}).ok
    assert d.s6_swallowed_error({"ok": True, "value": 42}).ok
    assert not d.s6_swallowed_error({"ok": False, "error": "fail"}).ok
    print("PASS: S6 swallowed error")


def test_s7_context_integrity():
    d = SilentFailureDetectors()
    assert d.s7_context_integrity("abc123", "abc123").ok
    assert not d.s7_context_integrity("abc123", "xyz789").ok
    print("PASS: S7 context integrity")


def test_s8_premature_done():
    d = SilentFailureDetectors()
    assert d.s8_premature_done(5, 5).ok
    assert not d.s8_premature_done(3, 5).ok
    assert not d.s8_premature_done(0, 0).ok
    print("PASS: S8 premature done")


def test_s9_judge_gaming():
    d = SilentFailureDetectors()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"data": "meaningful content here for testing purposes"}, f)
        f.flush()
        assert d.s9_judge_gaming(f.name).ok
    os.unlink(f.name)

    assert not d.s9_judge_gaming("/nonexistent/file.json").ok

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("")
        f.flush()
        assert not d.s9_judge_gaming(f.name).ok
    os.unlink(f.name)
    print("PASS: S9 judge gaming")


def test_s10_nondeterminism():
    d = SilentFailureDetectors()
    assert d.s10_nondeterminism([0.85, 0.85, 0.85]).ok
    assert not d.s10_nondeterminism([0.1, 0.9, 0.5]).ok
    print("PASS: S10 nondeterminism")


def test_s11_numeric_precision():
    d = SilentFailureDetectors()
    assert d.s11_numeric_precision(100.0, 100.5).ok
    assert not d.s11_numeric_precision(100.0, 200.0).ok
    print("PASS: S11 numeric precision")


def test_s12_cross_artifact():
    d = SilentFailureDetectors()
    consistent = {"memo": {"walls": 4}, "model": {"walls": 4}}
    assert d.s12_cross_artifact(consistent).ok

    inconsistent = {"memo": {"walls": 4}, "model": {"walls": 3}}
    assert not d.s12_cross_artifact(inconsistent).ok
    print("PASS: S12 cross-artifact consistency")


def test_task_context():
    ctx = TaskContext(task_id="test-001")
    ctx.constraints = {"load": 500, "code": "IBC-2021"}
    ctx.add_deliverable("report", False)
    ctx.add_deliverable("model", False)
    assert ctx.completion_pct == 0.0
    ctx.mark_complete("report")
    assert ctx.completion_pct == 50.0
    ctx.mark_complete("model")
    assert ctx.completion_pct == 100.0
    h1 = ctx.compute_constraint_hash()
    assert ctx.verify_constraint_integrity()
    ctx.constraints["load"] = 999
    assert not ctx.verify_constraint_integrity()
    print("PASS: TaskContext")


def test_tool_layer():
    tl = ToolLayer()
    result = tl.numeric_compute("2 + 3")
    assert result.ok
    assert result.value["value"] == 5

    result = tl.numeric_compute("sqrt(144)", {"sqrt": __import__("math").sqrt})
    assert result.ok
    assert result.value["value"] == 12.0

    result = tl.read_pdf_text("/nonexistent.pdf")
    assert not result.ok
    print("PASS: ToolLayer")


async def test_harness_solve():
    h = PLEHarness()
    with tempfile.TemporaryDirectory() as tmpdir:
        result = await h.solve("test-001", {
            "files": [],
            "deliverables": ["primary_output"],
            "constraints": {"max_load_kN": 500},
            "output_dir": tmpdir,
        })
        assert result["status"] == "completed"
        assert result["summary"]["completion"] == "100%"
    print("PASS: Harness solve")


def main():
    print("Running PLE Harness Tests")
    print("=" * 40)
    test_s1_unit_drift()
    test_s2_callout_misread()
    test_s5_clash_clearance()
    test_s6_swallowed_error()
    test_s7_context_integrity()
    test_s8_premature_done()
    test_s9_judge_gaming()
    test_s10_nondeterminism()
    test_s11_numeric_precision()
    test_s12_cross_artifact()
    test_task_context()
    test_tool_layer()
    asyncio.run(test_harness_solve())
    print("=" * 40)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()

