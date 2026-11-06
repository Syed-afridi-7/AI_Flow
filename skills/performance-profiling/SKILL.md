---
name: performance-profiling
description: Use when diagnosing and resolving performance bottlenecks across web applications and backend runtimes, optimizing Core Web Vitals (LCP, CLS, INP), analyzing heap memory leaks, optimizing CPU-bound event loops, or conducting database query plan analysis (EXPLAIN ANALYZE).
---

# Performance Profiling

## Overview
Acts as a Principal Performance Engineer to systematically diagnose, benchmark, and resolve performance regressions across frontend client applications, Node.js / backend runtimes, and relational database queries. Enforces empirical measurement over speculative optimization, targeting Google Core Web Vitals (LCP, CLS, INP), server-side Time to First Byte (TTFB), Node.js event loop lag, memory leaks in heap allocations, and database query execution plans (`EXPLAIN (ANALYZE, BUFFERS)`).

## When to Use
- **Trigger symptoms:** Slow page load speeds (LCP > 2.5s), layout instability during render (CLS > 0.1), unresponsive user interactions (INP > 200ms), excessive client JavaScript bundle sizes (>250KB initial gzip), backend memory leaks leading to Out-Of-Memory (OOM) container crashes, high CPU utilization on Node.js/Python event loops, or slow database queries blocking HTTP request workers.
- **When NOT to use:** Writing general unit tests without benchmarking, architecting high-level greenfield system topologies (use `system-architecture`), or drafting UI/UX visual style guides.

## Instructions

Execute performance profiling and optimization across five structured phases:

### Phase 1: Baseline Metrics & Empirical Profiling
1. **Frontend Core Web Vitals Capture:**
   - **Largest Contentful Paint (LCP):** Target $\le 2.5\text{s}$ (p75 on mobile 4G). Identify whether LCP is bounded by TTFB, resource load delay, resource load duration, or element render delay.
   - **Cumulative Layout Shift (CLS):** Target $\le 0.1$. Detect dynamic content insertion, unsized images/embeds, and web font FOIT/FOUT swaps.
   - **Interaction to Next Paint (INP):** Target $\le 200\text{ms}$. Identify long tasks (>50ms) on the main thread during input handling.
2. **Backend Runtime Diagnostics:**
   - Measure server-side TTFB (target $\le 200\text{ms}$).
   - Measure Node.js event loop delay (target $\le 20\text{ms}$).
   - Record V8 heap memory usage and allocation timelines.
3. **Database Query Profiling:**
   - Execute `EXPLAIN (ANALYZE, BUFFERS)` on slow queries to determine execution time, sequential scans vs. index scans, and buffer cache hit ratio.

### Phase 2: Frontend Bundle & Rendering Optimization
1. **Critical Rendering Path Acceleration:**
   - Eliminate render-blocking CSS and synchronous `<script>` tags in `<head>`.
   - Apply `preconnect` and `dns-prefetch` resource hints to critical third-party origins (e.g., fonts, CDN assets).
   - Ensure explicit `width` and `height` (or CSS `aspect-ratio`) on all `<img>`, `<video>`, and iframe elements to prevent layout shifts.
   - Preload the LCP hero image: `<link rel="preload" as="image" href="..." fetchpriority="high">`.
2. **Bundle Chunking & Tree-Shaking:**
   - Analyze bundle composition using webpack-bundle-analyzer or rollup-plugin-visualizer.
   - Implement route-based and interaction-based dynamic imports (`React.lazy()`, `import()`).
   - Replace bloated dependencies with lightweight alternatives (e.g., `date-fns` instead of `moment.js`).

### Phase 3: Runtime Memory & CPU De-bottlenecking
1. **JavaScript Main Thread Optimization:**
   - Break up long tasks (>50ms) using `scheduler.yield()` or `requestIdleCallback()`.
   - Offload expensive computations (data parsing, image manipulation, encryption) to Web Workers or background worker threads.
   - Eliminate forced synchronous layouts ("layout thrashing") by batching DOM reads before DOM writes.
2. **Heap Memory Leak Remediation:**
   - Detect detached DOM nodes and unreleased closures in browser heap snapshots.
   - Ensure all event listeners, `setInterval` timers, and WebSocket subscriptions are explicitly destroyed on component unmount (`useEffect` cleanup).

### Phase 4: Backend & Database Query Tuning
1. **Node.js / Server Event Loop Unblocking:**
   - Replace synchronous I/O operations (`fs.readFileSync`, synchronous crypto hashing) with non-blocking asynchronous APIs or thread pools.
   - Tune connection pool sizes to prevent worker thread saturation.
2. **Query Plan Execution Tuning:**
   - Convert Sequential Scans on large tables to targeted Index Scans or Bitmap Index Scans.
   - Add covering indexes with `INCLUDE` clauses to satisfy queries purely from the index tree without table heap visits.
   - Eliminate N+1 query loops using dataloaders, ORM eager loading (`select_related`, `preload`), or bulk queries.

### Phase 5: Verification & Regression Guarding
1. **Before-and-After Benchmark Assertion:** Document exact metric improvements under identical network/CPU throttling conditions (e.g., Simulated 4G, 4x CPU Slowdown).
2. **CI Performance Budgets:** Implement automated budget enforcement via Lighthouse CI, Playwright performance metrics, or k6 load tests.

## Rules & Constraints
- **Evidence-Based Remediations:** Never optimize without a baseline trace (DevTools performance recording, clinic.js flamegraph, or `EXPLAIN ANALYZE` output).
- **No Degradation of User Experience:** Optimizations must not sacrifice visual fidelity, accessibility (WCAG AA), or functional correctness.
- **Strict Network Conditions:** Web Vitals evaluations must be verified under simulated throttling (Mobile 4G, 4x CPU slowdown) to reflect realistic user devices.

## Common Anti-Patterns
| Anti-Pattern | Correction |
| :--- | :--- |
| Optimizing code speculatively without profiling traces | Profile first: collect Chrome DevTools trace or backend flamegraph before modifying code. |
| Neglecting `width` and `height` attributes on images | Set explicit `width`, `height`, or CSS `aspect-ratio` on all media elements to eliminate CLS. |
| Lazy-loading the above-the-fold hero image | Never set `loading="lazy"` on LCP images; preload with `fetchpriority="high"`. |
| Running synchronous CPU-heavy loops on the Node.js event loop | Offload CPU-intensive operations to Worker Threads or break up tasks with micro-delays. |
| Fixing slow queries by adding arbitrary single-column indexes | Analyze `EXPLAIN (ANALYZE, BUFFERS)` to build optimal composite or covering indexes. |
