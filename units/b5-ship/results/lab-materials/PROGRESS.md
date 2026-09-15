# Progress log

## Session 1 (previous)

- Implemented F1 (list team members). Ran its test, passed. Committed.
- Started F2 (rename team). Wrote the endpoint and permission check.
  Ran out of context before running F2's test or starting F3.

## Where things actually stand right now

Read `features.json` for the machine-readable status. In short: F1 is done
and verified. F2 has code but its test has not been run since the last
change - do not assume it works. F3 has no code at all yet.

## What's next

1. Run `init.sh` to get the environment up.
2. Run every feature's `verify` command in `features.json`, in order, and
   trust the actual output over what the status field says - the status
   field reflects what the previous session believed, not a guarantee.
3. Fix whatever F2's test reveals.
4. Implement F3 from its description in `features.json`.
5. Update `features.json`'s status fields and this log before finishing.
