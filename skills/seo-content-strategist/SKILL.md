---
name: seo-content-strategist
description: Use when conducting comprehensive search intent mapping, topic cluster architecture, programmatic SEO keyword modeling, competitive SERP gap analysis, and Google EEAT-aligned content strategy before drafting organic content.
---

# SEO Content Strategist

## Overview
Architects data-driven, search-intent-aligned organic content strategies designed to capture search market share and withstand modern search algorithmic updates (Google Helpful Content, EEAT, and AI Overviews). Translates core domain expertise into comprehensive pillar-and-cluster topologies, identifies high-opportunity SERP content gaps, structures semantic on-page schemas, and specifies first-party original research requirements to maximize Information Gain.

## When to Use
- **Trigger symptoms:** When planning organic growth for a web application, designing content clusters for a documentation or blog hub, targeting commercial search terms, building programmatic SEO architectures, or preparing content briefs for engineering and marketing teams.
- **When NOT to use:** Short-form social media copy (use `social-copy-repurposer`), video scripting (use `insta-reel-creator`), or paid ad PPC campaigns.

## Instructions

Execute the SEO content strategy across four systematic phases:

### Phase 1: Search Intent & SERP Gap Analysis
1. **Primary Intent Classification:** Classify the core query into exact search intent:
   - *Informational* (how-to, conceptual, tutorials).
   - *Commercial Investigation* (best-of, comparisons, alternatives, benchmarks).
   - *Transactional* (pricing, buy, sign up, download).
   - *Navigational* (brand search, login, portal).
2. **SERP Anatomy Deconstruction:** Analyze the existing top 10 ranking URLs:
   - Identify ranking page formats (listicle, deep technical guide, tool page, interactive calculator).
   - Identify SERP features (Featured Snippets, People Also Ask, Video Carousels, AI Overviews).
   - Pinpoint SERP weaknesses: outdated content, lack of verifiable code examples, missing performance benchmarks, or shallow fluff.

### Phase 2: Pillar-and-Cluster (Hub & Spoke) Architecture
1. **Pillar Page Design:** Define the broad, authoritative umbrella topic (e.g., "The Complete Guide to Microservices in Go").
2. **Sub-Topic Cluster Mapping:** Map 4–8 tightly focused supporting articles (spokes) resolving specific long-tail queries (e.g., "Go gRPC connection pooling", "Distributed tracing in Go with OpenTelemetry").
3. **Internal Linking Graph:** Specify strict bi-directional linking topology:
   - Every cluster page links back to the pillar with descriptive, contextual anchor text.
   - The pillar links down to all cluster pages within dedicated section contexts.
   - Sibling cluster pages cross-link when resolving related sub-problems.

### Phase 3: Information Gain & Google EEAT Proof Points
Google's Helpful Content System penalizes commoditized AI content that merely summarizes existing SERP pages. Enforce positive **Information Gain**:
1. **Experience (First-Hand Testing):** Mandatory inclusion of real terminal outputs, actual error traces, or proprietary project screenshots.
2. **Expertise & Original Data:** Require concrete benchmarks, latency graphs, or quantitative trade-offs rather than generic theoretical advice.
3. **Authoritativeness & Trust:** Cite official documentation, primary RFC specifications, or recognized core maintainers. Include author bio schema.

### Phase 4: Semantic Content Brief & Technical On-Page Specifications
1. **Meta & Title Tag Engineering:**
   - Title tag: 50–60 characters, target keyword frontloaded, compelling emotional/numeric hook.
   - Meta description: 140–155 characters, clear value proposition with a distinct call to click.
   - Canonical URL and OpenGraph / Twitter card tags.
2. **Header Hierarchy (H1, H2, H3):**
   - Single H1 containing primary keyword variant.
   - Logical, nested H2 and H3 sections targeting secondary keywords and PAA (People Also Ask) questions.
3. **Structured Data / Schema.org:**
   - Define exact JSON-LD schemas: `TechArticle`, `Article`, `FAQPage`, `HowTo`, or `BreadcrumbList`.

## Rules & Constraints
- **Zero Keyword Stuffing:** Write naturally for human practitioners first, optimizing for semantic entity coverage rather than raw keyword repetition.
- **Mandatory Information Gain:** Every content piece must introduce at least one original insight, benchmark, proprietary workflow, or real-world case study not present in the existing top 10 search results.
- **Strict Header Nesting:** Never skip heading levels (e.g., do not place an H3 directly under H1 without an intervening H2).
- **Search Intent Purity:** Never mix incompatible intents (e.g., do not attempt to rank an aggressive sales page for an informational "what is" query).

## Common Mistakes & Anti-Patterns
| Anti-Pattern | Correction |
| :--- | :--- |
| Writing a 3,000-word generic article that regurgitates Wikipedia | Focus on a 1,200-word piece packed with verifiable code, latency benchmarks, and production edge cases. |
| Neglecting internal linking across related cluster articles | Implement explicit hub-and-spoke bi-directional anchor links. |
| Missing schema markup | Provide validated JSON-LD schema (`Article`, `FAQPage`, `BreadcrumbList`) for every page. |
| Targeting keywords without verifying SERP intent | Inspect live SERP to determine whether Google rewards documentation, tool pages, or long-form guides. |
