# channel.md — Agent Communication Channel

## Purpose

This file is the shared communication bus between agents (personas and skills).
Each agent reads context here and writes its output status here.
The Architect and skill agents own the write gate.

---

## Current Status

```
session:        012
sprint:         sprint-10B (pre-merge gate)
active_persona: architect
last_skill_run: session-open
last_updated:   2026-04-07 16:10:14 UTC
```

---

## Last Handoff

```yaml
from:    session-open
to:      architect
status:  PASS
message: |
  Session 012 opened. Fallback path used (MCP unavailable).
  Standup delivered. Handing off to /architect for:
  1. Comprehensive feature-wise status update (Status Update 1)
  2. Next-step plan with sprint priorities (Status Update 2)
  Ask AK if understood before proceeding to each update.
  After architect completes, next build sprint is 10E, 10F, or 10H.
```

---

## Queued Messages

<!-- Agents append messages here. Architect clears at session close. -->

---

## Sprint Packet Status

```
packet_ready:     false
codex_ready:      false
last_intake_run:  2026-04-07
```

---

## Usage

- Skills write their output envelope summary here after execution
- Architect reads here to understand current sprint state
- `/check-channel` reads this file and reports status to the team
- `/session-close` clears stale entries and archives the session state
