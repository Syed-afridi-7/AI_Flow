---
name: security-gap-audit
description: Use when conducting a pre-launch security review, vulnerability assessment, threat model audit, or scanning a codebase for authentication, authorization, injection, and secrets risks.
---

# Security Gap Audit

## Overview
Acts as a Senior Application Security Engineer conducting an adversarial pre-launch security audit. Identifies vulnerabilities across authentication, authorization, data exposure, injection, and infrastructure misconfigurations with actionable remediation diffs.

## When to Use
- **Trigger symptoms:** Prior to merging critical PRs, before production releases, during compliance checks, or when user asks "audit security", "find vulnerabilities", or "check for security gaps".
- **When NOT to use:** Routine UI cosmetic reviews or performance-only optimization tasks.

## Instructions

### Step 1: Systematic Vulnerability Scan
Inspect the codebase across these 10 threat vectors:
1. **Authentication & Session Flaws:** Weak password hashing, broken token validation, session fixation, unrevoked JWTs.
2. **Authorization & IDOR:** Insecure Direct Object References (e.g., User A accessing User B's records via query params/IDs), missing role-based checks.
3. **Hardcoded Secrets & Credential Leakage:** API keys, database credentials, or private certificates committed in source or exposed in client-side bundles.
4. **Injection Risks:** SQL, NoSQL, OS command, LDAP, and Cross-Site Scripting (XSS).
5. **Route Protection & Validation:** Unprotected API endpoints, missing middleware, or unvalidated payloads.
6. **Input Validation & Sanitization:** Lack of schema validation (e.g., Zod, Joi, Pydantic) on untrusted inputs.
7. **Rate Limiting & Abuse Prevention:** Missing brute-force protection on auth endpoints and unthrottled public APIs.
8. **Network & Header Configuration:** Over-permissive CORS (`*` with credentials), missing security headers (`CSP`, `HSTS`, `X-Frame-Options`), unsafe cookie flags (`HttpOnly`, `SameSite`, `Secure`).
9. **Vulnerable Dependencies:** Known CVEs in dependencies, outdated packages.
10. **Telemetry & Log Leaks:** PII, passwords, tokens, or credit card numbers leaking into server logs or error responses.

### Step 2: Structured Findings Report
Report all findings ordered by severity (**Critical** &rarr; **High** &rarr; **Medium** &rarr; **Low**). For each finding:
- **Title & Severity:** Clear description and severity tag.
- **Location:** File path and exact line range (`[path/to/file#L12-L18]`).
- **Exploit Scenario:** Concrete attack vector demonstrating how an adversary could exploit this in production.
- **Remediation:** The exact code fix (before/after diff).

### Step 3: Explicit Clean Categories
If any of the 10 vectors are clean and well-defended, **state so explicitly** (e.g., "✅ SQL Injection: Clean — all queries use parameterized ORM queries."). Never stay silent on audited vectors.

## Rules & Constraints
- **MANDATORY SAFEGUARD:** Do NOT modify any application code during the audit. Deliver the report and wait for user approval before applying any patches.
- Highlight any finding requiring secrets rotation immediately as Critical.
