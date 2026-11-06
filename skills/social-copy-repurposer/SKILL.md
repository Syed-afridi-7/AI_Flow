---
name: social-copy-repurposer
description: Use when transforming long-form content (blog posts, engineering docs, podcasts, whitepapers, PRDs) into platform-native micro-content across LinkedIn carousels, X/Twitter threads, newsletter snippets, and viral social hooks.
---

# Social Copy Repurposer

## Overview
Atomizes long-form technical assets (engineering blog posts, architectural decisions, PRDs, whitepapers, podcast transcripts) into high-engagement, platform-native micro-content. Tailors tone, formatting, character constraints, and psychological hooks for LinkedIn, X/Twitter, and developer newsletters while ruthlessly eliminating generic AI copywriting clichés.

## When to Use
- **Trigger symptoms:** When syndicating an engineering post, converting a GitHub release or architectural doc into social posts, repurposing founder devlogs across LinkedIn and Twitter, generating viral technical threads, or creating newsletter teaser snippets.
- **When NOT to use:** Writing long-form blog articles from scratch (use `seo-content-strategist`), scripting short-form spoken videos (use `insta-reel-creator`), or writing customer support emails.

## Instructions

Execute cross-platform copy repurposing across four structured phases:

### Phase 1: Core Insight Extraction & Angle Modeling
1. **Isolate Atomic Insights:** Extract 3–5 self-contained, counter-intuitive, or high-value insights from the source material.
2. **Identify Proof Points:** Anchor each insight to a real metric, benchmark, customer story, code snippet, or architectural diagram.
3. **Draft Multi-Angle Hooks:** Create 3 distinct opening angles for each platform:
   - *The Counter-Intuitive Truth:* Challenges conventional wisdom.
   - *The Hard-Earned War Story:* "We broke production, here is what we learned."
   - *The Actionable Cheat Sheet / Framework:* Step-by-step tactical playbook.

### Phase 2: Platform-Native Transformation
Adapt each insight to the specific mechanics and reading habits of each platform:
1. **LinkedIn Post & PDF Carousel:**
   - **The 3-Line Hook:** Hook before the "...see more" fold (under 210 characters).
   - **Readability & Whitespace:** 1–2 sentence paragraphs, generous line breaks, bulleted key takeaways.
   - **Document Carousel:** 6–10 slide PDF storyboard with bold headlines (<8 words) and tight explanatory subtext (<30 words per slide).
   - **Engagement Question:** Natural conversational closer inviting peer perspectives.
2. **X / Twitter Thread:**
   - **Lead Tweet:** High-impact hook containing a specific data point, outcome, or provocative premise (<280 characters).
   - **Thread Structure:** 5–8 tweets. Each tweet must deliver standalone value. Use code snippets, bullet points, or ASCII diagrams.
   - **Closing Tweet:** TL;DR summary and a single link back to the primary source or repository.
3. **Developer Newsletter / Substack Teaser:**
   - **Subject Line:** Urgent, curious, or benefit-driven (<50 characters).
   - **Executive TL;DR:** 3 bullet points summarizing the core problem and solution.
   - **Narrative Bridge:** 2 conversational paragraphs building curiosity toward the full article.

### Phase 3: Slop Sanitization & Voice Enforcement
Purge all synthetic copy patterns:
- Ban generic AI filler: "In today's fast-paced world", "Game changer", "Unleash", "Dive into", "Let's unpack", "Without further ado".
- Remove artificial emojis at the start of every single line.
- Enforce active voice, pragmatic engineering vocabulary, and specific technical nouns.

### Phase 4: Packaging & Distribution Metadata
Deliver ready-to-publish assets including:
- Character and slide counts.
- Recommended visual asset pairings (charts, terminal screenshots, architecture sketches).
- Optimal posting timeframes and distribution sequencing.

## Rules & Constraints
- **Platform Native First:** Never broadcast the exact same text across different platforms. Format, tone, and character lengths must reflect native audience culture.
- **Standalone Value:** Every thread tweet or carousel slide must provide tangible insight on its own, even if the reader never clicks the external link.
- **No Link in First Post:** For LinkedIn, recommend placing links in the comments or in a post-edit pass to prevent algorithmic reach throttling.
- **Zero Sycophancy:** Avoid breathless exaggeration ("mind-blowing", "revolutionary"). Let the concrete facts, numbers, and code speak for themselves.

## Common Mistakes & Anti-Patterns
| Anti-Pattern | Correction |
| :--- | :--- |
| Copy-pasting a tweet thread directly into LinkedIn | Reformat with professional storytelling cadence and generous whitespace before the "...see more" fold. |
| Using 15 hashtags on LinkedIn or Twitter | Restrict to 3–5 relevant, niche hashtags. |
| Dropping an external URL in the first 2 lines of a post | Deliver complete in-feed value first; place external link as an optional deep-dive. |
| Starting with "I am thrilled to announce..." | Open with the problem solved, the quantitative outcome, or the architectural insight. |
