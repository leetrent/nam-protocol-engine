from dataclasses import dataclass, field
from typing import List, Optional
from src.matcher import ProtocolMatcher, MatchResult


@dataclass
class StrategyStep:
    step_number: int
    title: str
    rationale: str
    match_result: MatchResult
    decision_threshold: str


@dataclass
class TieredStrategyPlan:
    framework: str
    endpoint_battery: str
    test_article_state: str
    hazard_intent: str
    steps: List[StrategyStep] = field(default_factory=list)
    dossier_text: str = ""


class RegulatoryStrategyPlanner:
    """Plans tiered testing batteries according to OECD and UN GHS testing strategies."""

    def __init__(self, matcher: Optional[ProtocolMatcher] = None):
        self.matcher = matcher or ProtocolMatcher()

    def generate_strategy(
        self,
        framework: str,
        endpoint: str,
        physical_state: str,
        hazard_intent: str,
    ) -> TieredStrategyPlan:
        plan = TieredStrategyPlan(
            framework=framework,
            endpoint_battery=endpoint,
            test_article_state=physical_state,
            hazard_intent=hazard_intent,
        )

        if endpoint == "Dermal (Corrosion & Irritation)":
            # Tier 1: Corrosion evaluation
            t1_match = self.matcher.find_alternative("in vitro skin corrosion necrosis OECD TG 431")
            plan.steps.append(
                StrategyStep(
                    step_number=1,
                    title="Tier 1: Skin Corrosion Assessment (OECD TG 431)",
                    rationale=(
                        "Mandatory first step under UN GHS / OECD Guidance 203. Corrosion must be "
                        "ruled out prior to any skin irritation testing."
                    ),
                    match_result=t1_match,
                    decision_threshold=(
                        "If Viability < 50% (3 min) or < 15% (60 min) -> Classify UN GHS Category 1 "
                        "(Sub-cat 1A or 1B/1C). Stop testing. Living animals not permitted."
                    ),
                )
            )

            # Tier 2: Irritation evaluation (only if non-corrosive in Tier 1)
            t2_match = self.matcher.find_alternative("in vitro skin irritation reconstructed human epidermis OECD TG 439")
            plan.steps.append(
                StrategyStep(
                    step_number=2,
                    title="Tier 2: Skin Irritation Assessment (OECD TG 439)",
                    rationale=(
                        "Conducted only if Tier 1 yields Non-Corrosive. Determines UN GHS Category 2 "
                        "versus No Category (non-irritant)."
                    ),
                    match_result=t2_match,
                    decision_threshold=(
                        "If Viability <= 50% -> UN GHS Category 2 (Irritant). "
                        "If Viability > 50% -> UN GHS No Category."
                    ),
                )
            )

        elif endpoint == "Ocular (Severe Damage & Irritation)":
            if hazard_intent in ("Top-Down (Suspected High Hazard)", "Full Battery"):
                # BCOP for Severe Damage
                t1_match = self.matcher.find_alternative("bovine corneal opacity permeability severe eye damage OECD TG 437")
                plan.steps.append(
                    StrategyStep(
                        step_number=1,
                        title="Top-Down Tier 1: Bovine Corneal Opacity and Permeability (OECD TG 437)",
                        rationale="Screening for severe ocular damage (UN GHS Cat 1) directly.",
                        match_result=t1_match,
                        decision_threshold=(
                            "If IVIS > 55 -> Classify UN GHS Category 1 (Serious Eye Damage). Stop testing."
                        ),
                    )
                )

            if hazard_intent in ("Bottom-Up (Suspected Low/No Hazard)", "Full Battery"):
                # RhCE for Irritation / No Category
                t2_match = self.matcher.find_alternative("reconstructed human cornea rhce eye irritation OECD TG 492")
                plan.steps.append(
                    StrategyStep(
                        step_number=2 if plan.steps else 1,
                        title="Bottom-Up Tier: RhCE Eye Irritation (OECD TG 492)",
                        rationale="Identifies chemicals not requiring classification for eye irritation.",
                        match_result=t2_match,
                        decision_threshold=(
                            "If Viability > 60% -> UN GHS No Category without animal testing."
                        ),
                    )
                )

        elif endpoint == "Skin Sensitisation":
            sens_match = self.matcher.find_alternative("skin sensitisation defined approach OECD TG 497")
            plan.steps.append(
                StrategyStep(
                    step_number=1,
                    title="Stand-alone Defined Approach Battery (OECD TG 497)",
                    rationale="Replaces murine LLNA (TG 429) using in silico + in chemico/in vitro assays.",
                    match_result=sens_match,
                    decision_threshold=(
                        "Apply '2 out of 3' (DPRA, KeratinoSens, h-CLAT) or ITSv1/ITSv2 decision tree "
                        "to determine sensitizer vs. non-sensitizer and UN GHS 1A/1B sub-category."
                    ),
                )
            )

        # Generate the formatted dossier summary
        plan.dossier_text = self._compile_dossier(plan)
        return plan

    def _compile_dossier(self, plan: TieredStrategyPlan) -> str:
        dossier = [
            "# REGULATORY TESTING STRATEGY & NAM JUSTIFICATION DOSSIER",
            f"**Regulatory Framework Target:** {plan.framework}",
            f"**Endpoint Evaluated:** {plan.endpoint_battery}",
            f"**Test Article Physical Form:** {plan.test_article_state}",
            f"**Evaluation Strategy:** {plan.hazard_intent}",
            "\n---\n",
            "## 1. Executive Summary & 3Rs Non-Animal Replacement Strategy",
            (
                f"In accordance with 3Rs principles and {plan.framework} regulatory acceptance criteria, "
                f"this assessment specifies a non-animal testing cascade for '{plan.endpoint_battery}'. "
                "Animal testing (e.g., OECD TG 404, TG 405, TG 429) is waived in favor of fully accepted "
                "OECD Test Guidelines (Mutual Acceptance of Data - MAD compliant).\n"
            ),
            "## 2. Testing Battery & Decision Criteria",
        ]

        for step in plan.steps:
            proto = step.match_result.protocol
            dossier.append(f"### {step.title}")
            dossier.append(f"- **Rationale:** {step.rationale}")
            dossier.append(f"- **Decision Cut-off:** {step.decision_threshold}")
            if proto:
                dossier.append(f"- **Method Specification:** {proto.protocol_name} (`{proto.technology_category}`)")
                for cit in proto.citations:
                    dossier.append(f"- **Citation:** {cit.standard_body} {cit.guideline_id} - *{cit.document_title}*")
                    dossier.append(f"  - Scope: {cit.section_reference}")
            dossier.append("")

        dossier.append("## 3. Applicable Regulatory Excerpt References")
        for step in plan.steps:
            for ev in step.match_result.supporting_evidence:
                dossier.append(f"> {ev}\n")

        dossier.append("---\n*Generated by NAM Protocol Engine | Regulatory Strategy Module*")
        return "\n".join(dossier)