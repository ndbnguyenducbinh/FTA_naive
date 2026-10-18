import time
from typing import List, Dict, Any, Optional
from core.interfaces import ICaseMemoryRepository, CaseRecord

class CaseMemoryRepository(ICaseMemoryRepository):
    """
    Episodic Case Memory Repository.
    Stores historical repair cases and calculates continuous Laplace updates.
    Enables future plug-and-play migration to Qdrant/PostgreSQL pgvector.
    """

    def __init__(self):
        self._cases: List[CaseRecord] = [
            CaseRecord(
                case_id="CASE-20260912-0912",
                model="A912",
                symptom_text="Động cơ rung khựng kêu tạch tạch",
                telemetry_snapshot={"hall_state": "000", "fault_current": 45.0},
                verified_root_cause="Hall_Sensor_Phase_U_Cracked",
                action_taken="Replaced PCB Hall board, motor spins smoothly",
                confidence_score=0.98,
            ),
            CaseRecord(
                case_id="CASE-20261005-0552",
                model="A552",
                symptom_text="Khoan tự reset khi đảo chiều quay",
                telemetry_snapshot={"reset_reason": "WDT", "fault_current": 12.0},
                verified_root_cause="3V3_LDO_Capacitor_Cold_Joint",
                action_taken="Resoldered C14 10uF filter capacitor",
                confidence_score=0.96,
            ),
        ]

    def find_similar_cases(self, symptom_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        results = []
        for c in self._cases:
            # Simple keyword overlap / token score for prototype
            score = 0.5
            if any(w in symptom_text.lower() for w in c.symptom_text.lower().split()):
                score = 0.88
            results.append({
                "case_id": c.case_id,
                "model": c.model,
                "similarity_score": score,
                "verified_root_cause": c.verified_root_cause,
                "action_taken": c.action_taken,
            })
        return sorted(results, key=lambda x: x["similarity_score"], reverse=True)[:top_k]

    def save_resolved_case(self, case_data: CaseRecord) -> bool:
        self._cases.append(case_data)
        return True

    def get_all_cases(self) -> List[CaseRecord]:
        return list(self._cases)

