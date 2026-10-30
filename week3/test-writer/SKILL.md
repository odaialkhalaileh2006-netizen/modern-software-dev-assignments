---
name: test-writer
description: Use when the user asks to add tests, write tests, or improve coverage for a function or plugin, or wants it protected against regressions or silent breakage (for example "add tests for the X plugin" or "X needs better coverage"). Writes new unit tests in an existing JavaScript repo, first checking what current tests and coverage already cover, and reporting "nothing to add" when they are enough. Not for explaining code, reviewing a change, or fixing a failing test.
---

# Test writer

Add tests for one function or plugin. The goal is verified behavior, not a bigger test count. "Nothing to add" is a valid result.

Commands below assume Jest. Check package.json first; if the repo uses another runner, translate them.

## 1. Orient
- Read the `scripts` in package.json for the test and lint commands.
- Find the target's source file and its existing test file. Read the top of the test file: imports, setup, helpers. Reuse them. Do not add imports for things the setup already provides.
- If no test file exists, say so and ask where new tests should live.

## 2. Baseline (before changing anything)
- Run the whole suite once with `npx jest --coverage=false`. Save the output to a file outside the repo and read only the last 12 lines.
- Record suites and tests passed. If something already fails, stop and report it. Do not fix it.
- Do not use `npm test` for quick checks. It may run the suite several times under different time zones and enforce coverage.

## 3. What is already covered
- Coverage for the target only, as a plain table:
  `npx jest <test file> --coverage --coverageReporters=text --collectCoverageFrom=<source file>`
  Read only the table row for the source file. Other reporters print walls of warnings.
- List the existing test names, then read the assertions of any that sound relevant. A name is not proof of what is asserted.

## 4. Decide what to test
- If coverage on the target is 100% and every behavior you can name already has an assertion, stop and report "nothing to add", listing what you checked. Do not write a test just to have something to show.
- If coverage is 100%, still list the code's behaviors: each option, each branch, and edge cases such as equal values, swapped inputs, empty or default arguments. Write tests only for behaviors that no assertion checks. Full coverage means lines ran, not that behavior was verified.
- If you find behavior nobody documented or promised, such as an invalid option that silently falls through to a default, do not write a test that locks it in. Flag it and ask whether it is intended.
- If a new test shows the code is wrong, report it. Do not change the source to make the test pass.

## 5. Write the tests
- Match the repo: plain `test('name', () => { ... })` blocks and fixed dates (for example `new Date(2011, 3, 2, 3, 4, 5, 10)`), never the current time. If the code depends on today's date, use the repo's date-mocking helper.
- One behavior per test, with a name that says the behavior. Add them to the existing test file, at the end.
- Do not copy `.toBe(false, 'message')`: `toBe` takes one argument, so the message is ignored.
- End the file with a newline.

## 6. Prove it
- Run only the new test: `npx jest <test file> --coverage=false -t "<new test name>"`
- A passing test proves little. Flip the expected value, rerun, and confirm it fails. Flip it back.
- Lint: `npx eslint --rule "linebreak-style: off" <test file>`. Empty output means clean. On Windows the files often have CRLF and the line-ending rule fires on every line.
- Run the whole suite again. Expect the old totals plus the number of tests you added.

## 7. Do not
- Do not run `eslint --fix` on existing files. It rewrites line endings and buries the real change.
- Do not include `package-lock.json` in the change. `npm install` can rewrite it.
- Do not lower or work around the repo's coverage rules.

## Report
End with: target, baseline totals, what was already covered, tests added (or "nothing to add" and why), anything flagged, final totals.
