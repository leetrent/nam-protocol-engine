import pytest
from src.search import GuidelineIndex


@pytest.fixture(scope="module")
def search_index():
    index = GuidelineIndex()
    assert len(index.documents) > 0, "Index must contain parsed guideline sections."
    return index


def test_eval_retrieval_viability_cutoff(search_index):
    """
    Benchmark: Queries targeting viability criteria must prioritize
    the FUNCTIONAL CONDITIONS section containing Table 4 cut-offs.
    """
    query = "tissue viability cutoff threshold for classification"
    results = search_index.search(query, top_k=3)

    assert len(results) > 0, "Retrieval returned zero hits."

    top_hit = results[0]
    assert "FUNCTIONAL CONDITIONS" in top_hit["section_title"]
    assert top_hit["score"] > 50


def test_eval_retrieval_draize_replacement_context(search_index):
    """
    Benchmark: Queries regarding the historical Draize animal replacement
    must surface the INTRODUCTION or PRINCIPLE sections in top 2 results.
    """
    query = "Draize rabbit eye test replacement in vitro"
    results = search_index.search(query, top_k=2)

    assert len(results) > 0
    top_sections = [r["section_title"] for r in results]
    
    # Must retrieve background/principle context
    has_expected_context = any(
        sec in ("INTRODUCTION", "PRINCIPLE OF THE TEST", "FUNCTIONAL CONDITIONS")
        for sec in top_sections
    )
    assert has_expected_context, f"Unexpected sections retrieved: {top_sections}"


def test_eval_hit_attribution_has_pages(search_index):
    """
    Benchmark: Every retrieved hit must contain valid page range metadata
    to ensure full auditability.
    """
    query = "negative and positive control substances"
    results = search_index.search(query, top_k=3)

    for hit in results:
        assert "-" in hit["pages"], f"Malformed page range: {hit['pages']}"
        start_p, end_p = hit["pages"].split("-")
        assert int(start_p) > 0 and int(end_p) >= int(start_p)