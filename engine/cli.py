import argparse
import sys
from pathlib import Path
import json

# Ensure engine.agents is imported to auto-register all 30 skills & 60 agents
import engine.agents
from engine.core.registry import AgentRegistry
from engine.core.runner import DualAgentRunner
from engine.core.dispatcher import AgentDispatcher


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
    parser.add_argument("--skill", "-s", type=str, help="Name of the skill to execute (e.g., prd-generator)")
    parser.add_argument("--input", "-i", type=str, default="", help="Input prompt or task description for the agent")
    parser.add_argument("--mode", "-m", choices=["single", "dual"], default="dual", help="Execution mode (single or dual)")
    parser.add_argument("--provider", "-p", type=str, default="local", help="LLM inference provider (default: local)")
    parser.add_argument("--output", "-o", type=str, help="Optional output filepath or directory to save the artifact")
    parser.add_argument("--list", "-l", action="store_true", help="List all 30 skills and their 60 agent personas")
    parser.add_argument("--json", action="store_true", help="Output result as structured JSON to stdout")

    # Background task management arguments
    parser.add_argument("--background", "-bg", action="store_true", help="Dispatch task to run in the background without blocking")
    parser.add_argument("--status", type=str, metavar="TASK_ID", help="Check status of a background task")
    parser.add_argument("--list-tasks", action="store_true", help="List background tasks and their statuses")
    parser.add_argument("--logs", type=str, metavar="TASK_ID", help="View logs of a background task")
    parser.add_argument("--tail", type=int, default=50, help="Number of trailing log lines to view (default: 50)")
    parser.add_argument("--cancel", type=str, metavar="TASK_ID", help="Cancel a running background task")
    parser.add_argument("--prune-tasks", action="store_true", help="Prune historical tasks older than threshold days")
    parser.add_argument("--days", type=int, default=7, help="Threshold days for pruning tasks (default: 7)")

    args = parser.parse_args()

    if args.list:
        list_skills()
        sys.exit(0)

    # 1. Background Task Status
    if args.status:
        dispatcher = AgentDispatcher()
        record = dispatcher.get_status(args.status)
        if record is None:
            if args.json:
                print(json.dumps({"error": f"Task '{args.status}' not found", "task_id": args.status}, indent=2))
            else:
                print(f"\n{RED}Error: Task '{args.status}' not found.{RESET}\n")
            sys.exit(1)

        if args.json:
            print(json.dumps(record.to_dict(), indent=2))
        else:
            status_color = GREEN if record.status == "completed" else (YELLOW if record.status == "running" else RED)
            print(f"\n{BOLD}{CYAN}=== Background Task Status ==={RESET}")
            print(f"  • Task ID:       {BOLD}{record.task_id}{RESET}")
            print(f"  • Skill:         {record.skill_name}")
            print(f"  • Status:        {status_color}{record.status.upper()}{RESET}")
            print(f"  • Mode:          {record.mode}")
            print(f"  • Provider:      {record.provider}")
            print(f"  • PID:           {record.pid if record.pid else 'N/A'}")
            print(f"  • Started At:    {record.started_at or 'N/A'}")
            print(f"  • Completed At:  {record.completed_at or 'N/A'}")
            if record.score is not None:
                print(f"  • Score:         {record.score}/100 ({record.verdict or 'N/A'})")
            if record.exit_code is not None:
                print(f"  • Exit Code:     {record.exit_code}")
            if record.output_file:
                print(f"  • Output File:   {record.output_file}")
            if record.log_file:
                print(f"  • Log File:      {record.log_file}")
            if record.error_message:
                print(f"  • Error:         {RED}{record.error_message}{RESET}")
            print()
        sys.exit(0)

    # 2. List Background Tasks
    if args.list_tasks:
        dispatcher = AgentDispatcher()
        tasks = dispatcher.list_tasks()
        if args.json:
            print(json.dumps([t.to_dict() for t in tasks], indent=2))
        else:
            print(f"\n{BOLD}{CYAN}=== Background Tasks ({len(tasks)} Total) ==={RESET}\n")
            if not tasks:
                print("  No background tasks found.\n")
            else:
                header = f"  {'TASK ID':<24} {'SKILL':<26} {'STATUS':<12} {'PID':<8} {'SCORE':<7} {'STARTED AT':<20}"
                print(f"{BOLD}{header}{RESET}")
                print("  " + "─" * 100)
                for t in tasks:
                    st = t.status.upper()
                    st_color = GREEN if t.status == "completed" else (YELLOW if t.status == "running" else RED)
                    pid_str = str(t.pid) if t.pid else "-"
                    score_str = f"{t.score}/100" if t.score is not None else "-"
                    started_str = (t.started_at[:19] if t.started_at else "-")
                    line = f"  {t.task_id:<24} {t.skill_name:<26} {st_color}{st:<12}{RESET} {pid_str:<8} {score_str:<7} {started_str:<20}"
                    print(line)
                print()
        sys.exit(0)

    # 3. View Task Logs
    if args.logs:
        dispatcher = AgentDispatcher()
        logs = dispatcher.get_logs(args.logs, tail=args.tail)
        if args.json:
            print(json.dumps({"task_id": args.logs, "tail": args.tail, "logs": logs}, indent=2))
        else:
            if logs:
                print(logs, end="" if logs.endswith("\n") else "\n")
            else:
                print(f"(No logs found for task '{args.logs}')")
        sys.exit(0)

    # 4. Cancel Task
    if args.cancel:
        dispatcher = AgentDispatcher()
        record = dispatcher.task_manager.get_task(args.cancel)
        if record is None:
            if args.json:
                print(json.dumps({"task_id": args.cancel, "cancelled": False, "error": f"Task '{args.cancel}' not found"}, indent=2))
            else:
                print(f"\n{RED}Error: Task '{args.cancel}' not found.{RESET}\n")
            sys.exit(1)

        success = dispatcher.cancel_task(args.cancel)
        if args.json:
            print(json.dumps({"task_id": args.cancel, "cancelled": success, "status": "cancelled" if success else record.status}, indent=2))
        else:
            if success:
                print(f"\n{GREEN}✓ Task '{args.cancel}' cancelled successfully.{RESET}\n")
            else:
                print(f"\n{YELLOW}Notice: Task '{args.cancel}' could not be cancelled (already in {record.status} state).{RESET}\n")
        sys.exit(0)

    # 5. Prune Historical Tasks
    if args.prune_tasks:
        dispatcher = AgentDispatcher()
        pruned = dispatcher.prune_tasks(older_than_days=args.days)
        if args.json:
            print(json.dumps({"pruned_count": pruned, "older_than_days": args.days}, indent=2))
        else:
            print(f"\n{GREEN}✓ Pruned {pruned} task(s) older than {args.days} days.{RESET}\n")
        sys.exit(0)

    # 6. Background Dispatch
    if args.background:
        if not args.skill:
            if args.json:
                print(json.dumps({"error": "--skill is required for background execution"}, indent=2))
            else:
                print(f"\n{RED}Error: --skill is required for background execution.{RESET}\n")
            sys.exit(1)

        available_skills = AgentRegistry.list_skills()
        if args.skill not in available_skills:
            if args.json:
                print(json.dumps({"error": f"Skill '{args.skill}' not found in registry."}, indent=2))
            else:
                print(f"\n{RED}Error: Skill '{args.skill}' not found in registry.{RESET}")
                print(f"Available skills ({len(available_skills)}): {', '.join(available_skills)}")
            sys.exit(1)

        prompt_text = args.input or ""
        if prompt_text and Path(prompt_text).is_file():
            try:
                prompt_text = Path(prompt_text).read_text(encoding="utf-8")
            except Exception:
                pass

        dispatcher = AgentDispatcher()
        provider = getattr(args, "provider", "local") or "local"
        output_dir = args.output if args.output else None
        record = dispatcher.dispatch(
            skill_name=args.skill,
            input_text=prompt_text,
            mode=args.mode,
            provider=provider,
            output_dir=output_dir,
        )

        if args.json:
            print(json.dumps({
                "status": "dispatched",
                "task_id": record.task_id,
                "pid": record.pid,
                "skill": record.skill_name,
                "mode": record.mode,
                "provider": record.provider,
                "log_file": record.log_file,
            }, indent=2))
        else:
            print(f"\n{BOLD}{CYAN}======================================================================{RESET}")
            print(f"{BOLD}{CYAN}  AI_FLOW BACKGROUND AGENT DISPATCHED{RESET}")
            print(f"{BOLD}{CYAN}======================================================================{RESET}")
            print(f"  • Task ID:    {BOLD}{record.task_id}{RESET}")
            print(f"  • Worker PID: {record.pid if record.pid else 'N/A'}")
            print(f"  • Skill:      {BOLD}{record.skill_name}{RESET}")
            print(f"  • Mode:       {BOLD}{record.mode.upper()}{RESET}")
            print(f"  • Provider:   {record.provider}")
            if record.log_file:
                print(f"  • Log File:   {record.log_file}")
            print(f"\nCheck status:")
            print(f"  python -m engine.cli --status {record.task_id}")
            print(f"View logs:")
            print(f"  python -m engine.cli --logs {record.task_id}")
            print(f"{BOLD}{CYAN}======================================================================{RESET}\n")
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
