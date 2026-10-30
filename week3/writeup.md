# Week 3 Write-up

**Skill name**, and the repo you targeted:
> `test-writer` (`week3/test-writer/SKILL.md`), targeting `iamkun/dayjs` (shallow clone at commit `436bde0`, 2026-09-15, kept outside this repo at `C:\dev\dayjs`).

Setup: Claude Code run through the Free Claude Code proxy (`fcc-claude`) with the free model `nvidia/nemotron-3-super-120b-a12b`, on Windows with PowerShell and a Python 3.12.10 venv in `week3`. The skill is authored in `week3/test-writer/` and was copied to `C:\dev\dayjs\.claude\skills\test-writer\` for testing; the two copies have the same SHA-256 hash. Supporting evidence is in `week3/evidence/`.


## Part I: The Workflow

**What the workflow is**, and why it's worth encoding:
> A test writer. Given one function or plugin in a JavaScript repo, it works out what the existing tests already cover, decides whether anything is missing, adds tests in the repo's own style, and proves they work. I would run it again for any plugin and any Jest repo, and otherwise the same checklist gets re-explained in chat every time.

**The decision point** in it (what the agent has to judge, not just execute):
> Whether to write anything at all. If line coverage is already 100% and every behavior has an assertion, the right answer is "nothing to add". When coverage is full, the agent still has to list the code's behaviors and test only those that no assertion checks, and it has to flag undocumented accidents (such as an invalid option that silently falls through to a default) instead of locking them in with a test.

**What you learned running it manually** that you would not have guessed:
> I ran it by hand on the dayjs `isBetween` plugin first (`evidence/manual-run-notes.md`, `evidence/manual-run.diff`).
> - Baseline: 93 suites, 794 tests passed.
> - The test file is 688 lines with 12 tests, and its names suggested everything was covered. Coverage for the plugin was 100% in every column, so line coverage said nothing about gaps.
> - I added one behavior test (same date as both bounds, expects false with the default `()`), saw it fail when I flipped the expected value on purpose, then restored it. Total: 795 tests.
> - Things I would not have guessed: `eslint` reported 694 errors, 693 of them CRLF line endings that Git on Windows created (the repo wants LF) and one real missing final newline; `npm install` rewrote `package-lock.json`, which must not end up in the change; and an invalid inclusivity string such as `'x'` silently counts as inclusive, an accident I would flag and not pin down with a test.


## Part II: The Skill

**Your description**, verbatim:
```
Use when the user asks to add tests, write tests, or improve coverage for a function or plugin, or wants it protected against regressions or silent breakage (for example "add tests for the X plugin" or "X needs better coverage"). Writes new unit tests in an existing JavaScript repo, first checking what current tests and coverage already cover, and reporting "nothing to add" when they are enough. Not for explaining code, reviewing a change, or fixing a failing test.
```

**Why it's worded that way** (what a user would type to trigger it):
> It opens with "Use when" and the phrases a person would type: "add tests", "write tests", "improve coverage", and "protected against regressions or silent breakage", plus two example requests ("add tests for the X plugin", "X needs better coverage"). The second sentence says what it does differently from just asking for tests: check what already exists first, and report "nothing to add" when that is enough. The last sentence ("Not for explaining code, reviewing a change, or fixing a failing test") is aimed at the near-miss prompt. Version 1 (381 characters) started with what the skill does and put the trigger second; version 2 (469 characters) moved the trigger first. Neither fired automatically on this model (see Part III).

**Judgment encoded in the body** (what it says to do when things are ambiguous, and what not to do):
> `SKILL.md` is 52 lines in eight sections: Orient, Baseline, What is already covered, Decide what to test, Write the tests, Prove it, Do not, Report.
> - Coverage is 100% and every behavior is asserted: stop and report "nothing to add", listing what was checked. Do not write a test just to have something to show.
> - At 100% coverage, still list the behaviors (options, branches, equal values, swapped inputs, defaults) and test only what no assertion checks. Full coverage means lines ran, not that behavior was verified.
> - Undocumented behavior, for example an invalid option that falls through to a default: flag it and ask; do not lock it in with a test.
> - A new test shows a bug: report it and do not change the source.
> - No test file exists, or the suite already fails at baseline: say so and stop (ask where tests belong; do not fix existing failures).
> - Do not use `npm test` for quick checks, do not run `eslint --fix` on existing files, do not include `package-lock.json` in the change, and do not lower the repo's coverage rules.
> - Exact commands cover the deterministic parts: whole-suite baseline, single-file coverage with `--coverageReporters=text`, a single test with `-t`, and lint with `--rule "linebreak-style: off"`.

**Supporting files**, if any, and why they aren't inline:

| File | Contents | Why it's separate |
|---|---|---|
| (none) | n/a | The body is 52 lines, short enough to stay inline; splitting it would add a file read for no saving. |


## Part III: Testing

**Triggering:**

| Prompt | Should fire? | Did it? |
|---|---|---|
| `add tests for the isLeapYear plugin` | Yes | No, on both description versions. v1: ran `npm test` (it failed), no baseline or coverage check, replaced the 3-line test with a 51-line one. v2: read the tests and source, tried `npm test` (I denied it). |
| `toArray needs better coverage, can u sort that` | Yes | No (judged from behavior). It asked to overwrite `test\plugin\toArray.test.js` with about 65 added lines and a dozen padding tests; I rejected the edit. |
| `I'm worried a refactor could silently break minMax. Can you guard against that?` | Yes | No. It searched the whole tree, said the existing tests look fairly comprehensive, still planned to add "comprehensive" tests, and tried `npm test`; I interrupted before any edit. |
| `explain how the minMax plugin picks the earliest date` | No (near-miss) | Did not fire (correct), but this proves little because nothing fired on the other prompts either. It explained the code and wrote no tests. |

Method: this interface shows no explicit "skill loaded" line, even when I invoked the skill by name, so I judged each run by behavior. A whole-suite baseline, `--coverageReporters=text`, no `npm test`, and a report ending in "nothing to add" or a justified list counted as following the skill; `npm test` or going straight to padded tests counted as not following it. Every trigger test started in a fresh session. I reset the clone with `git checkout -- .` after trigger test 1, the only one where an edit was applied; in the others I refused or interrupted before any edit. Full notes are in `evidence/trigger-log.md`.

Findings:
- 0 of 4 should-fire attempts triggered the skill automatically (the first prompt twice, the other two once each).
- It is not a loading problem: `/skills` listed `test-writer`, and asking "What skills are available?" listed it with its description. A control skill (`secret-phrase`, holding only a made-up phrase) did fire from a plain question on the same setup.
- Invoking the skill by name worked (see the end-to-end run).
- Hypothesis, untested: the model believes it can write tests without help, so it does not reach for a skill; the control skill held information the model could not know. Rewording from v1 to v2 made no visible difference, and I stopped there instead of rewording until something fired. I did not try a stronger model.

**End-to-end run** on your repo, and the result:
```
Prompt:          /test-writer add tests for the isLeapYear plugin (dayjs clone, commit 436bde0)
Baseline:        whole suite, 93 suites / 794 tests passed
Coverage:        src/plugin/isLeapYear 100% (text reporter)
Existing tests:  one test, 2 assertions (years 2000 and 2100)
First proposal:  4 tests; two repeated rules already asserted (1900/1800/2200 and 2400/1600),
                 so I rejected it and told the agent to keep only the other two
Tests added:     2 tests, 6 assertions
                 - year divisible by 4 but not by 100 (2004, 2020, 1996) -> true
                 - year not divisible by 4 (2001, 2002, 2003) -> false
Fail on purpose: done for both new tests; each was flipped, failed, then restored,
                 with no reminder from me
Lint:            npx eslint --rule "linebreak-style: off" -> no issues
Final suite:     93 suites / 796 tests passed (794 + 2)
Diff:            12 added lines in test/plugin/isLeapYear.test.js (evidence/e2e.diff)
```

Where it fell short: the agent first listed the two redundant tests as "missing behaviors" and treated them as redundant only after I told it so. Its final report said nothing was flagged and mentioned the dropped cases only as redundant per my instruction. Also, I interrupted the first invocation after the baseline and coverage commands had been re-run several times (a wrapper in my setup shortens command output, so the agent repeated commands), then typed the same command again in the same session and the agent carried on from its earlier results. Some commands in that first invocation ran in auto mode.

An informal comparison on the same plugin: trigger test 1 (skill not used) added 6 tests and 51 lines, did no baseline, and ran `npm test`; the skill run added 2 tests and 12 lines, with baseline, coverage, fail-on-purpose and lint, and never ran `npm test`. This is one run each and not controlled: the first ran in auto mode, and the skill run needed one correction from me.

### What I would change next
- Section 4 should say that a different input is not a different behavior: write one test per rule or branch outcome and skip inputs that repeat a rule already asserted.
- Section 2 should require the whole suite, not one file (one earlier forced invocation ran only the target file).
- Try automatic triggering on a stronger model, and run a controlled comparison with the skill on and off.

### Limitations
- One model, one repo and one end-to-end target; no controlled baseline.
- Trigger results are judged from behavior, and the second one only from the edit the agent proposed.
- Some runs used auto mode: the first trigger test and the first end-to-end invocation.
- The submitted skill is the version I tested; I did not apply the changes listed above.


## Submission
1. Template placeholders: none left (I searched this file for the placeholder word and found no results).
2. The skill directory itself is committed under `week3/test-writer/` (`SKILL.md`, no supporting files).
3. Remote: my fork of the course assignments repo (`origin`, branch `master`). Gradescope submission and collaborator invitations do not apply, because I am self-studying and am not enrolled.