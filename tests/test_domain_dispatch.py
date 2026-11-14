#!/usr/bin/env python3
"""
Test Move 2: Positive control verifying that MechanicalSuite is actively dispatched
on all 7 Mechanical engineering dev tasks.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
from harness import TaskContext, dispatch_domain_tools

class TestDomainDispatch(unittest.TestCase):

    def test_all_7_mechanical_tasks_dispatch_mechanical_suite(self):
        mechanical_tasks = [
            ("data-hall-mep-routing", "Route chilled water pipes and ductwork avoiding structural clashes"),
            ("data-hall-mep-routing-offset", "Calculate pipe offsets for condenser water loop"),
            ("cooling-water-flush-plan", "Determine velocity and head loss for process cooling water flush MOP"),
            ("heat-rejection-life-cycle-cost", "Compute 25-year LCC and NPV for cooling tower heat rejection"),
            ("fire-solve-convergence", "Verify hydraulic convergence of fire suppression sprinkler system"),
            ("fire-test-validation-memo", "Prepare engineering memo validating sprinkler flow rates per NFPA 13"),
            ("les-mesh-resolution", "Airflow distribution and duct sizing mesh sensitivity")
        ]
        
        for task_id, instruction in mechanical_tasks:
            ctx = TaskContext(task_id=task_id, instruction=instruction)
            trace = dispatch_domain_tools(ctx, domain="Mechanical engineering", instruction=instruction)
            
            # Assert at least one MechanicalSuite tool was invoked
            mech_tools = [t["tool"] for t in trace if t["tool"].startswith("MechanicalSuite")]
            print(f"Task {task_id}: dispatched {mech_tools}")
            self.assertGreater(len(mech_tools), 0, f"No MechanicalSuite tool dispatched for {task_id}")
            self.assertGreater(ctx.tool_calls, 0)
            self.assertGreater(len(ctx.working_memory), 0)

    def test_structural_dispatch(self):
        structural_tasks = [
            ("wind-diaphragm-shear", "Calculate roof diaphragm shear and wind wall loads for Building A2", "StructuralSuite.wind_diaphragm_analysis"),
            ("seismic-diaphragm-shear", "Evaluate seismic diaphragm design force Fpx and accidental torsion", "StructuralSuite.seismic_diaphragm_analysis"),
            ("roof-deck-design", "Design steel roof deck fastener spacing for uplift zones", "StructuralSuite.roof_deck_analysis"),
            ("eor-review-corrections", "Address EOR review comments and revision dispositions", "StructuralSuite.eor_review_disposition"),
        ]
        for task_id, instruction, expected_suite_tool in structural_tasks:
            ctx = TaskContext(task_id=task_id, instruction=instruction)
            trace = dispatch_domain_tools(ctx, domain="Structural engineering", instruction=instruction)
            tools = [t["tool"] for t in trace]
            self.assertIn("DualCalloutParser", tools)
            self.assertIn("CodeClauseVerifier", tools)
            self.assertIn("DimensionalEngine.convert", tools)
            self.assertIn(expected_suite_tool, tools, f"Missing {expected_suite_tool} in {task_id}")
            self.assertGreater(ctx.tool_calls, 0)

    def test_civil_and_electrical_dispatch(self):
        # Civil
        ctx_c = TaskContext(task_id="footing-settlement", instruction="Check consolidation settlement and site drainage")
        trace_c = dispatch_domain_tools(ctx_c, domain="Civil engineering", instruction="Check consolidation settlement")
        tools_c = [t["tool"] for t in trace_c]
        self.assertIn("CivilSuite.consolidation_settlement", tools_c)
        self.assertIn("CivilSuite.rational_runoff", tools_c)

        # Electrical
        ctx_e = TaskContext(task_id="lv-cable-sizing", instruction="Size low-voltage feeder cable and transformer rating")
        trace_e = dispatch_domain_tools(ctx_e, domain="Electrical engineering", instruction="Size low-voltage feeder cable")
        tools_e = [t["tool"] for t in trace_e]
        self.assertIn("ElectricalSuite.feeder_voltage_drop", tools_e)
        self.assertIn("ElectricalSuite.transformer_sizing", tools_e)

if __name__ == "__main__":
    unittest.main()
