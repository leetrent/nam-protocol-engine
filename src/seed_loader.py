from pathlib import Path
from schemas import NAMProtocol, BiologicalEndpoint, RegulatoryCitation


def load_oecd_492_baseline() -> NAMProtocol:
    """Instantiates a validated ground-truth entry directly from OECD TG 492."""
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


if __name__ == "__main__":
    protocol = load_oecd_492_baseline()
    out_dir = Path("data/processed")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "oecd_tg_492_verified.json"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(protocol.model_dump_json(indent=2))
    print(f"Generated verified ground-truth record: {out_file}")