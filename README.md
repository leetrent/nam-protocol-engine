# NAM Protocol Engine

A deterministic regulatory decision and guidance engine for toxicological **New Approach Methodologies (NAMs)** supporting the 3Rs (Replacement, Reduction, Refinement) of animal testing under UN GHS and EU REACH frameworks.

The engine provides standardized non-animal alternative pathways, tiered testing strategies, and automated regulatory dossiers across five core OECD Test Guidelines.

---

## Supported Regulatory Frameworks & Guidelines

| Guideline | Method Name | Technology Type | Replaces Animal Assay | Primary Decision Scope |
| :--- | :--- | :--- | :--- | :--- |
| **OECD TG 431** | In Vitro Skin Corrosion (RhE) | In vitro 3D tissue | Acute Dermal (OECD 404) | Sub-categorisation (1A vs 1B/1C) vs Non-corrosive |
| **OECD TG 439** | In Vitro Skin Irritation (RhE) | In vitro 3D tissue | Acute Dermal (OECD 404) | UN GHS Category 2 vs No Category (>50% viability) |
| **OECD TG 437** | Bovine Corneal Opacity & Permeability (BCOP) | Ex vivo tissue | Draize Eye Test (OECD 405) | UN GHS Category 1 (IVIS >= 55.1) or No Category (<= 3) |
| **OECD TG 492** | Reconstructed Human Cornea-like Epithelium (RhCE) | In vitro 3D tissue | Draize Eye Test (OECD 405) | UN GHS No Category identification (>60% viability) |
| **OECD TG 497** | Defined Approaches for Skin Sensitisation | In silico / Battery | LLNA (OECD 429) / GPMT | 2o3 Decision Rule & Integrated Testing Strategies (ITSv1/v2) |

---

## Architecture

* **Runtime & Package Management:** Python 3.12 managed via `uv` for reproducible, deterministic builds.
* **Search & Retrieval:** In-memory deterministic ranking (`GuidelineIndex`) evaluating chunked regulatory guidelines with relevance thresholds and section-header boosts.
* **Data Schemas:** Pydantic v2 schemas enforcing strict typing for protocols, endpoints, regulatory citations, and tiered strategies.
* **UI Interface:** Gradio-based dual-tab application featuring an interactive natural-language guideline search and a guided dossier strategy builder.

---

## Quickstart (Local Development)

### 1. Prerequisites
Install `uv` (Astral Python package manager):
* **macOS/Linux:** curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh
* **Windows (PowerShell):** powershell -ExecutionPolicy ByPass -c "irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex"

### 2. Environment Setup & Dependency Sync
Clone the repository and install dependencies:
```bash
git clone https://github.com/your-org/nam-protocol-engine.git
cd nam-protocol-engine
uv sync
```

### 3. Run Test Suite
The test suite validates schema integrity, extraction logic, endpoint matching, and tiered evaluation paths (28 tests total):
```bash
uv run pytest -v
```

### 4. Launch Local Web Dashboard
```bash
uv run python src/app.py
```
Access the application at http://localhost:7860.

---

## Containerized Deployment (Docker)

The project includes a hardened multi-stage Dockerfile (Debian Bookworm base with OS security patching and non-root execution):

### Run via Docker Compose
Build and run in detached mode:
```bash
docker compose up --build -d
```

Check startup logs:
```bash
docker compose logs -f
```

Shut down container:
```bash
docker compose down
```

The container exposes port 7860 mapped directly to http://localhost:7860.

---

## Directory Structure

```text
nam-protocol-engine/
├── data/
│   └── processed/          # Pre-chunked JSON regulatory guidelines
├── src/
│   ├── app.py              # Gradio web interface & tab layouts
│   ├── extractor.py        # Protocol parsing & schema mapping
│   ├── matcher.py          # Regulatory endpoint & assay matcher
│   ├── models.py           # Pydantic data schemas
│   ├── search.py           # Deterministic GuidelineIndex engine
│   └── strategy.py         # Tiered testing strategy generator
├── tests/
│   ├── test_evals.py       # Guideline retrieval & citation evals
│   ├── test_extractor.py   # Schema extraction tests
│   ├── test_matcher.py     # Endpoint matching & fallback tests
│   └── test_strategy.py    # Tiered strategy compilation tests
├── Dockerfile              # Hardened multi-stage build definition
├── docker-compose.yml      # Container orchestration
├── pyproject.toml          # Project configuration & dependencies
└── uv.lock                 # Pinned lockfile
```