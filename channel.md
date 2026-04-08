# channel.md — Agent Communication Channel

## Purpose

This file is the shared communication bus between agents (personas and skills).
Each agent reads context here and writes its output status here.
The Architect and skill agents own the write gate.

---

## Current Status

```
session:        014
sprint:         sprint-10L
active_persona: junior-dev
last_skill_run: session-open
last_updated:   2026-04-07 18:00:00 UTC
```

---

## Last Handoff

```yaml
from:    architect
to:      AK
status:  PASS
message: |
  Sprint-10F complete. engagement_scoping.py + Option 0 built and merged to main.
  All 14 menu options import clean.
  Sprint-10E + 10H + Sprint-10F archived to releases/completed-tasks.md.
  todo.md decongested.
  Next: P7-GATE — AK must run python run.py with live API keys (FRM smoke test).
  Gate passes → Sprint-10D (FRM redesign) unblocked.
  Read tasks/next-action.md for options.
```

---

## Queued Messages

<!-- Agents append messages here. Architect clears at session close. -->

---

## Sprint Packet Status

```
packet_ready:     true
codex_ready:      false
last_intake_run:  2026-04-07
```

---

## Usage

- Skills write their output envelope summary here after execution
- Architect reads here to understand current sprint state
- `/check-channel` reads this file and reports status to the team
- `/session-close` clears stale entries and archives the session state
