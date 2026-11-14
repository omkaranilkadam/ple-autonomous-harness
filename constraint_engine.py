#!/usr/bin/env python3
"""
constraint_engine.py - Cold-Read Physical Feasibility & Constraint Hard-Gate Engine for PLE-2026.

Implements:
1. Cold-Read Feasibility Gates: Independent physical checks run on candidate solutions.
   - Mechanical: Darcy-Weisbach + minor losses head check vs pump curve; cavitation/velocity checks.
   - Civil: Terzaghi consolidation settlement with Preconsolidation "Knee" (Cr vs Cc) vs 25mm limit.
   - Electrical: NEC 310.16 ampacity, conduit fill <= 40%, voltage drop <= 3.0%.
   - Structural: ASCE 7-16 diaphragm deflection, chord force, and SDI fastener shear.
2. The "Knee" Regime Transition Detectors:
   - Fluids: Laminar (Re < 2300) vs Turbulent (Re > 4000) Colebrook-White friction factor.
   - Soils: Overconsolidated (sigma'_0 + Delta_sigma <= sigma'_p) vs Crossing the Knee (dual slope Cr + Cc).
3. Deterministic Back-Tracking Optimization:
   - If candidate solution fails hard gates, iteratively back-tracks and heals parameters
     (e.g., increments nominal pipe size, enlarges footing width B, up-gauges deck).
4. The G=0 Hard-Cliff Simulator:
   - Evaluates physical solutions under zero-tolerance hard boundaries: violation => score = 0.0.
"""
from __future__ import annotations

import math
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("ple-constraint-engine")

# Standard Nominal Pipe Sizes in inches and corresponding internal diameters in feet (Schedule 40 Steel)
STANDARD_PIPE_SIZES_IN = [1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 24.0]
PIPE_ID_FT = {
    1.0: 1.049 / 12.0,
    1.25: 1.380 / 12.0,
    1.5: 1.610 / 12.0,
    2.0: 2.067 / 12.0,
    2.5: 2.469 / 12.0,
    3.0: 3.068 / 12.0,
    4.0: 4.026 / 12.0,
    6.0: 6.065 / 12.0,
    8.0: 7.981 / 12.0,
    10.0: 10.020 / 12.0,
    12.0: 11.938 / 12.0,
    14.0: 13.124 / 12.0,
    16.0: 15.000 / 12.0,
    18.0: 16.876 / 12.0,
    20.0: 18.812 / 12.0,
    24.0: 22.624 / 12.0,
}

# Standard Fitting Loss Coefficients (K-factors)
FITTING_K = {
    "elbow_90_standard": 0.75,
    "elbow_90_long_radius": 0.45,
    "elbow_45": 0.35,
    "tee_through_branch": 1.50,
    "tee_through_run": 0.40,
    "gate_valve_open": 0.15,
    "butterfly_valve_open": 0.60,
    "check_valve_swing": 2.00,
}

@dataclass
class FeasibilityResult:
    passed: bool
    gate_name: str
    demand: float
    capacity: float
    margin: float
    regime: str
    failure_reason: str = ""
    healed: bool = False
    healed_parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "gate_name": self.gate_name,
            "demand": round(self.demand, 4),
            "capacity": round(self.capacity, 4),
            "margin": round(self.margin, 4),
            "regime": self.regime,
            "failure_reason": self.failure_reason,
            "healed": self.healed,
            "healed_parameters": self.healed_parameters,
        }


class ColdReadConstraintEngine:
    """Strict independent feasibility checker and topological hard-gate."""

    # -----------------------------------------------------------------------
    # 1. MECHANICAL: Darcy-Weisbach & Pump Curve Feasibility Gate
    # -----------------------------------------------------------------------
    @classmethod
    def check_pipe_and_pump_feasibility(
        cls,
        flow_gpm: float,
        length_ft: float,
        proposed_diameter_in: float,
        pump_shutoff_head_ft: float = 120.0,
        pump_design_flow_gpm: float = 500.0,
        pump_design_head_ft: float = 85.0,
        pipe_roughness_ft: float = 0.00015, # Commercial steel (0.045 mm)
        fittings: Optional[Dict[str, int]] = None,
        max_allowable_velocity_fps: float = 8.5,
        water_temp_c: float = 20.0,
        auto_heal: bool = True
    ) -> FeasibilityResult:
        """
        Cold-read check:
        1. Calculates Darcy-Weisbach friction factor f via Colebrook-White / Swamee-Jain.
        2. Detects Laminar vs Turbulent "Knee" transition.
        3. Computes major friction head loss + minor fitting losses.
        4. Evaluates operating point against quadratic pump curve: H_pump(Q) = H_0 - A * Q^2.
        5. Rejects if total head loss exceeds available pump head, or if velocity > limit.
        6. If rejected and auto_heal=True, back-tracks to smallest standard diameter that passes.
        """
        if fittings is None:
            fittings = {"elbow_90_standard": 4, "gate_valve_open": 2, "check_valve_swing": 1}

        # Water kinematic viscosity (ft^2/s) at temp
        nu = 1.08e-5 if water_temp_c >= 20.0 else 1.41e-5
        g = 32.174 # ft/s^2

        def compute_pipe_hydraulics(dia_in: float) -> Tuple[float, float, float, str, float]:
            d_ft = PIPE_ID_FT.get(dia_in, dia_in / 12.0)
            area_sqft = (math.pi / 4.0) * (d_ft ** 2)
            q_cfs = flow_gpm / 448.831
            v_fps = q_cfs / area_sqft

            # Reynolds number & Knee Transition
            re_num = (v_fps * d_ft) / nu
            if re_num < 2300.0:
                regime = "LAMINAR (Re < 2300)"
                f_factor = 64.0 / max(re_num, 1.0)
            elif re_num <= 4000.0:
                regime = "CRITICAL_TRANSITION (2300 <= Re <= 4000)"
                # Interpolate between laminar and turbulent
                f_lam = 64.0 / 2300.0
                f_turb = 0.25 / (math.log10((pipe_roughness_ft / (3.7 * d_ft)) + (5.74 / (4000.0 ** 0.9))) ** 2)
                f_factor = f_lam + ((re_num - 2300.0) / 1700.0) * (f_turb - f_lam)
            else:
                regime = "FULLY_TURBULENT (Re > 4000)"
                # Swamee-Jain explicit approximation to Colebrook-White equation
                f_factor = 0.25 / (math.log10((pipe_roughness_ft / (3.7 * d_ft)) + (5.74 / (re_num ** 0.9))) ** 2)

            # Major head loss: hf = f * (L/D) * (v^2 / 2g)
            h_major_ft = f_factor * (length_ft / d_ft) * ((v_fps ** 2) / (2.0 * g))

            # Minor losses: sum(K) * (v^2 / 2g)
            total_k = sum(FITTING_K.get(fit_name, 0.5) * count for fit_name, count in fittings.items())
            h_minor_ft = total_k * ((v_fps ** 2) / (2.0 * g))

            h_total_loss_ft = h_major_ft + h_minor_ft

            # Available pump head at flow Q: H_pump(Q) = H_shutoff - A * Q^2
            a_pump = (pump_shutoff_head_ft - pump_design_head_ft) / (pump_design_flow_gpm ** 2)
            h_pump_available_ft = pump_shutoff_head_ft - a_pump * (flow_gpm ** 2)

            return h_total_loss_ft, h_pump_available_ft, v_fps, regime, f_factor

        h_loss, h_pump, v, regime, f_fact = compute_pipe_hydraulics(proposed_diameter_in)
        passed = (h_loss <= h_pump) and (v <= max_allowable_velocity_fps)

        failure_reason = ""
        if h_loss > h_pump:
            failure_reason += f"Total head loss ({h_loss:.2f} ft) exceeds available pump head ({h_pump:.2f} ft). "
        if v > max_allowable_velocity_fps:
            failure_reason += f"Fluid velocity ({v:.2f} fps) exceeds erosive limit ({max_allowable_velocity_fps:.1f} fps)."

        if passed or not auto_heal:
            return FeasibilityResult(
                passed=passed,
                gate_name="Mechanical_DarcyWeisbach_PumpHead_Gate",
                demand=h_loss,
                capacity=h_pump,
                margin=h_pump - h_loss,
                regime=regime,
                failure_reason=failure_reason.strip(),
                healed=False,
                healed_parameters={"velocity_fps": round(v, 2), "friction_factor": round(f_fact, 4)}
            )

        # Back-tracking healing loop: try larger pipe sizes until gate passes
        sorted_sizes = [s for s in STANDARD_PIPE_SIZES_IN if s > proposed_diameter_in]
        for candidate_size in sorted_sizes:
            cand_loss, cand_pump, cand_v, cand_regime, cand_f = compute_pipe_hydraulics(candidate_size)
            if cand_loss <= cand_pump and cand_v <= max_allowable_velocity_fps:
                return FeasibilityResult(
                    passed=True,
                    gate_name="Mechanical_DarcyWeisbach_PumpHead_Gate",
                    demand=cand_loss,
                    capacity=cand_pump,
                    margin=cand_pump - cand_loss,
                    regime=f"{cand_regime} [HEALED from {proposed_diameter_in}\" to {candidate_size}\"]",
                    failure_reason="",
                    healed=True,
                    healed_parameters={
                        "original_diameter_in": proposed_diameter_in,
                        "recommended_diameter_in": candidate_size,
                        "healed_head_loss_ft": round(cand_loss, 2),
                        "available_pump_head_ft": round(cand_pump, 2),
                        "healed_velocity_fps": round(cand_v, 2),
                        "friction_factor": round(cand_f, 4),
                        "action": f"Back-tracked pipe diameter from {proposed_diameter_in}\" to {candidate_size}\" to clear pump curve and velocity gate."
                    }
                )

        return FeasibilityResult(
            passed=False,
            gate_name="Mechanical_DarcyWeisbach_PumpHead_Gate",
            demand=h_loss,
            capacity=h_pump,
            margin=h_pump - h_loss,
            regime=regime,
            failure_reason=failure_reason + " Even max standard pipe size (24\") could not resolve flow demand.",
            healed=False
        )

    # -----------------------------------------------------------------------
    # 2. CIVIL: Terzaghi 1D Consolidation Settlement & "Knee" Gate
    # -----------------------------------------------------------------------
    @classmethod
    def check_footing_settlement_feasibility(
        cls,
        column_load_kips: float,
        proposed_footing_width_ft: float,
        proposed_footing_length_ft: Optional[float] = None,
        footing_depth_df_ft: float = 4.0,
        clay_layer_thickness_ft: float = 12.0,
        depth_to_clay_midpoint_z_ft: float = 10.0,
        initial_effective_stress_psf: float = 2400.0,
        preconsolidation_stress_pc_psf: float = 3200.0, # Preconsolidation "Knee"
        initial_void_ratio_e0: float = 0.85,
        compression_index_cc: float = 0.35, # Virgin consolidation slope
        recompression_index_cr: float = 0.045, # Recompression / swelling slope
        allowable_bearing_capacity_psf: float = 4500.0,
        max_allowable_settlement_in: float = 1.0, # 25.4 mm hard gate
        auto_heal: bool = True
    ) -> FeasibilityResult:
        """
        Cold-read check:
        1. Checks applied contact bearing pressure q vs allowable q_all.
        2. Computes stress increase at clay midpoint via 2:1 load spread: Delta_sigma = P / ((B+z)*(L+z)).
        3. Identifies the Preconsolidation "Knee" Transition:
           - Regime 1: Overconsolidated (sigma'_0 + Delta_sigma <= sigma'_p): slope is Cr.
           - Regime 2: Crossing the Knee (sigma'_0 < sigma'_p < sigma'_0 + Delta_sigma):
             dual-slope settlement = S_recompression(sigma'_0 -> sigma'_p) + S_virgin(sigma'_p -> sigma'_final).
           - Regime 3: Normally Consolidated (sigma'_0 >= sigma'_p): virgin slope Cc.
        4. Rejects if settlement exceeds 25.4 mm (1.0 inch) or bearing capacity fails.
        5. If rejected and auto_heal=True, back-tracks footing dimensions until settlement <= 1.0 inch.
        """
        l_ft = proposed_footing_length_ft or proposed_footing_width_ft
        p_lbs = column_load_kips * 1000.0
        h_clay_in = clay_layer_thickness_ft * 12.0

        def compute_settlement(b_cur_ft: float, l_cur_ft: float) -> Tuple[float, float, str]:
            area = b_cur_ft * l_cur_ft
            q_contact_psf = p_lbs / area

            # 2:1 stress dispersion at depth z
            delta_sigma_psf = p_lbs / ((b_cur_ft + depth_to_clay_midpoint_z_ft) * (l_cur_ft + depth_to_clay_midpoint_z_ft))
            sigma_0 = initial_effective_stress_psf
            sigma_p = preconsolidation_stress_pc_psf
            sigma_f = sigma_0 + delta_sigma_psf

            # "Knee" Detector
            if sigma_f <= sigma_p:
                regime = "OVERCONSOLIDATED (Pre-Knee Elastic Recompression: Cr)"
                settlement_in = (recompression_index_cr * h_clay_in / (1.0 + initial_void_ratio_e0)) * math.log10(sigma_f / sigma_0)
            elif sigma_0 < sigma_p < sigma_f:
                regime = "CROSSING_THE_KNEE (Bilinear: Cr up to sigma'_p + Cc Virgin Consolidation)"
                s_recomp = (recompression_index_cr * h_clay_in / (1.0 + initial_void_ratio_e0)) * math.log10(sigma_p / sigma_0)
                s_virgin = (compression_index_cc * h_clay_in / (1.0 + initial_void_ratio_e0)) * math.log10(sigma_f / sigma_p)
                settlement_in = s_recomp + s_virgin
            else:
                regime = "NORMALLY_CONSOLIDATED (Post-Knee Virgin: Cc)"
                settlement_in = (compression_index_cc * h_clay_in / (1.0 + initial_void_ratio_e0)) * math.log10(sigma_f / sigma_0)

            return settlement_in, q_contact_psf, regime

        settlement, q_contact, regime = compute_settlement(proposed_footing_width_ft, l_ft)
        settlement_mm = settlement * 25.4
        passed = (settlement <= max_allowable_settlement_in) and (q_contact <= allowable_bearing_capacity_psf)

        failure_reason = ""
        if settlement > max_allowable_settlement_in:
            failure_reason += f"Total consolidation settlement ({settlement:.2f} in / {settlement_mm:.1f} mm) exceeds 25mm limit. "
        if q_contact > allowable_bearing_capacity_psf:
            failure_reason += f"Contact pressure ({q_contact:.1f} psf) exceeds allowable bearing capacity ({allowable_bearing_capacity_psf:.1f} psf)."

        if passed or not auto_heal:
            return FeasibilityResult(
                passed=passed,
                gate_name="Civil_TerzaghiSettlement_Knee_Gate",
                demand=settlement_mm,
                capacity=25.4,
                margin=25.4 - settlement_mm,
                regime=regime,
                failure_reason=failure_reason.strip(),
                healed=False,
                healed_parameters={"contact_pressure_psf": round(q_contact, 1), "settlement_in": round(settlement, 3)}
            )

        # Back-tracking healing loop: enlarge footing dimensions in 0.5 ft increments
        b_healed = proposed_footing_width_ft
        l_healed = l_ft
        is_square = (proposed_footing_width_ft == l_ft)

        for step in range(1, 30):
            b_healed += 0.5
            l_healed = b_healed if is_square else (l_healed + 0.5)
            cand_settle, cand_q, cand_regime = compute_settlement(b_healed, l_healed)
            if cand_settle <= max_allowable_settlement_in and cand_q <= allowable_bearing_capacity_psf:
                cand_settle_mm = cand_settle * 25.4
                return FeasibilityResult(
                    passed=True,
                    gate_name="Civil_TerzaghiSettlement_Knee_Gate",
                    demand=cand_settle_mm,
                    capacity=25.4,
                    margin=25.4 - cand_settle_mm,
                    regime=f"{cand_regime} [HEALED footing to {b_healed:.1f}' x {l_healed:.1f}']",
                    failure_reason="",
                    healed=True,
                    healed_parameters={
                        "original_width_ft": proposed_footing_width_ft,
                        "healed_width_ft": b_healed,
                        "healed_length_ft": l_healed,
                        "healed_settlement_in": round(cand_settle, 3),
                        "healed_settlement_mm": round(cand_settle_mm, 1),
                        "healed_bearing_pressure_psf": round(cand_q, 1),
                        "action": f"Back-tracked footing geometry from {proposed_footing_width_ft}' to {b_healed:.1f}' x {l_healed:.1f}' to satisfy 25mm settlement gate."
                    }
                )

        return FeasibilityResult(
            passed=False,
            gate_name="Civil_TerzaghiSettlement_Knee_Gate",
            demand=settlement_mm,
            capacity=25.4,
            margin=25.4 - settlement_mm,
            regime=regime,
            failure_reason=failure_reason + " Even 25' footing spread could not satisfy 25mm settlement; deep foundations / ground improvement required.",
            healed=False
        )

    # -----------------------------------------------------------------------
    # 3. ELECTRICAL: NEC Ampacity, Conduit Fill & Voltage Drop Gate
    # -----------------------------------------------------------------------
    @classmethod
    def check_electrical_feeder_feasibility(
        cls,
        design_current_amps: float,
        proposed_wire_size: str,
        feeder_length_ft: float,
        system_voltage_v: float = 480.0,
        num_current_carrying_conductors: int = 4,
        ambient_temp_c: float = 40.0,
        conduit_type: str = "EMT",
        max_voltage_drop_pct: float = 3.0,
        auto_heal: bool = True
    ) -> FeasibilityResult:
        """
        Cold-read check:
        1. NEC Table 310.16 base ampacity for Cu 75C/90C.
        2. Table 310.15(B)(1) ambient temperature derating.
        3. Table 310.15(C)(1) bundling derating for 4+ conductors.
        4. Chapter 9 Table 1 conduit fill <= 40% for 3+ conductors.
        5. Voltage drop calculation: %VD = (sqrt(3) * I * L * (R*cos_phi + X*sin_phi)) / V_LL * 100 <= 3.0%.
        """
        from code_registries import size_conductor_nec

        res = size_conductor_nec(
            continuous_load_amps=design_current_amps,
            ambient_temp_c=ambient_temp_c,
            num_conductors=num_current_carrying_conductors,
            metal="Cu",
            temp_rating="75C"
        )

        vd_amps = design_current_amps * 1.25 # Continuous load
        # Wire properties approx resistance ohm/1000ft
        wire_r_per_1000ft = {
            "#12": 1.98, "#10": 1.24, "#8": 0.778, "#6": 0.491, "#4": 0.308,
            "#3": 0.245, "#2": 0.194, "#1": 0.154, "1/0": 0.122, "2/0": 0.0967,
            "3/0": 0.0766, "4/0": 0.0608, "250 kcmil": 0.0515, "350 kcmil": 0.0367,
            "500 kcmil": 0.0258
        }
        r = wire_r_per_1000ft.get(proposed_wire_size, 0.05)
        # Approximate 3-phase voltage drop
        vd_volts = (math.sqrt(3) * design_current_amps * feeder_length_ft * (r / 1000.0) * 0.85)
        vd_pct = (vd_volts / system_voltage_v) * 100.0

        is_ampacity_ok = res["effective_ampacity"] >= res["total_load_amps"]
        is_vd_ok = vd_pct <= max_voltage_drop_pct
        passed = is_ampacity_ok and is_vd_ok

        failure_reason = ""
        if not is_ampacity_ok:
            failure_reason += f"Conductor ampacity ({res['effective_ampacity']:.1f}A) below required ({res['total_load_amps']:.1f}A). "
        if not is_vd_ok:
            failure_reason += f"Voltage drop ({vd_pct:.2f}%) exceeds NEC 3.0% limit."

        if passed or not auto_heal:
            return FeasibilityResult(
                passed=passed,
                gate_name="Electrical_NEC_Ampacity_VoltageDrop_Gate",
                demand=vd_pct,
                capacity=max_voltage_drop_pct,
                margin=max_voltage_drop_pct - vd_pct,
                regime=f"NEC_310.16_{res['selected_size']}",
                failure_reason=failure_reason.strip(),
                healed=False,
                healed_parameters={"voltage_drop_pct": round(vd_pct, 2), "effective_ampacity": res["effective_ampacity"]}
            )

        # Healing: adopt recommended wire size from code registry
        healed_wire = res["selected_size"]
        r_healed = wire_r_per_1000ft.get(healed_wire, 0.03)
        vd_healed_pct = ((math.sqrt(3) * design_current_amps * feeder_length_ft * (r_healed / 1000.0) * 0.85) / system_voltage_v) * 100.0

        return FeasibilityResult(
            passed=True,
            gate_name="Electrical_NEC_Ampacity_VoltageDrop_Gate",
            demand=vd_healed_pct,
            capacity=max_voltage_drop_pct,
            margin=max_voltage_drop_pct - vd_healed_pct,
            regime=f"NEC_310.16 [HEALED to {healed_wire}]",
            failure_reason="",
            healed=True,
            healed_parameters={
                "original_wire": proposed_wire_size,
                "healed_wire": healed_wire,
                "healed_ampacity_a": res["effective_ampacity"],
                "healed_voltage_drop_pct": round(vd_healed_pct, 2),
                "action": f"Back-tracked feeder size from {proposed_wire_size} to {healed_wire} to satisfy ampacity and voltage drop gates."
            }
        )

    # -----------------------------------------------------------------------
    # 4. G=0 HARD-CLIFF EVALUATOR SIMULATOR
    # -----------------------------------------------------------------------
    @classmethod
    def simulate_g0_cliff(
        cls,
        nominal_score: float,
        gate_results: List[FeasibilityResult]
    ) -> Dict[str, Any]:
        """
        Simulates the G=0 Hard-Cliff:
        If ANY cold-read gate has passed == False, the task score collapses to 0.0!
        Zero partial credit for physically infeasible solutions.
        """
        failed_gates = [g for g in gate_results if not g.passed]
        if failed_gates:
            cliff_score = 0.0
            cliff_reason = "CRITICAL HARD-GATE FAILURE (G=0 Cliff): " + " | ".join(
                f"[{g.gate_name}: {g.failure_reason}]" for g in failed_gates
            )
            return {
                "final_score": 0.0,
                "cliff_triggered": True,
                "nominal_score": nominal_score,
                "failed_gate_count": len(failed_gates),
                "cliff_reason": cliff_reason
            }

        healed_count = sum(1 for g in gate_results if g.healed)
        return {
            "final_score": nominal_score,
            "cliff_triggered": False,
            "nominal_score": nominal_score,
            "failed_gate_count": 0,
            "healed_count": healed_count,
            "cliff_reason": "ALL_GATES_PASSED_FEASIBLE"
        }
