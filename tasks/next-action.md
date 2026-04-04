# NEXT ACTION

## SESSION
CLOSED

## NEXT_PERSONA
junior-dev

## NEXT_TASK
AKR-05 through AKR-13 (Sprint-04 P1-P3 AK-CogOS v2.0 remediation)

## CARRY_FORWARD_CONTEXT
- Session 005 closed with AK-CogOS v2.0 P0 complete (7 artifacts created/updated).
- P1-P3 tasks are next: AKR-05 (session summaries), AKR-07 (docs/ stubs), AKR-09 (command install
  — REQUIRES dry-run + AK approval BEFORE live run), AKR-10 (metrics), AKR-12 (already done).
- AKR-09 is HIGH RISK: run install-claude-commands.sh --dry-run first, show AK the diff, get explicit
  approval before live run. Never skip the pre-flight.
- Sprint-03 items (PQA-01..12, PGP-01..02, C-01..C-07 open items) remain deferred — do not start
  until sprint-04 AK-CogOS remediation (P1 minimum) is complete.
- docs/ planning artifacts (AKR-07, AKR-08) require discovery conversations with AK — stubs only until then.

## BLOCKERS_AND_ENV_LIMITATIONS
- AKR-09 blocked until AK approves post-dry-run diff.
- AKR-08 (docs/ population) blocked on /ba + /architect discovery sessions with AK.
- R-002: Anthropic API key not confirmed in this environment — smoke test still pending.

## HANDOFF_NOTE
Session 005 closed by claude-core. P0 remediation done. Next session starts with /session-open
then /junior-dev on AKR-05, AKR-07, AKR-09 (dry-run only), AKR-11 in parallel.
