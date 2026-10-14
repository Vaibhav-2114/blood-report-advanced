import unittest

from backend.api.services.disease_service import predict_diseases
from backend.api.services.extract_service import extract_key_values, normalize_key
from backend.api.services.ml_service import compare_with_ranges, rule_based


class ExtractionTests(unittest.TestCase):
    def test_common_parameter_aliases(self):
        self.assertEqual(normalize_key("Hb"), "Hemoglobin")
        self.assertEqual(normalize_key("WBC Count"), "WBC")
        self.assertEqual(normalize_key("PLT"), "Platelets")
        self.assertEqual(normalize_key("ALT"), "SGPT")

    def test_extract_values_from_report_lines(self):
        text = (
            "Hemoglobin: 13.5 g/dL\n"
            "WBC Count: 7200 /uL\n"
            "Platelets 250000\n"
            "Creatinine: 0.8 mg/dL\n"
            "SGPT (ALT): 45 U/L\n"
        )
        self.assertEqual(
            extract_key_values(text),
            {
                "Hemoglobin": 13.5,
                "WBC": 7200.0,
                "Platelets": 250000.0,
                "Creatinine": 0.8,
                "SGPT": 45.0,
            },
        )


class AnalysisTests(unittest.TestCase):
    def test_range_comparison_requires_context_for_hemoglobin(self):
        result = compare_with_ranges({"Hemoglobin": 13.5, "Creatinine": 0.8})
        self.assertEqual(result["Hemoglobin"]["status"], "Context needed")
        self.assertEqual(result["Creatinine"]["status"], "Normal")

    def test_rule_fallback_flags_configured_thresholds(self):
        result = rule_based({"Hemoglobin": 9.0, "SGPT": 80.0})
        self.assertIn("Anemia_Risk", result["risks"])
        self.assertIn("Liver_Risk", result["risks"])
        self.assertEqual(result["overall_risk"], "Review")
        self.assertIn("not a diagnosis", result["disclaimer"])

    def test_rule_scores_are_disclaimed(self):
        result = predict_diseases({"Hemoglobin": 8.0})
        self.assertIn("disclaimer", result)
        self.assertIn("Anemia indicator", result["possible_diseases"])
        self.assertIn("not a diagnosis", result["summary"])

    def test_empty_data_does_not_claim_disease_is_ruled_out(self):
        result = predict_diseases({})
        self.assertEqual(result["possible_diseases"], {})
        self.assertIn("does not rule out", result["summary"])


if __name__ == "__main__":
    unittest.main()
