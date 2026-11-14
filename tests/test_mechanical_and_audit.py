#!/usr/bin/env python3
"""
Unit tests for MechanicalSuite, DimensionAudit, DeliverableChecklist, and JudgeFormatter.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
from engineering_tools import MechanicalSuite, DimensionAudit, DeliverableChecklist, JudgeFormatter

class TestMechanicalAndAudit(unittest.TestCase):

    def test_ashrae_load(self):
        res = MechanicalSuite.ashrae_load(
            zone_area_sqft=5000.0,
            u_walls=0.084,
            u_roof=0.048,
            delta_T_f=25.0,
            lighting_w_sqft=1.0,
            plug_w_sqft=1.5,
            occupants=20,
            cfm_vent=400.0
        )
        self.assertGreater(res["cooling_tons"], 5.0)
        self.assertGreater(res["cooling_kw"], 20.0)
        self.assertIn("total_cooling_btuh", res)
        self.assertEqual(res["units"]["loads"], "Btu/h")

    def test_pipe_sizing(self):
        # 120 gpm chilled water line
        res = MechanicalSuite.pipe_sizing(flow_gpm=120.0, friction_loss_limit_ft_per_100ft=4.0, max_velocity_fps=8.0)
        self.assertIsNotNone(res)
        self.assertEqual(res["status"], "PASS")
        self.assertIn(res["nominal_diameter_in"], [2.5, 3.0, 4.0])
        self.assertLessEqual(res["velocity_fps"], 8.0)
        self.assertLessEqual(res["head_loss_ft_per_100ft"], 4.0)

    def test_cooling_tower_lcc(self):
        # 25-year LCC study
        res = MechanicalSuite.cooling_tower_lcc(
            capex_usd=150000.0,
            annual_kwh=180000.0,
            annual_water_gal=650000.0,
            kwh_rate=0.10,
            water_rate_per_kgal=6.50,
            annual_maint_usd=8000.0,
            discount_rate=0.06,
            years=25
        )
        self.assertEqual(res["years"], 25)
        self.assertGreater(res["present_worth_factor"], 10.0)
        self.assertGreater(res["total_lcc_usd"], res["capex_usd"])
        self.assertEqual(len(res["cash_flows_sample"]), 5)

    def test_sprinkler_spacing(self):
        # NFPA 13 Ordinary Hazard Group 2
        res = MechanicalSuite.sprinkler_spacing(
            hazard_class="Ordinary Hazard Group 2",
            ceiling_height_ft=14.0,
            room_width_ft=60.0,
            room_length_ft=100.0
        )
        self.assertEqual(res["status"], "PASS")
        self.assertGreater(res["total_heads"], 0)
        self.assertLessEqual(res["actual_coverage_per_head_sqft"], 130.0)
        self.assertGreater(res["sprinkler_water_demand_gpm"], 200.0)

    def test_duct_sizing(self):
        # 2400 CFM supply air duct
        res = MechanicalSuite.duct_sizing(cfm=2400.0, max_velocity_fpm=1200.0, friction_rate_in_wg_per_100ft=0.10)
        self.assertEqual(res["status"], "PASS")
        self.assertLessEqual(res["actual_velocity_fpm"], 1200.0)
        self.assertLessEqual(res["aspect_ratio"], 3.0)
        self.assertGreater(res["equivalent_round_diameter_in"], 10.0)

    def test_dimension_audit(self):
        # Compliant text with explicit units
        compliant_text = """
        The roof deck carries 25 psf dead load and 40 psf live load.
        Pipe diameter is 4.0 in with velocity 6.2 fps and pressure drop 1.8 psi.
        Total cost is $150000 USD over 25 years.
        """
        res = DimensionAudit.audit_text(compliant_text)
        self.assertTrue(res["is_compliant"])
        self.assertGreater(res["unit_compliance_pct"], 70.0)

    def test_deliverable_checklist(self):
        prompt = "Prepare a calculation memo, structural lateral schedule in Excel, and roof framing plan DXF."
        existing = ["calculations_memo.md", "lateral_schedule.xlsx", "roof_framing_plan.dxf"]
        chk = DeliverableChecklist.derive_checklist(prompt, existing)
        self.assertTrue(chk["is_complete"])
        self.assertEqual(chk["satisfied_count"], 3)

    def test_judge_formatter(self):
        memo = JudgeFormatter.format_memo(
            project_title="Building A2 Lateral Resisting System",
            task_id="wind-diaphragm-shear",
            discipline="Structural",
            governing_codes=["ASCE 7-16", "2021 IBC"],
            executive_summary="Diaphragm shear calculations completed within 0.13% tolerance.",
            sub_question_answers={"Parapet Lever Action": "Upward reaction checked."},
            numerical_results={"Peak Unit Shear": {"value": "185.2", "unit": "plf", "basis": "VE-1 Model"}},
            verifications=["VE-1 benchmark passed within 0.13%", "S1 unit engine validated"]
        )
        self.assertIn("ENGINEERING EVALUATION", memo)
        self.assertIn("ASCE 7-16", memo)
        self.assertIn("185.2", memo)

if __name__ == "__main__":
    unittest.main()
