# AI_Flow Multi-CLI Universal Installation & User Guide

AI_Flow provides native, first-class support for **7 major AI coding agent ecosystems and local LLMs**, including **Google Antigravity & Gemini IDE**, **OpenAI Codex CLI**, **xAI Grok CLI**, **OpenCode Interpreter**, **Anthropic Claude Code**, **Cursor AI**, **Open Agents Standard**, and **Ollama Local LLMs**.

---

## ⚡ Quick Start: Universal Windows Installer

Run the automated installer to configure all targets in a single command:

```powershell
# Copy Mode (Recommended for standalone isolation)
powershell -File scripts/install.ps1 -Target all

# Symlink / Junction Mode (Live development: changes in repo reflect immediately)
powershell -File scripts/install.ps1 -Target all -Symlink
```

You can also target specific CLI environments individually:
```powershell
powershell -File scripts/install.ps1 -Target antigravity
powershell -File scripts/install.ps1 -Target codex
powershell -File scripts/install.ps1 -Target grok
powershell -File scripts/install.ps1 -Target opencode
powershell -File scripts/install.ps1 -Target claude
powershell -File scripts/install.ps1 -Target cursor
powershell -File scripts/install.ps1 -Target agents
```

---

## 🧭 Target Verification & Filesystem Audit

AI_Flow includes an automated verification script that verifies all manifests, JSON schemas, and skills across all target locations:

```bash
python scripts/verify_install.py
```

Expected output:
```text
============================================================================
        AI_Flow Multi-CLI Target Filesystem Verification Audit
============================================================================
User Home Directory: C:\Users\<Username>
Repository Root:     E:\Instructions
AI_Flow Skills:      31 distinct skills registered

[*] Target 1: Google Antigravity & Gemini IDE...
[*] Target 2: OpenAI Codex CLI...
[*] Target 3: xAI Grok CLI...
[*] Target 4: OpenCode Interpreter...
[*] Target 5: Anthropic Claude Code...
[*] Target 6: Open Agents Standard...
[*] Target 7: Cursor AI...

----------------------------------------------------------------------------
AUDIT SUMMARY:
----------------------------------------------------------------------------
[PASS] Antigravity Skills (~/.gemini/antigravity/skills): All 31/31 AI_Flow skills present
[PASS] Antigravity CLI Skills (~/.gemini/antigravity-cli/skills): All 31/31 AI_Flow skills present
[PASS] Directory verified: Antigravity Plugin Dir (~/.gemini/config/plugins/ai-flow)
[PASS] Antigravity Plugin Embedded Skills: All 31/31 AI_Flow skills present
[PASS] Valid JSON file: Antigravity gemini-extension.json (name=ai-flow)
[PASS] Valid JSON file: Antigravity plugin.json (name=ai-flow)
[PASS] File verified: Antigravity GEMINI.md
[PASS] Codex Skills (~/.codex/skills): All 31/31 AI_Flow skills present
[PASS] Directory verified: Codex Plugin Dir (~/.codex/plugins/ai-flow)
[PASS] Codex Plugin Embedded Skills: All 31/31 AI_Flow skills present
[PASS] Valid JSON file: Codex plugin.json (name=ai-flow)
[PASS] Valid JSON file: Codex .codex-plugin/plugin.json (name=ai-flow)
[PASS] Directory verified: Grok Plugin Dir (~/.grok/installed-plugins/ai-flow)
[PASS] Grok Skills (~/.grok/installed-plugins/ai-flow/skills): All 31/31 AI_Flow skills present
[PASS] Valid JSON file: Grok plugin.json (name=ai-flow)
[PASS] File verified: Grok AGENTS.md
[PASS] OpenCode Skills (~/.config/opencode/skills): All 31/31 AI_Flow skills present
[PASS] File verified: OpenCode plugin script (~/.config/opencode/plugins/ai-flow.js)
[PASS] Claude Skills (~/.claude/skills): All 31/31 AI_Flow skills present
[PASS] Agents Skills (~/.agents/skills): All 31/31 AI_Flow skills present
[PASS] Cursor Skills (~/.cursor/skills): All 31/31 AI_Flow skills present
[PASS] File verified: Cursor Rule MDC (~/.cursor/rules/ai-flow.mdc)
============================================================================
🎉 100% AUDIT PASS: All 22/22 filesystem checks verified successfully!
============================================================================
```

---

## 🔧 CLI Ecosystem Specific Activation & User Guides

### 1. Google Antigravity CLI & Gemini IDE

- **Manifests:** `gemini-extension.json`, `plugin.json`, `GEMINI.md`
- **Installed Locations:**
  - Plugin Directory: `~/.gemini/config/plugins/ai-flow/`
  - Skills Directories: `~/.gemini/antigravity/skills/` and `~/.gemini/antigravity-cli/skills/`
- **How It Works:**
  - The Gemini Extension manifest (`gemini-extension.json`) declares extension metadata, context rules (`GEMINI.md`), and capability mappings.
  - The Antigravity CLI automatically discovers the 31 skills in `~/.gemini/antigravity-cli/skills/`.
  - In Gemini IDE or CLI, any natural language prompt matching skill triggers (e.g. *"Plan product"*, *"Design database schema"*, *"Security audit"*) immediately invokes the respective dual-agent workflow.

### 2. OpenAI Codex CLI

- **Manifests:** `.codex-plugin/plugin.json`, `plugin.json`
- **Installed Locations:**
  - Plugin Directory: `~/.codex/plugins/ai-flow/` (contains `.codex-plugin/plugin.json` and `skills/`)
  - Global Skills Directory: `~/.codex/skills/`
- **How It Works:**
  - OpenAI Codex discovers plugins in `~/.codex/plugins/` and skills in `~/.codex/skills/`.
  - When active, Codex recognizes all 30 standard skills plus the meta-orchestration skill `ai-flow`.

### 3. xAI Grok CLI

- **Manifests:** `plugin.json`, `AGENTS.md`
- **Installed Locations:**
  - Plugin Directory: `~/.grok/installed-plugins/ai-flow/`
- **How It Works:**
  - Grok CLI reads plugin definitions and instructions from `~/.grok/installed-plugins/ai-flow/`.
  - The embedded `AGENTS.md` provides complete persona contracts and adversarial auditing instructions.

### 4. OpenCode Interpreter

- **Plugin Script:** `.opencode/plugins/ai-flow.js`
- **Installed Locations:**
  - Script: `~/.config/opencode/plugins/ai-flow.js`
  - Skills Directory: `~/.config/opencode/skills/`
- **How It Works:**
  - OpenCode executes `ai-flow.js` on startup.
  - The plugin hooks into interpreter events (`onInit`, `preStep`, `postStep`, `onToolCall`), dynamically indexing and injecting the 31 AI_Flow skills into OpenCode's system prompt and tool registry.

### 5. Anthropic Claude Code

- **Manifests:** `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`
- **Installed Location:** `~/.claude/skills/`
- **Activation Options:**
  - **Local Direct:** Skills in `~/.claude/skills/` are immediately active in any `claude` session.
  - **Marketplace Add:**
    ```bash
    claude plugin marketplace add Syed-afridi-7/AI_Flow
    claude plugin add ai-flow
    ```

### 6. Local Ollama LLM Runtime

AI_Flow includes full support for running 100% offline with locally hosted open-weight models via **Ollama**.

#### Step 1: Build the Custom `ai-flow` Model
The repository includes a tuned `Modelfile` with preconfigured system prompts, dual-agent instructions, and decoding parameters (`temperature 0.2`, `top_p 0.95`):

```bash
# Build the model using Ollama
ollama create ai-flow -f Modelfile
```

#### Step 2: Run Skills with Ollama
Use `scripts/run.py` with the `--provider ollama` flag:

```bash
# Single-mode generation using local Ollama model
python scripts/run.py --provider ollama --skill prd-generator --input "Decentralized crypto invoice payment gateway"

# Autonomous Dual-Agent Mode (Generator & Validator peer review loop)
python scripts/run.py --provider ollama --mode dual --skill security-gap-audit --input "Audit JWT authentication and refresh rotation"

# Specify a custom pulled model (e.g. qwen2.5-coder:latest, deepseek-coder-v2, llama3.1)
python scripts/run.py --provider ollama --model qwen2.5-coder:latest --skill trd-generator --input "High-throughput telemetry ingestion service"
```

### 7. Cursor AI & Open Agents Standard

- **Cursor Rules:** `.cursor/rules/ai-flow.mdc` is installed to `~/.cursor/rules/ai-flow.mdc` and project workspaces, automatically enforcing 8-phase software lifecycle constraints, dual-agent peer review, and zero hallucination rules.
- **Skills Directory:** Installed to `~/.cursor/skills/` and `~/.agents/skills/` for universal interoperability across any agent respecting the Agent Skills specification.

---

## 🧪 Comprehensive Verification & Test Suite

Verify complete test coverage across the repository:

```bash
# 1. Full unit test suite (99 tests including Ollama provider and mock HTTP tests)
python -m unittest discover -s tests -p "test_*.py"

# 2. Agent Skills Open Specification compliance
node scripts/validate.js
powershell -File scripts/validate.ps1

# 3. Filesystem Multi-CLI Target Verification
python scripts/verify_install.py
```
