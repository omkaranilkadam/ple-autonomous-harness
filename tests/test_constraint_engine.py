#!/usr/bin/env python3
"""
tests/test_constraint_engine.py - Unit & Hard-Gate Tests for Cold-Read Constraint Engine
Tests:
1. Darcy-Weisbach head loss vs pump curve rejection and auto-healing
2. Fluid flow Laminar vs Critical vs Turbulent "Knee" detection
3. Terzaghi consolidation settlement with Preconsolidation Knee (Cr vs Cc) and 25mm limit
4. Footing geometry back-tracking optimization
5. Electrical feeder ampacity & voltage drop cold-read gate
6. Simulation of the G=0 Hard-Cliff
"""
import pytest
from constraint_engine import ColdReadConstraintEngine, FeasibilityResult

def test_pipe_feasibility_pass():
    """Feasible 6-inch pipe for 350 gpm clears pump curve and velocity limit."""
    res = ColdReadConstraintEngine.check_pipe_and_pump_feasibility(
        flow_gpm=350.0,
        length_ft=250.0,
        proposed_diameter_in=6.0,
        pump_shutoff_head_ft=120.0,
        pump_design_flow_gpm=500.0,
        pump_design_head_ft=85.0,
        auto_heal=False
    )
    assert res.passed is True
    assert res.demand < res.capacity
    assert res.margin > 0
    assert "TURBULENT" in res.regime

def test_pipe_feasibility_reject_and_g0_cliff():
    """Undersized 1.5-inch pipe for 500 gpm produces catastrophic head loss exceeding pump curve."""
    res = ColdReadConstraintEngine.check_pipe_and_pump_feasibility(
        flow_gpm=500.0,
        length_ft=400.0,
        proposed_diameter_in=1.5,
        pump_shutoff_head_ft=120.0,
        pump_design_flow_gpm=500.0,
        pump_design_head_ft=85.0,
        auto_heal=False
    )
    assert res.passed is False
    assert res.demand > res.capacity
    assert "exceeds available pump head" in res.failure_reason

    # Verify G=0 Cliff behavior
    cliff = ColdReadConstraintEngine.simulate_g0_cliff(nominal_score=0.8850, gate_results=[res])
    assert cliff["final_score"] == 0.0
    assert cliff["cliff_triggered"] is True
    assert "G=0 Cliff" in cliff["cliff_reason"]

def test_pipe_feasibility_auto_heal_backtracking():
    """Undersized 2-inch pipe is automatically back-tracked to 6-inch to clear pump curve."""
    res = ColdReadConstraintEngine.check_pipe_and_pump_feasibility(
        flow_gpm=400.0,
        length_ft=300.0,
        proposed_diameter_in=2.0,
        pump_shutoff_head_ft=120.0,
        pump_design_flow_gpm=500.0,
        pump_design_head_ft=85.0,
        auto_heal=True
    )
    assert res.passed is True
    assert res.healed is True
    assert res.healed_parameters["recommended_diameter_in"] >= 4.0
    assert res.demand <= res.capacity

    # Post-healing cliff check
    cliff = ColdReadConstraintEngine.simulate_g0_cliff(nominal_score=0.8850, gate_results=[res])
    assert cliff["final_score"] == 0.8850
    assert cliff["cliff_triggered"] is False

def test_laminar_vs_turbulent_knee_detector():
    """Detects laminar regime at low flow and turbulent regime at normal flow."""
    # Low flow in 4-inch pipe => Laminar Re < 2300
    res_lam = ColdReadConstraintEngine.check_pipe_and_pump_feasibility(
        flow_gpm=2.0,
        length_ft=50.0,
        proposed_diameter_in=4.0,
        auto_heal=False
    )
    assert "LAMINAR" in res_lam.regime

    # Normal flow in 4-inch pipe => Fully turbulent Re > 4000
    res_turb = ColdReadConstraintEngine.check_pipe_and_pump_feasibility(
        flow_gpm=200.0,
        length_ft=50.0,
        proposed_diameter_in=4.0,
        auto_heal=False
    )
    assert "TURBULENT" in res_turb.regime

def test_footing_settlement_knee_crossing_and_25mm_gate():
    """Small footing crossing the preconsolidation knee exceeds 25mm settlement limit."""
    res = ColdReadConstraintEngine.check_footing_settlement_feasibility(
        column_load_kips=350.0,
        proposed_footing_width_ft=6.0, # 6x6 ft is too small for 350 kips
        proposed_footing_length_ft=6.0,
        clay_layer_thickness_ft=15.0,
        depth_to_clay_midpoint_z_ft=8.0,
        initial_effective_stress_psf=2200.0,
        preconsolidation_stress_pc_psf=3000.0, # Preconsolidation knee
        initial_void_ratio_e0=0.85,
        compression_index_cc=0.38,
        recompression_index_cr=0.045,
        max_allowable_settlement_in=1.0, # 25.4 mm
        auto_heal=False
    )
    assert res.passed is False
    assert "CROSSING_THE_KNEE" in res.regime
    assert res.demand > 25.4 # Settlement exceeds 25.4 mm
    assert "exceeds 25mm limit" in res.failure_reason

    # G=0 Cliff triggers on settlement failure
    cliff = ColdReadConstraintEngine.simulate_g0_cliff(nominal_score=0.8250, gate_results=[res])
    assert cliff["final_score"] == 0.0
    assert cliff["cliff_triggered"] is True

def test_footing_settlement_auto_heal_backtracking():
    """Small 6x6 footing is automatically enlarged until consolidation settlement <= 25.4 mm."""
    res = ColdReadConstraintEngine.check_footing_settlement_feasibility(
        column_load_kips=350.0,
        proposed_footing_width_ft=6.0,
        proposed_footing_length_ft=6.0,
        clay_layer_thickness_ft=15.0,
        depth_to_clay_midpoint_z_ft=8.0,
        initial_effective_stress_psf=2200.0,
        preconsolidation_stress_pc_psf=3000.0,
        initial_void_ratio_e0=0.85,
        compression_index_cc=0.38,
        recompression_index_cr=0.045,
        max_allowable_settlement_in=1.0,
        auto_heal=True
    )
    assert res.passed is True
    assert res.healed is True
    assert res.healed_parameters["healed_width_ft"] > 6.0
    assert res.demand <= 25.4 # Settlement healed under 25.4 mm

def test_electrical_feeder_feasibility_and_healing():
    """Undersized wire for continuous feeder is healed to NEC code-compliant size."""
    res = ColdReadConstraintEngine.check_electrical_feeder_feasibility(
        design_current_amps=220.0,
        proposed_wire_size="#4", # #4 is ~85A, severely undersized for 220A
        feeder_length_ft=300.0,
        system_voltage_v=480.0,
        auto_heal=True
    )
    assert res.passed is True
    assert res.healed is True
    assert res.demand <= 3.0 # Voltage drop <= 3.0%

def test_g0_cliff_composite_simulation():
    """Multiple gates: if any gate fails, score is 0.0; if all gates pass, score is preserved."""
    gate_pass = FeasibilityResult(passed=True, gate_name="Gate1", demand=10, capacity=20, margin=10, regime="OK")
    gate_fail = FeasibilityResult(passed=False, gate_name="Gate2", demand=30, capacity=20, margin=-10, regime="FAIL", failure_reason="Exceeded limit")

    # With failure => 0.0
    res_fail = ColdReadConstraintEngine.simulate_g0_cliff(nominal_score=0.8500, gate_results=[gate_pass, gate_fail])
    assert res_fail["final_score"] == 0.0
    assert res_fail["cliff_triggered"] is True

    # Without failure => preserved
    res_ok = ColdReadConstraintEngine.simulate_g0_cliff(nominal_score=0.8500, gate_results=[gate_pass])
    assert res_ok["final_score"] == 0.8500
    assert res_ok["cliff_triggered"] is False
