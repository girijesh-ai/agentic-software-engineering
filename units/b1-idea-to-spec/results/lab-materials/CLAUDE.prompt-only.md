# Working in this repo

This is a FastAPI + SQLModel + Postgres backend. When implementing a
requested change:

- Match the existing code style and patterns (see `app/api/routes/` for
  examples of how endpoints, permissions, and error handling are done
  here).
- Write it to actually work, not just to look plausible - run the tests
  before considering it done.
- Don't build more than what was asked. If the request is ambiguous,
  make the smallest reasonable choice rather than guessing at extra
  scope.
- Consider what should happen when things go wrong (bad input, missing
  permissions, edge cases), not only the success path.
