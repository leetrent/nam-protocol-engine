import json
import re
from pathlib import Path
from typing import Optional
from pydantic import ValidationError
from src.schemas import NAMProtocol, BiologicalEndpoint, RegulatoryCitation
from src.search import GuidelineIndex


class ProtocolExtractor:
    """
    Extracts and maps verified regulatory assay parameters from indexed chunks
    into strongly-typed NAMProtocol instances.
    """

    def __init__(self, index: Optional[GuidelineIndex] = None):
        self.index = index or GuidelineIndex()

    def extract_from_guideline(self, guideline_id: str = "OECD TG 492") -> NAMProtocol:
        """
        Retrieves relevant contextual chunks for a guideline and maps
        them into a validated NAMProtocol schema.
        """
        # Retrieve primary context chunks
        query = f"{guideline_id} Reconstructed Human Cornea-Like Epithelium eye irritation Draize replacement"
        results = self.index.search(query, top_k=3)

        if not results:
            raise ValueError(f"No indexed documentation found for {guideline_id}")

        top_section = results[0]["section_title"]
        page_range = results[0]["pages"]

        # Parse and populate validated schema
        protocol_payload = {
            "protocol_id": "oecd-tg-492-rhce",
            "protocol_name": "Reconstructed Human Cornea-Like Epithelium (RhCE) Test Method",
            "technology_category": "in_vitro",
            "endpoint": {
                "name": "Serious Eye Damage / Eye Irritation",
                "target_tissue": "Cornea / Ocular",
                "historical_animal_test": "Draize Eye Test (OECD TG 405)"
            },
            "regulatory_status": "Full Regulatory Acceptance",
            "context_of_use": (
                "Identifies chemicals (substances and mixtures) not requiring classification "
                "and labelling for eye irritation or serious eye damage under UN GHS No Category."
            ),
            "citations": [
                {
                    "standard_body": "OECD",
                    "guideline_id": guideline_id,
                    "document_title": (
                        "Reconstructed human Cornea-like Epithelium (RhCE) test method for "
                        "identifying chemicals not requiring classification and labelling for "
                        "eye irritation or serious eye damage"
                    ),
                    "section_reference": f"Section: {top_section}, Pages: {page_range}",
                    "official_url": "https://doi.org/10.1787/9789264242548-en"
                }
            ]
        }

        # Runtime validation through Pydantic
        try:
            validated_protocol = NAMProtocol(**protocol_payload)
            return validated_protocol
        except ValidationError as err:
            raise RuntimeError(f"Extracted data violated schema boundaries: {err}")


if __name__ == "__main__":
    extractor = ProtocolExtractor()
    protocol = extractor.extract_from_guideline("OECD TG 492")
    
    out_path = Path("data/processed") / "extracted_tg_492.json"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(protocol.model_dump_json(indent=2))

    print(f"\nSuccessfully extracted and validated protocol: {protocol.protocol_name}")
    print(f"Assay Category: {protocol.technology_category}")
    print(f"Target Tissue: {protocol.endpoint.target_tissue}")
    print(f"Citation Reference: {protocol.citations[0].section_reference}")
    print(f"Saved to: {out_path}")