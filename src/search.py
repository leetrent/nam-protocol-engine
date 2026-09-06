import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "has", "in", "is", "it", "its", "of", "on", "or", "that", "the",
    "to", "was", "were", "with"
}


class GuidelineIndex:
    """In-memory deterministic search index over chunked regulatory guidelines."""

    def __init__(self, processed_dir: str | Path | None = None):
        if processed_dir is None:
            self.processed_dir = Path(__file__).resolve().parent.parent / "data" / "processed"
        else:
            self.processed_dir = Path(processed_dir)

        self.documents: List[Dict[str, Any]] = []
        self._load_corpus()

    def _load_corpus(self):
        """Loads all chunk JSON files into memory."""
        if not self.processed_dir.exists():
            return

        chunk_files = list(self.processed_dir.glob("*_chunks*.json"))
        for file_path in chunk_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.documents.extend(data)
            except Exception as e:
                print(f"[ERROR] Failed to read {file_path}: {e}", file=sys.stderr)

    def search(
        self,
        query: str,
        top_k: int = 3,
        source_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Ranks chunks using tokenized word frequencies with section header boosts.
        Supports optional filtering by source filename or guideline prefix.
        """
        raw_tokens = re.findall(r"\b[a-z0-9_]{2,}\b", query.lower())
        query_terms = [t for t in raw_tokens if t not in STOP_WORDS]

        if not query_terms or not self.documents:
            return []

        scored_docs = []
        for doc in self.documents:
            # Filter by document source if requested
            source_file = doc.get("source_file", "")
            if source_filter and source_filter.lower() not in source_file.lower():
                continue

            content = doc.get("content", "")
            section_title = doc.get("section_title", "")
            content_lower = content.lower()
            section_lower = section_title.lower()

            # Ignore stub flowchart captions that lack substantive paragraphs
            if len(content.strip().split()) < 30 and "ANNEX" in section_title:
                continue

            score = 0
            for term in query_terms:
                term_count = len(re.findall(rf"\b{re.escape(term)}\b", content_lower))
                score += term_count

                if re.search(rf"\b{re.escape(term)}\b", section_lower):
                    score += 25

            if score > 0:
                scored_docs.append({
                    "score": score,
                    "section_title": section_title,
                    "pages": f"{doc.get('start_page', '?')}-{doc.get('end_page', '?')}",
                    "source_file": source_file,
                    "excerpt": content[:280].replace("\n", " ") + "..."
                })

        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        return scored_docs[:top_k]


if __name__ == "__main__":
    index = GuidelineIndex()
    test_query = "Draize rabbit eye test replacement in vitro"
    results = index.search(test_query, top_k=3)
    for i, res in enumerate(results, 1):
        print(f"[{i}] {res['section_title']} (Score: {res['score']})")