# SEO Health Checker — Automated Website SEO Audit Tool

**Free, open-source SEO health checker and website audit tool.** Enter any website URL to get a full SEO report: PageSpeed Insights (Performance, Core Web Vitals, Accessibility), optional SERP data, and AI-powered gap analysis — with results saved to formatted Google Docs or Markdown.

Automated SEO audit · Website SEO checker · PageSpeed report · Core Web Vitals · SEO health check · Free SEO tool

---

## Features

- **Website SEO audit** — Performance, Accessibility, Best Practices, and SEO scores (mobile + desktop) via Google PageSpeed Insights
- **Core Web Vitals** — FCP, LCP, CLS, TBT with pass/fail and improvement hints
- **AI gap analysis** — Gemini-powered summary: key gaps, risks, and prioritized recommendations
- **Google Docs export** — Two docs per run: one SEO report, one gap analysis (headings, bullets, spacing)
- **Scheduled audits** — Run daily (e.g. 10 AM) for a fixed URL; reports auto-saved to Google Docs
- **No n8n or RapidAPI** — Python + Streamlit; uses PageSpeed API, optional Serper, and Gemini

---

## Quick start

```bash
git clone https://github.com/AbhishekG27/SEO_Health_Checker_Website.git
cd SEO_Health_Checker_Website
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp .env.example .env            # Add your API keys
streamlit run app.py
```

Open the URL shown (e.g. `http://localhost:8501`), enter a website URL, and run the SEO audit.

---

## Setup

### 1. API keys (`.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_PAGESPEED_API_KEY` | Yes | [Google Cloud Console](https://console.cloud.google.com/) — enable PageSpeed Insights API |
| `GEMINI_API_KEY` | No | [Google AI Studio](https://aistudio.google.com/apikey) — for gap analysis |
| `SERPER_API_KEY` | No | [serper.dev](https://serper.dev) — for SERP data in the report |
| `GOOGLE_CREDENTIALS_FILE` | No | OAuth client JSON — for saving reports to Google Docs |
| `SCHEDULED_AUDIT_URL` | No | URL to audit on schedule (default: `https://tekspotedu.com/`) |

Copy `.env.example` to `.env` and fill in the keys you need.

### 2. Google Docs (optional)

To save reports as Google Docs:

1. In [Google Cloud Console](https://console.cloud.google.com/), enable **Google Docs API** and create OAuth 2.0 credentials (Desktop app).
2. Download the client secret JSON, put it in the project folder, and set `GOOGLE_CREDENTIALS_FILE` in `.env`.
3. Run the app once and complete the browser sign-in; `token_docs.json` is created for future runs.

Each audit creates two docs: **SEO Report - {domain} - {date}** and **SEO Gap Analysis - {domain} - {date}**.

### 3. Scheduled daily audit (e.g. 10 AM)

Set `SCHEDULED_AUDIT_URL` in `.env`, then:

```bash
python run_scheduled_audit.py
```

**Windows (Task Scheduler):** Create a daily task at 10:00 AM that runs `python run_scheduled_audit.py` with “Start in” set to this project folder.

**Linux / macOS (cron):**

```bash
0 10 * * * cd /path/to/SEO_Health_Checker_Website && python run_scheduled_audit.py
```

---

## Project structure

| File | Purpose |
|------|---------|
| `app.py` | Streamlit UI — URL input, audit, report preview, download, Google Docs |
| `seo_client.py` | PageSpeed + Serper API calls, report builder |
| `gemini_gap_analysis.py` | Gemini API — gap analysis from report text |
| `google_docs_export.py` | Create/append Google Docs with formatting |
| `run_scheduled_audit.py` | CLI for scheduled audit → report + analysis docs |
| `run_audit_daily.bat` | Windows batch for Task Scheduler |

---

## Deploy / contribute

```bash
git clone https://github.com/AbhishekG27/SEO_Health_Checker_Website.git
cd SEO_Health_Checker_Website
# Setup as in Quick start, then push your branch
git remote add origin https://github.com/AbhishekG27/SEO_Health_Checker_Website.git
git push -u origin main
```

Do not commit `.env`, `credentials.json`, `client_secret*.json`, or `token_docs.json`; they are in `.gitignore`.

---

## Keywords (for search)

SEO health checker · website SEO audit · automated SEO report · PageSpeed audit · Core Web Vitals checker · free SEO tool · website performance audit · SEO audit tool · Lighthouse report · Google PageSpeed · SEO gap analysis

---

## License

MIT
