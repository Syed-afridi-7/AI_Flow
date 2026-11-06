# CLAUDE.md - Instructions for Claude Code

## Project Context
This is **AI_Flow**, a production-grade framework of 30 standardized Agentic Skills and 60 dual-agent personas under the [Agent Skills Open Specification](https://agentskills.io).

## Available Skills (30 Skills, 60 Personas)
The following skills are available in `skills/` and can be invoked based on the task. Each skill contains an `agents/` folder pairing a **Generator** and **Validator** persona:

### Phase 1: Product, Requirements & Architecture
- `prd-generator`: Initiating new products or features. Ask clarifying discovery questions first.
- `trd-generator`: Translating PRD into technical requirements, p95/p99 latency budgets, and SLAs.
- `app-flow`: Mapping navigational user flows, state transitions, and edge-case recoveries.
- `uiux-design-brief`: Generating comprehensive UI/UX specifications, design tokens, and states.
- `backend-schema`: Designing database schemas (ERD, DDL, keys, composite indexes, and cascades).
- `system-architecture`: Designing system topologies, API contracts, boundaries, and resilience.
- `implementation-plan`: Breaking down features into phased engineering roadmaps.

### Phase 2: Execution & Quality
- `task-to-skill`: Converting completed tasks into permanent, reusable Agent Skills.
- `playwright-e2e-testing`: End-to-end browser testing and Playwright configuration with role locators.
- `systematic-debugging`: 5-step root-cause debugging. Never modify code before empirical verification.

### Phase 3: Auditing & Release
- `security-gap-audit`: Pre-launch application security review across 10 threat vectors. Read-only audit.
- `dead-code-cleanup`: 2-phase dead code pruning (Audit & Stop -> Execute with approval).
- `rigorous-code-review`: Staff Engineer code review focusing on Blockers and production crash scenarios.
- `clean-git-commits`: Conventional Commits organizing atomic, bisectable changes.

### Phase 4: Design Systems & Frontend (New)
- `design-system-tokens`: 3-tier token architecture (Primitives/Semantics/Components), Tailwind, dark-mode parity.
- `landing-page-converter`: Direct-response SaaS landing page copy, hero value propositions, and CTA conversion.
- `accessibility-wcag-audit`: Automated WCAG 2.1 AA/AAA compliance audit, ARIA trees, and keyboard navigation.

### Phase 5: API, Database & Performance (New)
- `api-contract-generator`: OpenAPI 3.1, tRPC, and GraphQL contracts with mock servers and RFC 7807 error envelopes.
- `db-migration-optimizer`: Zero-downtime database DDL migrations, lock avoidance, and query plan optimization.
- `performance-profiling`: Core Web Vitals (LCP, CLS, INP), runtime rendering, memory leak, and query profiling.

### Phase 6: DevOps, CI/CD & FinOps (New)
- `devops-docker-deploy`: Multi-stage Dockerfiles, non-root security, Docker Compose, and zero-downtime VPS deploy.
- `ci-cd-pipeline-builder`: GitHub Actions workflows, SHA-pinned actions, minimal permissions, and release automation.
- `finops-token-optimizer`: LLM API cost reduction, static prompt prefix caching (>1024 tokens), and model routing.

### Phase 7: Freelance & Client Business Operations (New)
- `freelance-client-onboarding`: Discovery intake, Statements of Work (SOW), scope boundary matrices, and milestone billing.
- `email-inbox-triage`: Autonomous email classification (P0-P5), client communications drafting, and task extraction.
- `invoice-billing-tracker`: Itemized invoice generation, aging accounts receivable, and late payment dunning reminders.

### Phase 8: Social Growth, Content & Founder OS (New)
- `insta-reel-creator`: 5-beat spoken vertical video scripts (30-45s), hook scoring (>=80), and anti-slop filtering.
- `seo-content-strategist`: Search intent mapping, pillar-cluster topic modeling, and programmatic content briefs.
- `social-copy-repurposer`: Transforming engineering PRs and devlogs into X/Twitter threads and LinkedIn posts.
- `executive-time-ledger`: Founder leverage auditing ($10k/hr vs $10/hr), deep-work protection, and daily devlogs.

## Autonomous Execution & Dual-Agent Mode
Run any skill in autonomous dual-agent mode (Generator &harr; Validator feedback loop):
```bash
python scripts/run.py --skill <skill-name> --input "<prompt>" --mode dual
```

## Background Daemon & Automation
The system runs natively as a local daemon for email triage and file drop queues:
```powershell
.\scripts\daemon-service.ps1 -Action Status
```
