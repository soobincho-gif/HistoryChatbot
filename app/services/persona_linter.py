from __future__ import annotations
from typing import List
from pydantic import BaseModel
from app.models.schemas import PersonaDossier

class LinterWarning(BaseModel):
    category: str
    message: str

class PersonaLinter:
    """
    Evaluates generated or edited PersonaDossiers for historical
    grounding, depth, and constraint adherence.
    """

    def lint(self, dossier: PersonaDossier) -> List[LinterWarning]:
        warnings: List[LinterWarning] = []

        # 1. Historical Grounding (Evidence Snippets)
        if not dossier.evidence_snippets:
            warnings.append(LinterWarning(
                category="Grounding",
                message="No `evidence_snippets` provided. The persona risks generating heavily hallucinated traits."
            ))
        elif len(dossier.evidence_snippets) < 2:
            warnings.append(LinterWarning(
                category="Grounding",
                message="Sparse `evidence_snippets`. Aim for at least 2 or 3 hints/sources to ground behavior."
            ))

        # 2. Chronology (Dates)
        if dossier.birth_year is None and dossier.death_year is None:
            warnings.append(LinterWarning(
                category="Chronology",
                message="Birth and death years are missing. The sequence might struggle with timeline anchoring."
            ))

        # 3. Policy Constraints
        posthumous = dossier.posthumous_policy or ""
        if len(posthumous.split()) < 4 or posthumous.upper() in ["N/A", "NONE", "UNKNOWN"]:
            warnings.append(LinterWarning(
                category="Policy",
                message="`posthumous_policy` is weak or missing. The figure may leak modern knowledge or break character."
            ))

        # 4. Narrative Depth
        if not dossier.core_topics or len(dossier.core_topics) < 3:
            warnings.append(LinterWarning(
                category="Depth",
                message="Fewer than 3 `core_topics`. The figure may not steer conversations effectively."
            ))
        
        if not dossier.worldview or len(dossier.worldview) < 2:
            warnings.append(LinterWarning(
                category="Depth",
                message="`worldview` is spare. Responses might default to 'generic assistant' rather than distinct perspectives."
            ))

        return warnings
