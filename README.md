# Forensic Consulting Framework

A Claude-powered AI system that simulates a full forensic consulting firm — Junior Analyst → Project Manager → Partner — running entirely in your terminal. Every case, draft, and output is saved locally with a full audit trail.

---

## What You Can Do With This

| # | Menu Option | What It Produces |
|---|-------------|-----------------|
| 1 | New Case Intake | Structured case file from a conversation |
| 2 | Investigation Report | Full forensic investigation report (English; Arabic generated when Arabic language is selected at intake) |
| 3 | Persona Review | How a CFO / Lawyer / Regulator / Insurer would challenge your report |
| 4 | Policy / SOP Generator | Internal compliance policy or procedure document |
| 5 | Training Material | Staff training content from a case or topic |
| **6** | **FRM Risk Register** | **Fraud Risk Register mapped to UAE regulations — flagship feature** |
| 7 | Client Proposal | Engagement letter / proposal document |
| 8 | PPT Prompt Pack | Slide-by-slide prompt kit to build a PowerPoint in Claude |
| 9 | Case Tracker | View status of all open and closed cases |
| 10 | Browse SOPs | Read saved policies and procedures |

---

## Before You Start — What You Need

### 1. A computer running macOS or Windows
- macOS: Terminal (built in) or iTerm2
- Windows: Windows Terminal or PowerShell (not Command Prompt)

### 2. Python 3.11 or later

**Check if you have it:**
```
python3 --version
```
If the output says `Python 3.11.x` or higher, you're good.

**If not installed:**
- macOS: Go to [python.org/downloads](https://python.org/downloads) and download the latest installer
- Windows: Same — download from python.org, and tick "Add Python to PATH" during install

### 3. Two API keys (free accounts available)

| Key | Where to get it | Free tier |
|-----|----------------|-----------|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) → API Keys → Create | Pay-per-use (very low cost) |
| `TAVILY_API_KEY` | [app.tavily.com](https://app.tavily.com) → Sign up → API Keys | 1,000 searches/month free |

**Getting your Anthropic key (step by step):**
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up or log in
3. Click your name in the top right → **API Keys**
4. Click **Create Key** — give it a name like "forensic-ai"
5. Copy the key (starts with `sk-ant-...`) — **you won't see it again**

**Getting your Tavily key:**
1. Go to [app.tavily.com](https://app.tavily.com)
2. Sign up (free)
3. Your API key is on the dashboard (starts with `tvly-...`)

---

## Installation — Step by Step

### Step 1: Open your terminal

- **macOS**: Press `Cmd + Space`, type `Terminal`, press Enter
- **Windows**: Press `Win + X`, click **Windows Terminal**

### Step 2: Go to the project folder

If someone sent you a zip file, unzip it first, then:

```bash
cd ~/forensic-ai
```

If you put it somewhere else, replace `~/forensic-ai` with the actual path. For example:
- macOS: `cd ~/Downloads/forensic-ai`
- Windows: `cd C:\Users\YourName\Downloads\forensic-ai`

### Step 3: Create a virtual environment (keeps everything clean)

```bash
python3 -m venv venv
```

Then activate it:

**macOS / Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

You'll see `(venv)` appear at the start of your terminal prompt. This is correct.

### Step 4: Install dependencies

```bash
pip install -r requirements.txt
```

This installs all required libraries. It takes about 1–2 minutes.

### Step 5: Set up your API keys

Copy the example file:

**macOS / Linux:**
```bash
cp .env.example .env
```

**Windows:**
```bash
copy .env.example .env
```

Now open the `.env` file in any text editor (Notepad, TextEdit, VS Code) and fill in your keys:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
TAVILY_API_KEY=tvly-your-key-here
```

Save the file.

### Step 6: Verify the installation

```bash
python3 -c "import anthropic, tavily, rich, pydantic; print('All dependencies OK')"
```

You should see: `All dependencies OK`

---

## Running the App

Every time you want to use the tool:

```bash
cd ~/forensic-ai
source venv/bin/activate    # macOS/Linux (skip this line on Windows: run venv\Scripts\activate instead)
python run.py
```

You'll see the main menu:

```
╔══════════════════════════════════════════╗
║   Forensic Consulting           ║
║   AI-Powered Case Management             ║
╠══════════════════════════════════════════╣
║  [INVESTIGATION]                         ║
║   1. New Case Intake                     ║
║   2. Investigation Report                ║
║   3. Persona Review                      ║
║                                          ║
║  [COMPLIANCE]                            ║
║   4. Policy / SOP Generator              ║
║   5. Training Material                   ║
║   6. FRM Risk Register                   ║
║                                          ║
║  [BUSINESS]                              ║
║   7. Create Client Proposal              ║
║   8. Build Proposal PPT Prompt Pack      ║
║   9. Case Tracker                        ║
║  10. Browse SOPs                         ║
╚══════════════════════════════════════════╝
```

Type a number and press Enter.

---

## Walkthrough: Your First FRM Risk Register (Option 6)

This is the flagship feature. Here's exactly what happens:

1. **Type `6` and press Enter**

2. **Claude asks you questions one at a time:**
   ```
   What industry is your client in?
   > construction and real estate, based in Dubai

   How large is the company — roughly how many employees?
   > around 800 people

   What is the main concern or trigger for this review?
   > recent staff turnover in finance and procurement
   ```

3. **The pipeline runs automatically — you'll see progress:**
   ```
   [Junior Analyst]  Researching construction fraud patterns in UAE...  ✓
   [Project Manager] Reviewing risk coverage and regulatory gaps...     ✓
   [Partner]         Finalising regulatory alignment (CBUAE, DFSA)...   ✓
   ```

4. **Output is saved to:**
   ```
   cases/0001/final_report.en.md   ← English report (always generated)
   cases/0001/final_report.ar.md   ← Arabic version (generated when language = ar)
   cases/0001/audit_log.jsonl      ← Full audit trail
   ```

The whole process takes 2–4 minutes.

---

## Understanding Your Output Files

Every case gets its own folder under `cases/`:

```
cases/
└── 0001/
    ├── state.json              ← Current status of the case pipeline
    ├── audit_log.jsonl         ← Every event, timestamped (immutable)
    ├── citations_index.json    ← All research sources cited
    ├── junior_output.v1.json   ← Junior Analyst's first draft
    ├── pm_review.v1.json       ← Project Manager's review notes
    ├── partner_approval.v1.json← Partner's approval decision
    ├── final_report.en.md      ← Final English report (open in any editor)
    └── final_report.ar.md      ← Arabic report (present when language = ar selected)
```

**Opening a report:**
- macOS: `open cases/0001/final_report.en.md` (opens in default app)
- Windows: `notepad cases\0001\final_report.en.md`
- Or drag the file into VS Code, Word, or any Markdown viewer

---

## If Something Gets Interrupted

If the app closes mid-run (power cut, accidental close, etc.), don't worry. The next time you run Option 6 (or whichever workflow was running), it will detect the unfinished case and ask:

```
Case 0001 is in progress (status: pm_review_complete).
Resume from where it stopped? [Y/n]
```

Press `Y` to continue from where it left off.

---

## Budget and Cost Guide

| Mode | Junior Analyst | Project Manager | Partner | Typical cost per FRM |
|------|---------------|-----------------|---------|---------------------|
| Economy | Haiku | Haiku | Sonnet | ~$0.05–0.15 |
| Balanced (default) | Haiku | Sonnet | Sonnet | ~$0.20–0.50 |
| Premium | Sonnet | Sonnet | Opus | ~$1.00–2.50 |

Set the mode in your `.env` file:
```
BUDGET_MODE=balanced
```

---

## Troubleshooting

### "command not found: python3"
- macOS: Install Python from [python.org](https://python.org)
- Try `python` instead of `python3`

### "ModuleNotFoundError: No module named 'anthropic'"
You're not in the virtual environment. Run:
```bash
source venv/bin/activate    # macOS/Linux
venv\Scripts\activate       # Windows
```
Then try again.

### "AuthenticationError" or "Invalid API key"
- Open your `.env` file and check the key has no extra spaces or quotes
- Make sure the file is named exactly `.env` (not `env.txt` or `.env.txt`)

### "Error: Tavily quota exceeded"
You've used your 1,000 free searches. Either:
- Upgrade your Tavily plan at app.tavily.com
- Set `USE_CACHED_RESEARCH=true` in `.env` to reuse previous research results

### Arabic text shows as boxes or question marks
Your terminal doesn't support Arabic. The Arabic report is still saved correctly to `cases/*/final_report.ar.md` — open it in VS Code or a browser instead.

### "Case stuck / pipeline didn't finish"
Re-run the same menu option. The orchestrator will detect the partial state and offer to resume.

---

## Frequently Asked Questions

**Q: Is my data sent anywhere?**
Only your prompts and research queries go to Anthropic (Claude API) and Tavily (search). Your case files stay on your computer in the `cases/` folder. Nothing is stored by the app on any server.

**Q: Can I use this without the Tavily key?**
The regulatory and sanctions lookups will not work without it. Basic report generation may still work with reduced research quality. Set `TAVILY_API_KEY=` empty in `.env` to try.

**Q: Can I edit the reports after they're generated?**
Yes — they're plain Markdown files. Open them in VS Code, Typora, or Word (File → Open → select the .md file). Or copy-paste into Google Docs.

**Q: Can I run multiple cases at the same time?**
Not recommended. Run one case at a time to avoid API rate limits.

**Q: How do I add a new client persona or workflow?**
Advanced feature — see the developer notes in `CLAUDE.md` under "Phase 5 — Personas" and "Plugin Manifest Format".

**Q: Where are the SOPs stored?**
In the `sops/` folder. Browse them via Option 10 in the menu, or open the files directly.

---

## Getting Help

- Re-read this guide from the top
- Check the `cases/{id}/audit_log.jsonl` for a detailed event log of what went wrong
- Open an issue on the GitHub repository (link in your purchase confirmation)

---

## Quick Reference Card

```
Start the app:
  cd ~/forensic-ai && source venv/bin/activate && python run.py

Check your API keys work:
  python3 -c "import anthropic; anthropic.Anthropic().models.list(); print('Anthropic OK')"

View a report:
  open cases/0001/final_report.en.md        (macOS)
  start cases\0001\final_report.en.md       (Windows)

Reset a broken case (delete and restart):
  rm -rf cases/0001    (macOS/Linux)
  rmdir /s cases\0001  (Windows)
```
