# Deploy to Streamlit Cloud + Daily 10 AM Automation

## Part 1: Deploy to Streamlit Cloud (share.streamlit.io)

### Step 1: Create streamlit.toml (optional config)
Create a file named `streamlit.toml` in the project root with:
```
[server]
headless = true
port = 8501
```

### Step 2: Push to GitHub
Your code is already on GitHub at: https://github.com/AbhishekG27/SEO_Health_Checker_Website

### Step 3: Connect to Streamlit Cloud
1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Click "New app"
4. Select repository: AbhishekG27/SEO_Health_Checker_Website
5. Main file path: app.py
6. Python version: 3.9 or higher

### Step 4: Add secrets in Streamlit Cloud
In the app settings, go to "Secrets" and add:
```
GOOGLE_PAGESPEED_API_KEY = your_key_here
GEMINI_API_KEY = your_key_here
SERPER_API_KEY = your_key_here
SCHEDULED_AUDIT_URL = https://tekspotedu.com/
GOOGLE_CREDENTIALS_FILE = (upload the JSON file content or path)
```

### Step 5: Deploy
Click "Deploy" - Streamlit Cloud will build and deploy your app. You'll get a URL like: https://seo-health-checker-website.streamlit.app

---

## Part 2: Daily 10 AM Automation

Streamlit Cloud does NOT support scheduled runs. Use one of these options:

### Option A: GitHub Actions (Recommended - Free)

Create `.github/workflows/daily-audit.yml`:

```yaml
name: Daily SEO Audit

on:
  schedule:
    - cron: '0 10 * * *'  # 10 AM UTC daily
  workflow_dispatch:  # Allow manual trigger

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run audit
        env:
          GOOGLE_PAGESPEED_API_KEY: ${{ secrets.GOOGLE_PAGESPEED_API_KEY }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          SERPER_API_KEY: ${{ secrets.SERPER_API_KEY }}
          SCHEDULED_AUDIT_URL: ${{ secrets.SCHEDULED_AUDIT_URL }}
          GOOGLE_CREDENTIALS_FILE: ${{ secrets.GOOGLE_CREDENTIALS_FILE }}
        run: python run_scheduled_audit.py
```

Then in GitHub repo Settings → Secrets and variables → Actions, add:
- GOOGLE_PAGESPEED_API_KEY
- GEMINI_API_KEY
- SERPER_API_KEY
- SCHEDULED_AUDIT_URL
- GOOGLE_CREDENTIALS_FILE (paste JSON content)

### Option B: External Cron Service (Free)

1. Sign up at https://cron-job.org (free) or https://www.easycron.com
2. Create a new cron job:
   - URL: Your Streamlit app URL + a webhook endpoint (you'd need to add one)
   - Schedule: Daily at 10:00 AM (your timezone)
   - Method: GET or POST

Note: This requires adding a webhook endpoint to your Streamlit app to trigger the audit.

### Option C: Keep Local Task Scheduler (Windows)

Keep using Windows Task Scheduler on your local machine to run `run_scheduled_audit.py` daily at 10 AM. The Streamlit app is just for manual audits.

---

## Summary

- Streamlit Cloud: For the web UI (manual audits)
- GitHub Actions: For daily 10 AM automation (recommended)
- Or: Keep local Task Scheduler for automation
