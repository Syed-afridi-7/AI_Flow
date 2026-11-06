# Pure Python 60-Agent Autonomous Engine Implementation Plan

> **For Claude / Pair Programmer:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a 100% self-contained, pure Python multi-agent execution engine powering 30 skills and 60 dual-agent personas (Generators & Validators) with zero external APIs, zero third-party wrappers, and zero cost.

**Architecture:** Pure Python standard library (`dataclasses`, `abc`, `ast`, `re`, `pathlib`, `json`, `unittest`). Each skill provides a `BaseGenerator` subclass synthesizing deliverables and a `BaseValidator` subclass running AST/static rule audits to generate a 100-point rubric scorecard. A `DualAgentRunner` coordinates the peer review and self-correction loop.

**Tech Stack:** Python 3.10+ Standard Library (no external pip dependencies).

---

## Proposed Changes

Grouped by component layer and ordered logically.

### Component 1: Core Engine Framework (`engine/core/`)

#### [NEW] `engine/__init__.py`
Package initializer.

#### [NEW] `engine/core/__init__.py`
Core package initializer exposing public types and runners.

#### [NEW] `engine/core/types.py`
Dataclasses for `TaskContext`, `GenerationResult`, `ValidationScorecard`, `Blocker`, and `Severity`.

#### [NEW] `engine/core/base.py`
Abstract base classes: `BaseAgent`, `BaseGenerator`, and `BaseValidator`.

#### [NEW] `engine/core/ast_tools.py`
Pure-Python AST and regex static analysis tools:
- Syntax validator (`ast.parse`)
- Security scanner (hardcoded secrets, eval/exec, SQL injection)
- Conventional commits linter
- WCAG contrast calculator
- Hookscore & retention evaluator

#### [NEW] `engine/core/registry.py`
`AgentRegistry` providing discovery and instantiation of all 30 skills (60 agents).

#### [NEW] `engine/core/runner.py`
`DualAgentRunner` orchestrating Generator pass -> Validator audit -> self-correction loop (if score < 85, max 2 iterations).

---

### Component 2: The 8 Lifecycle Phase Agents (`engine/agents/`)

#### [NEW] `engine/agents/phase1_architecture/` (7 Skills, 14 Agents)
- `prd_generator`: ProductDiscoveryStrategist & ScopeFeasibilityAuditor
- `trd_generator`: TechnicalSystemsArchitect & ReliabilitySlaStressTester
- `app_flow`: NavigationJourneyArchitect & StateMachineEdgeCaseAuditor
- `uiux_design_brief`: VisualTokenArchitect & DesignSystemTokenLinter
- `backend_schema`: RelationalModeler & QueryIndexOptimizer
- `system_architecture`: DistributedSystemsArchitect & ResilienceContractAuditor
- `implementation_plan`: RoadmapPlanner & CriticalPathAuditor

#### [NEW] `engine/agents/phase2_execution/` (3 Skills, 6 Agents)
- `task_to_skill`: WorkflowExtractor & SpecComplianceVerifier
- `playwright_e2e_testing`: BrowserAutomationEngineer & FlakinessDeterminismAuditor
- `systematic_debugging`: RootCauseInvestigator & RegressionProofVerifier

#### [NEW] `engine/agents/phase3_release/` (4 Skills, 8 Agents)
- `security_gap_audit`: VulnerabilityScanner & ThreatModelAuditor
- `dead_code_cleanup`: UnusedCodePruner & SafeDependencyVerifier
- `rigorous_code_review`: SeniorStaffCodeReviewer & NitpickFilterAuditor
- `clean_git_commits`: ConventionalCommitFormatter & DiffIntegrityAuditor

#### [NEW] `engine/agents/phase4_design_frontend/` (3 Skills, 6 Agents)
- `design_system_tokens`: TokenArchitect & WcagContrastLinter
- `landing_page_converter`: DirectResponseCopywriter & ConversionUxAuditor
- `accessibility_wcag_audit`: A11yRemediationEngineer & WcagComplianceAuditor

#### [NEW] `engine/agents/phase5_api_data_perf/` (3 Skills, 6 Agents)
- `api_contract_generator`: ApiContractArchitect & BreakingChangeVerifier
- `db_migration_optimizer`: MigrationDdlEngineer & LockContentionAuditor
- `performance_profiling`: WebVitalsOptimizer & MemoryLeakProfiler

#### [NEW] `engine/agents/phase6_devops_finops/` (3 Skills, 6 Agents)
- `devops_docker_deploy`: ContainerizationEngineer & DockerSecurityAuditor
- `ci_cd_pipeline_builder`: ActionsArchitect & PipelineSecurityAuditor
- `finops_token_optimizer`: PromptCompressor & TokenCacheAuditor

#### [NEW] `engine/agents/phase7_freelance_ops/` (3 Skills, 6 Agents)
- `freelance_client_onboarding`: SowProposalWriter & ContractScopeAuditor
- `email_inbox_triage`: InboundInquiryClassifier & ClientCommunicationsDrafter
- `invoice_billing_tracker`: MilestoneInvoiceGenerator & LedgerReconciliationAuditor

#### [NEW] `engine/agents/phase8_growth_founder/` (4 Skills, 8 Agents)
- `insta_reel_creator`: SpokenReelScriptArchitect & HookscoreAntiSlopAuditor
- `seo_content_strategist`: SearchIntentStrategist & TechnicalSeoAuditor
- `social_copy_repurposer`: ContentRepurposer & PlatformHookAuditor
- `executive_time_ledger`: PriorityQuartermaster & AccountabilityAuditor

---

### Component 3: CLI & Runner Integration

#### [NEW] `engine/cli.py`
Local CLI runner supporting `--skill`, `--input`, `--mode {single,dual}`, `--list`, and `--output`.

#### [MODIFY] `scripts/run.py`
Add support for `--mode local` that routes directly to `DualAgentRunner` with zero network requests.

#### [MODIFY] `scripts/daemon.py`
Add local execution route for file drop queues in `data/queue/inbox/`.

---

## Verification Plan

### Automated Tests
1. Core unit tests: `python -m unittest discover -s tests -p "test_*.py"`
2. Engine smoke test: `python -m engine.cli --list`
3. Sample dual-agent run: `python -m engine.cli --skill prd-generator --input "Crypto tracker" --mode dual`
4. Validation script parity: `node scripts/validate.js` & `powershell -File scripts/validate.ps1`

### Manual Verification
- Verify terminal outputs render clean colored progress bars, 100-point scorecards, and category score breakdowns.
- Verify artifacts write to disk cleanly.
- Verify memory consumption remains < 35MB with zero network I/O.
