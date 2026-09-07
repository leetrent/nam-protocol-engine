from typing import List, Optional, Literal
from pydantic import BaseModel, Field

TechnologyCategory = Literal[
    "in_vitro",
    "in_chemico",
    "in_silico",
    "organ_on_a_chip",
    "defined_approach",
    "ex_vivo",
]

class RegulatoryCitation(BaseModel):
    standard_body: Literal["OECD", "FDA", "EPA", "EMA", "ICH"] = Field(
        ..., description="Standard regulatory or governing agency"
    )
    guideline_id: str = Field(..., description="Official designation, e.g. 'OECD TG 497'")
    document_title: str
    section_reference: str = Field(..., description="Specific clause, table, or paragraph")
    official_url: Optional[str] = None

class BiologicalEndpoint(BaseModel):
    name: str = Field(..., description="e.g. Skin Sensitization, Eye Irritation, Hepatotoxicity")
    target_tissue: str = Field(..., description="e.g. Dermal, Ocular, Cardiac")
    historical_animal_test: str = Field(..., description="e.g. Draize Rabbit Test, Mouse LLNA")

class NAMProtocol(BaseModel):
    protocol_id: str = Field(..., description="Unique slug or identifier")
    protocol_name: str = Field(..., description="e.g. EpiOcular Eye Irritation Test (EIT)")
    technology_category: TechnologyCategory
    endpoint: BiologicalEndpoint
    regulatory_status: Literal["Full Regulatory Acceptance", "Weight of Evidence", "Exploratory"]
    context_of_use: str = Field(..., description="Clear conditions and bounds under which assay is accepted")
    citations: List[RegulatoryCitation]