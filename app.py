"""
Automated SEO Reports — Streamlit frontend.
Workflow: Form → PageSpeed Insights (+ optional Serper) → formatted report → new Google Doc.
"""
import os
from datetime import datetime
from urllib.parse import urlparse

import streamlit as st
from dotenv import load_dotenv

from seo_client import fetch_pagespeed, fetch_serper, build_report
from google_docs_export import append_to_doc, create_new_doc, create_report_and_analysis_docs, HAS_GOOGLE
from gemini_gap_analysis import get_gap_analysis

load_dotenv()

st.set_page_config(
    page_title="SEO Audit Report",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
<style>
    .main .block-container { max-width: 900px; padding-top: 2rem; }
    h1 { color: #1a1a2e; font-weight: 700; }
    .stDownloadButton button { background: linear-gradient(90deg, #4361ee 0%, #3a0ca3 100%); color: white; }
    div[data-testid="stExpander"] { border: 1px solid #e0e0e0; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Automated SEO Report")
st.caption("Enter a URL to run a performance & SEO audit (PageSpeed Insights + optional Serper SERP data).")

pagespeed_key = os.environ.get("GOOGLE_PAGESPEED_API_KEY") or os.environ.get("PAGESPEED_API_KEY") or st.secrets.get("GOOGLE_PAGESPEED_API_KEY") or st.secrets.get("PAGESPEED_API_KEY")
serper_key = os.environ.get("SERPER_API_KEY") or st.secrets.get("SERPER_API_KEY")
gemini_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if not pagespeed_key:
    st.warning(
        "Set **GOOGLE_PAGESPEED_API_KEY** or **PAGESPEED_API_KEY** in `.env`. "
        "Get a key from [Google Cloud Console](https://console.cloud.google.com/) (PageSpeed Insights API / enable it)."
    )

with st.form("seo_audit_form"):
    url = st.text_input(
        "Website URL",
        placeholder="https://example.com",
        help="URL of the page to analyze.",
    )
    include_serper = st.checkbox(
        "Include SERP data (Serper API)",
        value=bool(serper_key),
        help="Add search results and 'People also ask' for ranking context. Requires SERPER_API_KEY.",
    )
    serper_query = st.text_input(
        "Search query for SERP (optional)",
        placeholder="e.g. your brand or main keyword",
        help="Leave blank to use the URL's domain as the query.",
    )
    include_gap_analysis = st.checkbox(
        "Include Gemini gap analysis",
        value=bool(gemini_key),
        help="Use Gemini to analyze the report and add key gaps, risks, and prioritized recommendations. Requires GEMINI_API_KEY.",
    )
    submitted = st.form_submit_button("Run SEO Audit")

if submitted and url:
    if not pagespeed_key:
        st.error("Please set GOOGLE_PAGESPEED_API_KEY (or PAGESPEED_API_KEY) to run the audit.")
    else:
        with st.spinner("Running PageSpeed (mobile & desktop)…"):
            try:
                psi_mobile = fetch_pagespeed(url, pagespeed_key, strategy="mobile")
            except Exception as e:
                st.error(f"PageSpeed (mobile) failed: {e}")
                psi_mobile = None
            try:
                psi_desktop = fetch_pagespeed(url, pagespeed_key, strategy="desktop")
            except Exception as e:
                st.warning(f"PageSpeed (desktop) failed: {e}")
                psi_desktop = None
        serper_data = None
        actual_serper_query = (serper_query or urlparse(url).netloc or url).strip()
        if include_serper and serper_key:
            with st.spinner("Fetching SERP data…"):
                serper_data = fetch_serper(actual_serper_query, serper_key)
        if not psi_mobile and not psi_desktop:
            st.error("Audit failed: no PageSpeed data.")
        else:
            report_md = build_report(
                url,
                pagespeed_mobile=psi_mobile,
                pagespeed_desktop=psi_desktop,
                serper_data=serper_data,
                serper_query=actual_serper_query if serper_data else "",
            )
            gap_md = None
            if include_gap_analysis and gemini_key:
                with st.spinner("Running Gemini gap analysis…"):
                    gap_md, gap_err = get_gap_analysis(report_md, gemini_key)
                    if not gap_md:
                        st.warning(f"Gap analysis could not be generated. {gap_err or 'Gemini returned no content.'}")
            # Keep full report (with gap section) for preview and download; store gap separately for two-doc export
            report_with_gap = report_md + ("\n\n---\n\n## Gap Analysis (Gemini)\n\n" + gap_md if gap_md else "")
            st.session_state["last_report"] = report_with_gap
            st.session_state["last_url"] = url
            st.session_state["last_gap_md"] = gap_md
            # Create two separate Google Docs: report + gap analysis (or one doc if no gap)
            if HAS_GOOGLE and report_md:
                creds_path = os.environ.get("GOOGLE_CREDENTIALS_FILE") or "credentials.json"
                domain = urlparse(url).netloc or url.replace("https://", "").replace("http://", "").split("/")[0] or "report"
                date_str = datetime.now().strftime("%Y-%m-%d")
                report_doc_id, analysis_doc_id, export_err = create_report_and_analysis_docs(
                    domain, date_str, report_md, gap_md, creds_path
                )
                st.session_state["google_report_doc_id"] = report_doc_id
                st.session_state["google_analysis_doc_id"] = analysis_doc_id
                st.session_state["google_docs_export_error"] = export_err
            else:
                st.session_state["google_report_doc_id"] = None
                st.session_state["google_analysis_doc_id"] = None
                st.session_state["google_docs_export_error"] = None

if st.session_state.get("last_report"):
    report_md = st.session_state["last_report"]
    url_display = st.session_state.get("last_url", "")

    st.success(f"Report generated for **{url_display}**")
    export_err = st.session_state.get("google_docs_export_error")
    report_doc_id = st.session_state.get("google_report_doc_id")
    analysis_doc_id = st.session_state.get("google_analysis_doc_id")
    if export_err:
        st.error(f"Google Doc creation failed: {export_err}")
    else:
        if report_doc_id:
            st.success(f"**Report:** [Open report doc](https://docs.google.com/document/d/{report_doc_id}/edit)")
        if analysis_doc_id:
            st.success(f"**Gap analysis:** [Open analysis doc](https://docs.google.com/document/d/{analysis_doc_id}/edit)")
    st.markdown("---")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### Report preview")
    with col2:
        st.download_button(
            label="Download as Markdown",
            data=report_md,
            file_name="seo-audit-report.md",
            mime="text/markdown",
        )

    with st.expander("View full report", expanded=True):
        st.markdown(report_md)

    if HAS_GOOGLE:
        st.markdown("---")
        st.caption("Optionally append this report to an existing Google Doc.")
        doc_id = st.text_input(
            "Append to existing Doc (optional)",
            placeholder="Paste doc URL or ID",
            help="Paste a doc URL or ID to also add this report to that document.",
        )
        if doc_id.strip():
            creds_path = os.environ.get("GOOGLE_CREDENTIALS_FILE") or "credentials.json"
            if st.button("Append report to this Doc"):
                err = append_to_doc(doc_id.strip(), st.session_state.get("last_report", report_md), creds_path)
                if err is None:
                    st.success("Report appended to the document.")
                else:
                    st.error(f"Export failed: {err}")
    else:
        st.info("Install Google API packages and add credentials to enable Google Docs export.")
