import sys
from pathlib import Path
import gradio as gr

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.matcher import ProtocolMatcher
from src.strategy import RegulatoryStrategyPlanner

matcher = ProtocolMatcher()
planner = RegulatoryStrategyPlanner(matcher)

SAMPLE_QUERIES = [
    "Draize rabbit eye irritation test replacement",
    "severe eye damage bovine corneal opacity test",
    "in vitro skin corrosion necrosis sub-category 1A OECD TG 404",
    "acute dermal irritation rabbit test OECD 404 replacement",
    "skin sensitization local lymph node assay LLNA alternative",
    "unrelated aerospace tensile stress evaluation",
]


def execute_strategy(
    framework: str,
    endpoint: str,
    physical_state: str,
    hazard_intent: str,
):
    plan = planner.generate_strategy(
        framework=framework,
        endpoint=endpoint,
        physical_state=physical_state,
        hazard_intent=hazard_intent,
    )

    strategy_cards = []
    for step in plan.steps:
        proto = step.match_result.protocol
        proto_name = proto.protocol_name if proto else "No protocol registered"
        tech_cat = proto.technology_category if proto else "N/A"

        card = f"""
### {step.title}
* **Objective:** {step.rationale}
* **Testing Protocol:** **{proto_name}** (`{tech_cat}`)
* **Decision Rule:** `{step.decision_threshold}`
"""
        strategy_cards.append(card)

    strategy_display = "\n---\n".join(strategy_cards)
    return strategy_display, plan.dossier_text


def format_protocol_match(query_text: str):
    if not query_text or not query_text.strip():
        return (
            "<p style='color: gray;'>Enter a query above to see matches.</p>",
            "<p style='color: gray;'>No citations retrieved.</p>",
            "{}",
        )

    result = matcher.find_alternative(query_text)

    if result.matched and result.protocol:
        proto = result.protocol
        details_md = f"""
### Recommended Alternative
* **Protocol Name:** {proto.protocol_name}
* **Technology Category:** `{proto.technology_category}`
* **Target Tissue:** {proto.endpoint.target_tissue}
* **Historical Test Replaced:** {proto.endpoint.historical_animal_test}
* **Regulatory Acceptance:** {proto.regulatory_status}

> **Context of Use:** {proto.context_of_use}
"""
    else:
        details_md = f"### No Direct Protocol Match\n\n{result.recommendation}"

    if result.supporting_evidence:
        citations_md = "### Regulatory Citations & Excerpts\n"
        for ev in result.supporting_evidence:
            citations_md += f"- {ev}\n\n"
    else:
        citations_md = "### Supporting Citations\n*No specific guideline excerpts retrieved.*"

    json_payload = result.protocol.model_dump_json(indent=2) if result.protocol else "{}"

    return details_md, citations_md, json_payload


def build_app():
    with gr.Blocks(title="NAM Protocol Engine") as demo:
        gr.Markdown(
            """
            # 🔬 NAM Protocol Engine
            ### Regulatory Decision Dashboard for Animal Testing Alternatives (3Rs)
            Standardized non-animal replacement workflows across **OECD TG 431**, **TG 437**, **TG 439**, **TG 492**, and **TG 497**.
            """
        )

        with gr.Tabs():
            # Tab 1: Guided Decision Dashboard & Dossier Exporter
            with gr.TabItem("📋 Guided Strategy & Dossier Exporter"):
                gr.Markdown("Configure testing criteria to generate a tiered testing strategy and regulatory dossier.")

                with gr.Row():
                    with gr.Column(scale=1):
                        framework_in = gr.Dropdown(
                            label="Regulatory Target Framework",
                            choices=["UN GHS / EU REACH", "US EPA", "ICH / US FDA"],
                            value="UN GHS / EU REACH",
                        )
                        endpoint_in = gr.Dropdown(
                            label="Endpoint / Battery",
                            choices=[
                                "Dermal (Corrosion & Irritation)",
                                "Ocular (Severe Damage & Irritation)",
                                "Skin Sensitisation",
                            ],
                            value="Dermal (Corrosion & Irritation)",
                        )
                        state_in = gr.Dropdown(
                            label="Test Article Physical Form",
                            choices=["Liquid", "Solid / Powder", "Viscous / Waxy", "Surfactant / Neat"],
                            value="Liquid",
                        )
                        intent_in = gr.Dropdown(
                            label="Hazard Strategy / Intent",
                            choices=[
                                "Full Battery",
                                "Top-Down (Suspected High Hazard)",
                                "Bottom-Up (Suspected Low/No Hazard)",
                            ],
                            value="Full Battery",
                        )
                        generate_btn = gr.Button("Generate Strategy Plan", variant="primary")

                    with gr.Column(scale=2):
                        strategy_out = gr.Markdown(label="Tiered Strategy Sequence")
                        dossier_out = gr.Code(
                            label="Regulatory Dossier & NAM Justification (Markdown)",
                            language="markdown",
                            lines=16,
                        )

                generate_btn.click(
                    fn=execute_strategy,
                    inputs=[framework_in, endpoint_in, state_in, intent_in],
                    outputs=[strategy_out, dossier_out],
                )

            # Tab 2: Freeform Search Workbench
            with gr.TabItem("🔍 Interactive Guideline Search"):
                with gr.Row():
                    with gr.Column(scale=2):
                        query_input = gr.Textbox(
                            label="Enter Endpoint, Animal Test, or Assay Name",
                            placeholder="e.g. Draize rabbit eye test, skin sensitisation LLNA, acute dermal irritation...",
                            lines=2,
                        )
                        submit_btn = gr.Button("Find Regulatory Alternative", variant="primary")

                    with gr.Column(scale=1):
                        example_dropdown = gr.Dropdown(
                            label="Sample Regulatory Queries",
                            choices=SAMPLE_QUERIES,
                            value=SAMPLE_QUERIES[0],
                        )
                        load_example_btn = gr.Button("Load Example")

                with gr.Row():
                    details_output = gr.Markdown()
                    citations_output = gr.Markdown()

                with gr.Accordion("Raw Protocol Schema Payload (JSON)", open=False):
                    json_output = gr.Code(language="json")

                submit_btn.click(
                    fn=format_protocol_match,
                    inputs=[query_input],
                    outputs=[details_output, citations_output, json_output],
                )
                query_input.submit(
                    fn=format_protocol_match,
                    inputs=[query_input],
                    outputs=[details_output, citations_output, json_output],
                )

                def load_example(example_text: str):
                    d_md, c_md, j_out = format_protocol_match(example_text)
                    return example_text, d_md, c_md, j_out

                load_example_btn.click(
                    fn=load_example,
                    inputs=[example_dropdown],
                    outputs=[query_input, details_output, citations_output, json_output],
                )

    return demo


demo = build_app()

# if __name__ == "__main__":
#     demo.launch(
#         server_name="127.0.0.1",
#         server_port=7860,
#         theme=gr.themes.Soft(),
#     )
    
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860
    )