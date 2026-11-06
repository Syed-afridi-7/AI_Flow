Write Clean Git Commits

Review my current changes (staged and unstaged) and organise them into clean commits.

1. Summarise what actually changed and why, grouped by intent. 
2. Split the work into atomic commits - one logical change each. If something mixes a fix and a refactor, separate them. 
3. For each commit write a Conventional Commits message: 
        type(scope): short imperative summary under 60 chars
        Then a blank line and a body explaining WHY the change was needed and any tradeoffs. 
        Mark breaking changes with BREAKING CHANGE :.

 4. Order the commits so the repo builds and tests pass at every single step. 
 5. Output the exact git commands to run in sequence, including which files go in which commit.

Types: feat, fix, refactor, perf, docs, test, chore, style, build, ci Never write vague messages like "update", "fix stuff", "changes" or "wip".