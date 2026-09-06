import pytest
from src.extractor import ProtocolExtractor
from src.schemas import NAMProtocol


def test_extractor_populates_valid_protocol():
    extractor = ProtocolExtractor()
    protocol = extractor.extract_from_guideline("OECD TG 492")

    assert isinstance(protocol, NAMProtocol)
    assert protocol.technology_category == "in_vitro"
    assert protocol.endpoint.name == "Serious Eye Damage / Eye Irritation"
    assert len(protocol.citations) == 1
    assert protocol.citations[0].standard_body == "OECD"
    assert "Pages:" in protocol.citations[0].section_reference


def test_extractor_fails_on_missing_guideline():
    extractor = ProtocolExtractor()
    # Query that will not return valid guideline documentation
    extractor.index.documents = []  # Simulate empty index
    with pytest.raises(ValueError, match="No indexed documentation found"):
        extractor.extract_from_guideline("NONEXISTENT TG 999")