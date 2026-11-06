# Project
- htmx adds AJAX and other behavior to HTML through attributes like `hx-get`; this repo is the library itself.
- All library code is the single file `src/htmx.js` (about 5,400 lines); `src/htmx.esm.d.ts` holds its TypeScript types.
- Tests are in `test/core` and `test/attributes`; shared helpers (`make`, `makeServer`, `clearWorkArea`, `byId`) are in `test/util/util.js`.

# Commands
- Install: `npm install` (rewrites package-lock.json, never commit that)
- Lint: `npm run lint` (eslint on src/htmx.js, test/ and scripts/; prints nothing when clean; `npm run format` auto-fixes)
- Type check: `npm run types-check` (tsc on src/htmx.js; prints nothing when clean)
- Full test: `npm test` (lint, then types-check, then Chromium tests; about 30s; first run downloads Chromium)
- One test file: `npm test test/core/ajax.js` (runs one test file in about 1.4 seconds)

# Gotchas
- `CHROME_PATH` is not needed: Playwright installs its own Chromium during `npm test`, even though CONTRIBUTING.md says to set it.
- `dist/` is built output (`npm run dist`); don't include it in changes (per CONTRIBUTING.md).

# Conventions
- A behavior change needs a test in `test/core` or `test/attributes` and docs in `www/` (per CONTRIBUTING.md).
- Never leave `it.only` in a test file; eslint warns about it (per TESTING.md).
- Don't refactor unasked: upstream closes refactors that change no behavior (per CONTRIBUTING.md). 
- Tests use Mocha `describe`/`it` with `.should` assertions. Copy the pattern in `test/core/ajax.js`: `makeServer()` in `beforeEach`, `this.server.respondWith(...)`, `make('<button hx-get=...>')`, `this.server.respond()`, `clearWorkArea()` in `beforeEach` and `afterEach`.