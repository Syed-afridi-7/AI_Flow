---
name: finops-token-optimizer
description: Use when optimizing LLM API costs, implementing static prompt prefix caching, designing token-efficient system instructions, pruning verbose context windows, routing prompts across cost-tiered models, or monitoring and budgeting token expenditures.
---

# FinOps Token Optimizer

## Overview
Establishes a rigorous financial operations (FinOps) and token compression protocol for Large Language Model (LLM) applications. Maximizes provider prompt cache hit-rates (slashing input token costs by up to 80-90%), prunes conversational slop and redundant instruction boilerplate, enforces model tiering and intelligent routing (fast/cheap models for drafting, deep reasoning models for auditing), and establishes hard token budget guardrails against runaway execution loops.

## When to Use
- **Trigger symptoms:** Escalating LLM API invoices across OpenAI, Anthropic, or Google Gemini; latency degradation caused by ingesting oversized context windows (>30,000 tokens); designing autonomous agent loops and background daemons running hundreds of turns daily; structuring system prompts that fail to trigger automatic or explicit prompt caching (>1,024 token static prefix); selecting model tiers for multi-agent workflows.
- **When NOT to use:** Low-frequency manual chats where total API spend is negligible (<$1/month); tasks requiring completely unconstrained open-ended creative prose without cost boundaries; or non-LLM infrastructure optimization.

## Instructions

Execute token optimization and FinOps engineering across five structured phases:

### Phase 1: Static Prefix Caching Architecture
1. **Cache Anchor Positioning:**
   - Place all immutable system instructions, developer personas, standard tools, and few-shot examples at the absolute top of the prompt.
   - Append volatile, dynamic data (user inputs, timestamps, conversational history, search results) strictly at the end of the context window.
   - Any dynamic modification in early tokens invalidates the entire subsequent prompt cache for that request.
2. **Provider Threshold Compliance:**
   - **Anthropic Claude:** Requires a minimum of 1,024 tokens to trigger prompt caching (`cache_control: {"type": "ephemeral"}`).
   - **Google Gemini:** Automatic implicit caching or explicit Context Caching requires minimum thresholds (32k on 1.5 Pro, or structured caching on Flash).
   - **OpenAI:** Automatic prompt caching activates for prompt prefixes with a minimum of 1,024 tokens.
   - Maintain a standardized static invariant prefix containing >= 1,024 tokens to guarantee cache eligibility across all major providers.

### Phase 2: Context Pruning & Prompt Compression
1. **Instruction Boiled-Down Density:**
   - Purge conversational filler, polite pleasantries ("Please consider...", "It is important to remember..."), and duplicated formatting instructions.
   - Convert verbose narrative rules into concise, high-density imperative bullet points or compact tables.
2. **Context Window Pruning:**
   - Strip unnecessary metadata from ingested files (e.g., remove import statements and test code from backend schemas when designing frontend UI).
   - Minify data payloads: Supply structured context in compact YAML or minified JSON rather than loose conversational descriptions or bulky markdown tables.
   - In conversational or agentic loops, employ sliding window history (retaining only the last 3-5 turns) coupled with periodic rolling summarization.

### Phase 3: Model Tiering & Intelligent Routing
1. **Two-Tier Model Allocation:**
   - **Tier 1 (Fast & Economical):** Use lightweight models (`gemini-2.5-flash`, `gpt-4o-mini`, `claude-3-5-haiku`) for high-volume, low-risk operational tasks:
     - First draft generation, text classification, email triage, data extraction, JSON normalization.
     - Price profile: ~$0.075 to $0.15 per 1M input tokens.
   - **Tier 2 (Deep Reasoning & Auditing):** Use frontier reasoning models (`claude-3-7-sonnet`, `gemini-2.5-pro`, `gpt-4o`, `o1/o3-mini`) for high-consequence, complex verification tasks:
     - Pre-release security auditing, complex architectural trade-offs, formal contract verification, adversarial code reviews.
     - Price profile: ~$3.00 to $15.00 per 1M input tokens.
2. **Dual-Agent Feedback Routing:**
   - Configure multi-agent pipelines such that Generator runs on Tier 1, while Validator runs on Tier 2. This delivers 80% cost reduction compared to running both passes on frontier reasoning models while preserving audit rigor.

### Phase 4: Output Token Economy & Structured Schemas
1. **Strict Response Bounds:**
   - Explicitly cap `max_tokens` on LLM API calls based on expected output schema dimensions.
2. **Compact Response Formatting:**
   - Demand structured JSON or compact markdown directly. Forbid models from echoing the user prompt, repeating boilerplate disclaimers, or prefixing outputs with narrative pleasantries ("Sure! Here is the plan you requested:").
3. **Early Stop Triggers:**
   - Configure explicit `stop_sequences` (e.g., `["```\n\n", "<!-- END -->"]`) to prevent models from generating trailing conversational filler.

### Phase 5: FinOps Observability & Guardrails
1. **Loop Circuit Breaker:**
   - Enforce an inviolable hard cap on autonomous agent iterations (`max_iterations = 2` or `3`). Runaway recursive loops must terminate automatically and raise an alert.
2. **Token Accounting & Cost Attribution:**
   - Log input tokens, cached input tokens, and output tokens per invocation.
   - Compute real-time cost savings from prompt caching:
     $$\text{Savings} = (\text{Cached Tokens} \times (\text{Base Price} - \text{Cached Price}))$$
   - Configure threshold alerts when hourly or daily spend exceeds predefined budgets.

## Rules & Constraints
- **Invariant Prefix Anchor:** Never insert dynamic timestamps, random IDs, or changing variables ahead of the static system prompt.
- **Minimum Cache Token Threshold:** Maintain at least 1,024 static tokens in cached system prompts to qualify for provider caching tiers.
- **Hard Iteration Caps:** Autonomous agent reflection loops must never exceed 3 iterations without human-in-the-loop sign-off.
- **Zero Echoing:** Responses must never echo the input prompt back to the client.
- **Model Right-Sizing:** Never route simple categorization, classification, or initial draft scaffolding to expensive Tier 2 reasoning models.

## Common Mistakes & Anti-Patterns
| Anti-Pattern | Severity | Correction |
| :--- | :--- | :--- |
| Dynamic timestamps inserted at prompt start | Critical | Move current date/time to the bottom of the prompt in the dynamic user block. |
| Running draft generation on frontier models | High | Use Tier 1 models (`flash` / `mini`) for drafting; reserve Tier 2 for auditing. |
| Infinite agent reflection loops without cap | Critical | Implement hard `max_iterations = 2` circuit breaker in agent runner. |
| Missing `cache_control` headers | High | Explicitly mark static system prompt blocks for ephemeral caching in API calls. |
| Verbose markdown explanations for machine data | Medium | Require compact JSON schemas to minimize output token consumption. |
| Ingesting full repositories into prompt context | High | Prune AST, isolate relevant symbols, and exclude lockfiles and test fixtures. |
