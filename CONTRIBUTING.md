# Contributing to AI_Flow

Thank you for your interest in contributing to **AI_Flow**!

AI_Flow is a community-driven repository of battle-tested prompt workflows designed for software engineers and AI pair programming assistants.

---

## 📋 Prompt Template Guidelines

When proposing or updating a template, make sure it adheres to our quality criteria:

1. **Role-Driven Framing:** Clearly define the AI's persona (e.g., Senior Product Manager, Principal Architect, AppSec Engineer).
2. **Explicit Two-Phase Safeguards:** High-impact tasks (e.g., refactoring, dead code deletion, error debugging, security auditing) must enforce an **Audit / Clarify First** phase before any code execution.
3. **Structured Deliverables:** Every template must specify exact numbered deliverables and expected output formats.
4. **Resilience & Rules:** Include constraints that explicitly prevent hallucinated requirements, out-of-scope edits, and premature fixes.
5. **No Filler:** Avoid wordy generic fluff. Prompts should be concise, authoritative, and direct.

---

## 🚀 Submitting Changes

1. **Fork the Repository:** Create a copy of the repository on your GitHub account.
2. **Create a Feature Branch:**
   ```bash
   git checkout -b feature/your-template-name
   ```
3. **Write Clean Conventional Commits:** Follow the standard in [`GIT.md`](GIT.md):
   ```bash
   git commit -m "docs(workflow): add automated performance audit template"
   ```
4. **Push & Open a Pull Request:** Describe the engineering scenario your template solves and why it produces better AI output than freeform prompting.

---

## ⚖️ Code of Conduct

Be welcoming, constructive, and respectful to all contributors.

