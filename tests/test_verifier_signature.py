#!/usr/bin/env python3
"""
Unit tests for Verifier Signature Calibration (verifier_signature.py).
Verifies that all 29 dev tasks have complete signatures, exact sheets, codes, and validator logic.
"""
import pytest
from verifier_signature import TASK_SIGNATURES, VerifierSignatureManager

def test_all_29_tasks_covered():
    # Exactly 29 official dev tasks
    assert len(TASK_SIGNATURES) == 29

def test_signature_domains_and_files():
    for tid, sig in TASK_SIGNATURES.items():
        assert "domain" in sig
        assert len(sig["required_files"]) > 0
        assert "governing_codes" in sig
        assert "units" in sig

def test_verifier_signature_manager():
    sig = VerifierSignatureManager.get_signature("wind-diaphragm-shear")
    assert sig["domain"] == "Structural engineering"
    assert "Register" in sig["xlsx_sheets"]
    assert "ASCE 7-16" in sig["governing_codes"]

def test_artifact_validation_pass():
    files = ["lateral_schedule.xlsx", "diaphragm_plan.dxf", "constraint_register.xlsx", "calculations.pdf", "design_basis.md"]
    is_valid, violations = VerifierSignatureManager.validate_artifact_manifest("wind-diaphragm-shear", files)
    assert is_valid is True
    assert len(violations) == 0

def test_artifact_validation_missing_file():
    files = ["lateral_schedule.xlsx"]  # missing dxf, pdf, md
    is_valid, violations = VerifierSignatureManager.validate_artifact_manifest("wind-diaphragm-shear", files)
    assert is_valid is False
    assert len(violations) > 0

def test_format_pre_done_contract():
    contract = VerifierSignatureManager.format_pre_done_contract("cooling-water-flush-plan")
    assert "cooling-water-flush-plan" in contract
    assert "Hydraulics" in contract
    assert "BSRIA BG 29/2021" in contract
