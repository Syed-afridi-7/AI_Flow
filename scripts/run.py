#!/usr/bin/env python3
"""
AI_Flow Skill Runner — Standalone Auto-Writer
Run any AI_Flow skill against Gemini, ChatGPT, or Grok APIs and save the output directly to disk.

Usage:
  python run.py --skill prd-generator --input "A crypto portfolio tracker"
  python run.py --skill systematic-debugging --input "TypeError: Cannot read properties of undefined" --provider openai
  python run.py --skill system-architecture --input "Real-time chat app with WebSockets" --provider grok --output architecture_output.md

Setup:
  1. pip install requests python-dotenv
  2. Copy .env.example to .env and add your API key(s)
  3. Run: python run.py --skill <skill-name> --input "<your prompt>"
"""

import argparse
import json
import os
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

import requests

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
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
    "grok": {
        "env_key": "GROK_API_KEY",
        "name": "xAI Grok",
    },
}

# ---------------------------------------------------------------------------
# Skill loader
# ---------------------------------------------------------------------------
def list_skills() -> list[str]:
    """Return sorted list of available skill names."""
    if not SKILLS_DIR.exists():
        return []
    return sorted(d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and (d / "SKILL.md").exists())


def load_skill(name: str) -> str:
    """Read and return the full SKILL.md content for a given skill name."""
    skill_file = SKILLS_DIR / name / "SKILL.md"
    if not skill_file.exists():
        # Try fuzzy match
        available = list_skills()
        matches = [s for s in available if name.lower() in s.lower()]
        if len(matches) == 1:
            skill_file = SKILLS_DIR / matches[0] / "SKILL.md"
        else:
            print(f"\n❌ Skill '{name}' not found.\n")
            print("Available skills:")
            for s in available:
                print(f"  • {s}")
            sys.exit(1)
    return skill_file.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Provider API Callers
# ---------------------------------------------------------------------------
def call_gemini(system_prompt: str, user_prompt: str, api_key: str, model: str = "gemini-2.5-flash") -> str:
    """Call the Google Gemini API (v1beta generateContent)."""
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
    resp.raise_for_status()
    data = resp.json()

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        print(f"⚠️  Unexpected Gemini response:\n{json.dumps(data, indent=2)}")
        sys.exit(1)


def call_openai(system_prompt: str, user_prompt: str, api_key: str, model: str = "gpt-4o") -> str:
    """Call the OpenAI ChatCompletions API."""
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
    resp.raise_for_status()
    data = resp.json()

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        print(f"⚠️  Unexpected OpenAI response:\n{json.dumps(data, indent=2)}")
        sys.exit(1)


def call_grok(system_prompt: str, user_prompt: str, api_key: str, model: str = "grok-3-mini") -> str:
    """Call the xAI Grok API (OpenAI-compatible endpoint)."""
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
    resp.raise_for_status()
    data = resp.json()

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        print(f"⚠️  Unexpected Grok response:\n{json.dumps(data, indent=2)}")
        sys.exit(1)


CALLERS = {
    "gemini": call_gemini,
    "openai": call_openai,
    "grok": call_grok,
}


# ---------------------------------------------------------------------------
# Auto-detect available provider
# ---------------------------------------------------------------------------
def detect_provider() -> str:
    """Return the first provider that has an API key configured."""
    for name, cfg in PROVIDERS.items():
        if os.environ.get(cfg["env_key"]):
            return name
    print("\n❌ No API key found. Set one in your .env file:")
    print("   GEMINI_API_KEY=your-key-here")
    print("   OPENAI_API_KEY=your-key-here")
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
  python run.py --skill prd-generator --input "A fitness tracker app"
  python run.py --skill systematic-debugging --input "Error: ECONNREFUSED" --provider openai
  python run.py --skill system-architecture --input "Real-time chat" --provider grok
  python run.py --list
        """,
    )
    parser.add_argument("--skill", "-s", help="Name of the skill to run (e.g., prd-generator, systematic-debugging)")
    parser.add_argument("--input", "-i", help="Your prompt / input context for the skill")
    parser.add_argument("--provider", "-p", choices=list(PROVIDERS.keys()), help="AI provider (auto-detected from .env if omitted)")
    parser.add_argument("--model", "-m", help="Override the default model for the chosen provider")
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
            print(f"  • {s:<30} {desc_line[:80]}")
        print(f"\nUsage: python run.py --skill <name> --input \"<your prompt>\"")
        return

    # Validate required args
    if not args.skill:
        parser.error("--skill is required (or use --list to see available skills)")
    if not args.input:
        parser.error("--input is required")

    # Load skill
    skill_content = load_skill(args.skill)
    skill_name = args.skill

    # Resolve provider
    provider = args.provider or detect_provider()
    provider_cfg = PROVIDERS[provider]
    api_key = os.environ.get(provider_cfg["env_key"], "")
    if not api_key:
        print(f"\n❌ {provider_cfg['name']} API key not found.")
        print(f"   Set {provider_cfg['env_key']} in your .env file.")
        sys.exit(1)

    # Build prompts
    system_prompt = (
        "You are an expert AI coding assistant executing a specific engineering skill. "
        "Follow the skill instructions EXACTLY — including all phases, mandatory stops, "
        "numbered deliverables, and output formats defined below.\n\n"
        "=== SKILL INSTRUCTIONS ===\n\n"
        f"{skill_content}\n\n"
        "=== END SKILL INSTRUCTIONS ==="
    )
    user_prompt = args.input

    # Call API
    caller = CALLERS[provider]
    call_kwargs = {"system_prompt": system_prompt, "user_prompt": user_prompt, "api_key": api_key}
    if args.model:
        call_kwargs["model"] = args.model

    print(f"\n🚀 Running skill: {skill_name}")
    print(f"🤖 Provider: {provider_cfg['name']}")
    print(f"📝 Input: {user_prompt[:100]}{'...' if len(user_prompt) > 100 else ''}")
    print(f"⏳ Generating...\n")

    start = time.time()
    result = caller(**call_kwargs)
    elapsed = time.time() - start

    # Save output
    OUTPUT_DIR.mkdir(exist_ok=True)
    if args.output:
        out_path = Path(args.output)
    else:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        out_path = OUTPUT_DIR / f"{skill_name}_{timestamp}.md"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(result, encoding="utf-8")

    print(f"{'─' * 60}")
    print(result)
    print(f"{'─' * 60}")
    print(f"\n✅ Output saved to: {out_path}")
    print(f"⏱️  Generated in {elapsed:.1f}s using {provider_cfg['name']}")

    # Interactive follow-up mode
    if args.interactive:
        print(f"\n🔄 Interactive mode enabled. Type follow-up messages (type 'exit' to quit):\n")
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": result},
        ]
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

            # For interactive, we call OpenAI-style multi-turn (works for openai & grok)
            if provider == "gemini":
                # Gemini multi-turn
                gemini_contents = []
                for msg in messages:
                    if msg["role"] == "system":
                        continue
                    role = "user" if msg["role"] == "user" else "model"
                    gemini_contents.append({"role": role, "parts": [{"text": msg["content"]}]})

                url = f"https://generativelanguage.googleapis.com/v1beta/models/{args.model or 'gemini-2.5-flash'}:generateContent?key={api_key}"
                payload = {
                    "system_instruction": {"parts": [{"text": system_prompt}]},
                    "contents": gemini_contents,
                    "generationConfig": {"temperature": 0.7, "maxOutputTokens": 8192},
                }
                resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=120)
                resp.raise_for_status()
                reply = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            else:
                # OpenAI / Grok multi-turn
                base_url = "https://api.openai.com/v1" if provider == "openai" else "https://api.x.ai/v1"
                default_model = "gpt-4o" if provider == "openai" else "grok-3-mini"
                payload = {
                    "model": args.model or default_model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 8192,
                }
                headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
                resp = requests.post(f"{base_url}/chat/completions", json=payload, headers=headers, timeout=120)
                resp.raise_for_status()
                reply = resp.json()["choices"][0]["message"]["content"]

            messages.append({"role": "assistant", "content": reply})
            print(f"\nAssistant: {reply}\n")


if __name__ == "__main__":
    main()

