import pytest
from src.strategy import RegulatoryStrategyPlanner, evaluate_phototoxicity


@pytest.fixture
def planner():
    return RegulatoryStrategyPlanner()


def test_dermal_tiered_battery(planner):
    plan = planner.generate_strategy(
        framework="UN GHS / EU REACH",
        endpoint="Dermal (Corrosion & Irritation)",
        physical_state="Liquid",
        hazard_intent="Full Battery",
    )

    assert len(plan.steps) == 2
    assert plan.steps[0].title.startswith("Tier 1: Skin Corrosion")
    assert plan.steps[0].match_result.protocol.protocol_id == "oecd-tg-431-rhe-corrosion"
    assert plan.steps[1].title.startswith("Tier 2: Skin Irritation")
    assert plan.steps[1].match_result.protocol.protocol_id == "oecd-tg-439-rhe"
    assert "OECD TG 404" in plan.dossier_text


def test_ocular_top_down_strategy(planner):
    plan = planner.generate_strategy(
        framework="US EPA",
        endpoint="Ocular (Severe Damage & Irritation)",
        physical_state="Solid",
        hazard_intent="Top-Down (Suspected High Hazard)",
    )

    assert len(plan.steps) == 1
    assert "OECD TG 437" in plan.steps[0].title
    assert plan.steps[0].match_result.protocol.protocol_id == "oecd-tg-437-bcop"
    assert "IVIS > 55" in plan.steps[0].decision_threshold


def test_sensitisation_da_strategy(planner):
    plan = planner.generate_strategy(
        framework="UN GHS",
        endpoint="Skin Sensitisation",
        physical_state="Liquid",
        hazard_intent="Full Battery",
    )

    assert len(plan.steps) == 1
    assert plan.steps[0].match_result.protocol.protocol_id == "oecd-tg-497-da-sensitisation"
    assert "2 out of 3" in plan.steps[0].decision_threshold


def test_phototoxicity_strategy_plan(planner):
    plan = planner.generate_strategy(
        framework="UN GHS / EU REACH",
        endpoint="Phototoxicity",
        physical_state="Liquid",
        hazard_intent="Screening Battery",
    )

    assert len(plan.steps) == 1
    assert "OECD TG 432" in plan.steps[0].title
    assert plan.steps[0].match_result.protocol.protocol_id == "oecd-tg-432-3t3-nru"
    assert "PIF < 2" in plan.steps[0].decision_threshold
    assert "PIF >= 5" in plan.steps[0].decision_threshold


def test_evaluate_phototoxicity_pif_thresholds():
    # Negative: PIF < 2
    res_neg = evaluate_phototoxicity(pif=1.4)
    assert res_neg["classification"] == "No Phototoxicity"
    assert res_neg["prediction"] == "Negative"
    assert res_neg["requires_confirmatory"] is False

    # Equivocal: 2 <= PIF < 5
    res_eq = evaluate_phototoxicity(pif=3.2)
    assert res_eq["classification"] == "Equivocal Phototoxicity"
    assert res_eq["requires_confirmatory"] is True

    # Positive: PIF >= 5
    res_pos = evaluate_phototoxicity(pif=8.5)
    assert res_pos["classification"] == "Phototoxicity"
    assert res_pos["prediction"] == "Positive"
    assert res_pos["requires_confirmatory"] is False


def test_evaluate_phototoxicity_mpe_thresholds():
    # Negative: MPE < 0.1
    res_neg = evaluate_phototoxicity(mpe=0.04)
    assert res_neg["classification"] == "No Phototoxicity"

    # Equivocal: 0.1 <= MPE < 0.15
    res_eq = evaluate_phototoxicity(mpe=0.12)
    assert res_eq["classification"] == "Equivocal Phototoxicity"
    assert res_eq["requires_confirmatory"] is True

    # Positive: MPE >= 0.15
    res_pos = evaluate_phototoxicity(mpe=0.25)
    assert res_pos["classification"] == "Phototoxicity"


def test_evaluate_phototoxicity_mec_screening():
    # Low MEC: waives biological testing
    res_mec = evaluate_phototoxicity(mec=450.0)
    assert res_mec["prediction"] == "No Phototoxicity"
    assert "Waived" in res_mec["classification"]