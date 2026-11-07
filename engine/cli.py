import argparse
import sys
from pathlib import Path
import json

# Ensure engine.agents is imported to auto-register all 30 skills & 60 agents
import engine.agents
from engine.core.registry import AgentRegistry
from engine.core.runner import DualAgentRunner


# ANSI Color Codes
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def list_skills():
    skills = AgentRegistry.list_skills()
    print(f"\n{BOLD}{CYAN}=== Registered Skills ({len(skills)} Skills, {len(skills)*2} Agents) ==={RESET}\n")
    for i, skill in enumerate(skills, 1):
        gen, val = AgentRegistry.get_agents(skill)
        print(f"  {i:2d}. {BOLD}{skill}{RESET}")
        print(f"      • {GREEN}Generator:{RESET} {gen.role} ({gen.__class__.__name__})")
        print(f"      • {YELLOW}Validator:{RESET} {val.role} ({val.__class__.__name__})")
    print(f"\nTotal: {len(skills)} skills, {len(skills)*2} agents ready for 100% offline execution.\n")


def main():
    parser = argparse.ArgumentParser(
        description="AI_Flow Pure Python Autonomous Agent Runner (Zero API Keys, 100% Offline)"
    )
    parser.add_argument("--skill", type=str, help="Name of the skill to execute (e.g., prd-generator)")
    parser.add_argument("--input", type=str, default="", help="Input prompt or task description for the agent")
    parser.add_argument("--mode", choices=["single", "dual"], default="dual", help="Execution mode (single or dual)")
    parser.add_argument("--output", type=str, help="Optional output filepath or directory to save the artifact")
    parser.add_argument("--list", action="store_true", help="List all 30 skills and their 60 agent personas")
    parser.add_argument("--json", action="store_true", help="Output result as structured JSON to stdout")

    args = parser.parse_args()

    if args.list:
        list_skills()
        sys.exit(0)

    if not args.skill:
        parser.print_help()
        sys.exit(1)

    # Check skill exists
    available_skills = AgentRegistry.list_skills()
    if args.skill not in available_skills:
        print(f"\n{RED}Error: Skill '{args.skill}' not found in registry.{RESET}")
        print(f"Available skills ({len(available_skills)}): {', '.join(available_skills)}")
        sys.exit(1)

    runner = DualAgentRunner(max_refinements=2)

    # If input is a file path that exists, read its contents
    prompt_text = args.input
    if prompt_text and Path(prompt_text).is_file():
        try:
            prompt_text = Path(prompt_text).read_text(encoding="utf-8")
        except Exception:
            pass

    if not args.json:
        print(f"\n{BOLD}{CYAN}======================================================================{RESET}")
        print(f"{BOLD}{CYAN}  AI_FLOW AUTONOMOUS ENGINE (Pure Python, Zero API Keys){RESET}")
        print(f"{BOLD}{CYAN}======================================================================{RESET}")
        print(f"  • Skill: {BOLD}{args.skill}{RESET}")
        print(f"  • Mode:  {BOLD}{args.mode.upper()}{RESET}")
        print(f"  • Input: {prompt_text[:80]}...\n" if len(prompt_text) > 80 else f"  • Input: {prompt_text}\n")
        print(f"{CYAN}⚙️  Invoking Generator (Persona A)...{RESET}")

    result, scorecard = runner.run_skill(
        skill_name=args.skill,
        prompt=prompt_text,
        mode=args.mode
    )

    if not args.json:
        print(f"{GREEN}✓ Generation complete ({len(result.content)} bytes).{RESET}")

        if args.mode == "dual":
            print(f"\n{CYAN}🔍 Invoking Validator (Persona B) & Running AST Checks...{RESET}")
            if scorecard.passed:
                print(f"{GREEN}✓ Scorecard: {scorecard.score}/100 - PASSED (Iterations: {scorecard.iteration}){RESET}")
            else:
                print(f"{RED}✗ Scorecard: {scorecard.score}/100 - FAILED (Iterations: {scorecard.iteration}){RESET}")

            if scorecard.category_scores:
                cats = " | ".join(f"{k}: {v}" for k, v in scorecard.category_scores.items())
                print(f"  Categories: {cats}")

            if scorecard.blockers:
                print(f"\n{YELLOW}Blockers / Warnings:{RESET}")
                for b in scorecard.blockers:
                    print(f"  - [{b.rule_id}] {b.message}")

            print(f"\n{BOLD}Audit Verdict:{RESET} {scorecard.audit_summary}")
        else:
            print(f"{YELLOW}ℹ️  Single mode: validation skipped by user request.{RESET}")

        print(f"\n{BOLD}{CYAN}--- Artifact Preview ---{RESET}")
        preview_lines = result.content.strip().splitlines()
        for line in preview_lines[:25]:
            print(line)
        if len(preview_lines) > 25:
            print(f"... ({len(preview_lines) - 25} more lines)")
        print(f"{BOLD}{CYAN}------------------------{RESET}\n")

    # Save to output if requested
    if args.output:
        out_path = Path(args.output)
        if out_path.is_dir() or args.output.endswith(("/", "\\")):
            out_path.mkdir(parents=True, exist_ok=True)
            out_path = out_path / f"{args.skill}.md"
        else:
            out_path.parent.mkdir(parents=True, exist_ok=True)

        out_path.write_text(result.content, encoding="utf-8")
        if not args.json:
            print(f"{GREEN}💾 Saved deliverable to: {out_path}{RESET}")

    if args.json:
        payload = {
            "skill": args.skill,
            "mode": args.mode,
            "passed": scorecard.passed,
            "score": scorecard.score,
            "audit_summary": scorecard.audit_summary,
            "iteration": scorecard.iteration,
            "category_scores": scorecard.category_scores,
            "content": result.content,
        }
        print(json.dumps(payload, indent=2))

    sys.exit(0 if scorecard.passed else 1)


if __name__ == "__main__":
    main()
