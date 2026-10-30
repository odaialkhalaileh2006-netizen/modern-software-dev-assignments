Trigger tests (Nemotron via fcc-claude, fresh session each)
v1 description, prompt 1 "add tests for the isLeapYear plugin": fired NO. Used npm test, no baseline, wrote 51 lines.
v1 description, forced /test-writer: followed baseline + coverage command, interrupted by me.
v2 description (trigger-first), prompt 1: fired NO. Tried npm test (denied), no skill load seen.
"What skills are available?": test-writer listed? yes with description? yes
Prompt 2 (toArray): fired NO (judged from behavior). Agent asked to overwrite test\plugin\toArray.test.js with about 65 added lines (Write, whole file), including a dozen padding tests. In the part I watched, I saw no baseline run or coverage check. The first thing I saw was the permission prompt to edit the file, so I refused (option 3, No).
Prompt 3 (minMax guard): fired NO. Full session reviewed. First message: "I'll explore the codebase... and then add appropriate safeguards." Agent searched the whole tree (100 files incl. .git hooks), read the minMax tests (72 lines), source (35 lines) and package.json, said the tests "look fairly comprehensive" but still planned to add "comprehensive test coverage", and tried npm test (forbidden by the skill; the same script failed in test 1). I interrupted before any edit. No baseline, no coverage table, and "nothing to add" was never considered.
Prompt 4 near-miss (explain minMax): did NOT fire. Agent explored the repo, read minMax/index.js, answered with an explanation; no tests, no edits. Passes trivially: the skill did not fire on prompts 1-3 either, so this does not show the description is narrow.
Summary: with Nemotron via fcc-claude, auto-triggering failed on all 4 attempts (prompt 1 on both description versions, prompts 2 and 3 on v2). The model listed test-writer with its description when asked, and followed its steps (baseline, coverage command) when I invoked /test-writer by hand.
Hypothesis (untested): the free model treats writing tests as something it can do without a skill.

End-to-end (/test-writer add tests for the isLeapYear plugin): the agent ran the whole suite first (93 suites, 794 tests), found 100% coverage, listed behaviors and quoted the skill's Section 4. Its first edit added 4 tests; two repeated rules already tested (1900/1800/2200 and 2400), so I rejected it and told it to keep only the 2 tests for new behaviors.

Fail-on-purpose: done for both new tests, each by the agent with no reminder from me. First test: three toBe(true) flipped to toBe(false), failed, flipped back. Second test: three toBe(false) flipped to toBe(true), failed, flipped back.