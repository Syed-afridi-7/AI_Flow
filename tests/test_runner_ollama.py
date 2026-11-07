import io
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import scripts.run as runner


class TestRunnerOllama(unittest.TestCase):
    """Unit tests for Ollama local provider support in scripts/run.py."""

    def setUp(self):
        self.original_env = os.environ.copy()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_provider_registration(self):
        """Verify ollama provider metadata and model defaults."""
        self.assertIn("ollama", runner.PROVIDERS)
        self.assertEqual(runner.PROVIDERS["ollama"]["env_key"], "OLLAMA_HOST")
        self.assertEqual(runner.PROVIDERS["ollama"]["name"], "Ollama Local LLM")

        self.assertEqual(runner.DEFAULT_SINGLE_MODELS["ollama"], "qwen2.5-coder:latest")
        self.assertEqual(runner.DEFAULT_FAST_MODELS["ollama"], "qwen2.5-coder:latest")
        self.assertEqual(runner.DEFAULT_REASONING_MODELS["ollama"], "qwen2.5-coder:latest")
        self.assertEqual(runner.CALLERS["ollama"], runner.call_ollama)

    @patch("urllib.request.urlopen")
    def test_call_ollama_success(self, mock_urlopen):
        """Test successful call to Ollama endpoint with correct payload and headers."""
        response_payload = {
            "model": "qwen2.5-coder:latest",
            "created_at": "2026-11-07T12:00:00Z",
            "response": "# Generated PRD Document\n\nFeatures...",
            "done": True,
        }
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(response_payload).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_resp.__exit__.return_value = False
        mock_urlopen.return_value = mock_resp

        result = runner.call_ollama(
            system_prompt="You are a system architect.",
            user_prompt="Draft payments schema",
            model="qwen2.5-coder:latest",
        )

        self.assertEqual(result, "# Generated PRD Document\n\nFeatures...")
        mock_urlopen.assert_called_once()

        # Inspect request
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.full_url, "http://localhost:11434/api/generate")
        self.assertEqual(req.headers["Content-type"], "application/json")
        self.assertEqual(req.get_method(), "POST")

        body = json.loads(req.data.decode("utf-8"))
        self.assertEqual(body["model"], "qwen2.5-coder:latest")
        self.assertEqual(body["system"], "You are a system architect.")
        self.assertEqual(body["prompt"], "Draft payments schema")
        self.assertFalse(body["stream"])
        self.assertEqual(body["options"]["temperature"], 0.7)

    @patch("urllib.request.urlopen")
    def test_call_ollama_custom_host_and_model(self, mock_urlopen):
        """Test call_ollama respects custom OLLAMA_HOST and model override."""
        os.environ["OLLAMA_HOST"] = "http://remote-server:11434/"

        response_payload = {"response": "Custom model output"}
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(response_payload).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        result = runner.call_ollama(
            system_prompt="Test sys",
            user_prompt="Test user",
            model="llama3.3:70b",
        )

        self.assertEqual(result, "Custom model output")
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.full_url, "http://remote-server:11434/api/generate")
        body = json.loads(req.data.decode("utf-8"))
        self.assertEqual(body["model"], "llama3.3:70b")

    @patch("urllib.request.urlopen")
    def test_call_ollama_http_error(self, mock_urlopen):
        """Test call_ollama handles HTTP error cleanly."""
        import urllib.error

        error_fp = io.BytesIO(b'{"error": "model \'missing-model\' not found"}')
        http_error = urllib.error.HTTPError(
            url="http://localhost:11434/api/generate",
            code=404,
            msg="Not Found",
            hdrs={},
            fp=error_fp,
        )
        mock_urlopen.side_effect = http_error

        with self.assertRaises(SystemExit) as cm:
            runner.call_ollama("Sys", "User", model="missing-model")
        self.assertEqual(cm.exception.code, 1)

    @patch("urllib.request.urlopen")
    def test_call_ollama_connection_error(self, mock_urlopen):
        """Test call_ollama handles connection refused / URLError cleanly."""
        import urllib.error

        url_error = urllib.error.URLError("Connection refused")
        mock_urlopen.side_effect = url_error

        with self.assertRaises(SystemExit) as cm:
            runner.call_ollama("Sys", "User")
        self.assertEqual(cm.exception.code, 1)

    def test_provider_auto_detection_with_ollama_host(self):
        """Test has_available_provider detects ollama when OLLAMA_HOST is set."""
        # Unset all other provider keys
        for cfg in runner.PROVIDERS.values():
            os.environ.pop(cfg["env_key"], None)

        self.assertIsNone(runner.has_available_provider())

        os.environ["OLLAMA_HOST"] = "http://localhost:11434"
        self.assertEqual(runner.has_available_provider(), "ollama")

    def test_run_main_with_ollama_provider_single_mode(self):
        """Test running scripts/run.py with --provider ollama --mode single."""
        mock_call_ollama = MagicMock(return_value="# Generated Document Content")

        test_args = [
            "run.py",
            "--skill", "prd-generator",
            "--input", "E-commerce platform",
            "--provider", "ollama",
            "--mode", "single",
        ]

        with patch.dict(runner.CALLERS, {"ollama": mock_call_ollama}):
            with patch("pathlib.Path.write_text") as mock_write:
                with patch.object(sys, "argv", test_args):
                    runner.main()

        mock_call_ollama.assert_called_once()
        mock_write.assert_called_once()
        call_kwargs = mock_call_ollama.call_args[1]
        self.assertEqual(call_kwargs["model"], "qwen2.5-coder:latest")
        self.assertEqual(call_kwargs["user_prompt"], "E-commerce platform")
        self.assertEqual(call_kwargs["api_key"], "local")

    def test_run_main_auto_switches_to_dual_when_provider_specified(self):
        """Test that if --provider is specified but --mode is left at default 'local', it switches to dual mode."""
        # Generator turn 1
        mock_draft = "# Initial Draft"
        # Validator turn 2 (PASS verdict JSON)
        mock_val = json.dumps({"score": 95, "verdict": "PASS", "blockers": [], "recommendations": []})
        mock_call_ollama = MagicMock(side_effect=[mock_draft, mock_val])

        test_args = [
            "run.py",
            "--skill", "prd-generator",
            "--input", "Crypto portfolio tracker",
            "--provider", "ollama",
            # Note: --mode is NOT specified, defaults to "local"
        ]

        with patch.dict(runner.CALLERS, {"ollama": mock_call_ollama}):
            with patch("pathlib.Path.write_text") as mock_write:
                with patch.object(sys, "argv", test_args):
                    runner.main()

        # In dual mode, generator (turn 1) and validator (turn 2) are called
        self.assertEqual(mock_call_ollama.call_count, 2)
        mock_write.assert_called_once()


if __name__ == "__main__":
    unittest.main()
