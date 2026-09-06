import json
import re
from pathlib import Path
from typing import List, Dict, Any
from pypdf import PdfReader


class RegulatoryDocParser:
    """
    Layout-aware parser for regulatory guidelines (OECD, FDA, EPA).
    Filters headers/footers and groups text along coherent regulatory sections.
    """

    IGNORE_PATTERNS = [
        re.compile(r"^OECD/OCDE\s+\d+", re.IGNORECASE),
        re.compile(r"^©\s*OECD\s*\(\d{4}\)", re.IGNORECASE),
        re.compile(r"^Test Guideline No\.\s*\d+", re.IGNORECASE),
        re.compile(r"^Guideline No\.\s*\d+", re.IGNORECASE),
        re.compile(r"^\d+\s*$", re.IGNORECASE),
    ]

    # Flexible regex patterns matching TG 492 and TG 497 major sections
    HEADING_PATTERNS = [
        # Common OECD Headings (TG 492 & 497)
        re.compile(r"^(?:1\s+)?Section 1[-–\s]*Introduction", re.IGNORECASE),
        re.compile(r"^INTRODUCTION\b", re.IGNORECASE),
        re.compile(r"^INITIAL CONSIDERATIONS AND LIMITATIONS\b", re.IGNORECASE),
        re.compile(r"^1\.2\s+DAs included in the Guideline", re.IGNORECASE),
        re.compile(r"^1\.3\s+Limitations\b", re.IGNORECASE),
        re.compile(r"^PRINCIPLE OF THE TEST\b", re.IGNORECASE),
        re.compile(r"^DEMONSTRATION OF PROFICIENCY\b", re.IGNORECASE),
        re.compile(r"^PROCEDURE\b", re.IGNORECASE),
        re.compile(r"^RhCE TEST METHOD COMPONENTS\b", re.IGNORECASE),
        re.compile(r"^GENERAL CONDITIONS\b", re.IGNORECASE),
        re.compile(r"^FUNCTIONAL CONDITIONS\b", re.IGNORECASE),
        re.compile(r"^ACCEPTANCE CRITERIA\b", re.IGNORECASE),
        re.compile(r"^INTERPRETATION OF RESULTS AND PREDICTION MODEL\b", re.IGNORECASE),
        re.compile(r"^DATA AND REPORTING\b", re.IGNORECASE),

        # TG 497 Defined Approaches Specific Sections
        re.compile(r"^Part I\s+Section 2\s*[-–]\s*Defined Approaches", re.IGNORECASE),
        re.compile(r"^2\.1\s+[\"']?2 out of 3[\"']?\s+Defined Approach", re.IGNORECASE),
        re.compile(r"^Part II\s+SECTION 3\s*[-–]\s*Defined Approaches", re.IGNORECASE),
        re.compile(r"^3\.1\s+[\"']?Integrated Testing Strategy\s*\(ITS\)[\"']?", re.IGNORECASE),
        re.compile(r"^Part III\s+SECTION 4\s*[-–]\s*Defined Approaches", re.IGNORECASE),
        re.compile(r"^4\.1\s+[\"']?SARA-ICE[\"']?\s+Defined Approach", re.IGNORECASE),
        re.compile(r"^4\.2\s+[\"']?Regression-based[\"']?\s+Defined Approach", re.IGNORECASE),

        # Annexes and Appendices
        re.compile(r"^Annex \d+[\.:\s-].*", re.IGNORECASE),
        re.compile(r"^ANNEX [I|V|X]+[\.:\s-].*", re.IGNORECASE),
        re.compile(r"^Appendix [I|V|X]+[\.:\s-].*", re.IGNORECASE),
        re.compile(r"^LITERATURE\b", re.IGNORECASE),
        re.compile(r"^\bReferences\b", re.IGNORECASE),
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
        chunks = []
        current_chunk: List[str] = []
        current_section = "PREAMBLE"
        start_page = 1

        for page in pages:
            for line in page["lines"]:
                matched = any(pat.search(line) for pat in self.HEADING_PATTERNS)
                if matched:
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
    raw_dir = Path("data/raw")
    pdfs = list(raw_dir.glob("*.pdf"))

    if not pdfs:
        print(f"No PDFs found in {raw_dir}")
    else:
        for target_pdf in pdfs:
            parser = RegulatoryDocParser(target_pdf)
            pages = parser.extract_pages()
            chunks = parser.chunk_by_sections(pages)

            output_path = Path("data/processed") / f"{target_pdf.stem}_chunks.json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(chunks, f, indent=2)

            print(f"Parsed {target_pdf.name} -> {len(chunks)} sections saved to {output_path.name}")