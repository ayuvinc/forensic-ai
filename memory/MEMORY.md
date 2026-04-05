# Project Memory
# Persistent context that survives across sessions.
# Architect updates this at session close. All personas read it at session open.

---

## Project Identity

- **Name:** [PROJECT_NAME]
- **Stack:** [STACK]
- **Repo:** [REPO_URL]
- **Framework version:** [AK_COGOS_VERSION]

---

## Architectural Decisions

> Record key decisions that affect all future work. Format: decision + rationale + date.

<!-- Example:
- 2026-04-01: Chose Supabase over Firebase — need row-level security + PostgreSQL for complex queries
- 2026-04-02: API routes use /api/v1/ prefix — enables versioning without breaking clients
-->

---

## Patterns Established

> Patterns that Junior Dev must follow. Reference by name in task descriptions.

<!-- Example:
- **Auth pattern:** middleware checks session → redirects to /login if missing
- **Data fetch pattern:** server component → lib/queries.ts → Supabase client
- **Error pattern:** try/catch → log to console.error → return { error: message }
-->

---

## Known Constraints

> Hard limits that cannot be changed without PM approval.

<!-- Example:
- Max 3 API calls per page load (performance budget)
- No client-side Supabase access — all queries through server actions
- Mobile-first: all layouts must work at 375px before desktop
-->

---

## Tech Debt Register

> Items deferred intentionally. Include reason and session deferred.

<!-- Example:
- [ ] Session 2: Skipped input validation on /api/tasks — needs zod schemas (TASK-012)
- [ ] Session 3: Hard-coded admin email in seed script — move to env var
-->

---

## Cross-Session Context

<!-- Anything the next session's persona needs that doesn't fit in next-action.md -->
<!-- Architect clears and rewrites this section at each session close -->

No active context.

---

## Session History

| Session | Date | Focus | Key Outcomes |
|---------|------|-------|-------------|
<!-- Architect fills this at each session close -->
