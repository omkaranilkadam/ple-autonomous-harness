#!/usr/bin/env python3
"""
Unit tests for Advanced Physics & Engineering Computational Solvers (engineering_tools.py).
Tests:
1. Mechanical: LES mesh resolution, hydraulic network solver, CFL convergence analyzer
2. Structural: Semi-rigid diaphragm FEM deflection & classification, drag strut collector distribution
3. Civil: Terzaghi consolidation time rate, compaction acceptance ASTM
4. Electrical: Medium-voltage 3-phase fault study, conduit fill and derating
"""
import pytest
from engineering_tools import MechanicalSuite, StructuralSuite, CivilSuite, ElectricalSuite

def test_les_mesh_resolution():
    res = MechanicalSuite.les_mesh_resolution(
        heat_release_rate_kw=2500.0,
        characteristic_diameter_m=1.5,
        cell_size_dx_m=0.10
    )
    assert res["status"] == "PASS_RESOLVED"
    assert res["resolution_ratio_d_star_over_dx"] >= 10.0
    assert res["resolved_tke_pct"] >= 80.0

def test_hydraulic_network_solver():
    pipes = [
        {"id": "P-1", "flow_gpm": 250.0, "length_ft": 150.0, "diameter_in": 4.0, "c_factor": 120.0},
        {"id": "P-2", "flow_gpm": 150.0, "length_ft": 80.0, "diameter_in": 3.0, "c_factor": 120.0},
    ]
    res = MechanicalSuite.hydraulic_network_solver(pipes, static_head_ft=30.0)
    assert res["status"] == "PASS"
    assert res["total_dynamic_head_ft"] > 30.0
    assert res["max_velocity_fps"] < 10.0

def test_cfl_convergence_analyzer():
    # Stable CFL
    res = MechanicalSuite.cfl_convergence_analyzer(max_velocity_fps=20.0, grid_dx_ft=0.50, current_dt_s=0.01)
    assert res["status"] == "CONVERGENT_STABLE"
    assert res["current_cfl"] < 1.0

def test_semi_rigid_diaphragm_fem():
    res = StructuralSuite.semi_rigid_diaphragm_fem(
        span_ft=120.0,
        width_ft=80.0,
        total_lateral_kips=60.0,
        deck_gage=20,
        story_drift_in=0.40
    )
    assert res["status"] == "PASS"
    assert res["total_midspan_deflection_in"] > 0.0
    assert res["diaphragm_classification"] in ["FLEXIBLE", "SEMI_RIGID", "RIGID"]
    assert res["chord_force_kips"] > 0.0

def test_drag_strut_collector():
    res = StructuralSuite.drag_strut_collector_distribution(
        total_shear_kips=60.0,
        building_length_ft=120.0,
        wall_length_total_ft=40.0
    )
    assert res["status"] == "PASS"
    assert res["peak_collector_force_kips"] > 0.0
    assert "TS" in res["recommended_strut_size"]

def test_terzaghi_consolidation_time_rate():
    res = CivilSuite.terzaghi_consolidation_time_rate(
        clay_thickness_ft=10.0,
        cv_ft2_per_day=0.15,
        drainage="double",
        target_consolidation_pct=90.0
    )
    assert res["status"] == "PASS"
    assert res["required_time_days"] > 0.0
    assert res["required_time_months"] > 0.0

def test_compaction_acceptance():
    # Accepted compaction
    res = CivilSuite.compaction_acceptance_astm(
        dry_density_pcf=122.5,
        max_dry_density_pcf=125.0,
        moisture_content_pct=11.0,
        optimum_moisture_pct=10.5
    )
    assert res["status"] == "ACCEPTED"
    assert res["relative_compaction_pct"] >= 95.0

def test_mv_fault_study():
    res = ElectricalSuite.medium_voltage_fault_study(
        utility_mva_sc=500.0,
        xfmr_kva=2500.0,
        xfmr_z_percent=5.75,
        voltage_kv=13.8,
        cable_length_ft=800.0
    )
    assert res["status"] == "PASS"
    assert res["symmetrical_fault_current_ka"] > 0.0
    assert res["interrupting_headroom_pct"] > 0.0

def test_conduit_fill_and_derating():
    res = ElectricalSuite.conduit_fill_and_derating(
        conductor_size="4/0",
        num_conductors=4,
        conduit_type="EMT",
        ambient_temp_c=35.0
    )
    assert res["status"] == "PASS"
    assert res["actual_conduit_fill_pct"] <= 40.0
    assert res["net_derating_factor"] <= 1.0
