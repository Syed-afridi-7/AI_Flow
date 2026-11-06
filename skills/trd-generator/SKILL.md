---
name: trd-generator
description: Use when translating product requirements into technical requirements, defining non-functional requirements, setting service SLAs, or establishing architectural constraints before implementation.
---

# Technical Requirement Document (TRD) Generator

## Overview
Acts as a Principal Software Architect to translate product specifications (PRD) into a rigorous Technical Requirement Document (TRD). Defines non-functional requirements, throughput/latency budgets, reliability SLAs, compliance frameworks, integration boundaries, and telemetry specifications.

## When to Use
- **Trigger symptoms:** After PRD approval, prior to writing backend or infrastructure code, when evaluating system scale, or when user asks "generate a TRD", "write technical requirements", or "define system SLAs".
- **When NOT to use:** Writing code unit tests, fixing routine bugs, or brainstorming early product concepts.

## Instructions

Produce the TRD across these 7 structured sections:

### 1. Technical Problem Statement & Scope Boundaries
- Define technical goals, architectural constraints, and engineering boundaries.
- Explicitly list non-goals and out-of-scope technical work (e.g., "Multi-region replication is out of scope for v1").

### 2. Performance, Scalability & Throughput Budgets
- **Concurrency Targets:** Peak concurrent users and persistent connection limits (WebSockets, SSE).
- **Throughput:** Expected average and peak read/write Requests Per Second (RPS).
- **Latency Budgets:** Strict targets for p50, p95, and p99 server response latencies (e.g., p95 < 150ms).
- **Scaling Mechanisms:** Auto-scaling thresholds (CPU/memory/queue depth) and caching layers.

### 3. Reliability, Availability & Disaster Recovery
- **Uptime SLA:** Defined availability target (e.g., 99.9% uptime).
- **Failure Isolation:** Circuit breakers, rate limiters, and graceful degradation fallbacks.
- **Disaster Recovery:** Recovery Point Objective (RPO) and Recovery Time Objective (RTO) metrics with automated snapshot cadence.

### 4. Security, Identity & Compliance
- **Authentication Scheme:** Token lifecycle, rotation, and revocation architecture.
- **Authorization & RBAC:** Explicit permission matrix across user roles.
- **Encryption Standards:** Data in transit (TLS 1.3) and at rest (AES-256).
- **Regulatory Controls:** Audit trails, data retention policies, and PII anonymization procedures.

### 5. Third-Party Integrations & Resilience Contracts
- External API contracts: Timeout budgets, exponential backoff with jitter, and dead-letter queues.
- Webhook ingestion: Idempotency keys, signature verification, and deduplication windows.

### 6. Observability, Telemetry & SLO Framework
- Structured JSON logging schema (`timestamp`, `trace_id`, `span_id`, `service`, `level`, `message`).
- Service Level Indicators (SLIs) and Service Level Objectives (SLOs) with error budget alert triggers.
- Distributed tracing propagation across asynchronous boundaries.

### 7. Deployment Pipeline & Environment Matrix
- Build and containerization standards (Docker, multi-stage builds).
- CI/CD quality gates (test coverage, SAST security scans).
- Rollout strategy: Zero-downtime rolling updates, Blue/Green, or Canary deployments.

## Rules & Constraints
- Quantify every requirement. Never use vague phrases like "the system must be fast and secure".
- Specify numeric targets for latency, throughput, and error rates.
- Flag any technical uncertainty as an explicit open risk.

## Rationalization Table
| Temptation / Shortcut | Reality |
| :--- | :--- |
| "A PRD is enough to start coding." | PRDs describe user needs; TRDs define technical reality, scale limits, and reliability constraints. |
| "We'll tune performance after launch." | Latency and throughput bottlenecks are difficult to solve without upfront architectural targets. |
| "Security can be addressed during code review." | Auth models, data encryption, and RBAC must be architected before writing schemas or APIs. |

