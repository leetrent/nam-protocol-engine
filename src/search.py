import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Any


class GuidelineIndex:
    """In-memory deterministic search index over chunked regulatory guidelines."""

    def __init__(self, processed_dir: str | Path | None = None):
        if processed_dir is None:
            # Anchor path to project root (parent of src/)
            self.processed_dir = Path(__file__).resolve().parent.parent / "data" / "processed"
        else:
            self.processed_dir = Path(processed_dir)

        self.documents: List[Dict[str, Any]] = []
        self._load_corpus()

    def _load_corpus(self):
        """Loads all chunk JSON files into memory."""
        if not self.processed_dir.exists():
            print(f"[ERROR] Processed directory not found: {self.processed_dir}", file=sys.stderr)
            return

        chunk_files = list(self.processed_dir.glob("*_chunks*.json"))
        print(f"[INFO] Found {len(chunk_files)} chunk file(s) in {self.processed_dir}")

        for file_path in chunk_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.documents.extend(data)
                        print(f"       Loaded {len(data)} sections from {file_path.name}")
            except Exception as e:
                print(f"[ERROR] Failed to read {file_path}: {e}", file=sys.stderr)

        print(f"[INFO] Total searchable sections indexed: {len(self.documents)}\n")

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Ranks chunks using token term frequencies."""
        # Normalize punctuation out of words so words like 'cut-off' match 'cutoff' or 'cut' and 'off'
        query_terms = set(re.findall(r"\w+", query.lower()))
        if not query_terms or not self.documents:
            return []

        scored_docs = []
        for doc in self.documents:
            content_lower = doc.get("content", "").lower()
            section_lower = doc.get("section_title", "").lower()

            score = 0
            for term in query_terms:
                score += content_lower.count(term)
                if term in section_lower:
                    score += 10

            if score > 0:
                scored_docs.append({
                    "score": score,
                    "section_title": doc.get("section_title", "UNKNOWN"),
                    "pages": f"{doc.get('start_page', '?')}-{doc.get('end_page', '?')}",
                    "source_file": doc.get("source_file", "UNKNOWN"),
                    "excerpt": doc.get("content", "")[:280].replace("\n", " ") + "..."
                })

        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        return scored_docs[:top_k]


if __name__ == "__main__":
    index = GuidelineIndex()
    test_query = "Draize eye test replacement viability cutoff"
    print(f"Executing query: '{test_query}'")
    results = index.search(test_query, top_k=3)

    if not results:
        print("[WARNING] No matching sections found.")
    else:
        for i, res in enumerate(results, 1):
            print(f"\n[{i}] Section: {res['section_title']} (Pages: {res['pages']}) | Score: {res['score']}")
            print(f"    {res['excerpt']}")