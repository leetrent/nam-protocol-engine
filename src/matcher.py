import json
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field
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
        search_hits = self.index.search(query, top_k=2)

        if not search_hits:
            return MatchResult(
                query=query,
                matched=False,
                recommendation="No relevant regulatory testing guidelines found."
            )

        query_lower = query.lower()
        matched_protocol = None

        for proto in self.verified_protocols:
            # Check direct endpoint/test name matches
            if (
                proto.endpoint.name.lower() in query_lower or
                proto.endpoint.historical_animal_test.lower() in query_lower or
                proto.endpoint.target_tissue.lower() in query_lower
            ):
                matched_protocol = proto
                break

            # Keyword routing for Ocular/Draize
            if proto.protocol_id == "oecd-tg-492-rhce" and any(
                k in query_lower for k in ("eye", "draize", "ocular", "cornea")
            ):
                matched_protocol = proto
                break

            # Keyword routing for Dermal/Sensitisation
            if proto.protocol_id == "oecd-tg-497-da-sensitisation" and any(
                k in query_lower for k in ("skin", "sensitisation", "sensitization", "llna", "lymph node", "dermal")
            ):
                matched_protocol = proto
                break

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
        else:
            recommendation = "Relevant guideline sections located, but no verified full-replacement protocol is registered yet."

        return MatchResult(
            query=query,
            matched=matched_protocol is not None,
            protocol=matched_protocol,
            supporting_evidence=evidence,
            recommendation=recommendation
        )


if __name__ == "__main__":
    matcher = ProtocolMatcher()
    sample_query = "What is the validated in vitro replacement for the Draize rabbit eye test?"
    result = matcher.find_alternative(sample_query)

    print(f"Query: {result.query}\n")
    print(f"Matched: {result.matched}")
    print(f"Recommendation: {result.recommendation}\n")
    print("Supporting Regulatory Evidence:")
    for ev in result.supporting_evidence:
        print(f"  - {ev}")