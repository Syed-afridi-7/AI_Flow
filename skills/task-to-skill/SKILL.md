---
name: task-to-skill
description: Use when turning a completed engineering workflow, recurring process, or established problem-solving pattern into a permanent, reusable Agent Skill.
---

# Task to Skill Converter

## Overview
Converts a completed task or repeated sequence of instructions into a standalone, reusable Agent Skill compliant with the Agent Skills Open Specification. Captures the exact triggers, steps, rules, and failure modes so future agents execute it reliably with zero prior context.

## When to Use
- **Trigger symptoms:** When a user says "turn this into a skill", "save this workflow so you remember it next time", or when an engineer solves a tricky problem that will recur across projects.
- **When NOT to use:** One-off, project-specific solutions that cannot be generalized, or simple mechanical tasks enforceable with basic linting scripts.

## Instructions

Analyze the completed task and generate a new `SKILL.md` with these 7 components:

1. **Name:** Lowercase alphanumeric and hyphens only (`^[a-z0-9-]+$`), action-oriented (e.g., `condition-based-waiting`, `database-migration-rollback`).
2. **Description (Frontmatter):**
   - Must begin with `"Use when..."`.
   - Written in third person.
   - Strictly describes the problem symptoms, triggers, and situational context.
   - **Crucial:** Never summarize the workflow in the description; keep it under 500 characters.
3. **Overview & Principle:** 1-2 sentence core mental model.
4. **Step-by-Step Instructions:** Numbered, sequential actions written for an agent with zero prior context. Include pre-flight checks, input gathering, and ordering.
5. **Rules & Constraints:** Hard boundary rules, prohibitions ("what must never happen"), and rationalization tables counteracting common shortcuts.
6. **Output Format & Template:** The exact structure, code template, or artifact shape the skill must produce.
7. **Failure Modes & Troubleshooting:** Top 3-5 failure modes, how agents commonly fail the task, and how to recover.

## Rules & Constraints
- The generated skill must be self-contained: assume the executing agent has no access to the previous chat history.
- Never write narrative stories about "how we did it today"; write an authoritative, reusable reference specification.

