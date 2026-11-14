#!/usr/bin/env python3
"""
Unit tests for exhaustive offline code registries (code_registries.py).
Verifies ASCE 7-16, NEC 2023, ACI 318-19, ASHRAE 90.1, and SDI DDM04.
"""
import pytest
from code_registries import (
    get_asce7_kz,
    get_asce7_kzt,
    get_asce7_ke,
    calculate_asce7_velocity_pressure,
    get_nec_bundling_factor,
    get_nec_ambient_correction,
    size_conductor_nec,
    get_aci_development_length,
    ASHRAE_ENVELOPE_U_FACTORS,
    ASHRAE_CHILLER_EFFICIENCY,
    get_sdi_diaphragm_capacity
)

def test_asce7_kz_and_pressure():
    # Mean roof height 25 ft, Exposure C
    # Kz = 2.01 * (25/900)**(2/9.5) = 0.9453
    kz = get_asce7_kz(25.0, "C")
    assert 0.94 <= kz <= 0.95
    
    # Elevation 3900 ft
    ke = get_asce7_ke(3900.0)
    assert 0.86 <= ke <= 0.87
    
    # 115 mph wind pressure
    res = calculate_asce7_velocity_pressure(115.0, 25.0, "C", 3900.0, kzt=1.15, kd=0.85)
    assert res["qz_strength_psf"] > 25.0
    assert res["qz_asd_psf"] > 15.0

def test_nec_conductor_sizing():
    # 100A continuous load requires >= 125A base ampacity
    res = size_conductor_nec(100.0, 0.0, "Cu", "75C", ambient_temp_c=30.0, num_conductors=3)
    assert res["design_load_amps"] == 125.0
    # Table 310.16 75C: 1 AWG is 130A, 1/0 is 150A
    assert res["selected_size"] in ["1", "1/0"]
    assert res["effective_ampacity"] >= 125.0

def test_nec_bundling_and_ambient():
    # 7-9 conductors -> 0.70 factor
    assert get_nec_bundling_factor(8) == 0.70
    # 40C ambient at 75C rating -> 0.88 factor
    assert get_nec_ambient_correction(40.0, "75C") == 0.88

def test_aci_development_length():
    # #5 bar in 4000 psi concrete
    ld = get_aci_development_length(5, fc_psi=4000.0)
    assert ld > 12.0

def test_ashrae_envelope_and_chiller():
    # Climate zone 5 roof U-factor
    assert ASHRAE_ENVELOPE_U_FACTORS["5"]["roof_u"] == 0.028
    # Chiller path B efficiency
    assert ASHRAE_CHILLER_EFFICIENCY["water_cooled_centrifugal_ge_600_tons"]["path_b"]["iplv_kw_per_ton"] == 0.380

def test_sdi_diaphragm_capacity():
    # 20ga 36/7 @ 24" -> 580 plf
    cap = get_sdi_diaphragm_capacity(20, "36/7", 24)
    assert cap == 580.0
