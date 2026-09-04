import pytest
from pydantic import ValidationError
from src.schemas import NAMProtocol, BiologicalEndpoint, RegulatoryCitation


def test_valid_nam_protocol():
    protocol = NAMProtocol(
        protocol_id="oecd-tg-492-epiocular",
        protocol_name="EpiOcular Eye Irritation Test (EIT)",
        technology_category="in_vitro",
        endpoint=BiologicalEndpoint(
            name="Eye Irritation",
            target_tissue="Ocular",
            historical_animal_test="Draize Eye Test (OECD 405)",
        ),
        regulatory_status="Full Regulatory Acceptance",
        context_of_use="Identification of chemicals not requiring classification for eye irritation",
        citations=[
            RegulatoryCitation(
                standard_body="OECD",
                guideline_id="OECD TG 492",
                document_title="Reconstructed human Cornea-like Epithelium (RhCE) Test Method",
                section_reference="Section 2, Paragraph 14",
            )
        ],
    )
    assert protocol.technology_category == "in_vitro"
    assert len(protocol.citations) == 1
    assert protocol.endpoint.target_tissue == "Ocular"


def test_invalid_category_fails():
    with pytest.raises(ValidationError):
        NAMProtocol(
            protocol_id="invalid-test",
            protocol_name="Invalid Category Assay",
            technology_category="animal_test",  # Not in allowed Literal values
            endpoint=BiologicalEndpoint(
                name="Toxicity",
                target_tissue="General",
                historical_animal_test="None",
            ),
            regulatory_status="Exploratory",
            context_of_use="Testing validation bounds",
            citations=[],
        )


def test_invalid_standard_body_fails():
    with pytest.raises(ValidationError):
        RegulatoryCitation(
            standard_body="INVALID_BODY",  # Must be OECD, FDA, EPA, EMA, or ICH
            guideline_id="TG-000",
            document_title="Test Doc",
            section_reference="Para 1",
        )