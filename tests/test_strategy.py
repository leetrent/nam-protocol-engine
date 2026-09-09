import pytest
from src.strategy import RegulatoryStrategyPlanner


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