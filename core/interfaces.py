from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class TestPointDetail(BaseModel):
    id: str
    name: str
    schematic_refs: List[str] = Field(default_factory=list)
    description: str
    test_type: str = "observe"  # "observe" or "numeric"
    unit: Optional[str] = None
    expected_range: Optional[Dict[str, float]] = None
    cost: float = 1.0


class FailureModeNode(BaseModel):
    id: str
    category: str
    label: str
    schematic_refs: List[str] = Field(default_factory=list)
    test_points: List[str] = Field(default_factory=list)
    threshold: Optional[float] = None
    cost: float = 1.0
    prior_prob: float = 0.10


class InitialEvidence(BaseModel):
    model_id: str
    logged_fault_current: Optional[float] = None
    thermal_counter: int = 0
    bus_voltage: Optional[float] = None
    hall_state: Optional[str] = None
    reset_reason: Optional[str] = None
    raw_symptom_text: Optional[str] = None
    extracted_symptoms: List[str] = Field(default_factory=list)


class CandidateTest(BaseModel):
    id: str
    name: str
    category: str
    description: str
    schematic_ref: str
    cost: float
    test_type: str  # "observe" or "numeric"
    unit: Optional[str] = None
    normal_label: Optional[str] = None
    abnormal_label: Optional[str] = None
    nominal_min: Optional[float] = None
    nominal_max: Optional[float] = None
    priority_score: float = 0.0
    rank: int = 1


class DiagnosticSession(BaseModel):
    session_id: str
    model_id: str
    current_probs: Dict[str, float]
    completed_tests: Dict[str, Any] = Field(default_factory=dict)
    entropy: float
    next_best_tests: List[CandidateTest]
    explainable_signals: List[Dict[str, str]]
    root_cause_isolated: bool = False
    isolated_cause_id: Optional[str] = None


class CaseRecord(BaseModel):
    case_id: str
    model: str
    symptom_text: str
    telemetry_snapshot: Dict[str, Any]
    verified_root_cause: str
    action_taken: str
    engineer_rating: int = 5
    confidence_score: float = 0.95


# --- Core Interfaces defined in plan.md Section 4 ---

class IGraphRepository(ABC):
    @abstractmethod
    def get_fault_tree_for_model(self, model_id: str) -> List[FailureModeNode]:
        pass

    @abstractmethod
    def get_test_point_details(self, test_point_id: str) -> Dict[str, Any]:
        pass


class IBayesianInferenceEngine(ABC):
    @abstractmethod
    def evaluate_initial_state(
        self, tree: List[FailureModeNode], evidence: InitialEvidence
    ) -> Dict[str, float]:
        pass

    @abstractmethod
    def update_posterior(
        self,
        current_probs: Dict[str, float],
        test_id: str,
        test_result: Any,
        tree: List[FailureModeNode],
    ) -> Dict[str, float]:
        pass

    @abstractmethod
    def rank_next_tests(
        self,
        current_probs: Dict[str, float],
        completed_tests: List[str],
        available_tests: List[CandidateTest],
        alpha: float = 0.7,
    ) -> List[CandidateTest]:
        pass


class ICaseMemoryRepository(ABC):
    @abstractmethod
    def find_similar_cases(self, symptom_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def save_resolved_case(self, case_data: CaseRecord) -> bool:
        pass

