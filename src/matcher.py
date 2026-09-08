import json
import sys
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.schemas import NAMProtocol
from src.search import GuidelineIndex


class MatchResult(BaseModel):
    query: str
    matched: bool
    protocol: Optional[NAMProtocol] = None
    supporting_evidence: List[str] = Field(default_factory=list)
    recommendation: str


class ProtocolMatcher:
    """Matches testing intent against validated NAM protocols and regulatory guidelines."""

    def __init__(self, processed_dir: Optional[Path] = None):
        self.processed_dir = processed_dir or Path(__file__).resolve().parent.parent / "data" / "processed"
        self.index = GuidelineIndex(self.processed_dir)
        self.verified_protocols: List[NAMProtocol] = []
        self._load_verified_protocols()

    def _load_verified_protocols(self):
        """Loads all verified ground-truth protocol JSON files."""
        for file_path in self.processed_dir.glob("*_verified.json"):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.verified_protocols.append(NAMProtocol(**data))

    def find_alternative(self, query: str) -> MatchResult:
        query_lower = query.lower()

        matched_protocol = None
        for proto in self.verified_protocols:
            # Match 1: Ocular Severe Damage / BCOP replacement (TG 437)
            # Evaluated first so explicit severe/bovine ocular queries route to BCOP
            if "437" in proto.protocol_id and any(
                k in query_lower for k in ("bcop", "bovine corneal", "severe eye damage", "corrosive to eyes", "cat 1 ocular")
            ):
                matched_protocol = proto
                break

            # Match 2: Ocular Irritation / RhCE replacement (TG 492)
            if "rhce" in proto.protocol_id and any(
                k in query_lower for k in ("eye", "draize", "ocular", "cornea", "405")
            ):
                matched_protocol = proto
                break

            # Match 3: Dermal Sensitisation replacement (TG 497)
            if "sensitisation" in proto.protocol_id and any(
                k in query_lower for k in ("sensitisation", "sensitization", "llna", "lymph node", "429")
            ):
                matched_protocol = proto
                break

            # Match 4: Dermal Irritation replacement (TG 439)
            if "439" in proto.protocol_id and any(
                k in query_lower for k in ("skin irritation", "dermal irritation", "rhe", "404", "rabbit skin")
            ):
                matched_protocol = proto
                break

        # Derive source filter from matched guideline ID (e.g. "437", "439", "492", "497")
        source_filter = None
        if matched_protocol and matched_protocol.citations:
            guideline_id = matched_protocol.citations[0].guideline_id
            digits = "".join(filter(str.isdigit, guideline_id))
            if digits:
                source_filter = digits

        search_hits = self.index.search(query, top_k=2, source_filter=source_filter)

        evidence = [
            f"[{hit['section_title']} (pp. {hit['pages']})]: {hit['excerpt'][:160]}"
            for hit in search_hits
        ]

        if matched_protocol:
            recommendation = (
                f"Replace '{matched_protocol.endpoint.historical_animal_test}' with "
                f"'{matched_protocol.protocol_name}' ({matched_protocol.technology_category}). "
                f"Regulatory Status: {matched_protocol.regulatory_status}."
            )
        elif search_hits:
            recommendation = "Relevant guideline sections located, but no verified full-replacement protocol is registered yet."
        else:
            recommendation = "No relevant regulatory testing guidelines found."

        return MatchResult(
            query=query,
            matched=matched_protocol is not None,
            protocol=matched_protocol,
            supporting_evidence=evidence,
            recommendation=recommendation
        )