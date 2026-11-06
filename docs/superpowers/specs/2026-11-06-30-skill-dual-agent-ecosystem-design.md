# Master Design Specification: 30-Skill Dual-Agent Autonomous Ecosystem

**Date:** 2026-11-06  
**Status:** Approved  
**Author:** Syed Afridi & AI Pair Programming Agent  

---

## 1. Executive Summary & Vision

The objective of this architecture is to transform **AI_Flow** into a complete, MNC/startup-caliber autonomous engineering and business operating system for a solo "Super-Developer & Founder". The system empowers a solo unicorn—operating concurrently across roles as student, full-stack engineer, UI/UX designer, freelancer, and content creator—to build, ship, market, and manage multiple products autonomously.

The architecture expands AI_Flow from 14 to **30 standardized skills** organized across 8 lifecycle domains. Every skill domain incorporates a **Dual-Agent Architecture** (30 skills $\times$ 2 agents = **60 specialized agents**) with a self-correcting Generator &harr; Validator feedback loop. The system runs locally as an autonomous background daemon initiated at Windows boot/login, features email client triage and notifications, and modularizes the existing Instagram reel pipeline from `E:\Insta_Reel`.

---

## 2. Directory Topology & Skill Structure

Every skill domain resides in its own isolated directory in `skills/` compliant with the [Agent Skills Open Specification](https://agentskills.io), housing both the canonical spec and dedicated agent personas:

```
skills/<skill-name>/
  ├── SKILL.md              # Canonical Agent Skills spec (triggers, inputs, outputs)
  └── agents/
      ├── generator.md      # Persona A: Architect / Generator / Strategist
      └── validator.md      # Persona B: Auditor / Verifier / Quality Gate
```

---

## 3. The 30-Skill & 60-Agent Persona Matrix

### Phase 1: Product, Requirements & Architecture
1. **`prd-generator`**
   - *Generator:* Product Discovery Strategist (5-question discovery, user stories, MVP matrix)
   - *Validator:* Scope & Feasibility Auditor (Scope creep detection, unstated assumptions check)
2. **`trd-generator`**
   - *Generator:* Technical Systems Architect (Throughput targets, p95/p99 latency budgets, SLAs)
   - *Validator:* Reliability & SLA Stress Tester (Bottleneck analysis, failover validation)
3. **`app-flow`**
   - *Generator:* Navigational Journey Architect (Route mapping, modal stacks, state machines)
   - *Validator:* State Machine & Edge-Case Auditor (Dead-end detection, token expiry recovery)
4. **`uiux-design-brief`**
   - *Generator:* Visual & Token Architect (Hex palettes, 8px spacing, 5 screen states)
   - *Validator:* Design System & Token Linter (Contrast ratios, responsive breakpoint consistency)
5. **`backend-schema`**
   - *Generator:* Relational/Document Modeler (Mermaid ERD, strict SQL DDL, cascade rules)
   - *Validator:* Query & Index Optimizer (Composite index safety, N+1 risk audit)
6. **`system-architecture`**
   - *Generator:* Distributed Systems Architect (Topology diagrams, service boundaries, contracts)
   - *Validator:* Resilience & Contract Auditor (Single-point-of-failure analysis, circuit breakers)
7. **`implementation-plan`**
   - *Generator:* Engineering Roadmap Planner (Phased dependency graph, atomic tasks)
   - *Validator:* Critical Path & Dependency Auditor (Ordering safety, missing test checkpoints)

### Phase 2: Execution & Quality
8. **`task-to-skill`**
   - *Generator:* Workflow Extraction Engineer (Workflow synthesis, trigger detection)
   - *Validator:* Spec Compliance & Rigor Verifier (agentskills.io validation, rationalization check)
9. **`playwright-e2e-testing`**
   - *Generator:* Browser Automation Engineer (Resilient role locators, auth state fixtures)
   - *Validator:* Flakiness & Determinism Auditor (Hardcoded waits, timing race condition audit)
10. **`systematic-debugging`**
    - *Generator:* Root-Cause Investigator (Hypothesis ranking, minimal reproduction probe)
    - *Validator:* Regression Guard & Proof Verifier (Empirical proof check, fix isolation)

### Phase 3: Auditing & Release
11. **`security-gap-audit`**
    - *Generator:* Vulnerability Scanner (Threat model scanner, secrets and injection audit)
    - *Validator:* Exploit Verifier & Threat Modeler (Exploit proof-of-concept, false-positive filter)
12. **`dead-code-cleanup`**
    - *Generator:* Unused Code Pruner (AST scan, confidence score calculation)
    - *Validator:* Safe Dependency & Build Verifier (Dynamic import check, build test verify)
13. **`rigorous-code-review`**
    - *Generator:* Senior Staff Code Reviewer (Blocker detection, crash scenarios, regressions)
    - *Validator:* Nitpick Filter & Actionability Auditor (Filters minor styling, verifies reproduction)
14. **`clean-git-commits`**
    - *Generator:* Conventional Commits Formatter (Atomic commit staging, imperative summaries)
    - *Validator:* Git History & Diff Integrity Auditor (Multi-responsibility commit check)

### Phase 4: Design Systems & Frontend Engineering (New)
15. **`design-system-tokens`**
    - *Generator:* Design Token Architect (Tailwind config, CSS variables, primitives)
    - *Validator:* Token Compliance & Parity Linter (WCAG AA contrast, unused token audit)
16. **`landing-page-converter`**
    - *Generator:* Direct-Response SaaS Copywriter (Hero hook, value prop, CTA hierarchy)
    - *Validator:* Conversion UX & Cognitive Load Auditor (Friction points, skimming readability)
17. **`accessibility-wcag-audit`**
    - *Generator:* A11y Remediation Engineer (ARIA attributes, keyboard navigation, focus trap)
    - *Validator:* WCAG 2.1 AA Compliance Auditor (Automated axe-core heuristics, screen reader paths)

### Phase 5: API, Database & Performance Engineering (New)
18. **`api-contract-generator`**
    - *Generator:* OpenAPI 3.1 & tRPC Architect (Strict schema types, endpoint documentation)
    - *Validator:* Mock Server & Breaking-Change Verifier (Backward compatibility, idempotency keys)
19. **`db-migration-optimizer`**
    - *Generator:* Migration DDL Engineer (Safe non-blocking migrations, zero-downtime DDL)
    - *Validator:* Lock Contention & Query Plan Auditor (`EXPLAIN ANALYZE`, table lock risks)
20. **`performance-profiling`**
    - *Generator:* Web Vitals & Runtime Optimizer (Bundle splitting, rendering optimizations)
    - *Validator:* Memory Leak & Core Web Vitals Auditor (LCP/CLS/INP metrics, heap inspection)

### Phase 6: DevOps, CI/CD & FinOps (New)
21. **`devops-docker-deploy`**
    - *Generator:* Containerization Engineer (Multi-stage Dockerfiles, Docker Compose, VPS configs)
    - *Validator:* Container Security & Cache Optimizer (Non-root user check, minimal image size)
22. **`ci-cd-pipeline-builder`**
    - *Generator:* GitHub Actions Workflow Architect (Test, build, lint, release pipelines)
    - *Validator:* Pipeline Security & Concurrency Auditor (Secrets leakage check, cache reuse)
23. **`finops-token-optimizer`**
    - *Generator:* Prompt Compression Engineer (Prompt pruning, context window optimization)
    - *Validator:* LLM Cost & Cache Efficiency Auditor (Prefix cache hit-rate, model routing checks)

### Phase 7: Freelance & Client Business Operations (New)
24. **`freelance-client-onboarding`**
    - *Generator:* SOW & Client Proposal Writer (Statements of Work, deliverables, payment terms)
    - *Validator:* Scope Creep Guard & Contract Auditor (Liability boundaries, out-of-scope clauses)
25. **`email-inbox-triage`**
    - *Generator:* Inbound Inquiry Classifier (Categorization, task extraction, deadline analysis)
    - *Validator:* Professional Communications Drafter (Tone calibration, rate card adherence)
26. **`invoice-billing-tracker`**
    - *Generator:* Milestone Invoice Generator (Itemized invoice generation, payment schedules)
    - *Validator:* Ledger & Tax Reconciliation Auditor (Hours verification, milestone sign-off check)

### Phase 8: Social Growth, Content & Founder Operating System (New)
27. **`insta-reel-creator`** *(Modularized from `E:\Insta_Reel`)*
    - *Generator:* Spoken Reel Script & Beat Architect (5-beat structure, devlog angles, cover poster)
    - *Validator:* Hookscore Evaluator & Anti-Slop Sanitizer (`hookscore >= 80`, AI jargon removal)
28. **`seo-content-strategist`**
    - *Generator:* Search Intent & Cluster Strategist (Programmatic keywords, blog outlines, metadata)
    - *Validator:* Technical SEO & EEAT Auditor (Search intent alignment, keyword stuffing check)
29. **`social-copy-repurposer`**
    - *Generator:* Multi-Platform Content Repurposer (Turns commits/PRs into X threads & LinkedIn posts)
    - *Validator:* Engagement Hook & Platform Fit Auditor (Skimmability, platform algorithm fit)
30. **`executive-time-ledger`**
    - *Generator:* Founder Priority Quartermaster (Deep-work block planning, devlog journaling)
    - *Validator:* Daily Accountability & Time Auditor (Distraction auditing, weekly velocity tracking)

---

## 4. Dual-Agent Execution Engine & Token Optimization

### 4.1 Bounded Feedback Loop Protocol
1. **Turn 1 (Drafting):** Generator receives task context and system persona &rarr; produces structured Draft 1.
2. **Turn 2 (Auditing):** Validator reviews Draft 1 against an explicit scoring rubric &rarr; outputs JSON scorecard:
   ```json
   {
     "score": 88,
     "verdict": "PASS | REVISE",
     "blockers": ["..."],
     "recommendations": ["..."]
   }
   ```
3. **Turn 3 (Self-Correction):** If `verdict == "REVISE"`, Generator receives specific blockers and produces Draft 2.
4. **Hard Loop Cap:** Capped at `max_iterations = 2` to eliminate runaway API costs.

### 4.2 Model Tiering & Local Cost Efficiency
- **Tier 1 (Fast & Economical):** `gemini-2.5-flash` / `gpt-4o-mini` for draft generation, copy conversion, and email triage.
- **Tier 2 (Deep Reasoning):** `claude-3-7-sonnet` / `gemini-2.5-pro` for security audits, architecture verification, and hook evaluation.
- **Invariant Prefix Caching:** Pinned system instructions (>1,024 tokens) exploit Gemini and Claude automatic prompt caching, slashing input token costs by up to 80%.

---

## 5. Modular Integration of `E:\Insta_Reel`

The existing Instagram agent is modularized into `skills/insta-reel-creator/lib/`:
- `hookscore.py`: Evaluates hook strength against proven curiosity and counter-intuitive patterns.
- `beats.py`: Generates the 5-beat spoken timing sheet (30–45 seconds; 75–100 words).
- `humanize.py`: Purges robotic AI cliches, passive phrasing, and emojis.
- `memory.py` & `memory.db`: SQLite database logging past themes and preventing repetitive topics.

---

## 6. OS Background Daemon & Windows Integration

### 6.1 Daemon Core (`scripts/daemon.py`)
- Python standard-library daemon (`imaplib`, `sqlite3`, `time`).
- Heartbeat loop:
  1. Polls IMAP for incoming client emails (triage & draft).
  2. Scans `data/queue/inbox/` for dropped markdown tasks.
  3. Triggers daily content creation at scheduled intervals.
- Memory consumption: `< 35MB RAM`, `0% CPU` when idle.

### 6.2 Windows Service Integration (`scripts/daemon-service.ps1`)
- Registers on-login execution via Windows Task Scheduler (`schtasks /Create /SC ONLOGON`).
- Supports `-Action Install`, `-Action Status`, `-Action Stop`, `-Action Start`.

### 6.3 Security Guardrails
- **Read & Draft Only:** Inbound emails are parsed and draft replies written to `output/email_drafts/`. The daemon **never sends outbound emails** automatically.

---

## 7. Phased Implementation Roadmap

1. **Sub-Project 1: Foundation & Taxonomy:** Scaffold all 16 new skill directories, canonical `SKILL.md` files, and `agents/` dual personas.
2. **Sub-Project 2: Orchestration Engine:** Upgrade `scripts/run.py` to support `--mode dual` with model tiering, caching, and scorecards.
3. **Sub-Project 3: Instagram Integration:** Modularize `E:\Insta_Reel` utilities into `skills/insta-reel-creator/lib/` and wire into the dual-agent loop.
4. **Sub-Project 4: Background Daemon & Email Hooks:** Implement `scripts/daemon.py`, `scripts/daemon-service.ps1`, and task queue.
5. **Sub-Project 5: Verification & Documentation:** Validate all 30 skills via `validate.js` and `validate.ps1`, update `README.md`, `AGENTS.md`, and IDE rules.
