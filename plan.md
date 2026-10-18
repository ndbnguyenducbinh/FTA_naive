### 1. Đánh giá tính khả thi: Tech stack này có làm prototype dễ dàng không?

Nếu triển khai **nguyên xi toàn bộ stack production** (gồm Neo4j riêng, Qdrant riêng, PostgreSQL riêng, Rust parser và LangGraph) ngay từ ngày đầu, team sẽ rơi vào bẫy **over-engineering (quá tải kiến trúc)**. Chi phí thiết lập DevOps, đồng bộ dữ liệu giữa 3 database và debug phân tán sẽ kéo dài thời gian làm prototype từ 2 tuần lên 2–3 tháng.

Tuy nhiên, nếu áp dụng chiến lược **"Postgres-First / Monolithic-Prototype"**, bài toán sẽ cực kỳ khả thi và code rất nhanh:

* **Hạ tầng cơ sở dữ liệu rút gọn về 1 cụm duy nhất (PostgreSQL):** PostgreSQL đảm nhiệm cả 3 vai trò: quan hệ bảng thông thường, `pgvector` xử lý semantic search thay cho Qdrant, và `JSONB` hoặc Recursive CTE xử lý cây lỗi FTA thay cho Neo4j.
* **Backend thuần Python (FastAPI + Pydantic + NumPy):** Bỏ Rust parser ở giai đoạn này; dùng Python struct unpack đọc file nhị phân và NumPy tính ma trận Bayes. Tốc độ thực thi vẫn đạt mức sub-10ms.
* **Frontend (Next.js + React Flow):** Dùng trực tiếp canvas kéo thả của React Flow để trực quan hóa cây lỗi thay cho việc vẽ SVG thủ công.



Với cách tiếp cận này, kiến trúc vẫn tuân thủ Clean Architecture: khi hệ thống mở rộng lên hàng nghìn linh kiện, team chỉ cần tráo implementation của Repository từ Postgres sang Neo4j/Qdrant mà không phải viết lại business logic hay thuật toán Bayes.

---

### 2. Bản Đặc tả Kỹ thuật (Technical Requirement Document - TRD) gửi Team Kỹ sư

```
DỰ ÁN: Neuro-Symbolic Diagnostic Copilot (MVP Prototype)
TARGET DELIVERABLE: Web App chạy local/staging, nạp log thật/giả lập, hiển thị cây lỗi và gợi ý bước đo động.
THỜI GIAN THỰC HIỆN: 3 Sprints (3 tuần)

```

#### A. Kiến trúc Module & Phân định Trách nhiệm (Separation of Concerns)

```
[Client: Next.js + React Flow]
        │  (HTTP / SSE / WebSocket)
        ▼
[API Gateway: FastAPI]
  ├── Module 1: Telemetry & Semantic Ingestion (Pydantic + Gemini/OpenAI API)
  ├── Module 2: Bayesian Diagnostic Core (NumPy / SciPy Engine)
  └── Module 3: Active Testing & Next-Best-Test Ranker (Entropy Optimizer)
        │
        ▼
[Data Abstraction Layer: Repository Pattern]
        │
[Single Storage: PostgreSQL 16 + pgvector]
  ├── Relational: Model, Subsystem, Component, TestPoint
  ├── JSONB: Cấu trúc cây FTA DAG & Bảng CPT
  └── pgvector: Embedding triệu chứng & Case Memory

```

#### B. Yêu cầu Chi tiết từng Phân hệ

**Module 1: Telemetry Parser & Semantic Extractor**

* **Input:** File log nhị phân/CSV (chứa các thanh ghi mã lỗi, bộ đếm quá nhiệt, dòng ngắt snapshot) + Chuỗi string mô tả triệu chứng bằng tiếng Việt/Anh.


* **Xử lý:**
* Script Python parse các field nhị phân thành dictionary: `{fault_current: 295.0, thermal_counter: 1, vbatt: 18.2, hall_state: "011"}`.


* LLM Function Calling nhận mô tả ngôn ngữ tự nhiên, trích xuất thực thể và ánh xạ vào các ID triệu chứng chuẩn mà không can thiệp vào số liệu đo.




* **Output:** Đối tượng `InitialEvidence` (Pydantic model) chuyển cho Bayesian Engine.



**Module 2: Bayesian Diagnostic Core (Pure Python/NumPy)**

* **Yêu cầu cốt lõi:** Không để LLM tính toán xác suất.


* Triển khai công thức Noisy-OR và hàm Likelihood Sigmoid liên tục cho các giá trị đo số học (`numeric` như dòng điện $A$, áp $V$, nhiệt độ $°C$):



$$s(x) = \frac{1}{1 + \exp\left(-k \cdot \frac{x - m_0}{T_{\text{thresh}}}\right)}$$


* Quản lý trạng thái phiên chẩn đoán (`SessionState`): Khi người dùng gửi kết quả đo mới (Pass/Fail hoặc số đo thực tế), cập nhật lại phân phối xác suất của toàn bộ các nhánh lỗi trong thời gian $\le 15\text{ms}$.



**Module 3: Next-Best-Test Recommender**

* Tính toán Shannon Entropy của phân phối xác suất hiện tại:



$$H(C) = -\sum P(C_i) \log_2 P(C_i)$$


* Duyệt qua danh sách các phép đo chưa thực hiện, tính Information Gain kỳ vọng chia cho $(\text{Cost})^\alpha$ với $\alpha = 0.7$.


* Trả về danh sách bước kiểm tra sắp xếp theo thứ tự ưu tiên giảm dần.



**Module 4: Frontend UI (Next.js 15 + React Flow + TailwindCSS)**

* Tái hiện chính xác các luồng tương tác từ file HTML prototype:


* Bảng điều khiển nạp file log + khung nhập mô tả tiếng Việt.


* Khung vẽ cây lỗi trực quan (React Flow DAG): Đổi màu viền và hiển thị phần trăm xác suất động trên từng node (`Thermal`, `Overcurrent`, `Mech`, `Gate Drive`).


* Action Center: Hiển thị bước đo khuyến nghị số 1, các nút chọn trạng thái (Bình thường / Bất thường) và ô nhập giá trị số.


* Modal lưu tri thức (Case Commit) khi xác nhận xong nguyên nhân gốc.





---

### 3. Kế hoạch Triển khai (Engineering Sprint Plan - 3 Tuần)

| Tuần | Mục tiêu chính | Nhiệm vụ cụ thể của Backend / AI | Nhiệm vụ cụ thể của Frontend | Deliverable kiểm tra |
| --- | --- | --- | --- | --- |
| **Sprint 1** | **Core Engine & Data Schema** | - Thiết kế DB schema trên PostgreSQL (Model, Component, FailureMode, TestPoint).

<br>

<br>- Viết `BayesianEngine` bằng NumPy có unit tests đạt 100% độ phủ cho công thức Noisy-OR & Sigmoid.

<br>

<br>- Viết Telemetry Parser đọc file CSV/Log mẫu.

 | - Dựng khung dự án Next.js + TailwindCSS + Shadcn UI.

<br>

<br>- Dựng canvas React Flow cơ bản render cây FTA tĩnh từ JSON fixture.

 | Chạy test suite toán học độc lập; React Flow render được cây 4 nhánh.

 |
| **Sprint 2** | **RAG, LLM & API Integration** | - Tích hợp LLM API trích xuất Structured Output từ prompt tiếng Việt.

<br>

<br>- Dựng `pgvector` lưu trữ 10 ca sửa chữa mẫu.

<br>

<br>- Viết thuật toán xếp hạng bước đo Next-Best-Test ($IG/\text{Cost}^\alpha$).

<br>

<br>- Đóng gói các REST API endpoints (`/session/init`, `/test/submit`, `/case/commit`). | - Nối API nạp Log và mô tả triệu chứng.<br>

<br>- Render danh sách Explainable Signals.

<br>

<br>- Tạo form nhập liệu cho từng loại test (`numeric` input và `observe` buttons).

 | Hệ thống nhận input, tính toán Bayes và trả về bước đo số 1 chính xác qua Postman/UI. |
| **Sprint 3** | **Interactive UI, Feedback & Demo Polish** | - Tích hợp logic Laplace Smoothing khi kỹ sư bấm "Lưu tri thức".

<br>

<br>- Tối ưu hóa độ trễ API ($< 500\text{ms}$ cho luồng LLM, $< 20\text{ms}$ cho luồng Bayes). | - Hiệu ứng animation chạy node khi cập nhật xác suất.

<br>

<br>- Thanh đo độ bất định Shannon Entropy ($H(C)$).

<br>

<br>- Tích hợp tính năng "Chạy Demo Tự Động" (Auto Walkthrough) phục vụ thuyết trình.

 | Bản web demo hoàn chỉnh chạy mượt 3 kịch bản: A937 (Cắt bê tông), A912 (Lỗi Hall), A552 (Reset nguồn).

 |

---

### 4. Thiết kế Data Contracts (Interfaces) để dễ bảo trì và mở rộng

Để đảm bảo sau này có thể thay thế Postgres bằng Neo4j hoặc Qdrant mà không vỡ hệ thống, yêu cầu team tuân thủ nghiêm ngặt 3 interfaces trừu tượng sau:

```python
# 1. Interface lưu trữ cấu trúc mạch & đồ thị lỗi (Dễ dàng chuyển sang Neo4j sau này)
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from pydantic import BaseModel

class FailureModeNode(BaseModel):
    id: str
    category: str
    label: str
    schematic_refs: List[str]
    test_points: List[str]
    threshold: Optional[float]
    cost: float
    prior_prob: float

class IGraphRepository(ABC):
    @abstractmethod
    def get_fault_tree_for_model(self, model_id: str) -> List[FailureModeNode]:
        pass

    @abstractmethod
    def get_test_point_details(self, test_point_id: str) -> Dict:
        pass


# 2. Interface tính toán xác suất (Độc lập hoàn toàn với web framework và LLM)
class IBayesianInferenceEngine(ABC):
    @abstractmethod
    def evaluate_initial_state(self, tree: List[FailureModeNode], evidence: Dict) -> Dict[str, float]:
        pass

    @abstractmethod
    def update_posterior(self, current_probs: Dict[str, float], test_id: str, test_result: any) -> Dict[str, float]:
        pass

    @abstractmethod
    def rank_next_tests(self, current_probs: Dict[str, float], completed_tests: List[str]) -> List[Dict]:
        pass


# 3. Interface bộ nhớ ca bệnh (Dễ dàng chuyển sang Qdrant/Pinecone sau này)
class ICaseMemoryRepository(ABC):
    @abstractmethod
    def find_similar_cases(self, symptom_text: str, top_k: int = 3) -> List[Dict]:
        pass

    @abstractmethod
    def save_resolved_case(self, case_data: Dict) -> bool:
        pass

```

---

### 5. Gói bàn giao (Checklist gửi kèm cho Team Kỹ sư)

Khi gửi tài liệu cho team kỹ thuật, bạn đính kèm:

1. **File HTML prototype (`neuro_symbolic_diagnostic_copilot.html`)**: Đóng vai trò là bản UI/UX Spec sống và tài liệu nghiệm thu tính năng. Mọi hành vi click, đổi màu node, và hiệu ứng dữ liệu trên bản hoàn thiện phải khớp với bản HTML này.


2. **Kịch bản nghiệm thu (Acceptance Criteria):**
* *Test Case 1 (A937):* Nạp log $295\text{A}$ $\rightarrow$ Nhánh `Thermal` hiển thị $\ge 90\%$, `Overcurrent` $\ge 70\%$. Bước khuyến nghị số 1 phải là "Kiểm tra Tải cơ học & Độ mòn lưỡi cắt" (Cost 1). Khi bấm "Lưỡi mòn cùn", nhánh `Mech` phải vọt lên $\ge 95\%$, các nhánh khác hạ nhiệt.


* *Test Case 2 (A912):* Log báo `Hall = 000` $\rightarrow$ Nhánh `Mech / Hall` lập tức chiếm ưu thế $\ge 88\%$.


* *Test Case 3 (Continuous Learning):* Bấm "Xác nhận & Lưu tri thức" $\rightarrow$ Bản ghi được lưu vào database và API log hiển thị công thức cập nhật phân phối Laplace thành công.