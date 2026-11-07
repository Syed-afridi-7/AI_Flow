#!/usr/bin/env python3
"""
Multi-CLI Installation & Manifest Verification Script for AI_Flow.

Programmatically verifies that all target directories, manifests, and skills
have been successfully installed and populated on the Windows filesystem across:
- Google Antigravity & Gemini IDE
- OpenAI Codex CLI
- xAI Grok CLI
- OpenCode Interpreter
- Anthropic Claude Code
- Open Agents Standard
- Cursor AI
"""

import sys
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REPO_SKILLS_DIR = REPO_ROOT / "skills"
AI_FLOW_SKILLS = sorted([d.name for d in REPO_SKILLS_DIR.iterdir() if d.is_dir() and (d / "SKILL.md").exists()])
EXPECTED_SKILLS_COUNT = len(AI_FLOW_SKILLS)

def get_home_dir() -> Path:
    return Path.home()

def main():
    home = get_home_dir()
    print("=" * 76)
    print("        AI_Flow Multi-CLI Target Filesystem Verification Audit")
    print("=" * 76)
    print(f"User Home Directory: {home}")
    print(f"Repository Root:     {REPO_ROOT}")
    print(f"AI_Flow Skills:      {EXPECTED_SKILLS_COUNT} distinct skills registered\n")

    results = []

    def check_skills_target(name: str, path: Path):
        exists = path.is_dir()
        if not exists:
            results.append((False, f"[FAIL] Directory missing: {name} -> {path}"))
            return

        missing = []
        for s in AI_FLOW_SKILLS:
            skill_folder = path / s
            skill_md = skill_folder / "SKILL.md"
            if not (skill_folder.is_dir() and skill_md.is_file()):
                missing.append(s)

        total_dirs = len([d for d in path.iterdir() if d.is_dir()])
        if not missing:
            results.append((True, f"[PASS] {name}: All {EXPECTED_SKILLS_COUNT}/{EXPECTED_SKILLS_COUNT} AI_Flow skills present ({total_dirs} total installed) at {path}"))
        else:
            results.append((False, f"[FAIL] {name}: Missing {len(missing)} AI_Flow skills ({missing}) at {path}"))

    def check_dir(name: str, path: Path):
        exists = path.is_dir()
        if not exists:
            results.append((False, f"[FAIL] Directory missing: {name} -> {path}"))
        else:
            results.append((True, f"[PASS] Directory verified: {name} -> {path}"))

    def check_file(name: str, path: Path, is_json: bool = False):
        exists = path.is_file()
        if not exists:
            results.append((False, f"[FAIL] File missing: {name} -> {path}"))
            return

        size = path.stat().st_size
        if size == 0:
            results.append((False, f"[FAIL] File is empty (0 bytes): {name} -> {path}"))
            return

        if is_json:
            try:
                with path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                results.append((True, f"[PASS] Valid JSON file: {name} ({size} bytes, name={data.get('name')}) -> {path}"))
            except Exception as e:
                results.append((False, f"[FAIL] Invalid JSON in {name}: {e} -> {path}"))
        else:
            results.append((True, f"[PASS] File verified: {name} ({size} bytes) -> {path}"))

    # 1. Antigravity & Gemini CLI
    print("[*] Target 1: Google Antigravity & Gemini IDE...")
    check_skills_target("Antigravity Skills (~/.gemini/antigravity/skills)", home / ".gemini" / "antigravity" / "skills")
    check_skills_target("Antigravity CLI Skills (~/.gemini/antigravity-cli/skills)", home / ".gemini" / "antigravity-cli" / "skills")
    check_dir("Antigravity Plugin Dir (~/.gemini/config/plugins/ai-flow)", home / ".gemini" / "config" / "plugins" / "ai-flow")
    check_skills_target("Antigravity Plugin Embedded Skills", home / ".gemini" / "config" / "plugins" / "ai-flow" / "skills")
    check_file("Antigravity gemini-extension.json", home / ".gemini" / "config" / "plugins" / "ai-flow" / "gemini-extension.json", is_json=True)
    check_file("Antigravity plugin.json", home / ".gemini" / "config" / "plugins" / "ai-flow" / "plugin.json", is_json=True)
    check_file("Antigravity GEMINI.md", home / ".gemini" / "config" / "plugins" / "ai-flow" / "GEMINI.md")

    # 2. OpenAI Codex CLI
    print("[*] Target 2: OpenAI Codex CLI...")
    check_skills_target("Codex Skills (~/.codex/skills)", home / ".codex" / "skills")
    check_dir("Codex Plugin Dir (~/.codex/plugins/ai-flow)", home / ".codex" / "plugins" / "ai-flow")
    check_skills_target("Codex Plugin Embedded Skills", home / ".codex" / "plugins" / "ai-flow" / "skills")
    check_file("Codex plugin.json", home / ".codex" / "plugins" / "ai-flow" / "plugin.json", is_json=True)
    check_file("Codex .codex-plugin/plugin.json", home / ".codex" / "plugins" / "ai-flow" / ".codex-plugin" / "plugin.json", is_json=True)

    # 3. xAI Grok CLI
    print("[*] Target 3: xAI Grok CLI...")
    check_dir("Grok Plugin Dir (~/.grok/installed-plugins/ai-flow)", home / ".grok" / "installed-plugins" / "ai-flow")
    check_skills_target("Grok Skills (~/.grok/installed-plugins/ai-flow/skills)", home / ".grok" / "installed-plugins" / "ai-flow" / "skills")
    check_file("Grok plugin.json", home / ".grok" / "installed-plugins" / "ai-flow" / "plugin.json", is_json=True)
    check_file("Grok AGENTS.md", home / ".grok" / "installed-plugins" / "ai-flow" / "AGENTS.md")

    # 4. OpenCode Interpreter
    print("[*] Target 4: OpenCode Interpreter...")
    check_skills_target("OpenCode Skills (~/.config/opencode/skills)", home / ".config" / "opencode" / "skills")
    check_file("OpenCode plugin script", home / ".config" / "opencode" / "plugins" / "ai-flow.js")

    # 5. Anthropic Claude Code
    print("[*] Target 5: Anthropic Claude Code...")
    check_skills_target("Claude Skills (~/.claude/skills)", home / ".claude" / "skills")

    # 6. Open Agents Standard
    print("[*] Target 6: Open Agents Standard...")
    check_skills_target("Agents Skills (~/.agents/skills)", home / ".agents" / "skills")

    # 7. Cursor AI
    print("[*] Target 7: Cursor AI...")
    check_skills_target("Cursor Skills (~/.cursor/skills)", home / ".cursor" / "skills")
    check_file("Cursor Rule MDC", home / ".cursor" / "rules" / "ai-flow.mdc")

    print("\n" + "-" * 76)
    print("AUDIT SUMMARY:")
    print("-" * 76)
    all_passed = True
    pass_count = 0
    fail_count = 0
    for passed, msg in results:
        print(msg)
        if passed:
            pass_count += 1
        else:
            all_passed = False
            fail_count += 1

    print("=" * 76)
    if all_passed:
        print(f"🎉 100% AUDIT PASS: All {pass_count}/{len(results)} filesystem checks verified successfully!")
        print("=" * 76)
        sys.exit(0)
    else:
        print(f"❌ AUDIT FAILED: {fail_count} checks failed, {pass_count} passed out of {len(results)}.")
        print("=" * 76)
        sys.exit(1)

if __name__ == "__main__":
    main()
