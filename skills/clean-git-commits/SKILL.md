---
name: clean-git-commits
description: Use when staging changes, splitting work into atomic commits, writing Conventional Commits messages, or preparing clean git pull request histories.
---

# Clean Git Commits

## Overview
Organizes staged and unstaged changes into clean, atomic commits following the Conventional Commits specification. Ensures that every individual commit is self-contained, passes builds and tests, and communicates the rationale behind the change.

## When to Use
- **Trigger symptoms:** When preparing a pull request, after completing a feature or bugfix, when git working directory has mixed changes, or when the user says "organize my commits", "write commit messages", or "clean up my git changes".
- **When NOT to use:** Routine `git stash` operations or discarding temporary local experimentation.

## Instructions

Follow this 5-step sequence:

### Step 1: Intent Summarization
Analyze all modified files (`git status` and `git diff`). Group related changes by their underlying engineering intent (e.g., bug fix vs. documentation update vs. refactoring).

### Step 2: Atomic Separation
Split changes into atomic commits:
- Exactly **one logical change** per commit.
- If a file mixes a bugfix and a refactor, unstage and separate them into distinct commits.
- Group complementary changes together (e.g., an API change and its matching unit test belong in the same commit).

### Step 3: Conventional Commit Formatting
Author each commit message adhering to this structure:
```
<type>(<optional scope>): <imperative summary under 60 chars>

<blank line>
<Detailed body explaining WHY the change was needed, what was altered, and any technical tradeoffs.>

<blank line>
[BREAKING CHANGE: <description of breaking changes if applicable>]
```

#### Allowed Types:
- `feat`: A new user-facing feature.
- `fix`: A bug fix.
- `refactor`: Code change that neither fixes a bug nor adds a feature.
- `perf`: Performance improvement.
- `docs`: Documentation-only updates.
- `test`: Adding or correcting tests.
- `chore`: Tooling, configs, or auxiliary changes that do not modify src/test.
- `build`: Build system or external dependency changes.
- `ci`: CI configuration files and scripts.

### Step 4: Step-by-Step Build Order
Order the commit sequence so that the application builds cleanly and all automated tests pass at **every individual commit**. Never introduce a broken intermediate commit state.

### Step 5: Exact Git Execution Sequence
Output the exact sequence of shell commands to execute, including:
```bash
git add <specific-files>
git commit -m "<type>(<scope>): <summary>" -m "<body>"
```

## Prohibitions & Red Flags
- ❌ **No Vague Messages:** Never use messages like `"update"`, `"fix stuff"`, `"wip"`, or `"clean code"`.
- ❌ **No Mega-Commits:** Never combine unrelated changes (e.g., adding a feature + updating 10 dependencies) into one commit.
- ❌ **No Broken States:** Never commit a change that fails tests with the excuse "it will be fixed in the next commit".

## Rationalization Table
| Excuse / Shortcut | Reality |
| :--- | :--- |
| "It's all part of my session, one commit is fine." | Mega-commits make `git bisect` and code review painful. Split them. |
| "The body explanation isn't necessary." | The commit title says WHAT changed; the body explains WHY. Future maintainers need the WHY. |
| "I'll format the commits later with rebase." | Doing it right immediately saves rebase conflicts and time. |

