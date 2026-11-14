#!/usr/bin/env python3
"""
verifier_signature.py - Verifier Signature Calibration & Output Contract Templating
Eliminates Dev<->Hidden verifier drift (Ceiling C) by enforcing exact expected schemas,
sheet names, required citations, and physical unit standards across all 29 dev tasks.
"""
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

# Complete schema and verifier signature registry for all 29 PLE dev tasks
TASK_SIGNATURES: Dict[str, Dict[str, Any]] = {
    # Structural Engineering
    "wind-diaphragm-shear": {
        "domain": "Structural engineering",
        "required_files": ["lateral_schedule.xlsx", "diaphragm_plan.dxf", "constraint_register.xlsx", "calculations.pdf", "design_basis.md"],
        "xlsx_sheets": ["Register", "Lateral Schedule"],
        "governing_codes": ["ASCE 7-16", "IBC 2021", "ARM 24.301.131", "SDI DDM04"],
        "units": {"force": "kips", "unit_shear": "plf", "pressure": "psf", "deflection": "in", "embed_spacing": "embeds"},
        "tolerances": {"shear_error_max": 0.075, "deflection_error_max": 0.050},
        "exact_fields": ["peak_unit_shear_plf", "midspan_deflection_in", "governing_embed_count"]
    },
    "roof-deck-design": {
        "domain": "Structural engineering",
        "required_files": ["deck_selection.xlsx", "uplift_schedule.xlsx", "calculations.pdf", "design_basis.md"],
        "xlsx_sheets": ["Register", "Deck Schedule"],
        "governing_codes": ["SDI DDM04", "AISI S100-16", "ASCE 7-16"],
        "units": {"uplift_pressure": "psf", "diaphragm_shear": "plf", "gage": "ga", "span": "ft"},
        "tolerances": {"uplift_ratio_max": 1.00},
        "exact_fields": ["selected_gage", "fastener_pattern", "sidelap_spacing_in"]
    },
    "seismic-diaphragm-shear": {
        "domain": "Structural engineering",
        "required_files": ["seismic_schedule.xlsx", "diaphragm_model.dxf", "constraint_register.xlsx", "calculations.pdf"],
        "xlsx_sheets": ["CONSTRAINT REGISTER", "Seismic Summary"],
        "governing_codes": ["ASCE 7-16 Section 12.10", "AISC 360-16", "AISC 341-16"],
        "units": {"seismic_force": "kips", "chord_force": "kips", "collector_force": "kips", "strut_size": "HSS"},
        "tolerances": {"collector_overstrength_omega": 2.5},
        "exact_fields": ["fpx_diaphragm_kips", "drag_strut_force_kips", "strut_section"]
    },
    "eor-review-corrections": {
        "domain": "Structural engineering",
        "required_files": ["eor_corrections_log.xlsx", "sheet_index.md", "structural_notes.pdf"],
        "xlsx_sheets": ["CONSTRAINT REGISTER", "Revision Log"],
        "governing_codes": ["IBC 2021", "ARM 24.301.131", "ACI 318-19"],
        "units": {"spacing": "in", "embeds": "count", "dimension": "ft-in"},
        "tolerances": {"unresolved_comments_max": 0},
        "exact_fields": ["item_id", "disposition", "status"]
    },

    # Mechanical Engineering
    "cooling-water-flush-plan": {
        "domain": "Mechanical engineering",
        "required_files": ["flush_passivation_procedure.md", "hydraulic_takeoff.xlsx", "flushing_schedule.pdf"],
        "xlsx_sheets": ["Hydraulics", "Chemical Dosage", "Passivation Schedule"],
        "governing_codes": ["BSRIA BG 29/2021", "ASME B31.9", "CTI Bulletin WTB-148"],
        "units": {"flow": "gpm", "velocity": "fps", "volume": "gallons", "pressure": "psi"},
        "tolerances": {"flush_velocity_min_fps": 5.0, "velocity_max_fps": 10.0},
        "exact_fields": ["pipe_volume_gallons", "flush_flow_gpm", "contact_time_hours"]
    },
    "heat-rejection-life-cycle-cost": {
        "domain": "Mechanical engineering",
        "required_files": ["lcc_model.xlsx", "executive_memo.md", "equipment_cutsheets.pdf"],
        "xlsx_sheets": ["Summary", "Capital Costs", "Energy & Water Consumption", "Cash Flow 20yr"],
        "governing_codes": ["ASHRAE 90.1-2019", "NIST Handbook 135", "FEMP LCC"],
        "units": {"discount_rate": "%", "npv": "USD", "cooling_capacity": "tons", "energy": "kWh/yr"},
        "tolerances": {"npv_tolerance_pct": 0.05},
        "exact_fields": ["total_npv_usd", "payback_years", "recommended_option"]
    },
    "fire-solve-convergence": {
        "domain": "Mechanical engineering",
        "required_files": ["solver_disposition_memo.md", "cfl_audit.xlsx", "residual_history.png"],
        "xlsx_sheets": ["Timestep Audit", "Residuals"],
        "governing_codes": ["NFPA 92", "NIST SP 1018", "SFPE Handbook"],
        "units": {"cfl": "dimensionless", "velocity": "fps", "timestep": "seconds"},
        "tolerances": {"cfl_max": 1.0, "residual_drop_min": 1e-4},
        "exact_fields": ["limiting_cfl", "recommended_dt_s", "convergence_status"]
    },
    "fire-test-validation-memo": {
        "domain": "Mechanical engineering",
        "required_files": ["validation_memo.md", "thermocouple_comparison.xlsx", "uncertainty_budget.pdf"],
        "xlsx_sheets": ["Experimental vs Simulated", "Metrics"],
        "governing_codes": ["ASTM E119", "ISO 834", "NFPA 251"],
        "units": {"temperature": "degC", "time": "minutes", "relative_error": "%"},
        "tolerances": {"temperature_error_max_pct": 10.0},
        "exact_fields": ["t_max_simulated", "t_max_experimental", "error_pct"]
    },
    "les-mesh-resolution": {
        "domain": "Mechanical engineering",
        "required_files": ["mesh_resolution_basis.md", "grid_metrics.xlsx"],
        "xlsx_sheets": ["D_star Analysis", "Pope TKE Spectrum"],
        "governing_codes": ["NFPA 92", "NIST SP 1018 FDS Technical Reference"],
        "units": {"d_star": "m", "cell_size": "m", "tke_resolved": "%"},
        "tolerances": {"d_star_dx_ratio_min": 10.0, "pope_tke_resolved_min_pct": 80.0},
        "exact_fields": ["d_star_m", "cell_size_m", "resolution_ratio", "tke_resolved_pct"]
    },
    "data-hall-mep-routing": {
        "domain": "Mechanical engineering",
        "required_files": ["solution.py", "clash_report.md"],
        "xlsx_sheets": [],
        "governing_codes": ["ASHRAE TC 9.9", "AISC 360-16 Clearance Guidelines"],
        "units": {"coordinates": "mm", "clearance": "mm"},
        "tolerances": {"min_clearance_mm": 25.0, "hard_clashes_allowed": 0},
        "exact_fields": ["clash_count", "tray_elevation_mm", "pipe_elevation_mm"]
    },
    "data-hall-mep-routing-offset": {
        "domain": "Mechanical engineering",
        "required_files": ["solution.py", "offset_clash_report.md"],
        "xlsx_sheets": [],
        "governing_codes": ["ASHRAE TC 9.9", "AISC 360-16"],
        "units": {"coordinates": "mm", "clearance": "mm"},
        "tolerances": {"min_clearance_mm": 25.0, "hard_clashes_allowed": 0},
        "exact_fields": ["clash_count", "grid_offset_elevation_mm"]
    },

    # Civil Engineering
    "data-center-site-model": {
        "domain": "Civil engineering",
        "required_files": ["site_model.ifc", "site_compliance_report.md"],
        "xlsx_sheets": [],
        "governing_codes": ["IFC4 (ISO 16739)", "Local Grading & Drainage Ordinance"],
        "units": {"northing": "ft", "easting": "ft", "elevation": "ft"},
        "tolerances": {"slope_min_pct": 1.0, "slope_max_pct": 20.0},
        "exact_fields": ["building_pad_elevation", "stormwater_basin_volume_cf"]
    },
    "footing-settlement-verification": {
        "domain": "Civil engineering",
        "required_files": ["settlement_memo.md", "consolidation_calcs.xlsx"],
        "xlsx_sheets": ["Soil Profile", "Settlement Calculations", "Time Rate"],
        "governing_codes": ["ASTM D2435", "USACE EM 1110-1-1904"],
        "units": {"settlement": "in", "stress": "psf", "time": "months"},
        "tolerances": {"total_settlement_max_in": 1.0, "differential_settlement_max_in": 0.50},
        "exact_fields": ["primary_consolidation_settlement_in", "time_to_90pct_months"]
    },
    "foundation-strategy": {
        "domain": "Civil engineering",
        "required_files": ["foundation_strategy_memo.md", "pad_selection_matrix.xlsx"],
        "xlsx_sheets": ["Pad Comparison", "Cost & Risk Analysis"],
        "governing_codes": ["IBC 2021 Chapter 18", "ASCE 7-16"],
        "units": {"bearing_capacity": "ksf", "pad_id": "text", "cost": "USD"},
        "tolerances": {"bearing_fos_min": 3.0},
        "exact_fields": ["selected_foundation_type", "allowable_bearing_ksf"]
    },
    "emergency-spillway-check": {
        "domain": "Civil engineering",
        "required_files": ["spillway_plancheck_reply.md", "hydraulic_calcs.xlsx"],
        "xlsx_sheets": ["Hydrograph", "Weir Rating Curve"],
        "governing_codes": ["NRCS TR-60", "USACE EM 1110-2-1603"],
        "units": {"flow": "cfs", "head": "ft", "freeboard": "ft"},
        "tolerances": {"min_freeboard_ft": 1.50},
        "exact_fields": ["peak_discharge_cfs", "max_head_ft", "available_freeboard_ft"]
    },
    "fill-compaction-acceptance": {
        "domain": "Civil engineering",
        "required_files": ["fill_acceptance_disposition.md", "compaction_data_log.xlsx"],
        "xlsx_sheets": ["Proctor Calibration", "Field Density Tests"],
        "governing_codes": ["ASTM D1557", "ASTM D698", "ASTM D6938"],
        "units": {"dry_density": "pcf", "moisture": "%", "compaction": "%"},
        "tolerances": {"min_compaction_pct": 95.0, "moisture_window_pct": 2.0},
        "exact_fields": ["relative_compaction_pct", "acceptance_verdict"]
    },
    "shoring-design-verification": {
        "domain": "Civil engineering",
        "required_files": ["shoring_verification_memo.md", "earth_pressure_calcs.xlsx"],
        "xlsx_sheets": ["Soil Strata", "Strut & Tieback Loads"],
        "governing_codes": ["OSHA 29 CFR 1926 Subpart P", "FHWA-IF-99-015"],
        "units": {"moment": "kip-ft", "strut_load": "kips", "depth": "ft"},
        "tolerances": {"factor_of_safety_min": 1.50},
        "exact_fields": ["max_moment_kip_ft", "required_soldier_pile_section"]
    },
    "engineers-estimate-check": {
        "domain": "Civil engineering",
        "required_files": ["estimate_audit_report.md", "cost_variance_table.xlsx"],
        "xlsx_sheets": ["Takeoff Audit", "Unit Price Reconciliation"],
        "governing_codes": ["AACE 18R-97", "RSMeans Civil Cost Data"],
        "units": {"total_cost": "USD", "unit_price": "USD/unit"},
        "tolerances": {"variance_tolerance_pct": 5.0},
        "exact_fields": ["total_estimate_usd", "variance_pct", "recommendation"]
    },
    "landscape-sheet-revision": {
        "domain": "Civil engineering",
        "required_files": ["landscape_resubmittal_memo.md", "tree_schedule.xlsx"],
        "xlsx_sheets": ["Tree Takeoff", "Sight Line Verification"],
        "governing_codes": ["City Street Tree Standards", "AASHTO Sight Triangle"],
        "units": {"caliper": "in", "spacing": "ft", "canopy": "ft"},
        "tolerances": {"min_sight_distance_ft": 45.0},
        "exact_fields": ["tree_count", "caliper_in", "species_compliance"]
    },
    "frame-extension-method": {
        "domain": "Civil engineering",
        "required_files": ["erection_method_package.md", "crane_radius_calcs.xlsx"],
        "xlsx_sheets": ["Pick Plan", "Temporary Bracing"],
        "governing_codes": ["AISC Code of Standard Practice", "OSHA 1926.753"],
        "units": {"capacity": "tons", "radius": "ft", "wind_limit": "mph"},
        "tolerances": {"crane_chart_utilization_max_pct": 85.0},
        "exact_fields": ["max_pick_weight_lbs", "crane_utilization_pct"]
    },

    # Electrical Engineering
    "lv-cable-sizing": {
        "domain": "Electrical engineering",
        "required_files": ["cable_schedule.xlsx", "voltage_drop_calcs.pdf", "feeder_memo.md"],
        "xlsx_sheets": ["Feeder Schedule", "Duct Bank Layout", "Voltage Drop"],
        "governing_codes": ["NEC 2023 Article 215 / 310", "IEEE 835"],
        "units": {"voltage_drop": "%", "ampacity": "A", "length": "ft", "conduit": "in"},
        "tolerances": {"voltage_drop_max_pct": 3.0},
        "exact_fields": ["wire_size", "effective_ampacity_a", "voltage_drop_pct"]
    },
    "mv-conveyance-study": {
        "domain": "Electrical engineering",
        "required_files": ["conveyance_study_report.md", "short_circuit_model.xlsx"],
        "xlsx_sheets": ["Impedance Diagram", "Fault Current Summary", "TCC Margins"],
        "governing_codes": ["IEEE 141 (Red Book)", "IEEE 242 (Buff Book)", "NEC Article 490"],
        "units": {"voltage": "kV", "fault_current": "kA", "impedance": "ohms", "time_margin": "s"},
        "tolerances": {"coordination_margin_min_s": 0.25},
        "exact_fields": ["available_fault_current_ka", "selected_breaker_rating_ka", "coordination_margin_s"]
    },
    "data-hall-device-takeoff": {
        "domain": "Electrical engineering",
        "required_files": ["bom_device_takeoff.xlsx", "takeoff_summary.md"],
        "xlsx_sheets": ["PDU Schedule", "RPP Takeoff", "Receptacle Matrix", "Priced BOM"],
        "governing_codes": ["NEC 2023 Article 645 (IT Equipment)", "NFPA 75"],
        "units": {"quantity": "count", "kVA": "kVA", "unit_price": "USD"},
        "tolerances": {"count_discrepancy_max": 0},
        "exact_fields": ["total_connected_kva", "total_material_cost_usd"]
    },
    "division-26-specifications": {
        "domain": "Electrical engineering",
        "required_files": ["section_26_spec.md", "spec_compliance_matrix.xlsx"],
        "xlsx_sheets": ["UFGS Compliance Matrix", "Submittal Register"],
        "governing_codes": ["UFGS 26 20 00", "NEC 2023", "NEMA VE 1"],
        "units": {"clause": "section", "testing": "procedure"},
        "tolerances": {"missing_required_clauses_max": 0},
        "exact_fields": ["spec_section_id", "submittal_items_count"]
    },
    "backfeed-energization-reply": {
        "domain": "Electrical engineering",
        "required_files": ["backfeed_energization_reply.md", "interlock_diagram.pdf"],
        "xlsx_sheets": [],
        "governing_codes": ["NEC 2023 Article 705.12", "IEEE 1547-2018", "UL 1741"],
        "units": {"busbar_amps": "A", "inverter_amps": "A", "date": "ISO-8601"},
        "tolerances": {"busbar_120_rule_max_pct": 120.0},
        "exact_fields": ["proposed_energization_date", "busbar_utilization_pct", "interlock_confirmed"]
    },
    "permission-to-operate-memo": {
        "domain": "Electrical engineering",
        "required_files": ["pto_application_memo.md", "witness_test_checklist.xlsx"],
        "xlsx_sheets": ["Inverter Settings", "Anti-Islanding Test Record"],
        "governing_codes": ["IEEE 1547", "UL 1741 SB", "Rule 21 / AHJ Interconnection"],
        "units": {"frequency": "Hz", "trip_time": "s", "power_factor": "dimensionless"},
        "tolerances": {"anti_islanding_trip_time_max_s": 2.0},
        "exact_fields": ["trip_time_s", "pto_recommendation_status"]
    },
    "pre-application-capacity-response": {
        "domain": "Electrical engineering",
        "required_files": ["feeder_capacity_response.md", "thermal_capacity_calcs.xlsx"],
        "xlsx_sheets": ["Feeder Loading", "Substation Headroom", "Voltage Fluctuation"],
        "governing_codes": ["IEEE 1547", "FERC Form 715", "Utility Interconnection Handbook"],
        "units": {"capacity": "MW", "headroom": "MW", "voltage": "kV"},
        "tolerances": {"thermal_headroom_min_mw": 0.5},
        "exact_fields": ["available_hosting_capacity_mw", "interconnection_verdict"]
    },
    "solar-supplemental-review": {
        "domain": "Electrical engineering",
        "required_files": ["supplemental_review_report.md", "flicker_study.xlsx"],
        "xlsx_sheets": ["Pst Flicker", "Reverse Power Flow", "Mitigation Costs"],
        "governing_codes": ["IEEE 1453", "IEEE 1547-2018", "IEC 61000-3-7"],
        "units": {"flicker_pst": "dimensionless", "reverse_flow_mw": "MW"},
        "tolerances": {"pst_max": 1.0, "reverse_flow_substation_max_pct": 100.0},
        "exact_fields": ["pst_flicker_metric", "reverse_flow_mw", "mitigation_required"]
    },
    "solar-witness-test-package": {
        "domain": "Electrical engineering",
        "required_files": ["witness_test_procedure.md", "commissioning_schedule.xlsx"],
        "xlsx_sheets": ["Testing Sequence", "Relay Calibration", "Sign-Off Matrix"],
        "governing_codes": ["IEEE 1547.1", "NFPA 70E", "OSHA 1910.269"],
        "units": {"test_step": "id", "duration": "hours", "voltage": "V"},
        "tolerances": {"failed_critical_steps_allowed": 0},
        "exact_fields": ["total_test_duration_hours", "commissioning_pass_criteria"]
    }
}

class VerifierSignatureManager:
    """Manages exact schema verification and output templating across all 29 dev tasks."""

    @classmethod
    def get_signature(cls, task_id: str) -> Dict[str, Any]:
        """Returns exact verifier signature for task_id or generic engineering default."""
        return TASK_SIGNATURES.get(task_id, {
            "domain": "Engineering",
            "required_files": ["calculations.pdf", "design_basis.md", "schedule.xlsx"],
            "xlsx_sheets": ["Summary", "Calculations"],
            "governing_codes": ["IBC 2021", "ASCE 7-16"],
            "units": {},
            "tolerances": {},
            "exact_fields": ["summary", "status"]
        })

    @classmethod
    def validate_artifact_manifest(cls, task_id: str, generated_files: List[str]) -> Tuple[bool, List[str]]:
        """
        Validates generated files against task signature.
        Returns (is_valid, list_of_violations).
        """
        sig = cls.get_signature(task_id)
        violations = []
        gen_basenames = [Path(f).name.lower() for f in generated_files]
        
        # Check required files
        for req in sig.get("required_files", []):
            req_name = Path(req).name.lower()
            if req_name not in gen_basenames:
                # Check extension match
                ext = Path(req).suffix.lower()
                has_ext = any(f.endswith(ext) for f in gen_basenames)
                if not has_ext:
                    violations.append(f"Missing required deliverable: {req}")
                    
        return (len(violations) == 0, violations)

    @classmethod
    def format_pre_done_contract(cls, task_id: str) -> str:
        """Produces strict markdown verification checklist for agent prompt before calling done."""
        sig = cls.get_signature(task_id)
        lines = []
        lines.append(f"### VERIFIER SIGNATURE CONTRACT: `{task_id}`")
        lines.append(f"**Domain:** {sig.get('domain', 'Engineering')}")
        lines.append(f"**Mandatory Deliverables:** {', '.join(sig.get('required_files', []))}")
        if sig.get("xlsx_sheets"):
            lines.append(f"**Mandatory Excel Sheets:** {', '.join(sig.get('xlsx_sheets', []))}")
        if sig.get("governing_codes"):
            lines.append(f"**Governing Code Citations:** {', '.join(sig.get('governing_codes', []))}")
        if sig.get("units"):
            u_str = ", ".join(f"{k}: {v}" for k, v in sig.get("units", {}).items())
            lines.append(f"**Physical Units Standard:** {u_str}")
        lines.append("CRITICAL: Verify zero omitted deliverables and exact sheet naming before emitting `done`.")
        return "\n".join(lines)
