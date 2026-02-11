"""
Scheduled SEO audit: run for a fixed URL (default tekspotedu.com), build report +
detailed Gemini gap analysis, and save to a new Google Doc.
Run this script daily at 10 AM via Windows Task Scheduler or cron.

Requires: .env with GOOGLE_PAGESPEED_API_KEY, GEMINI_API_KEY, GOOGLE_CREDENTIALS_FILE.
You must have run the Streamlit app once and signed in to Google so token_docs.json exists.
"""
import os
import sys
from datetime import datetime
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()

from seo_client import fetch_pagespeed, fetch_serper, build_report
from google_docs_export import create_report_and_analysis_docs, HAS_GOOGLE
from gemini_gap_analysis import get_gap_analysis

# URL to audit (set in .env as SCHEDULED_AUDIT_URL or default)
DEFAULT_URL = "https://tekspotedu.com/"
URL = os.environ.get("SCHEDULED_AUDIT_URL", "").strip() or DEFAULT_URL


def main() -> int:
    pagespeed_key = os.environ.get("GOOGLE_PAGESPEED_API_KEY") or os.environ.get("PAGESPEED_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    serper_key = os.environ.get("SERPER_API_KEY")
    creds_path = os.environ.get("GOOGLE_CREDENTIALS_FILE") or "credentials.json"

    if not pagespeed_key:
        print("ERROR: Set GOOGLE_PAGESPEED_API_KEY (or PAGESPEED_API_KEY) in .env", file=sys.stderr)
        return 1
    if not HAS_GOOGLE:
        print("ERROR: Google API packages required. pip install google-auth google-auth-oauthlib google-api-python-client", file=sys.stderr)
        return 1

    print(f"Scheduled audit started for {URL} at {datetime.now().isoformat()}")

    try:
        print("Running PageSpeed (mobile)...")
        psi_mobile = fetch_pagespeed(URL, pagespeed_key, strategy="mobile")
        print("Running PageSpeed (desktop)...")
        psi_desktop = fetch_pagespeed(URL, pagespeed_key, strategy="desktop")
    except Exception as e:
        print(f"ERROR: PageSpeed failed: {e}", file=sys.stderr)
        return 1

    serper_data = None
    actual_serper_query = urlparse(URL).netloc or URL
    if serper_key:
        try:
            print("Fetching SERP data...")
            serper_data = fetch_serper(actual_serper_query, serper_key)
        except Exception:
            pass

    report_md = build_report(
        URL,
        pagespeed_mobile=psi_mobile,
        pagespeed_desktop=psi_desktop,
        serper_data=serper_data,
        serper_query=actual_serper_query if serper_data else "",
    )

    gap_md = None
    if gemini_key:
        print("Running Gemini gap analysis...")
        gap_md, gap_err = get_gap_analysis(report_md, gemini_key)
        if not gap_md:
            print(f"WARNING: Gap analysis failed: {gap_err}", file=sys.stderr)

    domain = urlparse(URL).netloc or "report"
    date_str = datetime.now().strftime("%Y-%m-%d")
    print("Creating Google Docs (report + gap analysis)...")
    report_doc_id, analysis_doc_id, export_err = create_report_and_analysis_docs(
        domain, date_str, report_md, gap_md, creds_path
    )
    if export_err:
        print(f"ERROR: Google Doc creation failed: {export_err}", file=sys.stderr)
        return 1
    print(f"Report: https://docs.google.com/document/d/{report_doc_id}/edit")
    if analysis_doc_id:
        print(f"Gap analysis: https://docs.google.com/document/d/{analysis_doc_id}/edit")
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
