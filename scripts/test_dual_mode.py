import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import run

def test_json_extraction():
    # Case 1: Markdown code fences
    case1 = '```json\n{"score": 92, "verdict": "PASS", "blockers": [], "recommendations": ["Tip 1"]}\n```'
    res1 = run.extract_json_from_response(case1)
    assert res1["score"] == 92, f"Expected 92, got {res1['score']}"
    assert res1["verdict"] == "PASS", f"Expected PASS, got {res1['verdict']}"
    assert res1["recommendations"] == ["Tip 1"], f"Unexpected recommendations: {res1['recommendations']}"

    # Case 2: Free text with embedded JSON
    case2 = 'Here is the audit:\n{"score": 72, "verdict": "REVISE", "blockers": ["Blocker 1"], "recommendations": []}'
    res2 = run.extract_json_from_response(case2)
    assert res2["score"] == 72, f"Expected 72, got {res2['score']}"
    assert res2["verdict"] == "REVISE", f"Expected REVISE, got {res2['verdict']}"
    assert res2["blockers"] == ["Blocker 1"], f"Unexpected blockers: {res2['blockers']}"

    # Case 3: Regex fallback
    case3 = 'Score: 65\nVerdict: REVISE\nBlockers: ["Error in form"]\nRecommendations: ["Fix it"]'
    res3 = run.extract_json_from_response(case3)
    assert res3["score"] == 65, f"Expected 65, got {res3['score']}"
    assert res3["verdict"] == "REVISE", f"Expected REVISE, got {res3['verdict']}"
    assert res3["blockers"] == ["Error in form"], f"Unexpected blockers: {res3['blockers']}"

    print("✅ All JSON extraction tests passed!")

def test_dual_agent_resolution():
    dual_dir = run.SKILLS_DIR / "accessibility-wcag-audit"
    non_dual_dir = run.REPO_ROOT / "scripts"

    assert run.get_dual_agent_files(dual_dir) is not None, "Expected dual agents for accessibility-wcag-audit"
    assert run.get_dual_agent_files(non_dual_dir) is None, "Expected no dual agents for scripts directory"

    print("✅ Dual agent file resolution tests passed!")

def test_model_defaults():
    assert run.DEFAULT_FAST_MODELS["gemini"] == "gemini-2.5-flash"
    assert run.DEFAULT_FAST_MODELS["anthropic"] == "claude-3-5-sonnet-latest"
    assert run.DEFAULT_FAST_MODELS["openai"] == "gpt-4o-mini"
    assert run.DEFAULT_FAST_MODELS["grok"] == "grok-3-mini"

    assert run.DEFAULT_REASONING_MODELS["gemini"] == "gemini-2.5-pro"
    assert run.DEFAULT_REASONING_MODELS["anthropic"] == "claude-3-7-sonnet-latest"
    assert run.DEFAULT_REASONING_MODELS["openai"] == "gpt-4o"
    assert run.DEFAULT_REASONING_MODELS["grok"] == "grok-3-mini"

    print("✅ Model tier defaults verified!")

def test_mock_dual_run_pass():
    """Test Turn 1 + Turn 2 with PASS verdict (no Turn 3 needed)."""
    mock_draft = "# Initial Accessibility Audit Draft\n\nAll tests pass."
    mock_val_json = json.dumps({
        "score": 95,
        "verdict": "PASS",
        "blockers": [],
        "recommendations": ["Ensure high contrast on dark mode"]
    })

    call_count = 0
    def mock_caller(system_prompt, user_prompt, api_key, model):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            # Turn 1 Generator
            assert "A11y Remediation Engineer" in system_prompt or "Generator Agent" in system_prompt
            assert model == "gemini-2.5-flash"
            return mock_draft
        elif call_count == 2:
            # Turn 2 Validator
            assert "Validator Agent" in system_prompt or "Compliance Auditor" in system_prompt
            assert "=== GENERATED DRAFT ===" in user_prompt
            assert model == "gemini-2.5-pro"
            return mock_val_json
        raise RuntimeError("Turn 3 should not be called on PASS with score >= 85")

    out_file = Path(tempfile.gettempdir()) / "test_dual_pass.md"

    with patch.dict(run.CALLERS, {"mock_prov": mock_caller}), \
         patch.dict(run.PROVIDERS, {"mock_prov": {"env_key": "MOCK_KEY", "name": "Mock Provider"}}), \
         patch.dict(run.os.environ, {"MOCK_KEY": "fake-key"}):
        
        test_args = [
            "run.py",
            "--skill", "accessibility-wcag-audit",
            "--input", "Audit navbar",
            "--mode", "dual",
            "--provider", "mock_prov",
            "--output", str(out_file)
        ]
        with patch.object(sys, "argv", test_args):
            run.main()

    assert out_file.exists(), "Output file was not created"
    content = out_file.read_text(encoding="utf-8")
    assert "Autonomous Dual-Agent Audit Scorecard" in content
    assert "Quality Score:** 95/100" in content
    assert "Verdict:** PASS" in content
    assert "Ensure high contrast on dark mode" in content
    out_file.unlink() # Cleanup
    print("✅ Mock dual run (PASS) verified!")

def test_mock_dual_run_revise():
    """Test Turn 1 + Turn 2 (REVISE) + Turn 3 Self-Correction."""
    mock_draft_1 = "# Draft 1\n\nIncomplete audit."
    mock_val_json = json.dumps({
        "score": 70,
        "verdict": "REVISE",
        "blockers": ["Missing keyboard trap checks"],
        "recommendations": ["Add Escape handler"]
    })
    mock_draft_final = "# Final Corrected Audit\n\nAdded Escape handler."

    call_count = 0
    def mock_caller(system_prompt, user_prompt, api_key, model):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return mock_draft_1
        elif call_count == 2:
            return mock_val_json
        elif call_count == 3:
            # Turn 3 Self-Correction
            assert "=== VALIDATOR BLOCKERS & FEEDBACK ===" in user_prompt
            assert "Missing keyboard trap checks" in user_prompt
            return mock_draft_final
        raise RuntimeError(f"Unexpected call {call_count}")

    out_file = Path(tempfile.gettempdir()) / "test_dual_revise.md"

    with patch.dict(run.CALLERS, {"mock_prov": mock_caller}), \
         patch.dict(run.PROVIDERS, {"mock_prov": {"env_key": "MOCK_KEY", "name": "Mock Provider"}}), \
         patch.dict(run.os.environ, {"MOCK_KEY": "fake-key"}):

        test_args = [
            "run.py",
            "--skill", "accessibility-wcag-audit",
            "--input", "Audit modal dialog",
            "--mode", "dual",
            "--provider", "mock_prov",
            "--output", str(out_file)
        ]
        with patch.object(sys, "argv", test_args):
            run.main()

    assert call_count == 3, f"Expected 3 calls, got {call_count}"
    assert out_file.exists(), "Output file was not created"
    content = out_file.read_text(encoding="utf-8")
    assert "Final Corrected Audit" in content
    assert "Autonomous Dual-Agent Audit Scorecard" in content
    assert "Quality Score:** 70/100" in content
    assert "Verdict:** REVISE" in content
    out_file.unlink() # Cleanup
    print("✅ Mock dual run (REVISE + Turn 3 self-correction) verified!")

def test_mock_fallback_to_single():
    """Test fallback when dual mode requested for skill without agents."""
    mock_single_output = "# Clean Commits Output\n\nSingle turn result."
    call_count = 0
    def mock_caller(system_prompt, user_prompt, api_key, model):
        nonlocal call_count
        call_count += 1
        return mock_single_output

    out_file = Path(tempfile.gettempdir()) / "test_fallback.md"

    with patch.dict(run.CALLERS, {"mock_prov": mock_caller}), \
         patch.dict(run.PROVIDERS, {"mock_prov": {"env_key": "MOCK_KEY", "name": "Mock Provider"}}), \
         patch.dict(run.os.environ, {"MOCK_KEY": "fake-key"}), \
         patch("run.get_dual_agent_files", return_value=None):

        test_args = [
            "run.py",
            "--skill", "clean-git-commits",
            "--input", "Format commit message",
            "--mode", "dual",
            "--provider", "mock_prov",
            "--output", str(out_file)
        ]
        with patch.object(sys, "argv", test_args):
            run.main()

    assert call_count == 1, f"Expected 1 call due to fallback, got {call_count}"
    assert out_file.exists(), "Fallback output file was not created"
    content = out_file.read_text(encoding="utf-8")
    assert "Clean Commits Output" in content
    out_file.unlink() # Cleanup
    print("✅ Fallback to single mode verified!")

if __name__ == "__main__":
    test_json_extraction()
    test_dual_agent_resolution()
    test_model_defaults()
    test_mock_dual_run_pass()
    test_mock_dual_run_revise()
    test_mock_fallback_to_single()
    print("\n🎉 ALL TESTS PASSED WITH 100% SUCCESS!")
