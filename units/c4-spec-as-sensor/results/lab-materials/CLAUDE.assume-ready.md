# Working in this repo

The database and mail service are already running. Implement the task
described in the prompt directly, then verify your work with the test command
named in the task before considering it done. If a command fails because the
environment genuinely isn't up, `docker compose up -d --wait db mailpit` and
`(cd backend && FASTAPI_ENV=development uv run bash scripts/prestart.sh)`
bring it up.
