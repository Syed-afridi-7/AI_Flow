#!/usr/bin/env python3
"""
AI_Flow Skill Runner — Standalone Auto-Writer & Dual-Agent Autonomous Orchestrator
Run any AI_Flow skill against Gemini, ChatGPT, Claude, or Grok APIs and save the output directly to disk.
Supports both fast single-turn mode and autonomous dual-agent generation + validation loops.

Usage:
  # Fast single-turn mode
  python run.py --skill prd-generator --input "A crypto portfolio tracker"
  python run.py --skill systematic-debugging --input "TypeError: Cannot read properties of undefined" --provider openai

  # Autonomous dual-agent mode (Generator + Validator feedback loop)
  python run.py --skill accessibility-wcag-audit --input "Audit login form" --mode dual
  python run.py --skill api-contract-generator --input "Payments API" --mode dual --provider anthropic

Setup:
  1. pip install requests python-dotenv
  2. Copy .env.example to .env and add your API key(s)
  3. Run: python run.py --skill <skill-name> --input "<your prompt>"
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Load environment variables from .env
# ---------------------------------------------------------------------------
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional; user can set env vars directly

try:
    import requests
except ImportError:
    requests = None

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
SKILLS_DIR = REPO_ROOT / "skills"
OUTPUT_DIR = REPO_ROOT / "output"

PROVIDERS = {
    "gemini": {
        "env_key": "GEMINI_API_KEY",
        "name": "Google Gemini",
    },
    "openai": {
        "env_key": "OPENAI_API_KEY",
        "name": "OpenAI ChatGPT",
    },
    "anthropic": {
        "env_key": "ANTHROPIC_API_KEY",
        "name": "Anthropic Claude",
    },
    "grok": {
        "env_key": "GROK_API_KEY",
        "name": "xAI Grok",
    },
}

# Model tiering defaults
DEFAULT_SINGLE_MODELS = {
    "gemini": "gemini-2.5-flash",
    "openai": "gpt-4o",
    "anthropic": "claude-3-7-sonnet-latest",
    "grok": "grok-3-mini",
}

DEFAULT_FAST_MODELS = {
    "gemini": "gemini-2.5-flash",
    "anthropic": "claude-3-5-sonnet-latest",
    "openai": "gpt-4o-mini",
    "grok": "grok-3-mini",
}

DEFAULT_REASONING_MODELS = {
    "gemini": "gemini-2.5-pro",
    "anthropic": "claude-3-7-sonnet-latest",
    "openai": "gpt-4o",
    "grok": "grok-3-mini",
}


# ---------------------------------------------------------------------------
# Skill loader
# ---------------------------------------------------------------------------
def list_skills() -> list[str]:
    """Return sorted list of available skill names."""
    if not SKILLS_DIR.exists():
        return []
    return sorted(d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and (d / "SKILL.md").exists())


def resolve_skill_dir(name: str) -> Path:
    """Resolve skill directory by exact or fuzzy match."""
    skill_dir = SKILLS_DIR / name
    if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
        return skill_dir

    # Try fuzzy match
    available = list_skills()
    matches = [s for s in available if name.lower() in s.lower()]
    if len(matches) == 1:
        return SKILLS_DIR / matches[0]

    print(f"\n❌ Skill '{name}' not found.\n")
    print("Available skills:")
    for s in available:
        print(f"  • {s}")
    sys.exit(1)


def load_skill(name: str) -> str:
    """Read and return the full SKILL.md content for a given skill name."""
    skill_dir = resolve_skill_dir(name)
    skill_file = skill_dir / "SKILL.md"
    return skill_file.read_text(encoding="utf-8")


def get_dual_agent_files(skill_dir: Path) -> tuple[Path, Path] | None:
    """Return paths to (generator.md, validator.md) if both exist for the skill directory."""
    gen_file = skill_dir / "agents" / "generator.md"
    val_file = skill_dir / "agents" / "validator.md"
    if gen_file.exists() and val_file.exists():
        return gen_file, val_file
    return None


# ---------------------------------------------------------------------------
# Validation JSON Parser (Robust Extraction)
# ---------------------------------------------------------------------------
def extract_json_from_response(raw_text: str) -> dict:
    """Robustly parse JSON evaluation object from validator response."""
    text = raw_text.strip()

    # 1. Try stripping markdown code fences if wrapped in ```json ... ``` or ``` ... ```
    if "```" in text:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if match:
            candidate = match.group(1).strip()
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                pass

    # 2. Try direct json.loads
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    # 3. Find outermost { and }
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace > first_brace:
        snippet = text[first_brace : last_brace + 1]
        try:
            parsed = json.loads(snippet)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass

    # 4. Fallback regex extraction
    score_match = re.search(r'["\']?score["\']?\s*[:=]\s*(\d+)', text, re.IGNORECASE)
    score = int(score_match.group(1)) if score_match else 85

    verdict_match = re.search(r'["\']?verdict["\']?\s*[:=]\s*["\']?(PASS|REVISE)["\']?', text, re.IGNORECASE)
    verdict = verdict_match.group(1).upper() if verdict_match else ("PASS" if score >= 85 else "REVISE")

    blockers = []
    blockers_match = re.search(r'["\']?blockers["\']?\s*[:=]\s*\[([\s\S]*?)\]', text, re.IGNORECASE)
    if blockers_match:
        items = re.findall(r'["\']([^"\']+)["\']', blockers_match.group(1))
        blockers = [item.strip() for item in items if item.strip()]

    recs = []
    recs_match = re.search(r'["\']?recommendations["\']?\s*[:=]\s*\[([\s\S]*?)\]', text, re.IGNORECASE)
    if recs_match:
        items = re.findall(r'["\']([^"\']+)["\']', recs_match.group(1))
        recs = [item.strip() for item in items if item.strip()]

    return {
        "score": score,
        "verdict": verdict,
        "blockers": blockers,
        "recommendations": recs,
    }


# ---------------------------------------------------------------------------
# Provider API Callers
# ---------------------------------------------------------------------------
def _ensure_requests() -> None:
    """Ensure requests library is installed when calling cloud APIs."""
    if requests is None:
        print("\n❌ The 'requests' library is required for cloud API execution.")
        print("   Install it via: pip install requests")
        print("   Or run in 100% offline local mode without any third-party packages: python run.py --mode local")
        sys.exit(1)


def call_gemini(system_prompt: str, user_prompt: str, api_key: str, model: str = "gemini-2.5-flash") -> str:
    """Call the Google Gemini API (v1beta generateContent)."""
    _ensure_requests()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "system_instruction": {
            "parts": [{"text": system_prompt}]
        },
        "contents": [
            {"role": "user", "parts": [{"text": user_prompt}]}
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 8192,
        },
    }
    headers = {"Content-Type": "application/json"}

    resp = requests.post(url, json=payload, headers=headers, timeout=120)
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ Gemini API Error: {e}")
        try:
            print(f"Details: {resp.text}")
        except Exception:
            pass
        sys.exit(1)

    data = resp.json()

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        print(f"⚠️  Unexpected Gemini response:\n{json.dumps(data, indent=2)}")
        sys.exit(1)


def call_openai(system_prompt: str, user_prompt: str, api_key: str, model: str = "gpt-4o") -> str:
    """Call the OpenAI ChatCompletions API."""
    _ensure_requests()
    url = "https://api.openai.com/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 8192,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=120)
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ OpenAI API Error: {e}")
        try:
            print(f"Details: {resp.text}")
        except Exception:
            pass
        sys.exit(1)

    data = resp.json()

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        print(f"⚠️  Unexpected OpenAI response:\n{json.dumps(data, indent=2)}")
        sys.exit(1)


def call_anthropic(system_prompt: str, user_prompt: str, api_key: str, model: str = "claude-3-7-sonnet-latest") -> str:
    """Call the Anthropic Claude Messages API."""
    _ensure_requests()
    url = "https://api.anthropic.com/v1/messages"
    payload = {
        "model": model,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 8192,
    }
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=120)
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ Anthropic API Error: {e}")
        try:
            print(f"Details: {resp.text}")
        except Exception:
            pass
        sys.exit(1)

    data = resp.json()

    try:
        return data["content"][0]["text"]
    except (KeyError, IndexError):
        print(f"⚠️  Unexpected Anthropic response:\n{json.dumps(data, indent=2)}")
        sys.exit(1)


def call_grok(system_prompt: str, user_prompt: str, api_key: str, model: str = "grok-3-mini") -> str:
    """Call the xAI Grok API (OpenAI-compatible endpoint)."""
    _ensure_requests()
    url = "https://api.x.ai/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 8192,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=120)
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ Grok API Error: {e}")
        try:
            print(f"Details: {resp.text}")
        except Exception:
            pass
        sys.exit(1)

    data = resp.json()

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        print(f"⚠️  Unexpected Grok response:\n{json.dumps(data, indent=2)}")
        sys.exit(1)


CALLERS = {
    "gemini": call_gemini,
    "openai": call_openai,
    "anthropic": call_anthropic,
    "grok": call_grok,
}


# ---------------------------------------------------------------------------
# Auto-detect available provider
# ---------------------------------------------------------------------------
def has_available_provider() -> str | None:
    """Return the first provider that has an API key configured, or None."""
    for name, cfg in PROVIDERS.items():
        if os.environ.get(cfg["env_key"]):
            return name
    return None


def detect_provider() -> str:
    """Return the first provider that has an API key configured."""
    prov = has_available_provider()
    if prov:
        return prov
    print("\n❌ No API key found. Set one in your .env file:")
    print("   GEMINI_API_KEY=your-key-here")
    print("   OPENAI_API_KEY=your-key-here")
    print("   ANTHROPIC_API_KEY=your-key-here")
    print("   GROK_API_KEY=your-key-here")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="AI_Flow Skill Runner — Generate engineering documents using AI skills.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fast single-turn execution
  python run.py --skill prd-generator --input "A fitness tracker app"
  python run.py --skill systematic-debugging --input "Error: ECONNREFUSED" --provider openai

  # Autonomous dual-agent loop (Generator + Validator self-correction)
  python run.py --skill accessibility-wcag-audit --input "Audit login modal" --mode dual
  python run.py --skill api-contract-generator --input "Payments API" --mode dual --provider anthropic

  # List all available skills
  python run.py --list
        """,
    )
    parser.add_argument("--skill", "-s", help="Name of the skill to run (e.g., prd-generator, systematic-debugging)")
    parser.add_argument("--input", "-i", help="Your prompt / input context for the skill")
    parser.add_argument("--provider", "-p", choices=list(PROVIDERS.keys()), help="AI provider (auto-detected from .env if omitted)")
    parser.add_argument(
        "--mode",
        choices=["single", "dual", "local"],
        default="local",
        help="Execution mode: local (pure Python engine, zero API keys), single (cloud 1-turn), or dual (cloud peer review)",
    )
    parser.add_argument("--model", "-m", help="Override the default model for single mode, or apply to both agents in dual mode")
    parser.add_argument(
        "--model-generator",
        help="Override model for the Generator agent (defaults to fast tier: gemini-2.5-flash or gpt-4o-mini)",
    )
    parser.add_argument(
        "--model-validator",
        help="Override model for the Validator agent (defaults to reasoning tier: claude-3-7-sonnet or gemini-2.5-pro)",
    )
    parser.add_argument("--output", "-o", help="Output file path (defaults to output/<skill-name>_<timestamp>.md)")
    parser.add_argument("--list", "-l", action="store_true", help="List all available skills and exit")
    parser.add_argument("--interactive", action="store_true", help="Enter interactive multi-turn mode (for skills with approval stops)")

    args = parser.parse_args()

    # List mode
    if args.list:
        skills = list_skills()
        print(f"\n📂 Available AI_Flow Skills ({len(skills)}):\n")
        for s in skills:
            skill_text = (SKILLS_DIR / s / "SKILL.md").read_text(encoding="utf-8")
            desc_line = ""
            for line in skill_text.splitlines():
                if line.startswith("description:"):
                    desc_line = line.replace("description:", "").strip()
                    break
            badge = ""
            if (SKILLS_DIR / s / "agents" / "generator.md").exists() and (SKILLS_DIR / s / "agents" / "validator.md").exists():
                badge = "[dual]"
            print(f"  • {s:<32} {badge:<8} {desc_line[:65]}")
        print(f"\nUsage: python run.py --skill <name> --input \"<your prompt>\" [--mode dual]")
        return

    # Validate required args
    if not args.skill:
        parser.error("--skill is required (or use --list to see available skills)")
    if not args.input:
        parser.error("--input is required")

    # Resolve skill
    skill_dir = resolve_skill_dir(args.skill)
    skill_name = skill_dir.name
    skill_content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")

    # -----------------------------------------------------------------------
    # Local Offline Mode (Pure Python Engine, Zero API Keys)
    # Activates automatically if mode is 'local' or if no cloud API keys exist.
    # -----------------------------------------------------------------------
    active_cloud_provider = args.provider or has_available_provider()
    if args.mode == "local" or not active_cloud_provider:
        if args.mode != "local" and not active_cloud_provider:
            print(f"\nℹ️  No cloud API key found. Executing skill in 100% OFFLINE LOCAL mode with pure Python dual-agent engine.")
        try:
            import engine.agents
            from engine.core.runner import DualAgentRunner
        except ImportError as e:
            print(f"\n❌ Error loading pure Python engine: {e}")
            sys.exit(1)

        runner = DualAgentRunner(max_refinements=2)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        print(f"\n🚀 Running skill in 100% OFFLINE LOCAL mode: {skill_name}")
        print(f"⚡ Pure Python Dual-Agent Engine (Zero Cloud APIs / Zero Keys)")
        print(f"📝 Input: {args.input[:100]}{'...' if len(args.input) > 100 else ''}\n")

        result, scorecard = runner.run_skill(
            skill_name=skill_name,
            prompt=args.input,
            mode="dual"
        )

        out_path = Path(args.output) if args.output else OUTPUT_DIR / f"{skill_name}_{timestamp}.md"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(result.content, encoding="utf-8")

        print(f"{'─' * 60}")
        print(result.content)
        print(f"{'─' * 60}")
        print(f"\n✅ Output saved to: {out_path}")
        print(f"📊 Scorecard: {scorecard.score}/100 ({'PASSED' if scorecard.passed else 'FAILED'}) - Iterations: {scorecard.iteration}")
        if scorecard.audit_summary:
            print(f"🔍 Verdict: {scorecard.audit_summary}")
        return

    # Resolve provider
    provider = args.provider or detect_provider()
    provider_cfg = PROVIDERS[provider]
    api_key = os.environ.get(provider_cfg["env_key"], "")
    if not api_key:
        print(f"\n❌ {provider_cfg['name']} API key not found.")
        print(f"   Set {provider_cfg['env_key']} in your .env file.")
        sys.exit(1)

    caller = CALLERS[provider]
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------------------------------------
    # Dual-Agent Mode Execution
    # -----------------------------------------------------------------------
    mode = args.mode
    dual_files = get_dual_agent_files(skill_dir)

    if mode == "dual" and not dual_files:
        print(f"\n⚠️  Dual-agent definitions not found for '{skill_name}'.")
        print(f"   (Looked for skills/{skill_name}/agents/generator.md and validator.md)")
        print(f"ℹ️  Falling back gracefully to single-agent mode.\n")
        mode = "single"

    if mode == "dual":
        gen_file, val_file = dual_files
        # Static system prompts for KV prompt caching optimization
        gen_system = gen_file.read_text(encoding="utf-8")
        val_system = val_file.read_text(encoding="utf-8")

        # Resolve tier models
        gen_model = args.model_generator or args.model or DEFAULT_FAST_MODELS.get(provider, "gemini-2.5-flash")
        val_model = args.model_validator or args.model or DEFAULT_REASONING_MODELS.get(provider, "gemini-2.5-pro")

        print(f"\n🚀 Running skill in DUAL-AGENT mode: {skill_name}")
        print(f"🤖 Provider: {provider_cfg['name']}")
        print(f"⚡ Generator model: {gen_model} | 🧠 Validator model: {val_model}")
        print(f"📝 Input: {args.input[:100]}{'...' if len(args.input) > 100 else ''}\n")

        start_total = time.time()

        # Turn 1: Initial Generation
        draft_1 = caller(system_prompt=gen_system, user_prompt=args.input, api_key=api_key, model=gen_model)
        print("🤖 [Turn 1/3] Generator drafted initial artifact...")

        # Turn 2: Validation Audit
        turn2_prompt = (
            f"Evaluate the following draft artifact generated for the user prompt:\n\n"
            f"=== USER PROMPT ===\n{args.input}\n\n"
            f"=== GENERATED DRAFT ===\n{draft_1}\n\n"
            f"Provide your evaluation strictly as a valid JSON object matching the rubric in your system instructions."
        )
        val_resp = caller(system_prompt=val_system, user_prompt=turn2_prompt, api_key=api_key, model=val_model)
        eval_data = extract_json_from_response(val_resp)

        score_val = eval_data.get("score", 85)
        try:
            score = int(round(float(score_val)))
        except (ValueError, TypeError):
            score = 85

        verdict = str(eval_data.get("verdict", "PASS" if score >= 85 else "REVISE")).strip().upper()
        if verdict not in ("PASS", "REVISE"):
            verdict = "PASS" if score >= 85 else "REVISE"

        blockers = eval_data.get("blockers", [])
        if isinstance(blockers, str):
            blockers = [blockers]
        elif not isinstance(blockers, list):
            blockers = []

        recommendations = eval_data.get("recommendations", [])
        if isinstance(recommendations, str):
            recommendations = [recommendations]
        elif not isinstance(recommendations, list):
            recommendations = []

        print(f"🔍 [Turn 2/3] Validator audited draft. Score: {score}/100 | Verdict: {verdict}")

        # Turn 3: Self-Correction if REVISE
        if verdict == "REVISE" and score < 85:
            print("🛠️ [Turn 3/3] Self-correcting draft based on validator blockers...")
            turn3_prompt = (
                f"=== ORIGINAL USER PROMPT ===\n{args.input}\n\n"
                f"=== DRAFT 1 ===\n{draft_1}\n\n"
                f"=== VALIDATOR BLOCKERS & FEEDBACK ===\n"
                f"Score: {score}/100\n"
                f"Blockers: {json.dumps(blockers, indent=2)}\n"
                f"Recommendations: {json.dumps(recommendations, indent=2)}\n\n"
                f"Please revise and generate the final, corrected artifact addressing all blockers."
            )
            final_artifact = caller(system_prompt=gen_system, user_prompt=turn3_prompt, api_key=api_key, model=gen_model)
        else:
            final_artifact = draft_1

        elapsed = time.time() - start_total

        # Prepare Audit Scorecard
        notes_list = []
        if recommendations:
            notes_list.extend([str(r) for r in recommendations])
        elif blockers:
            notes_list.extend([str(b) for b in blockers])

        if notes_list:
            notes_str = "; ".join(notes_list)
        else:
            notes_str = "All criteria evaluated and verified compliant."

        scorecard = (
            f"---\n"
            f"## 🛡️ Autonomous Dual-Agent Audit Scorecard\n"
            f"- **Quality Score:** {score}/100\n"
            f"- **Verdict:** {verdict}\n"
            f"- **Generator Model:** {gen_model}\n"
            f"- **Validator Model:** {val_model}\n"
            f"- **Auditor Notes:** {notes_str}\n"
        )

        result = f"{final_artifact.rstrip()}\n\n{scorecard}"

        # Determine output path
        if args.output:
            out_path = Path(args.output)
        else:
            out_path = OUTPUT_DIR / f"{skill_name}_dual_{timestamp}.md"

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(result, encoding="utf-8")

        print(f"{'─' * 60}")
        print(result)
        print(f"{'─' * 60}")
        print(f"\n✅ Output saved to: {out_path}")
        print(f"⏱️  Autonomous dual-agent loop completed in {elapsed:.1f}s ({provider_cfg['name']})")

        active_system_prompt = gen_system
        last_response = final_artifact

    # -----------------------------------------------------------------------
    # Single-Agent Mode Execution
    # -----------------------------------------------------------------------
    else:
        single_model = args.model or DEFAULT_SINGLE_MODELS.get(provider, "gemini-2.5-flash")

        system_prompt = (
            "You are an expert AI coding assistant executing a specific engineering skill. "
            "Follow the skill instructions EXACTLY — including all phases, mandatory stops, "
            "numbered deliverables, and output formats defined below.\n\n"
            "=== SKILL INSTRUCTIONS ===\n\n"
            f"{skill_content}\n\n"
            "=== END SKILL INSTRUCTIONS ==="
        )
        user_prompt = args.input

        print(f"\n🚀 Running skill in SINGLE mode: {skill_name}")
        print(f"🤖 Provider: {provider_cfg['name']} ({single_model})")
        print(f"📝 Input: {user_prompt[:100]}{'...' if len(user_prompt) > 100 else ''}")
        print(f"⏳ Generating...\n")

        start = time.time()
        result = caller(system_prompt=system_prompt, user_prompt=user_prompt, api_key=api_key, model=single_model)
        elapsed = time.time() - start

        if args.output:
            out_path = Path(args.output)
        else:
            out_path = OUTPUT_DIR / f"{skill_name}_{timestamp}.md"

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(result, encoding="utf-8")

        print(f"{'─' * 60}")
        print(result)
        print(f"{'─' * 60}")
        print(f"\n✅ Output saved to: {out_path}")
        print(f"⏱️  Generated in {elapsed:.1f}s using {provider_cfg['name']} ({single_model})")

        active_system_prompt = system_prompt
        last_response = result

    # -----------------------------------------------------------------------
    # Interactive Follow-up Mode
    # -----------------------------------------------------------------------
    if args.interactive:
        print(f"\n🔄 Interactive mode enabled. Type follow-up messages (type 'exit' to quit):\n")
        messages = [
            {"role": "system", "content": active_system_prompt},
            {"role": "user", "content": args.input},
            {"role": "assistant", "content": last_response},
        ]
        interactive_model = args.model or (gen_model if args.mode == "dual" else single_model)

        while True:
            try:
                follow_up = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if follow_up.lower() in ("exit", "quit", "q"):
                break
            if not follow_up:
                continue

            messages.append({"role": "user", "content": follow_up})

            # Multi-turn API dispatch
            if provider == "gemini":
                gemini_contents = []
                for msg in messages:
                    if msg["role"] == "system":
                        continue
                    role = "user" if msg["role"] == "user" else "model"
                    gemini_contents.append({"role": role, "parts": [{"text": msg["content"]}]})

                url = f"https://generativelanguage.googleapis.com/v1beta/models/{interactive_model}:generateContent?key={api_key}"
                payload = {
                    "system_instruction": {"parts": [{"text": active_system_prompt}]},
                    "contents": gemini_contents,
                    "generationConfig": {"temperature": 0.7, "maxOutputTokens": 8192},
                }
                resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=120)
                try:
                    resp.raise_for_status()
                except requests.exceptions.HTTPError as e:
                    print(f"\n❌ Gemini API Error: {e}")
                    break
                reply = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            elif provider == "anthropic":
                anthropic_messages = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in messages
                    if msg["role"] in ("user", "assistant")
                ]
                url = "https://api.anthropic.com/v1/messages"
                payload = {
                    "model": interactive_model,
                    "system": active_system_prompt,
                    "messages": anthropic_messages,
                    "temperature": 0.7,
                    "max_tokens": 8192,
                }
                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                }
                resp = requests.post(url, json=payload, headers=headers, timeout=120)
                try:
                    resp.raise_for_status()
                except requests.exceptions.HTTPError as e:
                    print(f"\n❌ Anthropic API Error: {e}")
                    break
                reply = resp.json()["content"][0]["text"]
            else:
                base_url = "https://api.openai.com/v1" if provider == "openai" else "https://api.x.ai/v1"
                payload = {
                    "model": interactive_model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 8192,
                }
                headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
                resp = requests.post(f"{base_url}/chat/completions", json=payload, headers=headers, timeout=120)
                try:
                    resp.raise_for_status()
                except requests.exceptions.HTTPError as e:
                    print(f"\n❌ API Error: {e}")
                    break
                reply = resp.json()["choices"][0]["message"]["content"]

            messages.append({"role": "assistant", "content": reply})
            print(f"\nAssistant: {reply}\n")


if __name__ == "__main__":
    main()
