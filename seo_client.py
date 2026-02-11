"""
SEO report: Google PageSpeed Insights + optional Serper API.
No RapidAPI dependency.
"""
import re
from typing import Any

import requests


PAGESPEED_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
SERPER_URL = "https://google.serper.dev/search"


def _normalize_url(url: str) -> str:
    url = url.strip()
    if not re.match(r"^https?://", url, re.IGNORECASE):
        url = "https://" + url
    return url


def fetch_pagespeed(url: str, api_key: str, strategy: str = "mobile") -> dict[str, Any]:
    """
    Run PageSpeed Insights for a URL.
    strategy: "mobile" or "desktop"
    Returns raw API response (lighthouseResult, loadingExperience, etc.).
    """
    url = _normalize_url(url)
    params = {
        "url": url,
        "key": api_key,
        "strategy": strategy,
        "category": ["performance", "accessibility", "best-practices", "seo"],
    }
    response = requests.get(PAGESPEED_URL, params=params, timeout=90)
    response.raise_for_status()
    return response.json()


def fetch_serper(query: str, api_key: str, num: int = 10) -> dict[str, Any] | None:
    """
    Run Serper search for SERP data (organic results, people also ask).
    Returns raw API response or None if key missing / request fails.
    """
    if not query.strip() or not api_key:
        return None
    try:
        response = requests.post(
            SERPER_URL,
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            json={"q": query.strip(), "num": num},
            timeout=15,
        )
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


def _score_pct(score: float | None) -> str:
    if score is None:
        return "—"
    return f"{round(score * 100)}%"


def _format_audits(audits: dict[str, Any] | None) -> list[str]:
    if not audits:
        return []
    lines = []
    for audit_id, audit in audits.items():
        if not isinstance(audit, dict):
            continue
        title = audit.get("title")
        score = audit.get("score")
        display = audit.get("displayValue") or audit.get("description")
        if not title:
            continue
        if score is not None:
            status = "✔" if score >= 0.9 else ("⚠" if score >= 0.5 else "✖")
            lines.append(f"- {status} **{title}** {_score_pct(score)}" + (f" — {display}" if display else ""))
        else:
            lines.append(f"- **{title}**" + (f" — {display}" if display else ""))
    return lines


def _pagespeed_to_markdown(data: dict[str, Any], url: str, strategy: str) -> str:
    parts = [
        f"## PageSpeed Insights ({strategy})\n",
        f"**URL:** {url}\n",
    ]
    lh = data.get("lighthouseResult") or {}
    categories = lh.get("categories") or {}
    # Category scores
    parts.append("### Scores\n")
    for cat_id, cat in categories.items():
        if isinstance(cat, dict) and "score" in cat:
            score = cat.get("score")
            title = (cat.get("title") or cat_id).replace("-", " ").title()
            parts.append(f"- **{title}:** {_score_pct(score)}\n")
    # Core Web Vitals from audits if present
    audits = lh.get("audits") or {}
    cwv = ["first-contentful-paint", "largest-contentful-paint", "cumulative-layout-shift", "total-blocking-time"]
    cwv_found = [a for a in cwv if a in audits]
    if cwv_found:
        parts.append("\n### Core Web Vitals\n")
        for aid in cwv_found:
            a = audits[aid]
            title = a.get("title", aid)
            display = a.get("displayValue") or ""
            score = a.get("score")
            s = "✔" if score and score >= 0.9 else ("⚠" if score and score >= 0.5 else "✖")
            parts.append(f"- {s} **{title}** {display}\n")
    # SEO audits
    if "seo" in categories and isinstance(categories["seo"], dict):
        seo_audit_ids = (categories["seo"].get("auditRefs") or [])
        seo_ids = [r.get("id") for r in seo_audit_ids if r.get("id") in audits]
        if seo_ids:
            parts.append("\n### SEO checks\n")
            for aid in seo_ids[:15]:
                a = audits.get(aid)
                if not a:
                    continue
                title = a.get("title", aid)
                score = a.get("score")
                display = a.get("displayValue") or a.get("description") or ""
                s = "✔" if score is not None and score >= 0.9 else ("⚠" if score is not None and score >= 0.5 else "✖")
                parts.append(f"- {s} **{title}**" + (f" — {display}" if display else "") + "\n")
    # Accessibility highlights
    if "accessibility" in categories:
        acc_audit_ids = (categories["accessibility"].get("auditRefs") or []) if isinstance(categories["accessibility"], dict) else []
        acc_ids = [r.get("id") for r in acc_audit_ids if r.get("id") in audits][:12]
        if acc_ids:
            parts.append("\n### Accessibility\n")
            for aid in acc_ids:
                a = audits.get(aid)
                if not a:
                    continue
                title = a.get("title", aid)
                score = a.get("score")
                s = "✔" if score is not None and score >= 0.9 else ("⚠" if score is not None and score >= 0.5 else "✖")
                parts.append(f"- {s} **{title}**\n")
    return "".join(parts)


def build_report(
    url: str,
    pagespeed_mobile: dict[str, Any] | None,
    pagespeed_desktop: dict[str, Any] | None,
    serper_data: dict[str, Any] | None,
    serper_query: str = "",
) -> str:
    """
    Combine PageSpeed (and optional Serper) data into one Markdown report.
    """
    url = _normalize_url(url)
    parts = [
        "# SEO & Performance Report\n",
        f"**Site:** {url}\n",
        "---\n",
    ]
    if pagespeed_mobile:
        parts.append(_pagespeed_to_markdown(pagespeed_mobile, url, "Mobile"))
        parts.append("\n---\n")
    if pagespeed_desktop:
        parts.append(_pagespeed_to_markdown(pagespeed_desktop, url, "Desktop"))
        parts.append("\n---\n")
    if serper_data and serper_query:
        parts.append("## SERP context\n")
        parts.append(f"*Query:* \"{serper_query}\"\n\n")
        organic = serper_data.get("organic") or []
        if organic:
            parts.append("### Top results\n")
            for i, o in enumerate(organic[:10], 1):
                title = o.get("title") or ""
                link = o.get("link") or ""
                snippet = o.get("snippet") or ""
                parts.append(f"{i}. **{title}**  \n   {link}  \n   {snippet}\n\n")
        people_ask = serper_data.get("peopleAlsoAsk") or []
        if people_ask:
            parts.append("### People also ask\n")
            for pa in people_ask[:5]:
                q = pa.get("question") or ""
                snippet = pa.get("snippet") or ""
                if q:
                    parts.append(f"- **{q}**  \n  {snippet}\n\n")
    return "".join(parts).strip()
