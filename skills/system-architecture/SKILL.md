---
name: system-architecture
description: Use when architecting a software system, selecting technology stacks, designing database schemas, defining API contracts, or evaluating scalability and resilience trade-offs before implementation.
---

# System Architecture & Technical Specification

## Overview
Acts as a Principal Software Architect to deliver a complete, production-ready technical architecture document. Translates requirements and UI designs into concrete system topologies, data persistence schemas, API contracts, and resilience patterns.

## When to Use
- **Trigger symptoms:** Prior to implementing new services, defining backend schemas, designing REST/GraphQL/gRPC APIs, selecting database engines, or refactoring monoliths into distributed services.
- **When NOT to use:** Self-contained single-function changes, minor bug fixes, or non-technical documentation tasks.

## Instructions

Deliver the architecture specification with the following structured sections:

1. **High-Level System Topology:**
   - Architecture diagram using Mermaid (`graph TD` or `sequenceDiagram`).
   - Defined services, responsibilities, and communication protocols (Synchronous HTTP/gRPC vs. Asynchronous Pub/Sub).
2. **Tech Stack & Trade-Off Justification:**
   - Concrete framework, language, persistence, and hosting selections.
   - Explicit trade-off rationale: Why Option A was selected over Option B and C (performance, ecosystem, operational overhead).
3. **Data Architecture & Persistence:**
   - Relational (SQL) or Document (NoSQL) schema definition with entity relationships, types, constraints, and foreign keys.
   - Strategic indexing plan for high-frequency query paths and unique constraints.
   - Migration and seed data execution plan.
4. **API Contracts & Interface Specifications:**
   - Endpoint table: HTTP Method, Path, Auth requirements, Request Body, Response Shapes (200, 400, 401, 404, 500).
   - Authentication scheme (Bearer JWT, HttpOnly Cookies, OAuth2, API Keys) and RBAC rules.
   - Pagination, sorting conventions, and caching headers (`Cache-Control`, `ETag`).
5. **State Management & Data Flow:**
   - Client state caching (e.g., TanStack Query, SWR) vs. global app state (Zustand, Redux).
   - Optimistic mutations and rollback strategies on mutation failure.
6. **Non-Functional Requirements & Resilience:**
   - Performance budgets: Target latency (p95 < 200ms, p99 < 500ms).
   - Fault tolerance: Retries with exponential backoff, circuit breakers, and rate limiting.
   - Observability: Structured logging standards (trace IDs), metrics, and error telemetry.

## Rules & Constraints
- Be opinionated. Never list 5 possible databases without explicitly choosing one with rationale.
- If a technical requirement is ambiguous or underspecified, flag the risk explicitly instead of making silent assumptions.
