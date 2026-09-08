from src.matcher import ProtocolMatcher


def test_matcher_finds_draize_alternative():
    matcher = ProtocolMatcher()
    result = matcher.find_alternative("in vitro Draize rabbit eye test replacement")

    assert result.matched is True
    assert result.protocol is not None
    assert result.protocol.protocol_id == "oecd-tg-492-rhce"
    assert "Draize Eye Test" in result.recommendation
    assert len(result.supporting_evidence) > 0
    
def test_matcher_finds_skin_sensitisation_alternative():
    matcher = ProtocolMatcher()
    result = matcher.find_alternative("skin sensitization local lymph node assay replacement")

    assert result.matched is True
    assert result.protocol is not None
    assert result.protocol.protocol_id == "oecd-tg-497-da-sensitisation"
    assert "LLNA" in result.recommendation or "Local Lymph Node" in result.recommendation    
    
def test_matcher_handles_unknown_query():
    matcher = ProtocolMatcher()
    result = matcher.find_alternative("unrelated aerospace metallurgy stress test")

    assert result.matched is False
    assert result.protocol is None
    
def test_matcher_finds_skin_irritation_alternative():
    matcher = ProtocolMatcher()
    result = matcher.find_alternative("in vitro skin irritation Draize rabbit skin replacement OECD TG 404")

    assert result.matched is True
    assert result.protocol is not None
    assert result.protocol.protocol_id == "oecd-tg-439-rhe"
    assert "OECD TG 404" in result.recommendation
    
def test_matcher_finds_bcop_alternative():
    matcher = ProtocolMatcher()
    result = matcher.find_alternative("bovine corneal opacity permeability severe eye damage Draize replacement")

    assert result.matched is True
    assert result.protocol is not None
    assert result.protocol.protocol_id == "oecd-tg-437-bcop"
    assert result.protocol.technology_category == "ex_vivo"
    assert "OECD TG 405" in result.recommendation