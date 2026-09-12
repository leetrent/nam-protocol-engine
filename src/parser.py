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
    
    HEADING_PATTERNS = [
            # Common OECD Guideline Sections (TG 431, TG 432, TG 437, TG 439, TG 492, TG 497)
            re.compile(r"^(?:1\s+)?Section 1[-–\s]*Introduction\b", re.IGNORECASE),
            re.compile(r"^1\.1\.\s+General Introduction\b", re.IGNORECASE),
            re.compile(r"^1\.2\s+DAs included in the Guideline\b", re.IGNORECASE),
            re.compile(r"^1\.3\s+Limitations\b", re.IGNORECASE),
            re.compile(r"^INTRODUCTION\s*$", re.IGNORECASE),
            re.compile(r"^INITIAL CONSIDERATIONS?(?:\s+AND\s+LIMITATIONS)?\s*$", re.IGNORECASE),
            re.compile(r"^DEFINITIONS\s*$", re.IGNORECASE),
            re.compile(r"^PRINCIPLE OF THE TEST(?:\s+METHOD)?\s*$", re.IGNORECASE),
            re.compile(r"^DESCRIPTION OF THE TEST METHOD\s*$", re.IGNORECASE),
            re.compile(r"^DEMONSTRATION OF PROFICIENCY\s*$", re.IGNORECASE),
            re.compile(r"^PROCEDURE\s*$", re.IGNORECASE),
            re.compile(r"^(?:RhCE|RHE)\s+TEST METHOD COMPONENTS\s*$", re.IGNORECASE),
            re.compile(r"^GENERAL CONDITIONS\s*$", re.IGNORECASE),
            re.compile(r"^FUNCTIONAL CONDITIONS\s*$", re.IGNORECASE),
            re.compile(r"^ACCEPTANCE CRITERIA\s*$", re.IGNORECASE),
            re.compile(r"^INTERPRETATION OF RESULTS", re.IGNORECASE),
            re.compile(r"^Decision Criteria\s*$", re.IGNORECASE),
            re.compile(r"^Study Acceptance Criteria\s*$", re.IGNORECASE),
            re.compile(r"^DATA AND REPORTING\s*$", re.IGNORECASE),
            re.compile(r"^Test Report\s*$", re.IGNORECASE),

            # TG 497 Structural Sections
            re.compile(r"^Part I\s+SECTION 2\b", re.IGNORECASE),
            re.compile(r"^2\.1\s+[\"']?2 out of 3[\"']?\s+Defined Approach\b", re.IGNORECASE),
            re.compile(r"^Part II\s+SECTION 3\b", re.IGNORECASE),
            re.compile(r"^3\.1\s+[\"']?Integrated Testing Strategy\s*\(ITS\)[\"']?\s+Defined Approach\b", re.IGNORECASE),
            re.compile(r"^Part III\s+SECTION 4\b", re.IGNORECASE),
            re.compile(r"^4\.1\s+[\"']?SARA-ICE[\"']?\s+Defined Approach\b", re.IGNORECASE),
            re.compile(r"^4\.2\s+[\"']?Regression-based[\"']?\s+Defined Approach\b", re.IGNORECASE),

            # Annexes & Appendices (supports numbers, roman numerals, or letters like Annex A, Annex B)
            re.compile(r"^(?:ANNEX|Annex)\s+(?:\d+|[IVX]+|[A-Z])\s*[-–\.:]\s*[A-Za-z]", re.IGNORECASE),
            re.compile(r"^(?:APPENDIX|Appendix)\s+(?:\d+|[IVX]+|[A-Z])\s*[-–\.:]\s*[A-Za-z]", re.IGNORECASE),
            re.compile(r"^LITERATURE\s*$", re.IGNORECASE),
            re.compile(r"^References\s*$", re.IGNORECASE),
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
        in_toc = False

        for page in pages:
            first_lines = " ".join(page["lines"][:3]).lower()
            if "table of contents" in first_lines:
                in_toc = True
            if in_toc:
                if any(re.match(r"^(?:1\s+)?Section 1[-–\s]*Introduction", l, re.IGNORECASE) for l in page["lines"]):
                    in_toc = False
                elif any(re.match(r"^INTRODUCTION\s*$", l, re.IGNORECASE) for l in page["lines"]):
                    in_toc = False
                else:
                    continue

            for line in page["lines"]:
                # Ignore lines that are citations or narrative references
                if re.match(r"^(?:Annex|Appendix)\s+\w+\s+(?:of\s+the|for\b)\b", line, re.IGNORECASE):
                    current_chunk.append(line)
                    continue

                matched = any(pat.match(line) for pat in self.HEADING_PATTERNS)
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