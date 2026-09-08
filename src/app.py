import json
import sys
from pathlib import Path
import gradio as gr

# Ensure repository root is on sys.path when running script directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.matcher import ProtocolMatcher

matcher = ProtocolMatcher()

SAMPLE_QUERIES = [
    "Draize rabbit eye irritation test replacement",
    "severe eye damage bovine corneal opacity test",
    "skin sensitization local lymph node assay LLNA alternative",
    "acute dermal irritation rabbit test OECD 404 replacement",
    "unrelated aerospace tensile stress evaluation",
]

def format_protocol_match(query: str):
    if not query.strip():
        return (
            "### ⚠️ Please enter a query",
            "",
            "{}",
        )

    result = matcher.find_alternative(query)

    if not result.matched:
        summary_md = f"""### ❌ No Direct Protocol Match
**Query:** `{result.query}`

**Recommendation:**
{result.recommendation}
"""
        evidence_md = "#### Supporting Regulatory Index Hits:\n"
        if result.supporting_evidence:
            for ev in result.supporting_evidence:
                evidence_md += f"- {ev}\n"
        else:
            evidence_md += "_No relevant regulatory sections found in corpus._"

        return summary_md, evidence_md, json.dumps(result.model_dump(), indent=2)

    proto = result.protocol
    summary_md = f"""### ✅ Validated NAM Alternative Located

| Attribute | Specification |
| :--- | :--- |
| **Protocol Name** | **{proto.protocol_name}** |
| **Protocol ID** | `{proto.protocol_id}` |
| **Technology Category** | `{proto.technology_category}` |
| **Regulatory Status** | **{proto.regulatory_status}** |
| **Target Tissue** | {proto.endpoint.target_tissue} |
| **Historical Animal Test** | **{proto.endpoint.historical_animal_test}** |

#### Context of Use
> {proto.context_of_use}

#### Primary Recommendation
{result.recommendation}
"""

    evidence_md = "#### Primary Regulatory Citations\n"
    for cit in proto.citations:
        evidence_md += f"- **{cit.standard_body} - {cit.guideline_id}**: *{cit.document_title}*\n"
        evidence_md += f"  - Section Reference: `{cit.section_reference}`\n"
        if cit.official_url:
            evidence_md += f"  - URL: [{cit.official_url}]({cit.official_url})\n"

    evidence_md += "\n#### Scoped Excerpt Previews\n"
    for idx, ev in enumerate(result.supporting_evidence, 1):
        evidence_md += f"**[{idx}]** {ev}\n\n"

    return summary_md, evidence_md, json.dumps(result.model_dump(), indent=2)


#with gr.Blocks(title="NAM Protocol Engine", theme=gr.themes.Soft()) as demo:
with gr.Blocks(title="NAM Protocol Engine") as demo:
    gr.Markdown(
        """
        # 🔬 NAM Protocol Engine
        ### Regulatory Alternative Matcher for Animal Toxicity Testing Guidelines
        Query endpoint replacements across **OECD TG 437**, **TG 439**, **TG 492**, and **TG 497**.
        """
    )

    with gr.Row():
        with gr.Column(scale=4):
            query_input = gr.Textbox(
                label="Enter Endpoint, Animal Test, or Assay Name",
                placeholder="e.g. Draize rabbit eye test, skin sensitization LLNA, acute dermal irritation...",
                lines=2,
            )
            submit_btn = gr.Button("Find Regulatory Alternative", variant="primary")
        
        with gr.Column(scale=2):
            gr.Markdown("**Quick Examples**")
            example_dropdown = gr.Dropdown(
                choices=SAMPLE_QUERIES,
                label="Sample Regulatory Queries",
                value=SAMPLE_QUERIES[0],
            )
            example_btn = gr.Button("Load Example", size="sm")

    with gr.Row():
        with gr.Column(scale=1):
            match_summary = gr.Markdown(label="Match Details")
        with gr.Column(scale=1):
            citations_box = gr.Markdown(label="Citations & Evidence")

    with gr.Accordion("Raw Protocol Schema Payload (JSON)", open=False):
        json_output = gr.Code(language="json", label="Serialized Pydantic Output")

    submit_btn.click(
        fn=format_protocol_match,
        inputs=[query_input],
        outputs=[match_summary, citations_box, json_output],
    )

    query_input.submit(
        fn=format_protocol_match,
        inputs=[query_input],
        outputs=[match_summary, citations_box, json_output],
    )

    example_btn.click(
        fn=lambda ex: (ex, *format_protocol_match(ex)),
        inputs=[example_dropdown],
        outputs=[query_input, match_summary, citations_box, json_output],
    )


# if __name__ == "__main__":
#     demo.launch(server_name="127.0.0.1", server_port=7860)
    
if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        theme=gr.themes.Soft(),
    )