import unittest
import time
from core.interfaces import FailureModeNode, InitialEvidence, CandidateTest
from core.bayesian_engine import BayesianEngine

class TestBayesianEngine(unittest.TestCase):
    def setUp(self):
        self.engine = BayesianEngine()
        self.sample_tree = [
            FailureModeNode(id="therm", category="Thermal", label="Thermal Overload", prior_prob=0.10, cost=4.0),
            FailureModeNode(id="oc", category="Overcurrent", label="Hardware Overcurrent", prior_prob=0.12, cost=8.0),
            FailureModeNode(id="mech", category="Mechanical", label="Mechanical Stall / Worn Blade", prior_prob=0.08, cost=1.0),
            FailureModeNode(id="gate", category="GateDrive", label="Gate Driver & Power Rail", prior_prob=0.05, cost=6.0),
        ]
        self.sample_tests = [
            CandidateTest(
                id="test_mech",
                name="Kiểm tra Ngoại quan: Tải Cơ & Độ mòn Lưỡi cắt",
                category="mech",
                description="Quan sát lưỡi cắt kim cương",
                schematic_ref="Mechanical Assembly",
                cost=1.0,
                test_type="observe",
            ),
            CandidateTest(
                id="test_rt1",
                name="Đo Điện trở Thermistor RT1",
                category="therm",
                description="Đo điện trở tại FET_LS_THERM",
                schematic_ref="RT1",
                cost=4.0,
                test_type="numeric",
                unit="kΩ",
            ),
            CandidateTest(
                id="test_shunt",
                name="Đo Dạng sóng Dòng Shunt R42",
                category="oc",
                description="Kẹp máy hiện sóng vào CSP1/CSN1",
                schematic_ref="R42, U7",
                cost=8.0,
                test_type="observe",
            ),
        ]

    def test_sigmoid_continuous_likelihood(self):
        # Normal current (200A) should yield low anomaly score
        s_norm = self.engine.sigmoid_likelihood(200.0, thresh=320.0, m0=288.0)
        self.assertLess(s_norm, 0.10)

        # Danger zone current (295A) should yield high anomaly score (> 0.50)
        s_near = self.engine.sigmoid_likelihood(295.0, thresh=320.0, m0=288.0)
        self.assertGreater(s_near, 0.50)

        # Tripped current (330A) should yield very high anomaly score (> 0.90)
        s_trip = self.engine.sigmoid_likelihood(330.0, thresh=320.0, m0=288.0)
        self.assertGreater(s_trip, 0.90)

    def test_acceptance_criteria_case1_a937(self):
        """
        Acceptance Criteria 1:
        Nạp log 295A -> Thermal >= 90%, Overcurrent >= 70%.
        Bước khuyến nghị số 1: Kiểm tra Tải cơ học & Độ mòn lưỡi cắt (Cost 1).
        Khi bấm 'Lưỡi mòn cùn' -> Mech vọt lên >= 95%, các nhánh khác hạ nhiệt.
        """
        evidence = InitialEvidence(
            model_id="A937",
            logged_fault_current=295.0,
            thermal_counter=1,
            bus_voltage=18.2,
            hall_state="011",
            raw_symptom_text="A937 tắt ngúm khi cắt bê tông đá nặng",
            extracted_symptoms=["heavy_concrete_cutting"],
        )

        # 1. Initial State
        probs = self.engine.evaluate_initial_state(self.sample_tree, evidence)
        self.assertGreaterEqual(probs["therm"], 0.90, "Thermal must be >= 90%")
        self.assertGreaterEqual(probs["oc"], 0.70, "Overcurrent must be >= 70%")

        # 2. Next-Best-Test Ranking
        ranked = self.engine.rank_next_tests(probs, completed_tests=[], available_tests=self.sample_tests)
        self.assertEqual(ranked[0].id, "test_mech", "Rank #1 test must be Mechanical load test")
        self.assertEqual(ranked[0].cost, 1.0)

        # 3. Posterior Update after abnormal blade observation
        updated = self.engine.update_posterior(probs, "mech", "abnorm", self.sample_tree)
        self.assertGreaterEqual(updated["mech"], 0.95, "Mech must jump to >= 95%")
        self.assertLess(updated["therm"], probs["therm"], "Thermal must cool down as secondary effect")
        self.assertLess(updated["oc"], probs["oc"], "Overcurrent must cool down as secondary effect")

    def test_acceptance_criteria_case2_a912(self):
        """
        Acceptance Criteria 2:
        Log báo Hall = 000 -> Nhánh Mech / Hall lập tức chiếm ưu thế >= 88%.
        """
        evidence = InitialEvidence(
            model_id="A912",
            logged_fault_current=45.0,
            thermal_counter=0,
            bus_voltage=19.4,
            hall_state="000",
            raw_symptom_text="Máy bóp cò giật cục khựng lại",
            extracted_symptoms=["hall_jitter"],
        )
        probs = self.engine.evaluate_initial_state(self.sample_tree, evidence)
        self.assertGreaterEqual(probs["mech"], 0.88, "Mech/Hall must be >= 88%")

    def test_acceptance_criteria_case3_continuous_learning_laplace(self):
        """
        Acceptance Criteria 3:
        Continuous learning via Laplace conjugate update.
        """
        res = self.engine.laplace_conjugate_update(alpha_prior=8.0, beta_prior=92.0, observed_success=1)
        self.assertGreater(res["updated_prob"], res["prior_prob"])
        self.assertEqual(res["alpha_new"], 9.0)

    def test_shannon_entropy(self):
        initial_probs = {"therm": 0.91, "oc": 0.74, "mech": 0.68, "gate": 0.06}
        h_initial = self.engine.compute_shannon_entropy(initial_probs)
        self.assertGreater(h_initial, 1.5)

        # After isolated root cause (mech = 0.96, others low)
        isolated_probs = {"therm": 0.42, "oc": 0.34, "mech": 0.96, "gate": 0.02}
        h_isolated = self.engine.compute_shannon_entropy(isolated_probs)
        self.assertLess(h_isolated, h_initial, "Entropy must decrease after isolating root cause")

    def test_execution_latency_sub_10ms(self):
        evidence = InitialEvidence(
            model_id="A937",
            logged_fault_current=295.0,
            thermal_counter=1,
            bus_voltage=18.2,
        )
        start = time.perf_counter()
        for _ in range(100):
            probs = self.engine.evaluate_initial_state(self.sample_tree, evidence)
            self.engine.rank_next_tests(probs, [], self.sample_tests)
            self.engine.update_posterior(probs, "mech", "abnorm", self.sample_tree)
        elapsed_per_run_ms = ((time.perf_counter() - start) / 100.0) * 1000.0
        print(f"\n[BENCHMARK] Average Bayesian pipeline latency: {elapsed_per_run_ms:.3f} ms")
        self.assertLess(elapsed_per_run_ms, 10.0, "Execution latency must be sub-10ms")

if __name__ == "__main__":
    unittest.main()

