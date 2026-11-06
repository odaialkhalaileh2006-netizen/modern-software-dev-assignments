# Week 4 Write-up

**Repo chosen** and link to your fork:
> bigskysoftware/htmx (https://github.com/bigskysoftware/htmx), v2.0.11, a JavaScript library. My fork: https://github.com/odaialkhalaileh2006-netizen/htmx

**File you wrote** (`AGENTS.md` or `CLAUDE.md`):
> `CLAUDE.md`, 21 lines, at the root of my fork (commit a2cee1ca: https://github.com/odaialkhalaileh2006-netizen/htmx/commit/a2cee1ca3ba726a576ef61a2c158b88e4be3b01c) and copied to `week4/CLAUDE.md`. I chose `CLAUDE.md` over `AGENTS.md` because the Claude Code memory docs say it is read on every version, while `AGENTS.md` is only read directly on newer versions.


## Part I: Exploration

| | Finding |
|---|---|
| Build / run | `npm install` (527 packages, 40s on my Windows machine; it rewrote 2 version lines in package-lock.json, which I restored). Nothing to build for tests. `npm run dist` builds `dist/` (from package.json; I did not run it). |
| Test | `npm test` runs lint, then types-check, then Chromium tests: 50 files, 868 passed, 0 failed, 3 skipped, about 31s, 99.98% coverage. One file: `npm test test/core/ajax.js` gave 77 passed, 1 skipped in 1.4s. No `CHROME_PATH` needed. |
| Lint / format | `npm run lint` and `npm run types-check` both ran clean (no output). `npm run format` is `eslint --fix` on the same files (from package.json; I did not run it). |
| Key directories and entry points | `src/htmx.js` is the whole library (one file, about 5,400 lines); `src/htmx.esm.d.ts` has the TypeScript types; package.json `main` points to `dist/htmx.esm.js`. Tests are in `test/core` and `test/attributes`, with shared helpers `make`, `makeServer`, `clearWorkArea` and `byId` in `test/util/util.js`. Docs are in `www/` (per CONTRIBUTING.md; I did not open it). |
| Unstated conventions | Tests use Mocha `describe`/`it` with chai `.should`, a fake server (`makeServer`, `this.server.respondWith`, `this.server.respond`) and `make('<html>')` to build elements. I read the first 30 lines of `test/core/ajax.js` and the helper definitions; I did not read other test files. `package-lock.json` is one release behind package.json (2.0.10 vs 2.0.11), so every `npm install` modifies it. CONTRIBUTING.md says `CHROME_PATH` must be set, but my tests ran without it. |
| Off-limits (generated, vendored) | `dist/` is built output but is committed (it is not in .gitignore), and CONTRIBUTING.md asks that PRs not include it. `node_modules/` and `coverage/` are git-ignored (.gitignore; git status was clean after my test run). The package-lock.json change from `npm install` should not be committed. I did not check for vendored code. |

**How you figured it out**: what you asked the agent, what you had to read yourself:
> I read `TESTING.md` and `CONTRIBUTING.md` myself and ran every build, test and lint command myself, keeping the output logs. I used Claude in the chat app as a guide: it checked GitHub raw files to see whether candidate repos already had an `AGENTS.md` or `CLAUDE.md` (TheAlgorithms/Python did, so I dropped it), compared the `dev` and `master` package.json scripts, and read the Claude Code docs for me. I did not use the agent inside the repo for exploration; I only ran it for Part III.


## Part II: The File

**Anything you deliberately left out**, and why:
> What htmx does beyond one sentence (it is in the README). Code style rules (eslint already enforces them). The internal structure of `src/htmx.js` (I did not read it, and the agent can read the file). `npm run test:ci` and `npm run test:all` (I did not run them). The rule that pull requests go to the `dev` branch (nothing in this assignment opens an upstream PR).

**The hardest call** on what to include:
> Whether to include rules from CONTRIBUTING.md that I could not test myself. I kept the ones with a clear source (no `dist/` in changes, tests and docs with behavior changes, no unasked refactors) and wrote "per CONTRIBUTING.md" on them, so the file does not claim more than I verified. I also kept the `CHROME_PATH` correction, since the docs and my own run disagree.


## Part III: Trying It Out

| # | Task | Did the agent use your commands and conventions? |
|---|---|---|
| 1 | "Run the full test suite and tell me the result", without naming a command. | It ran `npm test` and got 868 passed, 0 failed, 3 skipped, matching my own run. It reported coverage as 100% where my log says 99.98%. `npm test` is also the default guess for a Node repo, so this does not prove it read the file. `/context` showed `CLAUDE.md` loaded (462 tokens). `git status` was clean afterwards. |
| 2 | Add one test for an `hx-swap="outerHTML"` button to `test/core/ajax.js`, run only that file, change nothing else. | Only `test/core/ajax.js` changed (saved diff, 21 lines). It followed the file's pattern (`make`, `this.server.respondWith`, `this.server.respond`, `byId`, `.should`) and ran `npm test test/core/ajax.js`: 78 passed, 1 skipped. The first draft at the approval prompt asserted that `p1` was absent and then read it, which contradicts itself. The final diff was corrected, but I did not capture the transcript, so I cannot say whether it fixed this after a failing run. I did this on a throwaway branch (`scratch/week4-task2`), never pushed, then discarded it. |

**One thing you'd change** about the file after watching it get used:
> Add `byId` to the helper list. The agent used `byId` in its new test but my file did not mention it; it only found it by reading line 46 of `ajax.js`. It is defined in `test/util/util.js` with the other helpers. I made this change before committing, so the committed file already includes it.


## Submission
1. `Command (⌘) + F` for `TODO`. No results means you're done.
2. Push all changes to your remote repository and submit via Gradescope.