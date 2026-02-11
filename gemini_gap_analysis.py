"""
Gemini-powered gap analysis for SEO/performance reports.
"""
import requests

# Gemini 2.5 Flash (Google AI Studio / generativelanguage.googleapis.com)
GEMINI_MODEL = "gemini-2.5-flash"
MAX_REPORT_CHARS = 28000  # Leave room for prompt and response

GAP_ANALYSIS_PROMPT = """You are an expert SEO and web performance consultant. Analyze the following audit report in detail so the site owner can actually improve their website. Your response MUST be in Markdown and include these sections:

## 1. Executive summary
2–3 sentences: overall health, biggest win to fix first, and one-line priority.

## 2. Metric-by-metric analysis
For each category (Performance, Accessibility, Best Practices, SEO) and each Core Web Vital (FCP, LCP, CLS, TBT):
- State the current value/score from the report.
- Say whether it passes or fails and why it matters for users and search.
- If it fails or is weak, give a short technical reason (e.g. “FCP 8.7s usually means heavy render-blocking resources or slow server”).

## 3. Root cause focus
Call out the most likely technical causes from the report (e.g. render-blocking JS/CSS, large images, no caching, slow server response). Be specific and cite the report where possible.

## 4. Prioritized action plan (to improve the website)
List 7–10 concrete, actionable steps in order of impact. For each step:
- **What to do** (clear action).
- **Why** (which metric it improves).
- **How** (brief technical approach: e.g. “Use `<link rel=preload>` for critical CSS”, “Lazy-load images below the fold”, “Enable Brotli and set long cache headers”).
Where relevant, mention tools or standards (e.g. Lighthouse, PageSpeed, Core Web Vitals).

## 5. Quick reference
A short bullet list of “Do this first” items (3–5) so the owner can start immediately.

Be detailed and specific so someone can use this document to improve the site. Do not repeat the raw report; only analyze and recommend."""


def _extract_text(data: dict) -> str | None:
    """Extract generated text from Gemini API response."""
    candidates = data.get("candidates") or []
    if not candidates:
        return None
    c = candidates[0]
    content = c.get("content")
    if not content:
        return None
    parts = content.get("parts") or []
    if not parts:
        return None
    text = parts[0].get("text")
    if not text or not isinstance(text, str):
        return None
    return text.strip() or None


def _extract_error(data: dict, status_code: int, response_text: str) -> str:
    """Build a user-facing error message from response."""
    err = data.get("error")
    if err:
        msg = err.get("message", str(err))
        code = err.get("code")
        if code:
            return f"API error {code}: {msg}"
        return msg
    feedback = data.get("promptFeedback") or {}
    block = feedback.get("blockReason")
    if block:
        return f"Prompt blocked ({block}). Try a shorter report or different content."
    candidates = data.get("candidates") or []
    if candidates:
        fr = candidates[0].get("finishReason") or ""
        if fr and fr != "STOP":
            return f"Generation stopped: {fr}"
    if status_code != 200:
        return f"HTTP {status_code}: {response_text[:200]}"
    return "No content in response."


def get_gap_analysis(report_md: str, api_key: str) -> tuple[str | None, str | None]:
    """
    Send the report to Gemini and return (gap_analysis_text, error_message).
    On success: (text, None). On failure: (None, error_string).
    """
    if not api_key or not report_md:
        return None, "Missing API key or report."
    # Truncate to avoid token limits and timeouts
    report_truncated = report_md[:MAX_REPORT_CHARS]
    if len(report_md) > MAX_REPORT_CHARS:
        report_truncated += "\n\n[... report truncated ...]"
    payload = {
        "contents": [{"parts": [{"text": GAP_ANALYSIS_PROMPT + "\n\n---\n\n" + report_truncated}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 8192,
        },
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={api_key}"
    try:
        response = requests.post(url, json=payload, timeout=90)
        data = response.json() if response.text else {}
        text = _extract_text(data)
        if text:
            return text, None
        return None, _extract_error(data, response.status_code, response.text or "")
    except requests.exceptions.RequestException as e:
        return None, str(e)
    except Exception as e:
        return None, str(e)
