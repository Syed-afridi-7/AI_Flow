---
name: devops-docker-deploy
description: Use when containerizing web applications, writing multi-stage Dockerfiles, structuring production Docker Compose topologies, configuring VPS deploy scripts, hardening container security, or optimizing image layer caching for minimal deployment footprint.
---

# DevOps Docker Deploy

## Overview
Provides a production-grade containerization and deployment engineering protocol. Guides the creation of minimal, secure Open Container Initiative (OCI) images, resilient Docker Compose topologies, and zero-downtime VPS deployment pipelines. Ensures containers follow the principle of least privilege, run without root rights, include robust healthchecks, handle OS signals correctly via PID 1 init processes, and minimize layer cache invalidation.

## When to Use
- **Trigger symptoms:** Containerizing Node.js, Python, Go, Rust, or Next.js applications for staging or production; restructuring oversized Docker images (>1GB down to <100MB); fixing Docker build cache misses; configuring single-node VPS topologies (e.g., DigitalOcean, Hetzner, AWS EC2); securing containers against container escape or root privilege escalation; writing automated zero-downtime deployment scripts.
- **When NOT to use:** Deploying purely static frontends to managed CDN edge platforms (Cloudflare Pages, Vercel) where container runtimes are unneeded; serverless functions (AWS Lambda); or enterprise multi-tenant Kubernetes clusters requiring Helm charts and custom CRD operators.

## Instructions

Execute containerization and deployment engineering across five standardized phases:

### Phase 1: Multi-Stage Dockerfile Architecture
1. **Base Image Selection:**
   - Default to minimal, security-patched base images (e.g., `alpine:3.x`, `node:20-alpine`, `python:3.11-slim`, `distroless/static-debian12`, or `scratch` for statically compiled Go/Rust).
   - Pin exact minor versions or SHA256 digests; avoid mutable `:latest` tags.
2. **Stage Separation:**
   - **Stage 1 (Builder / Dependencies):** Install toolchains, compilers, dev-dependencies, and run build/bundling commands (`npm run build`, `cargo build --release`, `go build`).
   - **Stage 2 (Runtime Runner):** Copy only build artifacts, compiled binaries, and production-only dependencies into a clean base image. Purge package manager caches, temporary headers, and dev tooling.
3. **Layer Cache Optimization:**
   - Order instructions from lowest-frequency of change to highest.
   - Copy dependency definitions first (`package*.json`, `go.mod`, `Cargo.lock`, `requirements.txt`).
   - Run dependency installation (`npm ci --only=production`, `go mod download`, `pip install --no-cache-dir`) before copying application source code (`COPY . .`).

### Phase 2: Container Security Hardening
1. **Non-Root Execution:**
   - Explicitly create a non-system group and user with limited permissions:
     ```dockerfile
     RUN addgroup -S appgroup && adduser -S appuser -G appgroup
     USER appuser
     ```
   - Never allow production containers to run as `root` (UID 0).
2. **Process Initialization & Signal Forwarding (PID 1):**
   - Utilize a lightweight init system (`tini` or `dumb-init`) to handle reap zombie child processes and correctly forward `SIGTERM` and `SIGINT` signals for graceful shutdowns:
     ```dockerfile
     ENTRYPOINT ["/sbin/tini", "--"]
     CMD ["node", "dist/server.js"]
     ```
3. **Secrets & Environment Isolation:**
   - Never embed credentials, API tokens, or `.env` files into Docker images using `ENV` or build `ARG`.
   - Inject secrets at container runtime via environment files or Docker secrets.
4. **Healthcheck Definition:**
   - Mandate an explicit `HEALTHCHECK` directive verifying application liveliness:
     ```dockerfile
     HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
       CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1
     ```

### Phase 3: File System & Build Context Sanitization
1. Author a comprehensive `.dockerignore` file excluding:
   - Dependency caches: `node_modules`, `vendor/`, `target/`, `.venv`
   - Version control & docs: `.git`, `.github`, `docs/`, `*.md`
   - Secrets & local configs: `.env*`, `*.pem`, `*.key`, `id_rsa`
   - Testing & coverage: `coverage/`, `tests/`, `*.test.js`
   - OS metadata: `.DS_Store`, `Thumbs.db`

### Phase 4: Production Docker Compose Topology
1. **Network Segmentation:**
   - Define custom bridge networks isolating public-facing ingress from internal datastores:
     - `frontend_net`: Connects reverse proxy and web applications.
     - `backend_net`: Connects web applications, workers, and databases (internal only).
2. **Data Persistence & Volumes:**
   - Configure named volumes for persistent datastores (PostgreSQL, Redis, Meilisearch).
   - Enforce explicit file ownership and backup mounts.
3. **Resource Quotas & Restart Policies:**
   - Set container restart policies: `restart: unless-stopped`.
   - Define CPU and memory hard limits under `deploy.resources.limits` to prevent noisy neighbors or runaway memory leaks from crashing the host node.
4. **Log Rotation Configuration:**
   - Enforce host-level or service-level Docker log driver rotation:
     ```yaml
     logging:
       driver: "json-file"
       options:
         max-size: "10m"
         max-file: "3"
     ```

### Phase 5: Zero-Downtime VPS Deployment Automation
1. **Deployment Pipeline (`deploy.sh`):**
   - Author an idempotent bash deployment script:
     - Pull latest git commit or pre-built container image.
     - Run database migrations in an ephemeral migration container (`docker compose run --rm migrations`).
     - Spin up new service containers with rolling restart (`docker compose up -d --no-deps --build web`).
     - Poll the `/health` endpoint until healthy (timeout after 60s).
     - If healthcheck fails, trigger automated rollback to the previous commit / image tag.
     - Prune dangling images safely (`docker image prune -f`).

## Rules & Constraints
- **Zero Root Execution:** Every production runtime image must explicitly declare `USER <non-root>`.
- **Zero Secrets in Layers:** No API keys, passwords, private SSH keys, or JWT secrets may exist in any Docker layer or commit history.
- **Layer Count Discipline:** Consolidate consecutive shell commands (`RUN apt-get update && apt-get install ... && rm -rf /var/lib/apt/lists/*`) into single atomic layers.
- **Deterministic Tags:** Base images must specify exact version tags or hashes; never rely on `:latest`.
- **Log Quotas:** All production compose services must configure log rotation to prevent disk exhaustion.

## Common Mistakes & Anti-Patterns
| Anti-Pattern | Severity | Correction |
| :--- | :--- | :--- |
| Running container as `root` (UID 0) | High | Create an unprivileged user/group (`appuser:appgroup`) and switch with `USER`. |
| Copying source code before dependency files | Medium | Copy `package.json` / `go.mod` first, run install, then copy source code. |
| Missing `.dockerignore` file | High | Exclude `node_modules`, `.git`, `.env*` to prevent bloated context and secrets leaks. |
| Direct `node index.js` without init process | Medium | Wrap with `tini` or `dumb-init` to handle zombie processes and signal termination. |
| Hardcoding database credentials in compose | High | Use environment variable interpolation (`${DB_PASSWORD}`) with a local `.env.production`. |
| Unbounded container memory limits | Critical | Define `mem_limit` or `deploy.resources.limits.memory` to avoid Linux OOM killer panic. |
