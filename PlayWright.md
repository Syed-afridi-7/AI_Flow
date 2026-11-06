E2E Test Your App (Playwright)

Set up end-to-end testing for this app with Playwright.

1. Install and configure Playwright for this stack. Add config for local + CI, with retries, traces on failure, and screenshots. 
2. Identify the critical user journeys from the codebase and List them for my approval BEFORE writing any tests. 
3. For each approved journey, write tests covering the happy path plus realistic failure states (bad input, expired session, network error, empty data). 
4. Use resilient selectors - prefer role-based or data-testid. Add the missing data-testid attributes to components where needed. 
5. Create an auth fixture so logged-in tests don't repeat the login flow every run. 
6. Add test data seeding and cleanup so tests are isolated and repeatable. 
7. Add npm scripts: test:e2e, test:e2e:ui, test:e2e:ci 8. Add a CI workflow that runs the suite on every PR.

Explain how to run everything. Flag any journey that can't be reliably tested and tell me why.