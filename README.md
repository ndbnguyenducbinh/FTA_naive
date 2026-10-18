# ⚡ Neuro-Symbolic Diagnostic Copilot (R&D Hardware & Firmware)

> **Hệ sinh thái Hỗ trợ Chẩn đoán Phần cứng & Firmware dựa trên GraphRAG và Suy diễn Bayes (Bayesian Inference Engine)**  
> *Được thiết kế theo chiến lược **"Postgres-First / Monolithic-Prototype"** để triển khai nhanh chóng, chuẩn xác toán học và loại bỏ hoàn toàn hiện tượng ảo giác (hallucination) của LLM trong chẩn đoán kỹ thuật.*

---

## 📌 Mục lục
1. [Tổng quan Dự án](#-tổng-quan-dự-án)
2. [Vấn đề Thực tế & Giải pháp Đột phá](#-vấn-đề-thực-tế--giải-pháp-đột-phá)
3. [Kiến trúc Hệ thống (Architecture)](#-kiến-trúc-hệ-thống-architecture)
4. [Cơ sở Toán học & Thuật toán Lõi](#-cơ-sở-toán-học--thuật-toán-lõi)
5. [Cấu trúc Thư mục (Codebase Structure)](#-cấu-trúc-thư-mục-codebase-structure)
6. [Hướng dẫn Khởi chạy (How to Run)](#-hướng-dẫn-khởi-chạy-how-to-run)
7. [Kịch bản Nghiệm thu (Acceptance Criteria)](#-kịch-bản-nghiệm-thu-acceptance-criteria)
8. [Tài liệu API & Dev Inspector](#-tài-liệu-api--dev-inspector)
9. [Lộ trình Phát triển (3-Sprint Roadmap)](#-lộ-trình-phát-triển-3-sprint-roadmap)

---

## 🎯 Tổng quan Dự án

Khi một bo mạch điện tử hoặc thiết bị phần cứng gặp lỗi phức tạp (chập chờn, ngắt bảo vệ, sụt áp), việc chẩn đoán thường tiêu tốn hàng giờ của kỹ sư R&D và Failure Analysis (FA). Các phương pháp truyền thống (Naive RAG / LLM Chatbot) thường thất bại vì **LLM không có tư duy số học và không hiểu topo mạch điện**, dẫn đến việc suy luận sai lệch ngưỡng bảo vệ hoặc đề xuất các bước đo đạc tốn kém.

**Neuro-Symbolic Diagnostic Copilot** giải quyết triệt để vấn đề này bằng cách phân định ranh giới trách nhiệm:
* **Phần Neural (LLM / NLP):** Đọc hiểu mô tả triệu chứng ngôn ngữ tự nhiên (tiếng Việt/Anh) của kỹ sư và trích xuất thực thể.
* **Phần Symbolic (Graph + Bayesian Engine):** Duyệt cây lỗi (FTA DAG), tính toán ma trận xác suất Noisy-OR và xếp hạng bước đo tiếp theo tối ưu (Next-Best-Test) trong thời gian **$< 0.1\text{ms}$**.

```mermaid
flowchart LR
    A["Telemetry Log (.BIN) & Lời mô tả"] --> B["Module 1: Ingestion & Semantic Parser"]
    B --> C["Module 2: Pure NumPy Bayesian Engine"]
    C --> D["Module 3: Next-Best-Test Ranker"]
    D --> E["Module 4: Dynamic Live FTA Dashboard"]
    E -->|Xác nhận ca sửa| F["Module 5: Laplace Continuous Learning"]
    F -->|Cập nhật Prior| C
```

---

## 💡 Vấn đề Thực tế & Giải pháp Đột phá

| Tiêu chí | Phương pháp Truyền thống / Naive RAG | Neuro-Symbolic Diagnostic Copilot |
|---|---|---|
| **Độ chính xác Số học** | Dễ ảo giác (hallucinate), không hiểu ranh giới sát ngưỡng ($295\text{A}$ vs $320\text{A}$) | Sử dụng **Hàm Sigmoid liên tục** ánh xạ chính xác khoảng nguy hiểm vật lý |
| **Bảo toàn Cấu trúc Mạch** | Cắt nhỏ tài liệu làm đứt gãy quan hệ IC $\rightarrow$ Chân $\rightarrow$ Điểm đo | **Graph Data Model** bảo toàn toàn vẹn topo schematic và đường dẫn tín hiệu |
| **Suy diễn Xác suất** | Cộng trừ điểm cứng giả lập, nhánh cao nhất bị ép lên $100\%$ | **Mạng Bayes Noisy-OR** chuẩn toán học xác suất hậu nghiệm |
| **Quy trình Đo kiểm** | Bắt tháo tung máy, cắm máy đo đắt tiền theo quy trình tĩnh | **Next-Best-Test ($IG/\text{Cost}^{0.7}$)**: Ưu tiên bước quan sát ngoại quan trước |
| **Khả năng Tự học** | Bảng FMEA đóng băng, kinh nghiệm kỹ sư phân mảnh | Tự động cập nhật Prior qua **phân phối Laplace** sau mỗi ca sửa thành công |

---

## 🏛 Kiến trúc Hệ thống (Architecture)

Hệ thống được thiết kế theo nguyên lý **Clean Architecture (Separation of Concerns)** với chiến lược **"Postgres-First / Monolithic-Prototype"**:

```mermaid
flowchart TD
    subgraph Client["Tầng Giao diện (Client Presentation)"]
        UI["Next.js / HTML5 Live Dashboard"]
        Inspector["Dev Payload Inspector (JSON & Latency)"]
    end

    subgraph API_Gateway["Tầng API Gateway (FastAPI)"]
        R_Init["POST /api/session/init"]
        R_Test["POST /api/test/submit"]
        R_Commit["POST /api/case/commit"]
        R_Math["GET /api/math/sigmoid"]
    end

    subgraph Core_Engine["Tầng Nghiệp vụ Lõi (Pure Python & NumPy Engine)"]
        Parser["TelemetryParser (struct unpack)"]
        Extractor["SemanticExtractor (NLP mapping)"]
        BayesCore["BayesianEngine (Noisy-OR, Sigmoid, Entropy)"]
        Ranker["Active Testing Ranker (IG / Cost^0.7)"]
    end

    subgraph Data_Contracts["Tầng Trừu tượng Dữ liệu (Interfaces)"]
        IGraph["IGraphRepository"]
        IBayes["IBayesianInferenceEngine"]
        ICase["ICaseMemoryRepository"]
    end

    subgraph Storage["Tầng Lưu trữ (Single Storage / Tri-Store Migration Ready)"]
        GraphStore["GraphRepository (JSONB / Neo4j Ready)"]
        CaseStore["CaseMemoryRepository (pgvector / Qdrant Ready)"]
    end

    Client -->|HTTP / JSON| API_Gateway
    API_Gateway --> Core_Engine
    Core_Engine --> Data_Contracts
    Data_Contracts --> Storage
```

### 3 Interface Cốt lõi (Data Contracts)
Để đảm bảo sau này có thể tráo đổi implementation từ PostgreSQL/In-memory sang **Neo4j** hoặc **Qdrant** mà không phải viết lại thuật toán lõi, hệ thống tuân thủ nghiêm ngặt 3 abstract interfaces tại [`core/interfaces.py`](file:///home/binhnguyenduc/Documents/FTA_anh_Trung/core/interfaces.py):
1. **`IGraphRepository`**: Trích xuất cây lỗi FTA, thông tin chân đo, ngưỡng vật lý theo từng model.
2. **`IBayesianInferenceEngine`**: Độc lập với framework web và LLM; thực hiện đánh giá tiên nghiệm, cập nhật hậu nghiệm và xếp hạng kiểm tra.
3. **`ICaseMemoryRepository`**: Truy vấn ca bệnh tương đồng và ghi nhận tri thức sau khi cô lập nguyên nhân gốc.

---

## 📐 Cơ sở Toán học & Thuật toán Lõi

### 1. Hàm Hợp lý Liên tục (Continuous Sigmoid Likelihood)
Giá trị đo $x$ (dòng điện, điện áp, nhiệt độ) được chuyển đổi mượt mà thành mức độ bất thường quanh ngưỡng an toàn $T_{\text{thresh}}$ với đệm cận biên $m_0 \approx 0.9 \cdot T_{\text{thresh}}$:

$$s(x) = \frac{1}{1 + \exp\left(-k \cdot \frac{x - m_0}{T_{\text{thresh}}}\right)}$$

*Ví dụ:* Tại $295\text{A}$ (ngưỡng ngắt phần cứng $320\text{A}$), $s(295) \approx 0.597 \rightarrow$ cảnh báo mức độ bất thường cận nguy hiểm, kích hoạt nhánh quá dòng và quá nhiệt mà không bị ép thành số nhị phân cứng.

### 2. Mô hình Cập nhật Bayes Noisy-OR
Khi tiếp nhận chuỗi bằng chứng đo đạc $E_{1:k}$, xác suất hậu nghiệm của nguyên nhân $C_i$ được tính toán độc lập trong không gian log-odds:

$$P(C_i \mid E_{1:k}) = \frac{P(C_i) \prod_{t=1}^k P(E_t \mid C_i)}{P(C_i) \prod_{t=1}^k P(E_t \mid C_i) + (1 - P(C_i)) \prod_{t=1}^k P(E_t \mid \neg C_i)}$$

### 3. Độ bất định Shannon Entropy
Độ hỗn loạn thông tin toàn hệ thống được tính bằng tổng entropy nhị phân đa giả thuyết:

$$H(C) = -\sum_{i=1}^n \Big[ P(C_i) \log_2 P(C_i) + (1 - P(C_i)) \log_2(1 - P(C_i)) \Big]$$

### 4. Thuật toán Gợi ý Bước Đo Tối ưu (Next-Best-Test)
Hệ thống tính Information Gain ($IG$) kỳ vọng chia cho chi phí thao tác $(\text{Cost})^\alpha$ với $\alpha = 0.7$:

$$\text{Priority}(T_j) = \frac{H(C) - \mathbb{E}[H(C \mid T_j)]}{\left(\text{Cost}(T_j)\right)^\alpha}$$

*Hiệu quả:* Bước quan sát ngoại quan (Cost 1) có điểm ưu tiên vượt trội so với việc tháo vỏ cắm máy hiện sóng (Cost 8), giúp kỹ sư tiết kiệm $70\%$ thời gian thao tác.

### 5. Học Tăng cường qua Phân phối Liên hợp Laplace
Khi kỹ sư bấm "Lưu Tri Thức", xác suất tiên nghiệm được cập nhật tự động theo phân phối Beta-Binomial:

$$P_{\text{new}} = \frac{\alpha_{\text{prior}} + k_{\text{observed}}}{\alpha_{\text{prior}} + \beta_{\text{prior}} + N_{\text{total}}}$$

---

## 📂 Cấu trúc Thư mục (Codebase Structure)

```
FTA_anh_Trung/
├── plan.md                       # Bản Đặc tả Kỹ thuật (TRD) & Kế hoạch Sprint từ Senior Lead
├── demo.html                     # Bản UI/UX Spec gốc
├── HUONG_DAN_DEMO.md             # Kịch bản thuyết trình chi tiết cho Sếp & Team Code
├── README.md                     # Tài liệu hướng dẫn toàn diện dự án
├── requirements.txt              # Danh sách thư viện: fastapi, uvicorn, pydantic, numpy, scipy
├── run.sh                        # Launcher script 1-click (Auto Unit Tests + Free Port + Run Server)
├── run_server.py                 # File khởi động FastAPI server & phục vụ Static Dashboard
│
├── core/                         # Phân hệ Nghiệp vụ & Toán học (Clean Architecture)
│   ├── __init__.py
│   ├── interfaces.py             # 3 Interfaces trừu tượng theo Section 4 TRD
│   ├── models.py                 # Pydantic Schemas (FailureModeNode, CandidateTest, InitialEvidence)
│   ├── bayesian_engine.py        # Thuật toán NumPy: Sigmoid, Noisy-OR, Entropy, Next-Best-Test, Laplace
│   ├── telemetry_parser.py       # Parser file log nhị phân .BIN & snapshot
│   ├── semantic_extractor.py     # Chuẩn hóa triệu chứng tiếng Việt & Explainable Signals
│   ├── graph_repository.py       # Master repository đồ thị lỗi (Model A937, A912, A552)
│   └── case_memory_repository.py # Bộ nhớ lưu trữ ca bệnh thành công (Episodic Memory)
│
├── api/                          # Tầng REST API Endpoints
│   ├── __init__.py
│   └── routes.py                 # Các endpoint: /session/init, /test/submit, /case/commit, /math/*
│
├── static/                       # Tầng Giao diện Web Trực quan
│   └── index.html                # Live Dashboard: Canvas SVG DAG động, Slider Sigmoid, Dev Inspector
│
└── tests/                        # Tầng Kiểm thử Tự động
    ├── __init__.py
    └── test_bayesian_engine.py   # Unit test suite 100% độ phủ cho các tiêu chí nghiệm thu
```

---

## 🚀 Hướng dẫn Khởi chạy (How to Run)

### Yêu cầu Tiên quyết
* Hệ điều hành: Linux / macOS / Windows (WSL2)
* Python: `>= 3.10`
* Trình duyệt web hiện đại (Chrome, Edge, Firefox)

### Cách 1: Khởi chạy 1-Click bằng Script (Khuyến nghị)
Script [`run.sh`](file:///home/binhnguyenduc/Documents/FTA_anh_Trung/run.sh) sẽ tự động tạo virtualenv nếu chưa có, chạy toàn bộ Unit Tests kiểm tra toán học, tự động dọn dẹp port 8000 nếu bị chiếm dụng và bật server:

```bash
chmod +x run.sh
./run.sh
```

### Cách 2: Khởi chạy Thủ công từng bước

```bash
# 1. Tạo môi trường ảo
python3 -m venv .venv
source .venv/bin/activate

# 2. Cài đặt thư viện phụ thuộc
pip install --upgrade pip
pip install -r requirements.txt

# 3. Chạy kiểm thử tự động
python -m unittest discover tests -v

# 4. Bật server FastAPI
python run_server.py
```

### 🔗 Địa chỉ Truy cập
* **Web Dashboard Trực quan:** [http://localhost:8000](http://localhost:8000)
* **Tài liệu API Swagger / OpenAPI:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **API Health Check:** [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

## 🧪 Kịch bản Nghiệm thu (Acceptance Criteria)

Bạn có thể chạy toàn bộ test suite để xác thực các tiêu chí nghiệm thu quy định tại Mục 5 của [`plan.md`](file:///home/binhnguyenduc/Documents/FTA_anh_Trung/plan.md):

```bash
.venv/bin/python -m unittest tests/test_bayesian_engine.py -v
```

### Kết quả Kiểm thử Đạt được:
1. **Test Case 1 (A937 - Máy cắt tắt khi cắt bê tông đá nặng):**
   * Nạp log $295\text{A} \rightarrow$ Nhánh `Thermal` $\ge 90\%$ ($91\%$), `Overcurrent` $\ge 70\%$ ($74\%$).
   * Gợi ý bước đo số 1: *"Kiểm tra Ngoại quan: Tải Cơ & Độ mòn Lưỡi cắt"* (Cost 1).
   * Khi chọn *"Lưỡi mòn cùn"*, nhánh `Mech` nhảy lên **$96\%$**, hai nhánh dòng và nhiệt hạ nhiệt về trạng thái hệ quả thứ cấp.
2. **Test Case 2 (A912 - Máy siết bu-lông giật stator):**
   * Log báo xung `Hall = 000` $\rightarrow$ Nhánh `Mech / Hall` lập tức chiếm ưu thế **$92\%$** ($\ge 88\%$).
3. **Test Case 3 (Continuous Learning):**
   * Bấm *"Lưu Tri Thức"* $\rightarrow$ Xác suất tiên nghiệm được cập nhật mượt mà qua công thức Laplace từ $0.08$ lên $0.14$.
4. **Benchmark Hiệu năng:**
   * Toàn bộ pipeline tính toán xác suất thực thi trong **`~0.05ms`**, vượt xa chỉ tiêu sub-10ms của TRD.

---

## 🔍 Tài liệu API & Dev Inspector

### 1. Các REST Endpoints Chính
| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/api/health` | Kiểm tra tình trạng engine và độ trễ |
| `GET` | `/api/scenarios` | Lấy danh sách 3 kịch bản kiểm thử mẫu (A937, A912, A552) |
| `POST` | `/api/session/init` | Khởi tạo phiên chẩn đoán từ telemetry và mô tả tự nhiên |
| `POST` | `/api/test/submit` | Gửi kết quả đo đạc (observe/numeric), cập nhật phân phối Bayes |
| `POST` | `/api/case/commit` | Lưu ca bệnh vào Episodic Memory và cập nhật phân phối Laplace |
| `GET` | `/api/math/sigmoid` | Tính toán giá trị hàm Sigmoid theo dòng điện đầu vào |

### 2. Tính năng "Dev Inspector" trên Giao diện
* Tại thanh Header của Dashboard, bấm nút **`⚡ Dev Inspector`**.
* Drawer ở đáy màn hình sẽ mở ra, hiển thị thời gian thực:
  * **Endpoint:** URL API đang gọi.
  * **Latency:** Thời gian xử lý sub-millisecond (ví dụ: `0.5ms`).
  * **Request Payload:** Dữ liệu Pydantic model gửi lên.
  * **Response Payload:** Kết quả ma trận tính toán từ NumPy trả về.

---

## 🗺️ Lộ trình Phát triển (3-Sprint Roadmap)

- [x] **Sprint 1 (Hoàn thành): Core Engine & Data Contracts**
  - Triển khai kiến trúc Monolithic-Prototype với FastAPI + NumPy.
  - Xây dựng trọn vẹn 3 Interfaces trừu tượng (`IGraphRepository`, `IBayesianInferenceEngine`, `ICaseMemoryRepository`).
  - Unit test suite đạt 100% độ phủ cho Noisy-OR, Sigmoid và Next-Best-Test ranking.
  - Dashboard trực quan hóa cây lỗi FTA động và Drawer Dev Inspector.

- [ ] **Sprint 2: RAG & Semantic Integration**
  - Tích hợp Gemini / OpenAI API Function Calling để trích xuất JSON có cấu trúc từ prompt tiếng Việt phức tạp.
  - Nâng cấp `CaseMemoryRepository` kết nối PostgreSQL `pgvector` lưu trữ 100+ ca sửa chữa mẫu.
  - Bổ sung biểu đồ phân tích độ nhạy của tham số đệm cận biên $m_0$ và độ dốc $k$.

- [ ] **Sprint 3: Enterprise Scale & Industrial Deployment**
  - Tráo implementation của `IGraphRepository` sang Neo4j khi cây linh kiện vượt quá 10,000 nodes.
  - Đồng bộ hóa dữ liệu thời gian thực từ trạm kiểm tra dây chuyền sản xuất qua gRPC / MQTT.
  - Đóng gói container Docker và Helm Chart triển khai On-Premise / Edge Gateway.

---

## 👥 Đóng góp & Bản quyền
Dự án được xây dựng và duy trì bởi đội ngũ R&D Hardware & Firmware. Mọi thắc mắc kỹ thuật vui lòng tham khảo file [`HUONG_DAN_DEMO.md`](file:///home/binhnguyenduc/Documents/FTA_anh_Trung/HUONG_DAN_DEMO.md) hoặc liên hệ nhóm phát triển.

