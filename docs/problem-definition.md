---
Status: confirmed
Source: user-confirmed
Last confirmed with user: 2026-04-06
Owner: Product
Open questions: 0
---

# Problem Definition

## Primary User

Maher Hashash, CFE — Managing Director, GoodWork LLC, UAE. Solo forensic consulting practitioner with 17+ years experience (Big Four background, 40+ fraud risk assessments, 40+ investigations across Middle East government and private sectors). He is simultaneously the junior analyst, project manager, and partner on every case. Technical level: capable user, not a developer. Runs engagements across UAE, GCC, and India markets.

## User Pain / Problem

Maher spends 3–5 hours per engagement producing first drafts of deliverables that a junior associate at a staffed firm would produce in the same time — but he has no junior associate. Every investigation report, FRM risk register, due diligence report, sanctions screening memo, and client proposal is written from scratch, manually, with no structured support. He cannot take on more cases without this becoming the bottleneck that limits GoodWork's revenue.

Secondary problem: deliverable quality depends entirely on what Maher remembers to include on any given day. There is no structured review hierarchy enforcing that every risk is regulatory-mapped, every finding has a citation, every proposal has complete pricing. Quality is inconsistent across engagements.

## Current Workaround

Maher uses generic AI tools (ChatGPT, Claude.ai) to draft sections of reports. These produce generic output with no forensic methodology, no UAE regulatory grounding, no evidence chain enforcement, and no review layer. He discards most of the output and rewrites it himself. He also maintains his own templates and checklists in Word, updated manually.

## Why Current State Fails

- Generic AI tools have no forensic domain knowledge — no ACFE standards, no UAE regulatory context, no understanding of what makes a finding admissible vs inadmissible.
- No review layer — generic AI produces one-shot drafts with no PM or Partner quality gate.
- No case memory — each session starts from scratch; prior case context is lost.
- No audit trail — no immutable record of what was researched, reviewed, or approved.
- No bilingual output — Arabic deliverables require manual translation from English drafts.
- No structured intake — engagement scope is defined informally; edge cases and exclusions are often missed until the client asks a question mid-engagement.

## Success Outcome

Maher produces a partner-reviewed, regulation-cited, evidence-grounded first draft of any standard forensic deliverable in under 30 minutes of active engagement time, with a complete audit trail and bilingual output. He can run 3× as many concurrent cases without additional headcount.

## Non-Goals

- Not a multi-user platform — single practitioner only (Maher) in v1.
- Not a cloud SaaS product — runs locally; no client data leaves the machine.
- Not a replacement for Maher's professional judgment — Partner AI recommends; Maher decides.
- Not a general-purpose AI assistant — purpose-built for forensic consulting workflows only.
- Not a Decision Quality Enforcement Platform for financial institution investigation teams (separate product concept documented in Desktop/GoodWork/Investigative Tool/ — out of scope for this build).
