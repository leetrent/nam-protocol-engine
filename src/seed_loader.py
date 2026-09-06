from pathlib import Path
from schemas import NAMProtocol, BiologicalEndpoint, RegulatoryCitation


def load_oecd_492_baseline() -> NAMProtocol:
    return NAMProtocol(
        protocol_id="oecd-tg-492-rhce",
        protocol_name="Reconstructed Human Cornea-Like Epithelium (RhCE) Test Method",
        technology_category="in_vitro",
        endpoint=BiologicalEndpoint(
            name="Serious Eye Damage / Eye Irritation",
            target_tissue="Cornea / Ocular",
            historical_animal_test="Draize Eye Test (OECD TG 405)",
        ),
        regulatory_status="Full Regulatory Acceptance",
        context_of_use=(
            "Identifies chemicals (substances and mixtures) not requiring classification "
            "and labelling for eye irritation or serious eye damage under UN GHS No Category."
        ),
        citations=[
            RegulatoryCitation(
                standard_body="OECD",
                guideline_id="OECD TG 492",
                document_title=(
                    "Reconstructed human Cornea-like Epithelium (RhCE) test method for "
                    "identifying chemicals not requiring classification and labelling for "
                    "eye irritation or serious eye damage"
                ),
                section_reference="Paragraphs 3-6, Table 4",
                official_url="https://doi.org/10.1787/9789264242548-en",
            )
        ],
    )


def load_oecd_497_baseline() -> NAMProtocol:
    """Instantiates validated ground-truth for OECD TG 497 Defined Approaches."""
    return NAMProtocol(
        protocol_id="oecd-tg-497-da-sensitisation",
        protocol_name="Defined Approaches on Skin Sensitisation (2o3 DA & ITSv1/v2)",
        technology_category="defined_approach",
        endpoint=BiologicalEndpoint(
            name="Skin Sensitisation",
            target_tissue="Dermal / Epidermal",
            historical_animal_test="Local Lymph Node Assay (LLNA - OECD TG 429) / Guinea Pig Maximisation Test (GPMT)",
        ),
        regulatory_status="Full Regulatory Acceptance",
        context_of_use=(
            "Rules-based combination of in chemico (DPRA) and in vitro assays (KeratinoSens, h-CLAT) "
            "with in silico tools to discriminate skin sensitisers from non-sensitisers and determine UN GHS sub-categorisation."
        ),
        citations=[
            RegulatoryCitation(
                standard_body="OECD",
                guideline_id="OECD TG 497",
                document_title="Defined Approaches on Skin Sensitisation",
                section_reference="Section 1, Paragraphs 1-12 & Annex I",
                official_url="https://doi.org/10.1787/ed27da84-en",
            )
        ],
    )


if __name__ == "__main__":
    out_dir = Path("data/processed")
    out_dir.mkdir(parents=True, exist_ok=True)

    protocols = [load_oecd_492_baseline(), load_oecd_497_baseline()]

    for proto in protocols:
        out_file = out_dir / f"{proto.protocol_id}_verified.json"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(proto.model_dump_json(indent=2))
        print(f"Generated verified ground-truth record: {out_file.name}")