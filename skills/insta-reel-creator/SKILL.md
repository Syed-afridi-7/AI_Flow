---
name: insta-reel-creator
description: Use when generating high-retention 30-to-60-second spoken vertical video scripts (Instagram Reels, TikTok, YouTube Shorts), structuring 5-beat spoken timing, optimizing Hookscores, and sanitizing AI slop for natural human delivery.
---

# Instagram Reel Creator

## Overview
Transforms raw concepts, technical workflows, devlogs, or business ideas into production-ready, high-retention vertical video scripts (Instagram Reels, YouTube Shorts, TikTok). Adheres to a strict 5-beat retention curve, separates spoken audio from on-screen text (OST), computes deterministic Hookscores, and aggressively eliminates AI slop phrases to ensure believable, conversational delivery.

## When to Use
- **Trigger symptoms:** When creating short-form vertical video content, writing scripts for Instagram Reels/TikTok/Shorts, converting a product feature or bugfix into a devlog reel, crafting viral video hooks, or optimizing spoken pacing and on-screen text.
- **When NOT to use:** Long-form YouTube essays (>3 minutes), static carousel graphics without spoken video, or internal engineering documentation.

## Instructions

Execute script creation across five rigorous phases:

### Phase 1: Topic Discovery & Voice Extraction
1. **Identify the Core Single Truth:** A reel can only convey ONE core idea. Determine what happened, who is impacted, and the concrete metric, cost, or payoff.
2. **Determine Target Duration:** Default to 30–45 seconds (~65–110 spoken words at an energetic 140–160 WPM cadence).
3. **Establish Speaker Persona:** Select voice profile (e.g., pragmatic senior software engineer, gritty solo founder, sharp growth hacker). Enforce natural conversational speech, contractions (`don't`, `it's`, `we've`), and punchy sentence fragments.

### Phase 2: The 5-Beat Retention Architecture
Structure the script strictly according to the five temporal beats:
1. **Beat 1: The Hook (0:00 – 0:02):**
   - **Spoken Hook:** A bold, counter-intuitive statement or visceral question (8–14 words).
   - **On-Screen Text (OST):** Shorter, high-contrast headline (4–7 words) complementing—never duplicating—the spoken line.
   - **Visual Cue:** Physical movement or immediate screen state transition in frame 1 (no static face).
2. **Beat 2: The Stake (0:02 – 0:07):**
   - Clarify why the viewer must care right now. State the risk, cost, or unfair advantage in one punchy sentence.
3. **Beat 3: The Body / Mechanism (0:07 – 0:35):**
   - Break the explanation into 2–4 sequential sub-beats.
   - Enforce one idea per sub-beat with visual camera or screen angle changes every 3–5 seconds.
4. **Beat 4: The Payoff & CTA (0:35 – 0:42):**
   - Deliver the resolution promised by the hook.
   - Provide a single, low-friction call-to-action (e.g., "Comment `KEYWORD` for the repo", "Save this for your next deploy").
5. **Beat 5: The Infinite Loop (Last 3 seconds):**
   - End with a phrase that grammatically or semantically loops seamlessly back into the opening hook line.

### Phase 3: Hookscore Optimization
Generate and evaluate at least 3 distinct hook variations:
- Evaluate curiosity gap, emotional velocity, specificity of numbers/claims, and conciseness.
- Calculate composite Hookscore (0–100 scale). Require a minimum score of 85 to pass into production.

### Phase 4: Slop Sanitization
Scrub the entire script against the forbidden AI clichés:
- **Banned Openers:** "Here's the thing...", "In today's fast-paced world...", "Have you ever wondered...", "What if I told you..."
- **Banned Buzzwords:** "Game changer", "Unleash", "Dive into", "Supercharge", "Let's unpack", "Without further ado", "Delve", "Tapestry".
- **Syntax Scrubbing:** Replace passive academic phrasing with spoken active voice.

### Phase 5: Production Beat Sheet Export
Deliver the finalized script formatted as an actionable shoot sheet:
- Timestamp intervals (`0:00-0:02`, `0:02-0:07`, etc.).
- Speaker Spoken Lines (exact teleprompter text).
- On-Screen Text (OST) overlays with typographic emphasis tags.
- B-Roll / Visual Action directions.
- Word count and estimated duration metrics.

## Rules & Constraints
- **Word Count Budget:** Strict cap of 115 spoken words for 45-second reels; 80 words for 30-second reels. Never exceed 150 WPM.
- **Zero Throat-Clearing:** The script must start on the very first syllable of the hook without greetings ("Hey guys", "Welcome back").
- **Visual-Audio Asynchrony:** On-screen text must never mirror the spoken audio verbatim; it must summarize, anchor keywords, or provide visual contrast.
- **Seamless Loop:** The final sentence must flow directly into Beat 1 without an awkward pause or goodbye.

## Common Mistakes & Anti-Patterns
| Anti-Pattern | Correction |
| :--- | :--- |
| Starting with "Hey guys, today I want to share..." | Cut straight to the conflict or result in Frame 1. |
| Cramming 3 separate lessons into one 45s reel | Split into 3 independent reels; focus on one atomic takeaway. |
| Reading on-screen text identically to spoken line | Use OST for bold keyword anchors while spoken line explains context. |
| Ending with "Follow for more tips, bye!" | Kill the greeting; end on an infinite loop sentence leading to Beat 1. |
