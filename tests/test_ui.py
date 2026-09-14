import pytest
from src.app import build_app, execute_strategy, run_phototoxicity_calc


def test_ui_build_app_structure():
    demo = build_app()
    assert demo is not None
    assert hasattr(demo, "blocks")


def test_ui_execute_phototoxicity_strategy():
    card_display, dossier_text = execute_strategy(
        framework="UN GHS / EU REACH",
        endpoint="Phototoxicity",
        physical_state="Liquid",
        hazard_intent="Screening Battery",
    )

    assert "In Vitro 3T3 NRU Phototoxicity Test (OECD TG 432)" in card_display
    assert "PIF < 2" in card_display
    assert "REGULATORY TESTING STRATEGY & NAM JUSTIFICATION DOSSIER" in dossier_text
    assert "OECD TG 432" in dossier_text


def test_ui_run_phototoxicity_calc_validation():
    # Empty inputs guard
    empty_res = run_phototoxicity_calc(0, 0, 0)
    assert "⚠️ Please provide at least one metric" in empty_res

    # Test Case A: MEC waive-out precedence over zeroed PIF/MPE
    mec_res = run_phototoxicity_calc(pif_val=0, mpe_val=0, mec_val=450)
    assert "Non-Photoreactive (Waived)" in mec_res
    assert "color:green" in mec_res
    assert "Requires Confirmatory Testing:** `No`" in mec_res

    # Equivocal warning & color badge
    equiv_res = run_phototoxicity_calc(pif_val=3.2, mpe_val=0, mec_val=0)
    assert "Equivocal Phototoxicity" in equiv_res
    assert "color:orange" in equiv_res
    assert "Requires Confirmatory Testing:** `Yes" in equiv_res

    # Positive classification & color badge
    pos_res = run_phototoxicity_calc(pif_val=8.5, mpe_val=0, mec_val=0)
    assert "Phototoxicity" in pos_res
    assert "color:red" in pos_res
    assert "Requires Confirmatory Testing:** `No`" in pos_res