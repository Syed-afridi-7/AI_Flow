---
name: ci-cd-pipeline-builder
description: Use when authoring, auditing, or optimizing automated CI/CD workflows, GitHub Actions pipelines, matrix testing grids, package build and release pipelines, branch protection enforcement, or secure secret management with concurrency controls.
---

# CI/CD Pipeline Builder

## Overview
Establishes enterprise-grade, deterministic Continuous Integration and Continuous Delivery (CI/CD) pipelines using GitHub Actions. Implements supply chain security best practices, token least-privilege permissions, aggressive artifact and dependency caching, matrix test parallelism, pull-request concurrency cancellation, and automated semantic releases with zero-downtime deployment triggers.

## When to Use
- **Trigger symptoms:** Bootstrapping CI/CD pipelines for new repositories; fixing slow or expensive builds (>10 minutes); resolving flaky test runs; eliminating wasted CI minutes from outdated PR commits; securing GitHub Actions against supply chain attacks and script injection; automating container image publishing to GHCR or Docker Hub; managing staging-to-production deployment gates.
- **When NOT to use:** Local one-off development scripts; purely manual manual testing checklists; or environments utilizing proprietary mainframe deployment mechanisms where modern GitOps workflows do not apply.

## Instructions

Execute pipeline design and automation across four structured phases:

### Phase 1: Security Hardening & Principle of Least Privilege
1. **Explicit Token Permissions:**
   - Define a top-level `permissions` block on every workflow file. Never rely on default repository-wide read-write permissions:
     ```yaml
     permissions:
       contents: read
     ```
   - Grant elevated permissions (`pull-requests: write`, `packages: write`, `id-token: write`) strictly at the individual job level where mandatory.
2. **Action SHA Pinning:**
   - Pin third-party community actions to full 40-character commit SHAs rather than mutable git tags (`@v4`, `@main`), appending the human-readable tag as a trailing comment:
     ```yaml
     - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
     ```
3. **Script Injection Prevention:**
   - Never directly interpolate untrusted context expressions (`${{ github.event.issue.title }}`, `${{ github.event.head_commit.message }}`) into inline bash `run:` scripts.
   - Always route dynamic contexts through intermediate environment variables:
     ```yaml
     env:
       COMMIT_MSG: ${{ github.event.head_commit.message }}
     run: echo "Commit message is: $COMMIT_MSG"
     ```

### Phase 2: Workflow Triggers & Concurrency Controls
1. **Precise Path & Event Filtering:**
   - Trigger CI workflows on `pull_request` targeting default branches (`main`, `master`) and `push` to default branches.
   - Filter out documentation, design assets, and metadata files to save CI compute:
     ```yaml
     on:
       pull_request:
         branches: [main]
         paths-ignore:
           - '**.md'
           - 'docs/**'
           - '.vscode/**'
     ```
2. **Concurrency Cancellation:**
   - Enforce concurrency groups with automatic cancellation of superseded in-flight runs on the same branch or PR:
     ```yaml
     concurrency:
       group: ${{ github.workflow }}-${{ github.head_ref || github.run_id }}
       cancel-in-progress: true
     ```

### Phase 3: High-Performance Matrix Testing & Caching
1. **Parallel Matrix Execution:**
   - Define matrix configurations across runtime versions (e.g., Node 18, 20, 22 or Python 3.10, 3.11, 3.12) or operating systems (`ubuntu-latest`, `windows-latest`, `macos-latest`):
     ```yaml
     strategy:
       fail-fast: false
       matrix:
         node-version: [18.x, 20.x]
     ```
2. **Aggressive Dependency Caching:**
   - Leverage native package manager caching via setup actions (`actions/setup-node` with `cache: 'pnpm'`, `actions/setup-python` with `cache: 'pip'`).
   - For custom build assets or compiler caches (`target/`, `.turbo/`, `node_modules/.cache`), use `actions/cache` keyed on OS and lockfile SHA256 hashes.
3. **Artifact Retention Policies:**
   - Set short retention periods (`retention-days: 7` or lower) for temporary test reports, coverage summaries, and build artifacts to prevent repo storage quota exhaustion.

### Phase 4: Continuous Delivery & Release Pipeline
1. **Job Dependency Graph:**
   - Chain delivery stages using explicit `needs:` dependencies (`lint` &rarr; `test` &rarr; `build` &rarr; `deploy`).
2. **Protected Environments & Secrets:**
   - Target designated GitHub Environments (`production`, `staging`) with configured branch protection rules, required reviewer approvals, and environment-scoped secrets.
3. **Automated Semantic Versioning & Changelogs:**
   - Integrate automated version tagging and GitHub Release creation based on Conventional Commits (`fix:`, `feat:`, `perf:`).

## Rules & Constraints
- **Zero Default Write Permissions:** Top-level permissions must be explicitly set to `contents: read` or `{}` across all workflows.
- **Mandatory Concurrency Control:** Every pull-request workflow must include `concurrency` with `cancel-in-progress: true`.
- **Zero Raw Context in Run Scripts:** Untrusted github event payloads must never be concatenated directly into shell execution blocks.
- **Fail-Fast Discipline:** Set `fail-fast: false` on matrix test suites so all platform failures are visible in a single run.
- **Artifact Expiration:** Never leave artifact retention at the default 90 days; specify explicit retention <= 14 days.

## Common Mistakes & Anti-Patterns
| Anti-Pattern | Severity | Correction |
| :--- | :--- | :--- |
| Leaving workflow permissions wide open (`write-all`) | Critical | Declare `permissions: contents: read` at top level; grant write only to specific jobs. |
| In-flight PR commits running concurrently | Medium | Configure `concurrency: group: ${{ github.ref }}, cancel-in-progress: true`. |
| Tag-based action references (`@v1`) | High | Pin to immutable 40-character commit SHAs with version comment. |
| Inline `${{ github.event.comment.body }}` in `run:` | Critical | Pass context variables into `env:` blocks to prevent command injection. |
| Missing lockfile cache keys | Medium | Cache on `hashFiles('**/pnpm-lock.yaml')` to ensure cache validity. |
| Running expensive test suites on markdown edits | Low | Use `paths-ignore: ['**.md', 'docs/**']` to avoid wasteful runs. |
