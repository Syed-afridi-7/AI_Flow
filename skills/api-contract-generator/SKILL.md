---
name: api-contract-generator
description: Use when authoring, validating, or maintaining strict API contracts (OpenAPI 3.1, JSON Schema, tRPC routers, GraphQL schemas, or gRPC Protobuf definitions), establishing type safety between client and server, generating client SDKs, or enforcing breaking change policies.
---

# API Contract Generator

## Overview
Acts as a Principal API Architect to design, standardize, and maintain production-grade API specifications across REST (OpenAPI 3.1), tRPC, GraphQL, and gRPC. Enforces end-to-end type safety, deterministic error representations (RFC 7807), strict idempotency guarantees, semantic pagination patterns, and rigorous backward compatibility policies before backend and frontend implementation begins.

## When to Use
- **Trigger symptoms:** When designing new backend endpoints, establishing client-server interfaces, decoupling frontend and backend teams with mockable contracts, versioning public or internal APIs, refactoring legacy ad-hoc JSON endpoints, or preventing breaking changes across microservices.
- **When NOT to use:** Designing relational database schemas (use `backend-schema`), writing database table migration scripts (use `db-migration-optimizer`), or styling user interfaces.

## Instructions

Execute the API contract specification across four structured phases:

### Phase 1: Protocol Selection & Transport Invariants
1. **Determine API Architecture:**
   - **OpenAPI 3.1 (REST):** Standard for public APIs, multi-language client SDK generation, webhook payloads, and third-party integrations.
   - **tRPC:** Ideal for TypeScript full-stack monorepos (Next.js/React to Node.js) requiring zero-overhead compile-time type sharing.
   - **GraphQL:** Best for complex client-driven data fetching with nested relation graphs and client-specified field selection.
   - **gRPC / Protocol Buffers:** Best for internal high-throughput, low-latency microservice-to-microservice communication.
2. **Base URI & Versioning Strategy:**
   - Establish URI path versioning (e.g., `/api/v1/...`) or header-based content negotiation.
   - Define lifecycle states: Active, Deprecated, Sunset, with standard `Sunset` and `Deprecation` HTTP headers (RFC 8594).

### Phase 2: Schema Modeling & Type Invariants
1. **Strict Type Definitions:**
   - Model all request bodies, query parameters, path variables, and responses using strict JSON Schema / Zod definitions.
   - Forbid untyped `any`, unconstrained string maps, or generic `object` types.
   - Enforce explicit formats: `uuid` (UUIDv4/v7), `date-time` (ISO 8601 UTC with trailing `Z`), `email`, `uri`, `ipv4`/`ipv6`.
   - Represent monetary amounts as 64-bit integers in the smallest currency unit (e.g., cents, satoshis) or decimal strings (`NUMERIC(12,2)`); never use floating-point types.
2. **Nullability vs. Optionality:**
   - Differentiate strictly between:
     - `optional` (omitted from request/response payload).
     - `nullable` (explicitly set to `null` to clear or reset a value).
     - `undefined` / `missing` in partial updates (PATCH operations).

### Phase 3: Endpoint Operations, Idempotency & Error Envelopes
1. **HTTP Method Semantics:**
   - `GET`: Safe, idempotent, cached. No request body.
   - `POST`: Non-idempotent resource creation or action dispatch.
   - `PUT`: Idempotent full resource replacement.
   - `PATCH`: Idempotent or non-idempotent partial resource update (using JSON Merge Patch RFC 7396 or JSON Patch RFC 6902).
   - `DELETE`: Idempotent resource removal.
2. **Idempotency Safeguards:**
   - For mutation endpoints (`POST /orders`, `POST /payments`), require the `Idempotency-Key` header with deduplication cache semantics (HTTP 409 Conflict on concurrent matching key; HTTP 200/201 on replay of settled key).
3. **Pagination Standards:**
   - Prefer cursor-based pagination for mutable and high-volume collections:
     - Query parameters: `cursor` (opaque base64 string), `limit` (default 20, max 100), `direction` (`forward` | `backward`).
     - Response envelope: `{ "data": [...], "pagination": { "next_cursor": "...", "has_more": true } }`.
4. **RFC 7807 Problem Details Error Envelope:**
   - Standardize all 4xx and 5xx responses:
     ```json
     {
       "type": "https://api.example.com/errors/validation-failed",
       "title": "Validation Failed",
       "status": 422,
       "detail": "The request body contains invalid parameters.",
       "instance": "/api/v1/orders/ord_123",
       "code": "VALIDATION_FAILED",
       "timestamp": "2026-11-06T12:00:00.000Z",
       "invalid_params": [
         { "name": "quantity", "reason": "Must be greater than 0" }
       ]
     }
     ```

### Phase 4: Mock Server & SDK Generation Readiness
1. **Prism / MSW Mock Configurations:** Provide realistic mock examples for every 200, 201, 400, 401, 403, 404, 409, 422, and 500 status code.
2. **Automated SDK Compatibility:** Ensure property identifiers use `camelCase` or `snake_case` consistently to support automated client generator tools (`openapi-typescript`, `openapi-generator`, `@hey-api/openapi-ts`).

## Rules & Constraints
- **Zero Ambiguity:** Every endpoint must define exact schemas for all request parameters, request bodies, and every potential HTTP response code.
- **Breaking Change Prohibition:** Never remove a field, rename a field, change a field type, or make an optional field required in existing API versions. Introduce a new schema version or optional additive fields.
- **Strict Headers:** Include `Content-Type: application/json; charset=utf-8` and require `Accept` headers on incoming calls.
- **Traceability:** Return a unique `X-Request-ID` or `traceparent` (W3C Trace Context) in all responses.

## Common Anti-Patterns
| Anti-Pattern | Correction |
| :--- | :--- |
| Returning 200 OK with `{ "error": "User not found" }` | Return appropriate HTTP status codes (404 Not Found) with an RFC 7807 problem details body. |
| Inconsistent pagination across endpoints | Standardize on cursor-based pagination with a uniform response metadata structure. |
| Floating point numbers for monetary calculations | Use integers representing cents or string-encoded arbitrary-precision decimals. |
| Using `PUT` for partial updates | Use `PATCH` for partial attribute updates and reserve `PUT` strictly for complete resource replacements. |
| Missing idempotency keys on payment or order submissions | Mandate `Idempotency-Key` headers on state-mutating requests to guard against network retries. |
