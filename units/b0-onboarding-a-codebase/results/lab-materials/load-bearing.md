# What's load-bearing here

Conventions that will break something real if violated, versus ones that are just
this repo's habit. Judgment call in each row; the "why" is what makes it checkable
by someone else later.

| Convention | Load-bearing? | Why |
|---|---|---|
| Never hand-edit `frontend/src/client/` | **Load-bearing.** | Auto-regenerated from the live backend OpenAPI schema on every backend route/model change (pre-commit hook + CI). Hand edits are silently discarded, not rejected — the failure mode is invisible, not loud. |
| Every schema change needs an Alembic migration | **Load-bearing.** | `alembic_version` is a row in Postgres, not a file. A model field with no migration works in a throwaway sqlite test DB and breaks against real Postgres. (Found the hard way in B1's ablation: a task requiring a new column scored 0% across every arm the first time, because the verifier never re-applied migrations between runs.) |
| Permission checks live inline in each route handler, not centralized | **Load-bearing, currently.** | No decorator or policy object exists to intercept. A new permission model (teams, roles) has to touch every handler in `items.py`, or the inline pattern has to be refactored into something centralized *first* — that refactor is itself a real design decision, not incidental to adding sharing. |
| Gitmoji-prefixed commit subjects (📝 ♻️ 🐛 💄 🔖 👷) | **Habit, not load-bearing.** | Cosmetic; nothing parses it. Follow it for review friction reasons (matches surrounding history), not because anything breaks if you don't. |
| `DATABASE_URL` as one connection string, not separate host/port/user/pass vars | **Load-bearing.** | Migrated to deliberately (#2184) after previously being separate. Reintroducing separate vars fights a change the maintainers already made on purpose. |
| `FASTAPI_ENV=development` set when running tests locally | **Load-bearing.** | Without it, `app.main` tries to mount a `frontend/` static directory that doesn't exist in a bare backend checkout and raises at import time — every test fails before running, for a reason that has nothing to do with the test. |
| pytest fixtures scoped `session`/`module` in `backend/tests/conftest.py` | **Load-bearing.** | The `db` fixture is `scope="session", autouse=True` — state accumulates across the whole test run unless a test cleans up after itself. Assuming per-test isolation (the more common pytest default) produces flaky, order-dependent failures. |
| Two type checkers configured (`mypy` and `ty`) | **Habit / in transition,** probably. | `ty` is Astral's newer, faster type checker; running both suggests a migration in progress rather than a permanent policy. Worth confirming before assuming both are required forever — this is exactly the kind of thing that ages out of a written map and needs a freshness check. |

## The honest budget

This map took real, bounded exploration: a directory listing, an unshallowed `git log`,
three config files, and one deliberately-triggered import error (the `FASTAPI_ENV` one,
found by running the test suite without it — see B1's own setup notes). That's cheap
because this repo is ~1500 commits and two apps, not the "400k lines" scale B0's own
question names. On a repo two orders of magnitude larger, the directory-listing-and-grep
approach here does not scale, and pretending it does is how brownfield harness work
gets budgeted like greenfield work and then runs over. The gate below tests whether a
map at *this* scale actually pays for itself; it does not claim the same technique
survives at 400k lines.
