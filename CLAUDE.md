# CLAUDE.md - Instructions for Claude Code

## Project Context
This is **AI_Flow**, a repository providing standardized Agentic Skills for software development under the [Agent Skills specification](https://agentskills.io).

## Available Skills
The following skills are available in `skills/` and can be invoked based on the task:
- `prd-generator`: Initiating new products or features. Ask clarifying questions first.
- `uiux-design-brief`: Generating comprehensive UI/UX specifications, design tokens, and states.
- `system-architecture`: Designing system topologies, API contracts, database schemas, and caching.
- `task-to-skill`: Converting completed tasks into permanent, reusable Agent Skills.
- `playwright-e2e-testing`: End-to-end browser testing and Playwright configuration.
- `systematic-debugging`: 5-step root-cause debugging. Never modify code before empirical verification.
- `security-gap-audit`: Pre-launch application security review. Read-only audit before fixes.
- `dead-code-cleanup`: 2-phase dead code pruning (Audit & Stop -> Execute with approval).
- `rigorous-code-review`: Staff Engineer code review focusing on Blockers and failure scenarios.
- `clean-git-commits`: Conventional Commits organizing atomic changes.

## Development & Git Workflow
- Always format commits using Conventional Commits (`type(scope): summary`).
- When fixing errors or removing dead code, strictly obey the two-phase verification stop.

