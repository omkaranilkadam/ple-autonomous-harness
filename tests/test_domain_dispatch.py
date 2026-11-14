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
        ctx = TaskContext(task_id="wind-diaphragm-shear", instruction="Calculate roof diaphragm shear and wall loads")
        trace = dispatch_domain_tools(ctx, domain="Structural engineering", instruction="Calculate roof diaphragm shear")
        tools = [t["tool"] for t in trace]
        self.assertIn("DualCalloutParser", tools)
        self.assertIn("CodeClauseVerifier", tools)
        self.assertIn("DimensionalEngine.convert", tools)

if __name__ == "__main__":
    unittest.main()
