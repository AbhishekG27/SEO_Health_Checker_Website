# GitHub Actions: Daily 10 AM SEO Audit Setup

The workflow `.github/workflows/daily-seo-audit.yml` runs every day at **10:00 AM India time (IST)** and creates two Google Docs (report + gap analysis) in the Drive folder **SEO-Health-Tekspot**.

## 1. One-time: Get Google token (for headless runs)

Someone must sign in to Google **once** on a machine where the app can open a browser:

1. Clone the repo and set up locally (Python, `pip install -r requirements.txt`, `.env` with API keys).
2. Set `GOOGLE_CREDENTIALS_FILE` to the **Docs** client secret JSON (e.g. `client_secret_...docs.json`).
3. Run: `streamlit run app.py`
4. When the browser opens, sign in with the **Google account** that should own the Drive folder and Docs.
5. After success, in the project folder you will see `token_docs.json`.
6. Open `token_docs.json` in a text editor, copy **all** its content (the whole JSON). You will paste this into a GitHub Secret in the next section.

## 2. Add GitHub Secrets

In your repo: **Settings → Secrets and variables → Actions → New repository secret.**

Create these secrets:

| Secret name | Value | Required |
|-------------|--------|----------|
| `GOOGLE_PAGESPEED_API_KEY` | Your PageSpeed Insights API key | Yes |
| `GEMINI_API_KEY` | Your Gemini API key | Yes (for gap analysis) |
| `GOOGLE_CREDENTIALS_JSON` | **Full file content** of the Docs client secret JSON (e.g. `client_secret_...docs.json`) | Yes |
| `GOOGLE_TOKEN_JSON` | **Full file content** of `token_docs.json` (from step 1 above) | Yes |
| `SERPER_API_KEY` | Your Serper API key | No (optional) |
| `SCHEDULED_AUDIT_URL` | e.g. `https://tekspotedu.com/` | No (default: tekspotedu.com) |
| `GOOGLE_DRIVE_FOLDER_NAME` | e.g. `SEO-Health-Tekspot` | No (default: SEO-Health-Tekspot) |

- For **GOOGLE_CREDENTIALS_JSON**: open the `.json` file in a text editor, select all, copy, paste into the secret value.
- For **GOOGLE_TOKEN_JSON**: open `token_docs.json` (created after sign-in in step 1), select all, copy, paste into the secret value.

Do **not** commit `credentials.json`, `token_docs.json`, or any client secret file to the repo.

## 3. Run the workflow

- **Automatic:** The workflow runs every day at 10:00 AM IST.
- **Manual:** Repo → **Actions** → **Daily SEO Health Check** → **Run workflow**.

After each run, two new Docs appear in the Google Drive folder (SEO-Health-Tekspot): **SEO Report - {domain} - {date}** and **SEO Gap Analysis - {domain} - {date}**.
