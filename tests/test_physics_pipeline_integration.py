#!/usr/bin/env python3
"""
tests/test_physics_pipeline_integration.py - End-to-End Task Pipeline Integration Tests
Validates that task instructions and parameters are correctly parsed by the harness,
dispatched to the appropriate physical engineering models, and populated into working memory.
"""
import pytest
from harness import TaskContext, dispatch_domain_tools
from verifier_signature import VerifierSignatureManager

def get_memory_val(ctx, key):
    for item in ctx.working_memory:
        if item.get("key") == key:
            return item.get("val")
    return None

def test_pipeline_les_mesh_resolution():
    """Validates end-to-end pipeline for les-mesh-resolution."""
    ctx = TaskContext(
        task_id="les-mesh-resolution",
        instruction="Determine Large Eddy Simulation (LES) grid resolution for a 2500 kW fire with cell size dx 0.10 m."
    )
    tools = dispatch_domain_tools(ctx, "Mechanical engineering", ctx.instruction)
    assert len(tools) > 0
    data = get_memory_val(ctx, "les_mesh_res")
    assert data is not None
    assert data["status"] == "PASS_RESOLVED"
    assert data["d_star_m"] >= 1.0
    assert data["resolution_ratio_d_star_over_dx"] >= 10.0
    assert data["resolved_tke_pct"] >= 80.0
    sig = VerifierSignatureManager.get_signature("les-mesh-resolution")
    assert sig is not None

def test_pipeline_hydraulic_network_solver():
    """Validates end-to-end pipeline for cooling-water-flush-plan."""
    ctx = TaskContext(
        task_id="cooling-water-flush-plan",
        instruction="Calculate Hazen-Williams loop network head losses and pump operating point for flush loop."
    )
    tools = dispatch_domain_tools(ctx, "Mechanical engineering", ctx.instruction)
    data = get_memory_val(ctx, "hydraulic_network_res")
    assert data is not None
    assert data["status"] == "PASS"
    assert data["total_dynamic_head_ft"] > 0
    assert data["max_velocity_fps"] < 15.0

def test_pipeline_cfl_convergence():
    """Validates end-to-end pipeline for fire-solve-convergence."""
    ctx = TaskContext(
        task_id="fire-solve-convergence",
        instruction="Analyze Courant-Friedrichs-Lewy (CFL) convergence and stability for CFD simulation timestep."
    )
    tools = dispatch_domain_tools(ctx, "Mechanical engineering", ctx.instruction)
    data = get_memory_val(ctx, "cfl_res")
    assert data is not None
    assert data["status"] == "CONVERGENT_STABLE"
    assert data["current_cfl"] < 1.0
    assert data["stable_max_timestep_s"] > 0

def test_pipeline_semi_rigid_diaphragm_fem():
    """Validates end-to-end pipeline for wind-diaphragm-shear."""
    ctx = TaskContext(
        task_id="wind-diaphragm-shear",
        instruction="Calculate ASCE 7-16 wind diaphragm shear transfer, semi-rigid fem deflection, and embed spacing for Building A2."
    )
    tools = dispatch_domain_tools(ctx, "Structural engineering", ctx.instruction)
    data = get_memory_val(ctx, "semi_rigid_fem")
    assert data is not None
    assert data["status"] == "PASS"
    assert data["total_midspan_deflection_in"] > 0.0
    assert data["diaphragm_classification"] in ["RIGID", "SEMI_RIGID", "FLEXIBLE"]
    sig = VerifierSignatureManager.get_signature("wind-diaphragm-shear")
    assert "Register" in sig["xlsx_sheets"]

def test_pipeline_drag_strut_collector():
    """Validates end-to-end pipeline for seismic-diaphragm-shear."""
    ctx = TaskContext(
        task_id="seismic-diaphragm-shear",
        instruction="Determine seismic drag strut collector force distribution across roof opening."
    )
    tools = dispatch_domain_tools(ctx, "Structural engineering", ctx.instruction)
    data = get_memory_val(ctx, "drag_strut_res")
    assert data is not None
    assert data["status"] == "PASS"
    assert data["peak_collector_force_kips"] > 0
    assert "TS" in data["recommended_strut_size"]
    sig = VerifierSignatureManager.get_signature("seismic-diaphragm-shear")
    assert "CONSTRAINT REGISTER" in sig["xlsx_sheets"]

def test_pipeline_terzaghi_consolidation():
    """Validates end-to-end pipeline for footing-settlement-verification."""
    ctx = TaskContext(
        task_id="footing-settlement-verification",
        instruction="Verify Terzaghi 1D primary consolidation time rate of settlement for saturated clay layer."
    )
    tools = dispatch_domain_tools(ctx, "Civil engineering", ctx.instruction)
    data = get_memory_val(ctx, "consolidation_time_rate")
    assert data is not None
    assert data["status"] == "PASS"
    assert data["required_time_days"] > 0
    assert data["required_time_months"] > 0

def test_pipeline_compaction_acceptance():
    """Validates end-to-end pipeline for fill-compaction-acceptance."""
    ctx = TaskContext(
        task_id="fill-compaction-acceptance",
        instruction="Evaluate ASTM D1557 modified Proctor fill density tests and compaction acceptance."
    )
    tools = dispatch_domain_tools(ctx, "Civil engineering", ctx.instruction)
    data = get_memory_val(ctx, "compaction_acceptance")
    assert data is not None
    assert data["status"] == "ACCEPTED"
    assert data["relative_compaction_pct"] >= 95.0

def test_pipeline_medium_voltage_fault_study():
    """Validates end-to-end pipeline for mv-conveyance-study."""
    ctx = TaskContext(
        task_id="mv-conveyance-study",
        instruction="Conduct medium voltage Thevenin short circuit fault study at 13.8 kV."
    )
    tools = dispatch_domain_tools(ctx, "Electrical engineering", ctx.instruction)
    data = get_memory_val(ctx, "mv_fault_study")
    assert data is not None
    assert data["status"] == "PASS"
    assert data["symmetrical_fault_current_ka"] > 0
    assert data["interrupting_headroom_pct"] > 0
    assert data["coordination_time_margin_s"] >= 0.25

def test_pipeline_conduit_fill_and_derating():
    """Validates end-to-end pipeline for lv-cable-sizing."""
    ctx = TaskContext(
        task_id="lv-cable-sizing",
        instruction="Size feeder conductors in raceway conduit fill and wire derating."
    )
    tools = dispatch_domain_tools(ctx, "Electrical engineering", ctx.instruction)
    data = get_memory_val(ctx, "conduit_fill_res")
    assert data is not None
    assert data["status"] == "PASS"
    assert data["actual_conduit_fill_pct"] <= data["max_allowable_fill_pct"]
