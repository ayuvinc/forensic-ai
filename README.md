# GoodWork Forensic AI

A private, local AI system that runs the full internal operations of a forensic consulting firm — from first client conversation to signed deliverable — on a single consultant's laptop. No cloud. No team. No data leaves your machine.

---

## What It Does

GoodWork Forensic AI gives a solo forensic consultant the output capacity of a staffed firm. It simulates a three-level internal review hierarchy — Junior Analyst, Project Manager, Partner — and produces structured, audit-trailed, CXO-grade deliverables across all major forensic service lines.

You organise all work into **Projects**. Each Project is a client engagement. Each Project can run one or more independent **workstreams** (Investigation Report, FRM Risk Register, Due Diligence, and more). All outputs accumulate under the same Project. You assemble the final client document yourself.

---

## Service Lines

| Workstream | Pipeline | What It Produces |
|---|---|---|
| **Investigation Report** | Full (3-agent) | Forensic investigation report — 9 types including AUP and Custom, 4 audience versions, ACFE-standard evidence chain |
| **FRM Risk Register** | Full (3-agent) | Fraud Risk Management Register — 8 modules, risk-rated, mapped to COSO / ISO 37001 / ACFE, UAE regulatory citations |
| **Due Diligence** | Assisted | DD screening memo — individual or entity, enhanced or standard depth |
| **Sanctions Screening** | Assisted | Sanctions screening report — OFAC, UN, EU lists |
| **Transaction Testing** | Assisted | Testing plan and findings — risk-based, random, or full population |
| **Policy / SOP** | Assisted | Internal compliance policy or procedure document, jurisdiction-aware |
| **Training Material** | Assisted | Staff training content from a case or compliance topic |
| **Client Proposal** | Assisted | 7-section engagement proposal with firm branding, credentials, and fee structure |
| **Proposal Deck** | Assisted | Slide-by-slide prompt kit to build the proposal PowerPoint |
| **Engagement Scoping** | Assisted | Scope of work document for ambiguous engagements |
| **Persona Review** | Standalone | How a CFO / Lawyer / UAE Regulator / Insurance Adjuster would challenge your report |

**Full pipeline** workflows run through Junior Analyst → Project Manager → Partner with revision loops, evidence chain enforcement, and full audit trail. **Assisted** workflows generate a complete deliverable in one AI pass with audit trail. Both produce .md and .docx output.

---

## The Two Arcs

**Arc 1 — Proposal** (before you are retained)
Use the Scope page to define the engagement, then generate a proposal deck. Once the client signs, you create a Project and work begins.

**Arc 2 — Engagement** (once you are retained)
Create a Project. Run as many workstreams as the engagement requires. All outputs live under the same Project. You decide what goes into the final client document.

---

## Before You Start

### What you need

**1. A computer running macOS or Windows**
- macOS: Terminal or iTerm2
- Windows: Windows Terminal or PowerShell

**2. Python 3.11 or later**
```bash
python3 --version
```
If not installed: download from [python.org](https://python.org). On Windows, tick "Add Python to PATH" during install.

**3. Two API keys**

| Key | Where to get it | Cost |
|---|---|---|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) → API Keys → Create | Pay-per-use (see cost guide below) |
| `TAVILY_API_KEY` | [app.tavily.com](https://app.tavily.com) → Sign up | 1,000 searches/month free |

---

## Installation

### Step 1 — Get the project folder
```bash
cd ~/forensic-ai
```

### Step 2 — Create a virtual environment
```bash
python3 -m venv venv
```
Activate it:
```bash
# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```
You will see `(venv)` at the start of your prompt. This is correct.

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```
Takes 2–3 minutes.

### Step 4 — Configure your API keys
```bash
# macOS / Linux
cp .env.example .env

# Windows
copy .env.example .env
```
Open `.env` in any text editor and fill in:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
TAVILY_API_KEY=tvly-your-key-here
```

### Step 5 — Verify
```bash
python3 -c "import anthropic, tavily, rich, pydantic, streamlit; print('All dependencies OK')"
```

---

## Running the App

```bash
cd ~/forensic-ai
source venv/bin/activate       # macOS/Linux
# venv\Scripts\activate        # Windows

streamlit run app.py
```

Your browser opens automatically at `http://localhost:8501`.

On first launch, the setup wizard walks you through:
- Firm name and logo
- Team member bios and credentials
- Pricing model and rates
- Standard terms and conditions

This is stored locally in `firm_profile/` and used in every proposal and report header.

---

## Sidebar Navigation

```
MAIN
  Engagements    ← create and manage Projects; launch workstreams
  Workspace      ← view all outputs under the active Project

PROPOSALS
  Scope          ← Arc 1 step 1: define the engagement scope
  Proposals      ← Arc 1 step 2: generate the proposal deck

MONITOR
  Case Tracker   ← status of all open and closed cases
  Activity Log   ← timestamped log of all actions

SETTINGS
  Team           ← manage firm profile and team credentials
  Settings       ← API keys, model tier, research mode

WORKFLOWS        ← direct access to any workstream
  Investigation Report
  FRM Risk Register
  Due Diligence
  Sanctions Screening
  Transaction Testing
  Policy / SOP
  Training Material
  Proposal Deck
  Persona Review
```

The normal path is: **Engagements → select or create a Project → Run Workflow**. The WORKFLOWS section gives direct access for power users.

---

## Your First FRM Risk Register

1. Open **Engagements** → create a new Project (give it a name, select FRM as a workstream)
2. From the Project detail panel, click **Run Workflow → FRM Risk Register**
3. Answer the intake questions: client industry, jurisdictions, modules in scope
4. The pipeline runs automatically:
   ```
   Junior Analyst   Researching fraud patterns and regulatory baseline...  ✓
   Project Manager  Reviewing risk coverage and citation quality...         ✓
   Partner          Validating UAE regulatory alignment...                  ✓
   ```
5. Output saved to the Project's workspace:
   ```
   F_Final/final_report.en.md
   F_Final/final_report.en.docx
   ```

The whole process takes 3–5 minutes.

---

## Output Files

Each workstream gets its own case folder under `cases/`. The folder follows an A–F structure:

```
cases/{case_id}/
  A_Engagement_Management/   intake.json, state.json, audit_log.jsonl
  B_Planning/                research plan, scope notes
  C_Fieldwork/               workpapers, interview notes
  D_Evidence/                indexed documents, evidence register
  E_Drafts/                  agent outputs (versioned: .v1, .v2, .v3)
  F_Final/                   final_report.en.md
                             final_report.en.docx
                             final_report.ar.md  (if Arabic selected)
```

The Workspace page shows all workstream outputs under the active Project with download links.

---

## Resume — If Something Is Interrupted

Full pipeline workstreams (Investigation Report, FRM Risk Register) checkpoint their state after each agent stage. If the run is interrupted, open the same workstream from Engagements and it will detect the unfinished state and offer to resume.

Assisted workstreams (DD, Sanctions, TT, Policy, Training, Proposal) complete in one pass. If interrupted, restart the workstream from the beginning.

---

## Cost Guide

| Mode | Junior | Project Manager | Partner | Typical cost per FRM |
|---|---|---|---|---|
| Economy | Haiku | Haiku | Sonnet | ~$0.05–0.15 |
| Balanced (default) | Haiku | Sonnet | Sonnet | ~$0.20–0.50 |
| Premium | Sonnet | Sonnet | Opus | ~$1.00–2.50 |

Set in Settings → Model Tier. FRM Risk Register and Expert Witness always use Opus for Partner regardless of tier.

Research mode: `knowledge_only` (default, no API calls to Tavily) or `live` (full web research). Set in Settings.

---

## CLI Mode (Advanced)

The original terminal interface is still available:
```bash
python run.py
```
This gives a 10-item numbered menu with the same workflows. Use it for scripting or if you prefer the terminal over the browser.

---

## Troubleshooting

**Browser does not open automatically**
Navigate to `http://localhost:8501` manually.

**"command not found: python3"**
Try `python` instead of `python3`. If neither works, install Python from [python.org](https://python.org).

**"ModuleNotFoundError"**
You are not in the virtual environment. Run:
```bash
source venv/bin/activate    # macOS/Linux
venv\Scripts\activate       # Windows
```

**"AuthenticationError" or "Invalid API key"**
Open `.env` and verify the key has no extra spaces or quotes. The file must be named exactly `.env`.

**"Tavily quota exceeded"**
You have used your 1,000 free monthly searches. Either upgrade at app.tavily.com or switch to `RESEARCH_MODE=knowledge_only` in Settings.

**Page shows an error panel instead of loading**
Check the error message. Most common cause: setup wizard was not completed. Go to Settings → Setup and complete it.

**Pipeline stopped mid-run**
For full pipeline workstreams, re-open the workstream from Engagements. It will offer to resume.

---

## Frequently Asked Questions

**Is my data sent anywhere?**
Only your prompts and research queries go to Anthropic (Claude API) and Tavily (search). All case files, project data, and firm credentials stay on your computer. Nothing is stored by the app on any server.

**Can I run multiple workstreams at the same time?**
Run one at a time to avoid API rate limits.

**Can I edit the reports after they are generated?**
Yes. The `.md` files are plain text. The `.docx` files open in Word. Edit freely — the original agent outputs are preserved separately in E_Drafts/.

**Can I use this without the Tavily key?**
Yes, with `RESEARCH_MODE=knowledge_only`. The regulatory and sanctions lookups use cached knowledge instead of live web calls. Research quality is reduced but the tool runs fully.

**How do I add a new client?**
Create a new Project in Engagements. Each Project is independent — different client, different folder, different audit trail.

---

## Quick Reference

```bash
# Start the app
cd ~/forensic-ai && source venv/bin/activate && streamlit run app.py

# CLI mode
cd ~/forensic-ai && source venv/bin/activate && python run.py

# Check API connectivity
python3 -c "import anthropic; anthropic.Anthropic().models.list(); print('Anthropic OK')"
```

---

*Built for GoodWork LLC — white-label distribution available*
