import pytest
from src.search import GuidelineIndex


@pytest.fixture(scope="module")
def search_index():
    index = GuidelineIndex()
    assert len(index.documents) > 0, "Index must contain parsed guideline sections."
    return index


# =====================================================================
# OECD TG 492 (Ocular Toxicity / RhCE) Benchmarks
# =====================================================================

def test_eval_retrieval_viability_cutoff(search_index):
    """
    Benchmark 1: Queries targeting viability criteria must prioritize
    the FUNCTIONAL CONDITIONS section containing Table 4 cut-offs.
    """
    query = "tissue viability cutoff threshold for classification"
    results = search_index.search(query, top_k=3, source_filter="492")

    assert len(results) > 0, "Retrieval returned zero hits."
    top_hit = results[0]
    assert "FUNCTIONAL CONDITIONS" in top_hit["section_title"]
    assert top_hit["score"] > 20


def test_eval_retrieval_draize_replacement_context(search_index):
    """
    Benchmark 2: Queries regarding historical Draize animal replacement
    must surface the INTRODUCTION or PRINCIPLE sections in top 2 results.
    """
    query = "Draize rabbit eye test replacement in vitro"
    results = search_index.search(query, top_k=2, source_filter="492")

    assert len(results) > 0
    top_sections = [r["section_title"] for r in results]
    has_expected_context = any(
        sec in ("INTRODUCTION", "PRINCIPLE OF THE TEST", "FUNCTIONAL CONDITIONS")
        for sec in top_sections
    )
    assert has_expected_context, f"Unexpected sections retrieved: {top_sections}"


def test_eval_hit_attribution_has_pages(search_index):
    """
    Benchmark 3: Every retrieved hit must contain valid page range metadata
    to ensure regulatory auditability.
    """
    query = "negative and positive control substances"
    results = search_index.search(query, top_k=3, source_filter="492")

    for hit in results:
        assert "-" in hit["pages"], f"Malformed page range: {hit['pages']}"
        start_p, end_p = hit["pages"].split("-")
        assert int(start_p) > 0 and int(end_p) >= int(start_p)


def test_eval_tg492_proficiency_chemicals_lookup(search_index):
    """
    Benchmark 4: Queries regarding laboratory demonstration of proficiency
    must surface DEMONSTRATION OF PROFICIENCY containing Table 1.
    """
    query = "fifteen proficiency chemicals technical proficiency validation"
    results = search_index.search(query, top_k=2, source_filter="492")

    assert len(results) > 0
    top_hit = results[0]
    assert "DEMONSTRATION OF PROFICIENCY" in top_hit["section_title"]


def test_eval_tg492_applicability_domain_exclusions(search_index):
    """
    Benchmark 5: Queries about non-applicable substance formats (gases, aerosols)
    must rank INITIAL CONSIDERATIONS AND LIMITATIONS or INTRODUCTION at top.
    """
    query = "gases aerosols applicability domain limitations"
    results = search_index.search(query, top_k=2, source_filter="492")

    assert len(results) > 0
    top_sections = [r["section_title"] for r in results]
    assert any("LIMITATIONS" in s or "INTRODUCTION" in s for s in top_sections)


# =====================================================================
# OECD TG 497 (Skin Sensitisation Defined Approaches) Benchmarks
# =====================================================================

def test_eval_retrieval_skin_sensitisation_da(search_index):
    """
    Benchmark 6: Queries targeting Defined Approaches for skin sensitisation
    must surface Section 1, Part I (2o3 DA), or Part II (ITS DA).
    """
    query = "defined approaches 2 out of 3 integrated testing strategy"
    results = search_index.search(query, top_k=3, source_filter="497")

    assert len(results) > 0, "Retrieval returned zero hits for TG 497."
    top_sections = [r["section_title"] for r in results]

    has_expected = any(
        any(k in s for k in ("Section 1", "Section 2", "SECTION 3", "Defined Approaches", "2 out of 3", "ITS"))
        for s in top_sections
    )
    assert has_expected, f"Unexpected sections retrieved: {top_sections}"


def test_eval_tg497_its_battery_scoring(search_index):
    """
    Benchmark 7: Queries regarding the Integrated Testing Strategy total battery score
    and potency sub-categorisation (1A, 1B, NC) must retrieve Part II SECTION 3 or DAs summary.
    """
    query = "integrated testing strategy total battery score UN GHS category 1A 1B"
    results = search_index.search(query, top_k=3, source_filter="497")

    assert len(results) > 0
    top_sections = [r["section_title"] for r in results]
    assert any(
        any(k in s for k in ("SECTION 3", "ITS", "Section 1", "DAs included"))
        for s in top_sections
    ), f"Failed to retrieve ITS section: {top_sections}"


def test_eval_tg497_aop_key_events(search_index):
    """
    Benchmark 8: Queries addressing Adverse Outcome Pathway key events
    (KE1 protein binding, KE2 keratinocyte, KE3 dendritic cell) must locate 
    AOP introductory or DA test-battery sections (Sections 1-4).
    """
    query = "adverse outcome pathway protein binding keratinocytes dendritic cells KE1 KE2 KE3"
    results = search_index.search(query, top_k=2, source_filter="497")

    assert len(results) > 0
    top_sections = [r["section_title"] for r in results]
    assert any(
        any(k in s for k in ("Section 1", "Section 2", "SECTION 3", "SECTION 4", "Introduction"))
        for s in top_sections
    ), f"Failed to retrieve AOP section: {top_sections}"
    
# =====================================================================
# OECD TG 439 (Skin Irritation / RhE) Benchmarks
# =====================================================================

def test_eval_retrieval_tg439_viability_cutoff(search_index):
    """
    Benchmark 9: Queries targeting skin irritation classification cut-offs (50% viability)
    must surface Functional conditions or Interpretation of Results in TG 439.
    """
    query = "percent cell viability threshold 50% UN GHS Category 2"
    results = search_index.search(query, top_k=2, source_filter="439")

    assert len(results) > 0, "Retrieval returned zero hits for TG 439."
    top_sections = [r["section_title"] for r in results]
    assert any(
        any(k in s for k in ("Functional conditions", "Interpretation of Results", "PRINCIPLE"))
        for s in top_sections
    ), f"Unexpected sections retrieved: {top_sections}"


def test_eval_retrieval_tg439_proficiency_substances(search_index):
    """
    Benchmark 10: Queries targeting demonstration of proficiency in TG 439
    must prioritize DEMONSTRATION OF PROFICIENCY containing Table 1.
    """
    query = "ten proficiency substances demonstration of technical proficiency"
    results = search_index.search(query, top_k=2, source_filter="439")

    assert len(results) > 0
    top_hit = results[0]
    assert "DEMONSTRATION OF PROFICIENCY" in top_hit["section_title"]
    
# =====================================================================
# OECD TG 437 (BCOP / Severe Eye Damage) Benchmarks
# =====================================================================
   
def test_eval_retrieval_tg437_ivis_cutoff(search_index):
    """
    Benchmark 11: Queries targeting IVIS decision thresholds in TG 437
    must surface Decision Criteria, DATA AND REPORTING, or ANNEX 1 definitions.
    """
    query = "IVIS cut-off threshold 55 UN GHS Category 1 Decision Criteria"
    results = search_index.search(query, top_k=2, source_filter="437")

    assert len(results) > 0, "Retrieval returned zero hits for TG 437."
    top_sections = [r["section_title"] for r in results]
    assert any(
        any(k in s for k in ("Decision Criteria", "DATA AND REPORTING", "ANNEX 1", "PRINCIPLE"))
        for s in top_sections
    ), f"Unexpected sections retrieved: {top_sections}"   


def test_eval_retrieval_tg437_proficiency_substances(search_index):
    """
    Benchmark 12: Queries targeting BCOP proficiency substances
    must prioritize ANNEX 3 or DEMONSTRATION OF PROFICIENCY.
    """
    query = "thirteen proficiency substances demonstration of technical proficiency"
    results = search_index.search(query, top_k=2, source_filter="437")

    assert len(results) > 0
    top_sections = [r["section_title"] for r in results]
    assert any(
        any(k in s for k in ("ANNEX 3", "DEMONSTRATION OF PROFICIENCY", "Table 1"))
        for s in top_sections
    ), f"Unexpected sections retrieved: {top_sections}"
    
    
# =====================================================================
# OECD TG 431 (RhE Skin Corrosion) Benchmarks
# =====================================================================

def test_eval_retrieval_tg431_prediction_model(search_index):
    """
    Benchmark 13: Queries targeting TG 431 two-step prediction model thresholds
    must surface Interpretation of Results or Acceptance Criteria.
    """
    query = "viability 50% 3 min 15% 60 min Sub-category 1A prediction model"
    results = search_index.search(query, top_k=2, source_filter="431")

    assert len(results) > 0, "Retrieval returned zero hits for TG 431."
    top_sections = [r["section_title"] for r in results]
    assert any(
        any(k in s for k in ("Interpretation of Results", "Acceptance Criteria", "FUNCTIONAL CONDITIONS"))
        for s in top_sections
    ), f"Unexpected sections retrieved: {top_sections}"


def test_eval_retrieval_tg431_proficiency_chemicals(search_index):
    """
    Benchmark 14: Queries targeting TG 431 proficiency substances
    must prioritize DEMONSTRATION OF PROFICIENCY.
    """
    query = "twelve proficiency substances bromoacetic acid boron trifluoride dihydrate"
    results = search_index.search(query, top_k=2, source_filter="431")

    assert len(results) > 0, "Retrieval returned zero hits for TG 431."
    top_sections = [r["section_title"] for r in results]
    assert any(
        "DEMONSTRATION OF PROFICIENCY" in s for s in top_sections
    ), f"Unexpected sections retrieved: {top_sections}"
    
    
# =====================================================================
# OECD TG 432 (In Vitro 3T3 NRU Phototoxicity) Benchmarks
# =====================================================================

def test_eval_retrieval_tg432_pif_mpe_cutoffs(search_index):
    """
    Benchmark 15: Queries targeting PIF and MPE prediction thresholds
    must surface Interpretation of Results or DATA AND REPORTING in TG 432.
    """
    query = "PIF 2 5 MPE 0.1 0.15 prediction phototoxicity equivocal"
    results = search_index.search(query, top_k=2, source_filter="432")

    assert len(results) > 0, "Retrieval returned zero hits for TG 432."
    top_sections = [r["section_title"] for r in results]
    assert any(
        any(k in s for k in ("Interpretation of Results", "DATA AND REPORTING"))
        for s in top_sections
    ), f"Unexpected sections retrieved: {top_sections}"


def test_eval_retrieval_tg432_mec_screening(search_index):
    """
    Benchmark 16: Queries targeting the molar extinction coefficient (MEC) screening
    must prioritize INITIAL CONSIDERATION or Annex B in TG 432.
    """
    query = "molar extinction coefficient MEC 1000 photoreactive absorption spectrum"
    results = search_index.search(query, top_k=2, source_filter="432")

    assert len(results) > 0, "Retrieval returned zero hits for TG 432."
    top_sections = [r["section_title"] for r in results]
    assert any(
        any(k in s for k in ("INITIAL CONSIDERATION", "Annex B", "Annex A"))
        for s in top_sections
    ), f"Unexpected sections retrieved: {top_sections}"


def test_eval_retrieval_tg432_irradiation_conditions(search_index):
    """
    Benchmark 17: Queries targeting UVA irradiation dose (5 J/cm2) and positive controls
    must locate DESCRIPTION OF THE TEST METHOD in TG 432.
    """
    query = "dose 5 J/cm2 UVA irradiance chlorpromazine positive control"
    results = search_index.search(query, top_k=2, source_filter="432")

    assert len(results) > 0, "Retrieval returned zero hits for TG 432."
    top_sections = [r["section_title"] for r in results]
    assert any(
        "DESCRIPTION OF THE TEST METHOD" in s for s in top_sections
    ), f"Unexpected sections retrieved: {top_sections}"