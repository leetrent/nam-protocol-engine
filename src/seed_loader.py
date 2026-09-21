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

def load_oecd_439_baseline() -> NAMProtocol:
    """Instantiates validated ground-truth for OECD TG 439 RhE Skin Irritation."""
    return NAMProtocol(
        protocol_id="oecd-tg-439-rhe",
        protocol_name="In Vitro Skin Irritation: Reconstructed Human Epidermis (RhE) Test Method",
        technology_category="in_vitro",
        endpoint=BiologicalEndpoint(
            name="Skin Irritation",
            target_tissue="Dermal / Epidermal",
            historical_animal_test="Acute Dermal Irritation / Corrosion Test (OECD TG 404)",
        ),
        regulatory_status="Full Regulatory Acceptance",
        context_of_use=(
            "Identifies chemicals (substances and mixtures) inducing moderate skin irritation (UN GHS Category 2) "
            "from non-irritants (UN GHS No Category) as a stand-alone replacement for the rabbit test."
        ),
        citations=[
            RegulatoryCitation(
                standard_body="OECD",
                guideline_id="OECD TG 439",
                document_title="In Vitro Skin Irritation: Reconstructed Human Epidermis Test Method",
                section_reference="Paragraphs 1-10, Table 2",
                official_url="https://doi.org/10.1787/9789264242845-en",
            )
        ],
    )

def load_oecd_437_baseline() -> NAMProtocol:
    """Instantiates validated ground-truth for OECD TG 437 BCOP Ocular Assay."""
    return NAMProtocol(
        protocol_id="oecd-tg-437-bcop",
        protocol_name="Bovine Corneal Opacity and Permeability (BCOP) Test Method",
        technology_category="ex_vivo",
        endpoint=BiologicalEndpoint(
            name="Serious Eye Damage / Eye Irritation",
            target_tissue="Cornea / Ocular",
            historical_animal_test="Draize Eye Test (OECD TG 405)",
        ),
        regulatory_status="Full Regulatory Acceptance",
        context_of_use=(
            "Identifies chemicals inducing serious eye damage (UN GHS Category 1) and chemicals "
            "not requiring classification (UN GHS No Category) without further testing."
        ),
        citations=[
            RegulatoryCitation(
                standard_body="OECD",
                guideline_id="OECD TG 437",
                document_title=(
                    "Bovine Corneal Opacity and Permeability Test Method for Identifying "
                    "i) Chemicals Inducing Serious Eye Damage and ii) Chemicals Not Requiring "
                    "Classification for Eye Irritation or Serious Eye Damage"
                ),
                section_reference="Paragraphs 1-9, Table 2",
                official_url="https://doi.org/10.1787/9789264203846-en",
            )
        ],
    )

def load_oecd_431_baseline() -> NAMProtocol:
    """Instantiates validated ground-truth for OECD TG 431 RhE Skin Corrosion Assay."""
    return NAMProtocol(
        protocol_id="oecd-tg-431-rhe-corrosion",
        protocol_name="In Vitro Skin Corrosion: Reconstructed Human Epidermis (RhE) Test Method",
        technology_category="in_vitro",
        endpoint=BiologicalEndpoint(
            name="Skin Corrosion",
            target_tissue="Dermal / Epidermal",
            historical_animal_test="Acute Dermal Irritation / Corrosion Test (OECD TG 404)",
        ),
        regulatory_status="Full Regulatory Acceptance",
        context_of_use=(
            "Identifies corrosive chemicals (substances and mixtures) and non-corrosive chemicals, "
            "and supports sub-categorisation into optional UN GHS Sub-category 1A versus a combination "
            "of Sub-categories 1B-and-1C, as a stand-alone replacement for the rabbit skin test."
        ),
        citations=[
            RegulatoryCitation(
                standard_body="OECD",
                guideline_id="OECD TG 431",
                document_title="In Vitro Skin Corrosion: Reconstructed Human Epidermis (RHE) Test Method",
                section_reference="Paragraphs 1-12, Tables 4 & 5",
                official_url="https://doi.org/10.1787/9789264264618-en",
            )
        ],
    )
    
def load_oecd_432_baseline() -> NAMProtocol:
    """Instantiates validated ground-truth for OECD TG 432 In Vitro 3T3 NRU Phototoxicity."""
    return NAMProtocol(
        protocol_id="oecd-tg-432-3t3-nru",
        protocol_name="In Vitro 3T3 NRU Phototoxicity Test",
        technology_category="in_vitro",
        endpoint=BiologicalEndpoint(
            name="Phototoxicity",
            target_tissue="Balb/c 3T3 Mouse Fibroblasts (Cellular / Dermal Surrogate)",
            historical_animal_test="In Vivo Acute Phototoxicity / Photo-irritation in Animals",
        ),
        regulatory_status="Full Regulatory Acceptance",
        context_of_use=(
            "Identifies the phototoxic potential of chemicals activated by exposure to light, "
            "evaluating photo-cytotoxicity through relative viability reduction in Balb/c 3T3 cells "
            "(+UVA vs -UVA) using PIF (Photo-Irritation Factor) and MPE (Mean Photo Effect) metrics."
        ),
        citations=[
            RegulatoryCitation(
                standard_body="OECD",
                guideline_id="OECD TG 432",
                document_title="In Vitro 3T3 NRU Phototoxicity Test",
                section_reference="Paragraphs 1-8, 53-58, Table 1",
                official_url="https://doi.org/10.1787/9789264071162-en",
            )
        ],
    )    
    
def load_oecd_442c_baseline() -> NAMProtocol:
    """Baseline seed definition for OECD TG 442C (Direct Peptide Reactivity Assay - DPRA)."""
    return NAMProtocol(
        protocol_id="oecd-tg-442c-dpra",
        protocol_name="In Chemico Skin Sensitisation: Direct Peptide Reactivity Assay (DPRA)",
        technology_category="in_chemico",
        endpoint=BiologicalEndpoint(
            name="Skin Sensitisation (Molecular Initiating Event / Key Event 1)",
            target_tissue="Dermal",
            historical_animal_test="OECD TG 429 Murine Local Lymph Node Assay (LLNA) / OECD TG 406 Guinea Pig Maximisation Test (GPMT)",
        ),
        regulatory_status="Full Regulatory Acceptance",
        context_of_use=(
            "Quantifies synthetic heptapeptide depletion (cysteine Ac-RFAACAA-COOH at 1:10 ratio and lysine "
            "Ac-RFAAKAA-COOH at 1:50 ratio) via HPLC-UV at 220 nm following 24h incubation. Supports "
            "discrimination between skin sensitisers (UN GHS Category 1) and non-sensitisers within IATA or "
            "Defined Approaches (e.g. OECD TG 497). Cysteine/lysine mean depletion > 6.38% (or cysteine-only > 13.89%) "
            "predicts skin sensitisation. Not applicable to metals, strict pro-haptens requiring enzymatic bioactivation, "
            "or test chemicals co-eluting with both peptides."
        ),
        citations=[
            RegulatoryCitation(
                standard_body="OECD",
                guideline_id="OECD TG 442C",
                document_title="Test No. 442C: In Chemico Skin Sensitisation: Assays addressing the Adverse Outcome Pathway key event on covalent binding to proteins",
                section_reference="Appendix I: Direct Peptide Reactivity Assay (DPRA), Paragraphs 1-26 & Table 1-2",
                official_url="https://doi.org/10.1787/9789264229709-en",
            ),
            RegulatoryCitation(
                standard_body="OECD",
                guideline_id="OECD TG 497",
                document_title="Guideline No. 497: Defined Approaches on Skin Sensitisation",
                section_reference="Section 2: Information Sources (Key Event 1 - DPRA)",
                official_url="https://doi.org/10.1787/b92879a4-en",
            ),
        ],
    )
    
    
    
if __name__ == "__main__":
    out_dir = Path("data/processed")
    out_dir.mkdir(parents=True, exist_ok=True)

    protocols = [
        load_oecd_492_baseline(),
        load_oecd_497_baseline(),
        load_oecd_439_baseline(),
        load_oecd_437_baseline(),
        load_oecd_431_baseline(),
        load_oecd_432_baseline(),
        load_oecd_442c_baseline()
    ]

    for proto in protocols:
        out_file = out_dir / f"{proto.protocol_id}_verified.json"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(proto.model_dump_json(indent=2))
        print(f"Generated verified ground-truth record: {out_file.name}")