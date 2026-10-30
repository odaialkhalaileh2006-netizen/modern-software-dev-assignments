Manual run: dayjs isBetween (commit 436bde0)
1. Run the suite first to get a baseline (93 suites, 794 tests).
2. Look at what exists: test names, then coverage. Names are not proof.
3. Coverage was already 100% on the plugin. Be willing to say "nothing to add".
4. 100% coverage does not mean every behavior is tested; look for behaviors.
5. Don't test accidents (nonsense inclusivity strings): flag them instead.
6. Match the repo style: fixed dates, plain test(...), no new imports. Don't copy toBe(false, 'msg').
7. Run a single test with: npx jest <file> --coverage=false -t "<name>"
8. A new test must fail once on purpose before it is trusted.
9. Coverage: use --coverageReporters=text and read only the table row.
10. Windows: lint with --rule "linebreak-style: off"; never run eslint --fix on old files.
11. End the file with a newline.
12. Run the full suite at the end. Expect old total + number of new tests.
13. npm install rewrites package-lock.json. Do not include it in a change.
