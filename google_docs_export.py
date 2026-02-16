"""
Optional Google Docs export for SEO reports.
Supports: credentials file path, or in-memory JSON strings (for Streamlit Secrets).
OAuth: local server (desktop) or redirect flow (Streamlit Cloud).
"""
import json
import os
import re
from pathlib import Path

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    HAS_GOOGLE = True
except ImportError:
    HAS_GOOGLE = False

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
]


def _client_config_with_redirect(client_secret_dict: dict, redirect_uri: str) -> dict:
    """Ensure client config has a single redirect_uri for web flow."""
    if "web" in client_secret_dict:
        config = {"web": dict(client_secret_dict["web"])}
        config["web"]["redirect_uris"] = [redirect_uri]
        return config
    if "installed" in client_secret_dict:
        config = {"installed": dict(client_secret_dict["installed"])}
        config["installed"]["redirect_uris"] = [redirect_uri]
        return config
    return client_secret_dict


def get_authorization_url(credentials_json_str: str, redirect_uri: str) -> str:
    """Build Google OAuth authorization URL for redirect flow (e.g. Streamlit Cloud)."""
    if not HAS_GOOGLE:
        return ""
    try:
        client_config = json.loads(credentials_json_str)
        config = _client_config_with_redirect(client_config, redirect_uri)
        flow = InstalledAppFlow.from_client_config(config, SCOPES)
        return flow.authorization_url(access_type="offline", prompt="consent")[0]
    except Exception:
        return ""


def get_creds_from_code(credentials_json_str: str, redirect_uri: str, code: str) -> "tuple[Credentials | None, str]":
    """Exchange authorization code for credentials. Returns (creds, token_json_str)."""
    if not HAS_GOOGLE:
        return None, ""
    try:
        client_config = json.loads(credentials_json_str)
        config = _client_config_with_redirect(client_config, redirect_uri)
        flow = InstalledAppFlow.from_client_config(config, SCOPES)
        flow.fetch_token(code=code)
        creds = flow.credentials
        token_json = creds.to_json()
        return creds, token_json
    except Exception:
        return None, ""


def get_creds_from_token_json(credentials_json_str: str, token_json_str: str) -> "Credentials | None":
    """Build credentials from client secret JSON string + saved token JSON string (no browser)."""
    if not HAS_GOOGLE or not token_json_str:
        return None
    try:
        creds = Credentials.from_authorized_user_info(json.loads(token_json_str), SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return creds
    except Exception:
        return None


def _get_creds(credentials_path: str | None) -> "Credentials | None":
    if not HAS_GOOGLE:
        return None
    path = Path(credentials_path or "credentials.json")
    if not path.exists():
        return None
    creds = None
    token_path = path.parent / "token_docs.json"
    if token_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        except Exception:
            pass
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(path), SCOPES)
            creds = flow.run_local_server(port=0)
        if token_path:
            with open(token_path, "w") as f:
                f.write(creds.to_json())
    return creds


def _ensure_doc_in_folder(creds: "Credentials", document_id: str) -> None:
    """
    Ensure the given Doc is inside the Drive folder defined by GOOGLE_DRIVE_FOLDER_NAME
    (default: SEO-Health-Tekspot). Creates the folder on first run.
    """
    folder_name = os.environ.get("GOOGLE_DRIVE_FOLDER_NAME") or "SEO-Health-Tekspot"
    if not folder_name:
        return
    try:
        drive_service = build("drive", "v3", credentials=creds)
        # Find or create folder
        query = (
            "mimeType = 'application/vnd.google-apps.folder' "
            f"and name = '{folder_name}' and trashed = false"
        )
        res = drive_service.files().list(
            q=query, pageSize=1, fields="files(id)"
        ).execute()
        files = res.get("files") or []
        if files:
            folder_id = files[0]["id"]
        else:
            meta = {
                "name": folder_name,
                "mimeType": "application/vnd.google-apps.folder",
            }
            folder = drive_service.files().create(
                body=meta, fields="id"
            ).execute()
            folder_id = folder.get("id")
        if not folder_id:
            return
        # Add the doc to this folder (keeps existing parents)
        drive_service.files().update(
            fileId=document_id,
            addParents=folder_id,
            fields="id, parents",
        ).execute()
    except Exception:
        # Folder placement is best-effort; ignore failures so report creation still works.
        return


def _markdown_to_plain(text: str) -> str:
    """Convert markdown to plain text so ** and ### etc. don't appear in Google Docs."""
    if not text:
        return text
    text = text.replace("\r", "")
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", text)
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    return text


def _strip_inline_markdown(line: str) -> str:
    """Remove ** and ` from a single line for display."""
    line = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
    line = re.sub(r"__(.+?)__", r"\1", line)
    line = re.sub(r"`([^`]+)`", r"\1", line)
    return line.strip()


def _parse_markdown_blocks(md: str) -> list[tuple[str, str]]:
    """
    Parse markdown into (display_text, block_type) segments.
    block_type: "heading", "subheading", "bullet", "numbered", "paragraph"
    """
    if not md:
        return []
    md = md.replace("\r", "")
    segments = []
    lines = md.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        if re.match(r"^###\s", line) or re.match(r"^###\s", stripped):
            segments.append((_strip_inline_markdown(re.sub(r"^#+\s*", "", stripped)), "subheading"))
            i += 1
            continue
        if re.match(r"^##\s", line) or re.match(r"^##\s", stripped):
            segments.append((_strip_inline_markdown(re.sub(r"^#+\s*", "", stripped)), "heading"))
            i += 1
            continue
        if re.match(r"^#\s", line) or re.match(r"^#\s", stripped):
            segments.append((_strip_inline_markdown(re.sub(r"^#+\s*", "", stripped)), "heading"))
            i += 1
            continue
        if re.match(r"^[-*]\s+", stripped) or (stripped.startswith("- ") or stripped.startswith("* ")):
            text = _strip_inline_markdown(re.sub(r"^[-*]\s+", "", stripped, count=1))
            segments.append((text, "bullet"))
            i += 1
            continue
        if re.match(r"^\d+\.\s+", stripped):
            # Keep "1. " prefix so the doc shows numbering as plain text
            text = _strip_inline_markdown(stripped)
            segments.append((text, "numbered"))
            i += 1
            continue
        # Paragraph: can span multiple lines until blank or next special line
        para_lines = [stripped]
        i += 1
        while i < len(lines) and lines[i].strip():
            next_line = lines[i].strip()
            if re.match(r"^#+\s", next_line) or re.match(r"^[-*]\s+", next_line) or re.match(r"^\d+\.\s+", next_line):
                break
            para_lines.append(next_line)
            i += 1
        segments.append((_strip_inline_markdown(" ".join(para_lines)), "paragraph"))
    return segments


def _build_formatted_doc_requests(md: str) -> tuple[str, list[dict]]:
    """
    Build (full_plain_text, batchUpdate requests) for a formatted Google Doc.
    Inserts text with spacing, then applies bold to headings and bullets to list items.
    """
    segments = _parse_markdown_blocks(md)
    if not segments:
        return "", []

    parts = []
    ranges_bold = []  # (start, end)
    ranges_bullet = []  # (start, end)
    pos = 1  # Docs indices are 1-based

    for j, (text, block_type) in enumerate(segments):
        if not text:
            continue
        if parts:
            if block_type in ("bullet", "numbered") and segments[j - 1][1] in ("bullet", "numbered"):
                sep = "\n"
            else:
                sep = "\n\n"
            parts.append(sep)
            pos += len(sep)
        start = pos
        parts.append(text)
        pos += len(text)
        end = pos
        # List item paragraph includes the following newline for Docs API. Numbered items stay as plain paragraphs (no valid numbered preset in API).
        if block_type == "bullet":
            if j + 1 < len(segments) and segments[j + 1][1] in ("bullet", "numbered"):
                end_para = end + 1  # include \n
            else:
                end_para = end
            ranges_bullet.append((start, end_para))
        elif block_type in ("heading", "subheading"):
            ranges_bold.append((start, end))

    full_text = "".join(parts)
    requests = [{"insertText": {"location": {"index": 1}, "text": full_text}}]
    for start, end in ranges_bold:
        requests.append({
            "updateTextStyle": {
                "range": {"startIndex": start, "endIndex": end},
                "textStyle": {"bold": True},
                "fields": "bold",
            }
        })
    for start, end in ranges_bullet:
        requests.append({
            "createParagraphBullets": {
                "range": {"startIndex": start, "endIndex": end},
                "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE",
            }
        })
    return full_text, requests


def _extract_doc_id(value: str) -> str | None:
    """Extract Google Doc ID from full URL or return as-is if already an ID."""
    value = value.strip()
    # Match .../d/DOCUMENT_ID/... or .../d/DOCUMENT_ID?...
    m = re.search(r"/document/d/([a-zA-Z0-9_-]+)", value)
    if m:
        return m.group(1)
    # If it looks like a raw ID (alphanumeric, hyphens, underscores, no slashes)
    if re.match(r"^[a-zA-Z0-9_-]+$", value):
        return value
    return None


def create_new_doc(
    title: str, markdown_text: str, credentials_path: str | None, *, formatted: bool = True
) -> tuple[str | None, str | None]:
    """
    Create a new Google Doc with the given title and insert the content.
    If formatted=True (default), applies spacing, bold headings, and bullet/numbered lists.
    Returns (document_id, None) on success, or (None, error_message) on failure.
    """
    if not HAS_GOOGLE:
        return None, "Google API libraries not installed"
    creds = _get_creds(credentials_path)
    if not creds:
        return None, "No Google credentials (credentials.json not found or invalid)"
    try:
        docs_service = build("docs", "v1", credentials=creds)
        # Create the empty doc
        doc = docs_service.documents().create(body={"title": title}).execute()
        document_id = doc.get("documentId")
        if not document_id:
            return None, "Created doc but no documentId returned"
        # Move into Drive folder (creates folder first time if needed)
        _ensure_doc_in_folder(creds, document_id)
        # Insert formatted content
        if formatted and markdown_text.strip():
            _, fmt_requests = _build_formatted_doc_requests(markdown_text)
            if fmt_requests:
                docs_service.documents().batchUpdate(
                    documentId=document_id, body={"requests": fmt_requests}
                ).execute()
                return document_id, None
        text = _markdown_to_plain(markdown_text)
        docs_service.documents().batchUpdate(
            documentId=document_id,
            body={"requests": [{"insertText": {"location": {"index": 1}, "text": text}}]},
        ).execute()
        return document_id, None
    except HttpError as e:
        return None, str(e)
    except Exception as e:
        return None, str(e)


def create_report_and_analysis_docs(
    domain: str,
    date_str: str,
    report_md: str,
    gap_md: str | None,
    credentials_path: str | None,
) -> tuple[str | None, str | None, str | None]:
    """
    Create two separate Google Docs: one for the SEO report, one for Gemini gap analysis.
    Returns (report_doc_id, analysis_doc_id, error). analysis_doc_id is None if gap_md is empty.
    """
    if not HAS_GOOGLE:
        return None, None, "Google API libraries not installed"
    creds = _get_creds(credentials_path)
    if not creds:
        return None, None, "No Google credentials (credentials.json not found or invalid)"
    report_id, err = create_new_doc(
        f"SEO Report - {domain} - {date_str}", report_md, credentials_path
    )
    if err:
        return None, None, err
    analysis_id = None
    if gap_md and gap_md.strip():
        analysis_id, err2 = create_new_doc(
            f"SEO Gap Analysis - {domain} - {date_str}", gap_md.strip(), credentials_path
        )
        if err2:
            return report_id, None, err2  # report succeeded, analysis failed
    return report_id, analysis_id, None


def append_to_doc(document_id: str, markdown_text: str, credentials_path: str | None) -> str | None:
    """
    Append markdown content to an existing Google Doc.
    document_id: the ID from the doc URL or the full URL (e.g. docs.google.com/document/d/DOCUMENT_ID/edit)
    Returns None on success; returns error message string on failure.
    """
    doc_id = _extract_doc_id(document_id)
    if not doc_id:
        return "Invalid Google Doc ID or URL. Paste the full doc URL or just the document ID."
    document_id = doc_id
    if not HAS_GOOGLE:
        return "Google API libraries not installed"
    creds = _get_creds(credentials_path)
    if not creds:
        return "No Google credentials (credentials.json not found or invalid)"
    try:
        service = build("docs", "v1", credentials=creds)
        # Insert at end: get current end index then insert text
        doc = service.documents().get(documentId=document_id).execute()
        end_index = doc.get("body", {}).get("content", [{}])[-1].get("endIndex", 1)
        # endIndex is 1-based; we need to insert before the final newline
        insert_index = max(1, end_index - 1)
        plain = _markdown_to_plain(markdown_text)
        requests = [
            {
                "insertText": {
                    "location": {"index": insert_index},
                    "text": "\n\n---\n\n" + plain,
                }
            }
        ]
        service.documents().batchUpdate(
            documentId=document_id, body={"requests": requests}
        ).execute()
        return None
    except HttpError as e:
        return str(e)
    except Exception as e:
        return str(e)
