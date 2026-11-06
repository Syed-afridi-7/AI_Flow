import unittest
from engine.core.ast_tools import (
    validate_python_syntax,
    scan_security_risks,
    check_conventional_commit,
    calculate_contrast_ratio,
    measure_hookscore,
)

class TestAstTools(unittest.TestCase):
    def test_validate_python_syntax_valid(self):
        code = "def foo():\n    return 42\n"
        errors = validate_python_syntax(code)
        self.assertEqual(len(errors), 0)

    def test_validate_python_syntax_invalid(self):
        code = "def foo(:\n    return 42\n"
        errors = validate_python_syntax(code)
        self.assertGreater(len(errors), 0)
        self.assertEqual(errors[0].rule_id, "AST_SYNTAX_ERROR")

    def test_scan_security_risks(self):
        insecure_code = """
import os
API_KEY = "sk-1234567890abcdef1234567890abcdef"
def run(cmd):
    eval(cmd)
def get_user(id):
    query = f"SELECT * FROM users WHERE id = {id}"
"""
        blockers = scan_security_risks(insecure_code)
        rule_ids = [b.rule_id for b in blockers]
        self.assertIn("SEC_HARDCODED_KEY", rule_ids)
        self.assertIn("SEC_DANGEROUS_EVAL", rule_ids)
        self.assertIn("SEC_SQL_INJECTION", rule_ids)

    def test_check_conventional_commit(self):
        valid_msg = "feat(auth): add OAuth2 provider verification"
        passed, reasons = check_conventional_commit(valid_msg)
        self.assertTrue(passed)

        invalid_msg = "fixed bug in auth"
        passed, reasons = check_conventional_commit(invalid_msg)
        self.assertFalse(passed)

    def test_calculate_contrast_ratio(self):
        # Black on white should be 21:1
        ratio = calculate_contrast_ratio("#000000", "#FFFFFF")
        self.assertAlmostEqual(ratio, 21.0, places=1)
        # Low contrast
        low_ratio = calculate_contrast_ratio("#777777", "#888888")
        self.assertLess(low_ratio, 4.5)

    def test_measure_hookscore(self):
        high_hook = "Stop wasting 10 hours a week on manual client onboarding. Here is the exact 3-step automation."
        score = measure_hookscore(high_hook)
        self.assertGreaterEqual(score, 75)

        weak_hook = "Hello everyone. Today in this video I would like to talk to you about some thoughts I had."
        weak_score = measure_hookscore(weak_hook)
        self.assertLess(weak_score, 60)

if __name__ == "__main__":
    unittest.main()
