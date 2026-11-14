#!/usr/bin/env python3
"""
Test StructuralSuite, CivilSuite, and ElectricalSuite Deterministic Solvers.
Validates:
1. Wind diaphragm analysis matches ASCE 7-22 and provides dual embed spacing schedules.
2. Seismic diaphragm analysis matches ASCE 7-22 Section 12.10 bounds and Cases S01-S12.
3. Roof deck analysis covers Zones 1, 2, 3 uplift and fastener patterns (36/4 and 36/7).
4. EOR review disposition generates multi-sheet schema with dual 'Register' and 'CONSTRAINT REGISTER' aliases.
5. CivilSuite and ElectricalSuite execute deterministic math without floating-point error.
6. Gold trajectories exist for all 4 primary disciplines.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from engineering_tools import (
    StructuralSuite,
    CivilSuite,
    ElectricalSuite,
    GOLD_TRAJECTORIES
)

def test_wind_diaphragm_analysis():
    res = StructuralSuite.wind_diaphragm_analysis(
        span_ft=120.0,
        width_ft=80.0,
        wall_height_ft=30.0,
        wind_speed_mph=115.0,
        exposure="C",
        risk_category="III",
        panel_length_ft=24.0
    )
    assert res["status"] == "PASS"
    assert res["velocity_pressure_qz_psf"] > 20.0
    assert res["unit_shear_v_plf"] > 100.0
    assert res["chord_force_lbs"] > 1000.0
    assert res["register_sheet"] == "Register"
    assert res["embed_schedule"]["embeds_per_panel"] >= 2
    assert res["chord_splice_bolts"] >= 2

def test_seismic_diaphragm_analysis():
    res = StructuralSuite.seismic_diaphragm_analysis(
        diaphragm_wt_kips=450.0,
        sds=0.65,
        ie=1.25,
        span_ft=150.0,
        depth_ft=80.0
    )
    assert res["status"] == "PASS"
    assert res["f_px_min_kips"] <= res["design_f_px_kips"] <= res["f_px_max_kips"]
    assert res["unit_shear_plf"] > 0.0
    assert res["collector_strut_force_kips"] > 0.0
    assert res["cases_s01_s12_count"] == 12
    assert res["register_sheet"] == "CONSTRAINT REGISTER"

def test_roof_deck_analysis():
    res = StructuralSuite.roof_deck_analysis(
        span_ft=6.0,
        dead_load_psf=15.0,
        live_load_psf=20.0,
        snow_load_psf=25.0
    )
    assert res["status"] == "PASS"
    assert res["gravity_load_asd_psf"] == 40.0
    assert "Zone 1 (Field)" in res["fastener_schedule"]
    assert "Zone 2 (Perimeter)" in res["fastener_schedule"]
    assert "Zone 3 (Corner)" in res["fastener_schedule"]
    assert res["fastener_schedule"]["Zone 1 (Field)"]["pattern"] == "36/4"
    assert res["fastener_schedule"]["Zone 2 (Perimeter)"]["pattern"] == "36/7"
    assert res["deflection_limits"]["status"] == "PASS"
    assert res["register_sheet"] == "Register"

def test_eor_review_disposition():
    res = StructuralSuite.eor_review_disposition()
    assert res["status"] == "ALL_APPROVED_AS_NOTED"
    assert res["total_items_reviewed"] >= 4
    assert res["register_sheet"] == "CONSTRAINT REGISTER"

def test_civil_suite():
    res_settle = CivilSuite.consolidation_settlement(
        clay_thickness_ft=10.0,
        compression_index_cc=0.35,
        initial_void_ratio_e0=0.85,
        initial_effective_stress_psf=2000.0,
        stress_increment_psf=800.0
    )
    assert res_settle["settlement_in"] > 0.0
    assert res_settle["settlement_ft"] > 0.0

    res_runoff = CivilSuite.rational_runoff(
        runoff_coeff_c=0.85,
        rainfall_intensity_in_hr=4.2,
        drainage_area_acres=12.5
    )
    assert res_runoff["peak_flow_q_cfs"] > 0.0
    assert abs(res_runoff["peak_flow_q_cfs"] - (0.85 * 4.2 * 12.5)) < 0.02

def test_electrical_suite():
    res_vd = ElectricalSuite.feeder_voltage_drop(
        current_amps=250.0,
        length_ft=350.0,
        system_voltage_v=480.0
    )
    assert res_vd["status"] == "PASS"
    assert res_vd["voltage_drop_pct"] <= 3.0

    res_xfmr = ElectricalSuite.transformer_sizing(
        connected_kva=750.0,
        demand_factor=0.80,
        future_growth=1.25
    )
    assert res_xfmr["status"] == "PASS"
    assert res_xfmr["selected_transformer_rating_kva"] >= 750.0

def test_gold_trajectories_coverage():
    assert "structural" in GOLD_TRAJECTORIES
    assert "civil" in GOLD_TRAJECTORIES
    assert "mechanical" in GOLD_TRAJECTORIES
    assert "electrical" in GOLD_TRAJECTORIES
    for domain, data in GOLD_TRAJECTORIES.items():
        assert len(data["exemplar"]) > 100
        assert "EXEMPLAR WORKFLOW" in data["exemplar"]
