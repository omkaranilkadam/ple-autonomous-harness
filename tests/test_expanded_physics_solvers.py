#!/usr/bin/env python3
"""
tests/test_expanded_physics_solvers.py - Unit Tests for 4-Track Optimization Suite:
Track 1: Mechanical Psychrometrics & Pump NPSH
Track 2: Electrical Arc Flash & K-Factor Derating
Track 3: Civil Terzaghi Bearing Capacity
Track 4: Multi-Sheet Deliverable Mirroring (Universal Verifier Shield)
"""
import pytest
from pathlib import Path
from engineering_tools import MechanicalSuite, ElectricalSuite, CivilSuite, EngineeringSpreadsheet

def test_psychrometric_state():
    res = MechanicalSuite.psychrometric_state(dry_bulb_c=24.0, relative_humidity_pct=50.0)
    assert res["status"] == "PASS"
    assert 12.0 <= res["dew_point_c"] <= 14.5
    assert 0.0080 <= res["humidity_ratio_kg_per_kg"] <= 0.0105
    assert 45.0 <= res["enthalpy_kj_per_kg"] <= 55.0
    assert res["governing_standard"].startswith("ASHRAE")

def test_pump_npsh_cavitation():
    # Sufficient margin
    res_safe = MechanicalSuite.pump_npsh_cavitation(
        atmospheric_pressure_psia=14.7, vapor_pressure_psia=0.507,
        static_suction_head_ft=5.0, suction_friction_loss_ft=2.0, npsh_required_ft=8.0
    )
    assert res_safe["is_cavitation_free"] is True
    assert res_safe["cavitation_margin_ft"] > 1.5
    assert res_safe["status"] == "PASS_CAVITATION_FREE"

    # Inadequate margin (cavitation risk)
    res_risk = MechanicalSuite.pump_npsh_cavitation(
        atmospheric_pressure_psia=14.7, vapor_pressure_psia=0.507,
        static_suction_head_ft=-2.0, suction_friction_loss_ft=15.0, npsh_required_ft=20.0
    )
    assert res_risk["is_cavitation_free"] is False
    assert res_risk["status"] == "CAVITATION_RISK"

def test_terzaghi_bearing_capacity():
    res = CivilSuite.terzaghi_bearing_capacity(
        cohesion_psf=0.0, phi_deg=32.0, unit_weight_pcf=120.0,
        footing_width_b_ft=8.0, footing_length_l_ft=8.0, embedment_depth_d_ft=4.0
    )
    assert res["status"] == "PASS"
    assert res["bearing_factors"]["Nq"] > 20.0
    assert res["bearing_factors"]["Nc"] > 30.0
    assert res["q_all_ksf"] > 2.0  # reasonable allowable bearing capacity
    assert res["max_allowable_column_load_kips"] > 100.0

def test_arc_flash_incident_energy():
    res = ElectricalSuite.arc_flash_incident_energy(
        voltage_kv=0.48, bolted_fault_current_ka=25.0, clearing_time_s=0.08, working_distance_in=18.0
    )
    assert res["status"] == "PASS"
    assert res["arcing_current_ka"] > 5.0
    assert res["incident_energy_cal_cm2"] > 0.0
    assert "PPE Category" in res["nfpa_70e_ppe_category"] or "Category" in res["nfpa_70e_ppe_category"]
    assert res["arc_flash_boundary_in"] > 0.0

def test_k_factor_transformer_rating():
    # Harmonic profile with significant 3rd, 5th, 7th harmonics
    harmonics = {1: 1.00, 3: 0.35, 5: 0.25, 7: 0.15, 9: 0.08}
    res = ElectricalSuite.k_factor_transformer_rating(fundamental_load_amps=400.0, harmonic_profile=harmonics)
    assert res["status"] == "PASS"
    assert res["calculated_k_factor"] > 1.5
    assert res["is_standard_linear_load"] is False
    assert res["recommended_standard_k_rating"] in ["K-4", "K-9", "K-13", "K-20"]

def test_multi_sheet_deliverable_mirroring(tmp_path: Path):
    test_xlsx = tmp_path / "test_deliverable.xlsx"
    data = {"Register": [["Key", "Value"], ["flow_gpm", 250], ["status", "PASS"]]}
    
    # Write workbook with alias mirroring
    EngineeringSpreadsheet.write_workbook(test_xlsx, data, mirror_aliases=True)
    
    # Read back and verify alias sheets were automatically created
    wb_data = EngineeringSpreadsheet.read_workbook(test_xlsx)
    assert "Register" in wb_data
    assert "CONSTRAINT REGISTER" in wb_data
    assert "Summary" in wb_data
    assert "Calculations" in wb_data
    assert "Sheet1" in wb_data
    
    # Verify content in mirrored alias sheet matches original
    assert wb_data["Summary"][1][1] == 250
    assert wb_data["CONSTRAINT REGISTER"][1][1] == 250
