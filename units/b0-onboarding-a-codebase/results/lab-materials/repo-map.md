# Repo map — tiangolo/full-stack-fastapi-template

Written by exploring the repo cold: directory listing, `git log` (unshallowed, 1511
commits), `.pre-commit-config.yaml`, `CONTRIBUTING.md`, and the two Docker Compose
files. No prior familiarity assumed beyond what's checked in.

## Shape

Two apps sharing one OpenAPI contract, plus deployment glue:

```
backend/app/          FastAPI + SQLModel + Postgres
  models.py            Every table AND every request/response schema, one file
  crud.py               DB writes, thin wrappers over SQLModel
  api/routes/*.py       One router per resource (items, users, login, private, utils)
  api/deps.py           SessionDep, CurrentUser, get_current_active_superuser
  core/config.py        Settings (pydantic-settings, reads .env)
  core/db.py            engine + init_db (seeds the first superuser)
  core/security.py      password hashing, JWT create/decode
  alembic/versions/     one migration per schema change, applied in order

frontend/src/
  routes/               TanStack Router, file-based; `_layout` prefix = behind auth
  client/               GENERATED — see "Do not hand-edit" below
  components/<Resource>/  one folder per backend resource, mirrors api/routes/
  hooks/                 useAuth, custom query hooks

compose.yml + compose.override.yml   local dev: db, backend, frontend, adminer, mailpit
compose.deploy.yml                   production shape (Traefik, no dev bind-mounts)
```

Entry points for a task, by kind:

| You're changing... | Start reading here |
|---|---|
| A data field | `backend/app/models.py`, then the alembic migration you'll need |
| An API behavior | `backend/app/api/routes/<resource>.py` |
| Who can do what | `backend/app/api/deps.py` + the route handler (see "Permissions" below) |
| A UI screen | `frontend/src/routes/_layout/<resource>.tsx` |
| A UI component | `frontend/src/components/<Resource>/` |
| Local dev environment | `compose.yml`, `compose.override.yml`, `.env` |

## Permissions are not centralized

There is no `@requires_owner` decorator and no policy object. Every route handler in
`items.py` repeats the same two-line check inline:

```python
if not current_user.is_superuser and (item.owner_id != current_user.id):
    raise HTTPException(status_code=403, detail="Not enough permissions")
```

This is the single fact that matters most for extending this app's permission model
(teams, roles, sharing): there is no one place to change. Grep for `is_superuser` in
`api/routes/` before assuming a change is "just update the check."

## The frontend client is generated, not written

`frontend/src/client/` is produced by `scripts/generate-client.sh`, which *imports and
runs* the backend app in-process to read its live OpenAPI schema, then generates a
TypeScript client and runs the frontend linter. A pre-commit hook (`generate-frontend-sdk`)
re-runs this automatically whenever backend route/model files or `uv.lock` change.
Consequence: hand-editing anything under `frontend/src/client/` is invisible work — the
next backend change silently regenerates and discards it. If a task needs a new frontend
API method, the fix is a backend change, not a client edit.

## History says: this repo is trending toward less, not more

Skimming commit subjects past the automated noise (dependency-bump PRs and release-note
bumps are the majority of recent history and carry no design intent):

- `Remove Copier project generation` (#2430) — it used to be a project generator/template
  engine; that machinery was deliberately cut.
- `Migrate to DATABASE_URL instead of separate variables` (#2184) — collapsed several
  Postgres env vars into one connection string.
- `Simplify CORS configuration`, `Simplify Docker Compose deployment`,
  `Simplify database readiness checks` — three separate deliberate simplifications,
  not accidents.

The pattern across maintainer-authored commits (as opposed to bot-authored dependency
bumps) is consistently toward fewer moving parts. An agent proposing a new
configuration knob, a new env var, or a new layer of indirection is swimming against
this repo's own direction of travel, and that's worth surfacing before writing code,
not after review comments say so.
