from typing import List, Dict, Any, Optional
from core.interfaces import IGraphRepository, FailureModeNode, TestPointDetail, CandidateTest

class GraphRepository(IGraphRepository):
    """
    In-memory / JSONB Repository implementing IGraphRepository.
    Enables future plug-and-play migration to Neo4j without modifying business logic.
    """

    def __init__(self):
        # Master models database
        self._fault_trees: Dict[str, List[FailureModeNode]] = {
            "A937": [
                FailureModeNode(
                    id="therm",
                    category="Thermal",
                    label="Thermal Overload (RT1)",
                    schematic_refs=["RT1", "U3_THERM"],
                    test_points=["FET_LS_THERM"],
                    threshold=139.0,
                    cost=4.0,
                    prior_prob=0.10,
                ),
                FailureModeNode(
                    id="oc",
                    category="Overcurrent",
                    label="Hardware Overcurrent (HWOC)",
                    schematic_refs=["R42", "U7", "CRNT_MCU"],
                    test_points=["CSP1", "CSN1"],
                    threshold=320.0,
                    cost=8.0,
                    prior_prob=0.12,
                ),
                FailureModeNode(
                    id="mech",
                    category="Mechanical",
                    label="Blade Wear & Mechanical Overload",
                    schematic_refs=["BLADE_ARBOR", "GEAR_ASSEMBLY"],
                    test_points=["MECH_ARBOR_INSPECT"],
                    threshold=None,
                    cost=1.0,
                    prior_prob=0.08,
                ),
                FailureModeNode(
                    id="gate",
                    category="GateDrive",
                    label="Gate Driver / High-side FET",
                    schematic_refs=["A4919", "Q1..Q6"],
                    test_points=["GH_U", "GL_U"],
                    threshold=18.0,
                    cost=6.0,
                    prior_prob=0.05,
                ),
            ],
            "A912": [
                FailureModeNode(
                    id="mech",
                    category="Mechanical",
                    label="Motor Hall Sensor Out-of-Sync",
                    schematic_refs=["HALL_U", "HALL_V", "HALL_W"],
                    test_points=["TP_HALL_UVW"],
                    threshold=None,
                    cost=2.0,
                    prior_prob=0.15,
                ),
                FailureModeNode(
                    id="gate",
                    category="GateDrive",
                    label="Inverter Phase Bridge Gate Stutter",
                    schematic_refs=["U4_DRV", "MOSFET_PHASE"],
                    test_points=["PWM_PHASE_A"],
                    threshold=None,
                    cost=6.0,
                    prior_prob=0.08,
                ),
                FailureModeNode(
                    id="oc",
                    category="Overcurrent",
                    label="Stator Locked Rotor Current",
                    schematic_refs=["RSENSE_1"],
                    test_points=["ISENSE_MAIN"],
                    threshold=80.0,
                    cost=5.0,
                    prior_prob=0.10,
                ),
                FailureModeNode(
                    id="therm",
                    category="Thermal",
                    label="Stator Winding Heat",
                    schematic_refs=["STATOR_TEMP"],
                    test_points=["STATOR_NTC"],
                    threshold=110.0,
                    cost=4.0,
                    prior_prob=0.05,
                ),
            ],
            "A552": [
                FailureModeNode(
                    id="gate",
                    category="GateDrive",
                    label="3.3V Logic Rail UVLO / Power-On Reset",
                    schematic_refs=["U1_LDO_3V3", "C14_DECOUPLING"],
                    test_points=["TP_3V3_MCU", "NRST_LINE"],
                    threshold=3.0,
                    cost=3.0,
                    prior_prob=0.08,
                ),
                FailureModeNode(
                    id="oc",
                    category="Overcurrent",
                    label="Inrush Current Transient",
                    schematic_refs=["Q_MAIN_SW"],
                    test_points=["VBATT_IN"],
                    threshold=40.0,
                    cost=5.0,
                    prior_prob=0.06,
                ),
                FailureModeNode(
                    id="therm",
                    category="Thermal",
                    label="Regulator Thermal Shutdown",
                    schematic_refs=["U1_LDO"],
                    test_points=["LDO_TAB"],
                    threshold=125.0,
                    cost=4.0,
                    prior_prob=0.04,
                ),
                FailureModeNode(
                    id="mech",
                    category="Mechanical",
                    label="Vibration Chuck Disconnect",
                    schematic_refs=["BATT_TERMINAL"],
                    test_points=["BATT_CLIP"],
                    threshold=None,
                    cost=1.0,
                    prior_prob=0.05,
                ),
            ],
        }

        # Available tests mapped by model
        self._tests_by_model: Dict[str, List[CandidateTest]] = {
            "A937": [
                CandidateTest(
                    id="mech",
                    name="Kiểm tra Ngoại quan: Tải Cơ & Độ mòn Lưỡi cắt",
                    category="mech",
                    description="Dòng 295A sát 320A nhưng không có mã ngắn mạch MOSFET. Hãy kiểm tra tình trạng răng đĩa cắt kim cương và khe hở cơ khí.",
                    schematic_ref="Blade Arbor & Mechanical Assembly",
                    cost=1.0,
                    test_type="observe",
                    normal_label="Lưỡi bén, quay êm",
                    abnormal_label="Lưỡi mòn cùn trơ thép, ma sát cực lớn",
                ),
                CandidateTest(
                    id="rt1",
                    name="Đo Điện trở Thermistor RT1 trên mạch FET",
                    category="therm",
                    description="Đo điện trở tại node FET_LS_THERM để loại trừ khả năng sensor nhiệt RT1 bị hở/ngắn mạch gây báo nhiệt giả về MCU.",
                    schematic_ref="RT1 (Ngưỡng: ~10.0kΩ ở 25°C)",
                    cost=4.0,
                    test_type="numeric",
                    unit="kΩ",
                    nominal_min=8.5,
                    nominal_max=12.0,
                ),
                CandidateTest(
                    id="shunt",
                    name="Đo Dạng sóng Dòng Shunt R42 / Khuyếch đại U7",
                    category="oc",
                    description="Kẹp máy hiện sóng vào CSP1/CSN1 để đối chiếu dòng thực tế với dòng 295A mà MCU ghi nhận.",
                    schematic_ref="R42, U7, CRNT_MCU",
                    cost=8.0,
                    test_type="observe",
                    normal_label="Dạng sóng chuẩn ~290A",
                    abnormal_label="Nhiễu cao / Lệch áp",
                ),
            ],
            "A912": [
                CandidateTest(
                    id="hall_sensor",
                    name="Đo Xung Logic Hall Sensor U, V, W",
                    category="mech",
                    description="Dùng Logic Analyzer kiểm tra 3 đường xung Hall khi xoay tay mâm cặp.",
                    schematic_ref="HALL_U, HALL_V, HALL_W",
                    cost=2.0,
                    test_type="observe",
                    normal_label="Đủ 6 trạng thái Gray code",
                    abnormal_label="Kẹt 000 hoặc đứt 1 pha",
                ),
                CandidateTest(
                    id="phase_resistance",
                    name="Đo Điện trở Cuộn Dây Stator 3 Pha",
                    category="gate",
                    description="Đo cân bằng điện trở pha U-V, V-W, W-U bằng Milli-Ohm meter.",
                    schematic_ref="MOTOR_UVW_TERMINALS",
                    cost=4.0,
                    test_type="numeric",
                    unit="mΩ",
                    nominal_min=24.0,
                    nominal_max=28.0,
                ),
            ],
            "A552": [
                CandidateTest(
                    id="vcc_3v3",
                    name="Đo Độ Gợn Sóng Áp 3.3V_MCU khi bấm cò",
                    category="gate",
                    description="Quan sát điện áp 3.3V xem có sụt dưới ngưỡng 3.0V UVLO của MCU không.",
                    schematic_ref="U1 LDO 3.3V Output & C14",
                    cost=3.0,
                    test_type="numeric",
                    unit="V",
                    nominal_min=3.2,
                    nominal_max=3.4,
                ),
                CandidateTest(
                    id="batt_contact",
                    name="Kiểm tra Ngàm Tiếp Xúc Chân Pin",
                    category="mech",
                    description="Quan sát các lá đồng tiếp xúc pin xem có bị lỏng, cháy đen hay oxy hóa.",
                    schematic_ref="BATT_CONNECTOR",
                    cost=1.0,
                    test_type="observe",
                    normal_label="Tiếp xúc tốt, đàn hồi mạnh",
                    abnormal_label="Cháy đen ngàm / Lỏng chân",
                ),
            ],
        }

    def get_fault_tree_for_model(self, model_id: str) -> List[FailureModeNode]:
        return self._fault_trees.get(model_id, self._fault_trees["A937"])

    def get_candidate_tests_for_model(self, model_id: str) -> List[CandidateTest]:
        return self._tests_by_model.get(model_id, self._tests_by_model["A937"])

    def get_test_point_details(self, test_point_id: str) -> Dict[str, Any]:
        return {
            "test_point_id": test_point_id,
            "status": "active",
            "schematic_sheet": "Power_Stage_Rev2.2.SchDoc",
        }

