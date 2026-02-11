# SEO Health Checker Website

**Code-based alternative to n8n workflow for SEO health checking.** Type a website URL → get automated SEO/performance audit → detailed gap analysis → formatted Google Docs reports.

This project replaces the [n8n SEO audit workflow](https://n8n.io/workflows/7630-generate-automated-seo-reports-with-rapidapis-seo-analyzer-and-google-docs/) with a Python/Streamlit app that:
- Uses **Google PageSpeed Insights** + **Serper API** (no RapidAPI dependency)
- Generates **detailed Gemini AI gap analysis** with actionable recommendations
- Creates **two separate Google Docs** (report + analysis) with proper formatting (bold headings, bullets, spacing)
- Supports **daily scheduled audits** at 10 AM for automatic monitoring

Perfect for SEO agencies, in-house web teams, or anyone who needs automated SEO health checks without n8n.

## What it does

- **Form**: Enter a website URL (and optional search query for SERP).
- **PageSpeed Insights**: Fetches mobile + desktop scores for Performance, Accessibility, Best Practices, SEO, plus Core Web Vitals and audit details.
- **Serper (optional)**: Adds top organic results and “People also ask” for ranking context.
- **Report**: Single Markdown report combining PageSpeed, optional SERP, and optional **Gemini gap analysis** (key gaps, risks, prioritized recommendations).
- **Export**: New Google Doc per report (auto-named), or download as `.md`, or append to an existing Doc.

## Setup

1. **Create a virtual environment** (recommended):

   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate   # macOS/Linux
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **API keys**  
   Copy `.env.example` to `.env` and set:

   - **`GOOGLE_PAGESPEED_API_KEY`** (required)  
     Get a key from [Google Cloud Console](https://console.cloud.google.com/). Create a project, enable **PageSpeed Insights API** (or use an existing API key that has it enabled).
   - **`SERPER_API_KEY`** (optional)  
     Get a key at [serper.dev](https://serper.dev) to include SERP data in the report.
   - **`GEMINI_API_KEY`** (optional)  
     Get a key at [Google AI Studio](https://aistudio.google.com/apikey) to add AI-powered gap analysis (key gaps, risks, recommendations) after each report.

4. **Run the app**:

   ```bash
   streamlit run app.py
   ```

   Open the URL shown (e.g. http://localhost:8501).

## Google Docs (automatic: new doc per report)

Each audit **creates a new Google Doc** with the report and names it automatically (e.g. `SEO Report - example.com - 2025-02-05`):

1. In [Google Cloud Console](https://console.cloud.google.com/), enable the **Google Docs API** and create OAuth 2.0 credentials (Desktop app). Download the client secret JSON and set `GOOGLE_CREDENTIALS_FILE` in `.env` to that file name.
2. On first run, the app will open a browser to sign in to Google and save `token_docs.json`.
3. After each audit, a new Doc is created with the report content and a link is shown. You can optionally append the same report to an existing Doc via the “Append to existing Doc” field.

## Files

| File | Purpose |
|------|--------|
| `app.py` | Streamlit UI: form, PageSpeed + optional Serper + optional Gemini gap analysis, report preview, download, Google Docs. |
| `seo_client.py` | PageSpeed Insights + Serper API calls and combined Markdown report. |
| `gemini_gap_analysis.py` | Gemini API call to generate gap analysis (gaps, risks, recommendations) from the report. |
| `google_docs_export.py` | Create new Google Doc or append to an existing one. |
| `run_scheduled_audit.py` | CLI script for daily audit (single URL, report + Gemini, new Doc). |
| `run_audit_daily.bat` | Windows batch file to run the scheduled audit (for Task Scheduler). |
| `requirements.txt` | Python dependencies. |
| `.env.example` | Example env vars (copy to `.env`). |

## Workflow

| Step | This project |
|------|----------------|
| Form trigger | Streamlit form (URL + optional SERP query) |
| Audit | `fetch_pagespeed()` (mobile + desktop), optional `fetch_serper()` |
| Format report | `build_report()` (PageSpeed scores, audits, SERP section) |
| Gap analysis | Optional `get_gap_analysis()` (Gemini) → appended to report |
| Export | New Google Doc (auto-named), download Markdown, or `append_to_doc()` |

---

## Daily 10 AM automatic audit (e.g. tekspotedu.com)

The app can run a **scheduled audit** for a fixed URL every day and save the report (with detailed Gemini gap analysis) to a new Google Doc.

### 1. One-time setup

- In `.env`, set **`SCHEDULED_AUDIT_URL`** to the site to audit (default is `https://tekspotedu.com/` if not set).
- Run the **Streamlit app once** and sign in to Google when prompted. This creates `token_docs.json` so the scheduled script can save to Google Docs without opening a browser.

### 2. Run the scheduled script manually (test)

From the project folder:

```bash
python run_scheduled_audit.py
```

This audits the URL in `SCHEDULED_AUDIT_URL`, runs Gemini gap analysis, creates a new Google Doc, and prints the doc link.

### 3. Schedule it every day at 10 AM

**Windows (Task Scheduler):**

1. Open **Task Scheduler** (search “Task Scheduler” in Start).
2. **Create Basic Task** → Name: e.g. “SEO daily audit” → Trigger: **Daily** → Time: **10:00 AM**.
3. Action: **Start a program**.
4. Program: full path to `run_audit_daily.bat` (e.g. `C:\Users\YourName\...\new-automation\run_audit_daily.bat`), or use:
   - **Program:** `python`  
   - **Add arguments:** `run_scheduled_audit.py`  
   - **Start in:** your project folder (e.g. `C:\Users\YourName\OneDrive\Documents\automations\new-automation`).
5. Finish. Ensure the user account that runs the task has the same `.env` and `token_docs.json` (run the app once while logged in as that user if needed).

**macOS / Linux (cron):**

```bash
crontab -e
```

Add a line (use your real project path):

```
0 10 * * * cd /path/to/new-automation && python run_scheduled_audit.py
```

This runs the audit every day at 10:00 AM and saves a new Google Doc (e.g. `SEO Report - tekspotedu.com - 2025-02-05`).

---

## Deploy to GitHub

### Initial Setup

If you're starting fresh or deploying this code to GitHub:

```bash
# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: SEO Health Checker Website"

# Rename branch to main
git branch -M main

# Add GitHub remote (replace with your repo URL)
git remote add origin git@github.com:AbhishekG27/SEO_Health_Checker_Website.git

# Push to GitHub
git push -u origin main
```

### Important: Don't commit secrets

Make sure `.env`, `credentials.json`, `client_secret*.json`, and `token_docs.json` are in `.gitignore` (they already are). Only commit `.env.example` as a template.

### For existing repositories

If the repo already exists on GitHub:

```bash
git remote add origin git@github.com:AbhishekG27/SEO_Health_Checker_Website.git
git branch -M main
git push -u origin main
```

### Clone and setup

Others can clone and use your repo:

```bash
git clone git@github.com:AbhishekG27/SEO_Health_Checker_Website.git
cd SEO_Health_Checker_Website
cp .env.example .env
# Edit .env with your API keys
pip install -r requirements.txt
streamlit run app.py
```

---

## Why this over n8n?

| Feature | n8n workflow | This code |
|---------|--------------|----------|
| **Setup** | Requires n8n account/hosting | Just Python + API keys |
| **Cost** | n8n Cloud pricing or self-host | Free (just API costs) |
| **Customization** | Limited by n8n nodes | Full Python control |
| **Gap analysis** | Basic formatting | Detailed Gemini AI analysis |
| **Doc formatting** | Plain text | Bold headings, bullets, spacing |
| **Scheduling** | n8n cron | Task Scheduler / cron (any OS) |
| **Deployment** | n8n platform | GitHub, local, or any server |

---

## License

MIT License - feel free to use, modify, and deploy.
