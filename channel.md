# channel.md — Agent Communication Channel

## Purpose

This file is the shared communication bus between agents (personas and skills).
Each agent reads context here and writes its output status here.
The Architect and skill agents own the write gate.

---

## Current Status

```
session:        012
sprint:         sprint-10F
active_persona: junior-dev
last_skill_run: architect
last_updated:   2026-04-07 17:30:00 UTC
```

---

## Last Handoff

```yaml
from:    architect
to:      junior-dev
status:  PASS
message: |
  Sprint-10E + 10H complete. All imports clean. Committed to main.
  Next: Sprint-10F — workflows/engagement_scoping.py + menu Option 0.
  Gates satisfied: KF-NEW merged, ARCH-S-04 merged.
  Read tasks/next-action.md for full task spec.
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
