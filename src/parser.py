import re
from pathlib import Path
from typing import List, Dict, Any
from pypdf import PdfReader


class RegulatoryDocParser:
    """
    Layout-aware parser for regulatory guidelines (OECD, FDA, EPA).
    Filters headers/footers and groups text along coherent regulatory sections.
    """

    # Common running headers/footers to discard
    IGNORE_PATTERNS = [
        re.compile(r"^OECD/OCDE\s+\d+", re.IGNORECASE),
        re.compile(r"^©\s*OECD\s*\(\d{4}\)", re.IGNORECASE),
        re.compile(r"^Test Guideline No\.\s*\d+", re.IGNORECASE),
        re.compile(r"^\d+\s*$", re.IGNORECASE),  # Standalone page numbers
    ]

    # Major section titles used in OECD guidelines
    KNOWN_SECTIONS = [
        "INTRODUCTION",
        "INITIAL CONSIDERATIONS AND LIMITATIONS",
        "PRINCIPLE OF THE TEST",
        "DEMONSTRATION OF PROFICIENCY",
        "PROCEDURE",
        "RhCE TEST METHOD COMPONENTS",
        "GENERAL CONDITIONS",
        "FUNCTIONAL CONDITIONS",
        "ACCEPTANCE CRITERIA",
        "INTERPRETATION OF RESULTS AND PREDICTION MODEL",
        "DATA AND REPORTING",
        "LITERATURE",
        "ANNEX I",
        "ANNEX II",
        "ANNEX III",
        "ANNEX IV",
        "ANNEX V",
        "ANNEX VI",
        "ANNEX VII",
    ]

    def __init__(self, pdf_path: str | Path):
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF not found at {self.pdf_path}")
        self.reader = PdfReader(str(self.pdf_path))

    def _is_boilerplate(self, line: str) -> bool:
        line = line.strip()
        return any(pattern.search(line) for pattern in self.IGNORE_PATTERNS)

    def extract_pages(self) -> List[Dict[str, Any]]:
        """Extracts text page by page with boilerplate filtering."""
        pages = []
        for idx, page in enumerate(self.reader.pages):
            raw_text = page.extract_text() or ""
            cleaned_lines = []
            for line in raw_text.splitlines():
                line_str = re.sub(r"[ \t]+", " ", line).strip()
                if line_str and not self._is_boilerplate(line_str):
                    cleaned_lines.append(line_str)

            pages.append({
                "page_number": idx + 1,
                "lines": cleaned_lines
            })
        return pages

    def chunk_by_sections(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Groups lines into structured blocks according to recognized regulatory headings."""
        chunks = []
        current_chunk: List[str] = []
        current_section = "PREAMBLE"
        start_page = 1

        for page in pages:
            for line in page["lines"]:
                # Check if this line signals a new major section
                matched_section = None
                for sec in self.KNOWN_SECTIONS:
                    if line.startswith(sec) or line == sec:
                        matched_section = sec
                        break

                if matched_section:
                    if current_chunk:
                        chunks.append({
                            "section_title": current_section,
                            "content": "\n".join(current_chunk),
                            "start_page": start_page,
                            "end_page": page["page_number"],
                            "source_file": self.pdf_path.name
                        })
                        current_chunk = []
                    current_section = line
                    start_page = page["page_number"]
                else:
                    current_chunk.append(line)

        if current_chunk:
            chunks.append({
                "section_title": current_section,
                "content": "\n".join(current_chunk),
                "start_page": start_page,
                "end_page": pages[-1]["page_number"] if pages else 1,
                "source_file": self.pdf_path.name
            })

        return chunks


if __name__ == "__main__":
    import json

    raw_dir = Path("data/raw")
    sample_pdfs = list(raw_dir.glob("*.pdf"))

    if not sample_pdfs:
        print(f"No PDF found in {raw_dir}.")
    else:
        target_pdf = sample_pdfs[0]
        parser = RegulatoryDocParser(target_pdf)
        pages = parser.extract_pages()
        chunks = parser.chunk_by_sections(pages)

        output_path = Path("data/processed") / f"{target_pdf.stem}_chunks.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2)

        print(f"Re-processed {target_pdf.name}: {len(chunks)} clean semantic sections saved.")