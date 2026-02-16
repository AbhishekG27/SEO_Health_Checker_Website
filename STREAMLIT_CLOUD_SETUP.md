# Deploy on share.streamlit.io (Streamlit Cloud)

## 1. Connect repo

In [share.streamlit.io](https://share.streamlit.io), connect **SEO_Health_Checker_Website**, set branch to `main`, main file to `app.py`.

## 2. Secrets (Settings → Secrets)

Add these in the **Secrets** text box. You can use separate keys for Docs and Drive client secrets; the app uses the Docs client for both Docs and Drive (one OAuth with both scopes).

**Required for audit:**
- `GOOGLE_PAGESPEED_API_KEY` — PageSpeed Insights API key  
- `GEMINI_API_KEY` — Gemini API key (for gap analysis)

**Required for Google Docs + Drive:**
- `GOOGLE_CREDENTIALS_JSON` or `GOOGLE_CREDENTIALS_DOCS_JSON` — **full contents** of your Google OAuth client secret JSON (Docs app, or one app with Docs + Drive scopes)
- `REDIRECT_URI` — Your Streamlit app URL, e.g. `https://yourapp-username.streamlit.app/` (must match the redirect URI set in Google Cloud Console for this OAuth client)

**After first sign-in (one-time):**
- `GOOGLE_TOKEN_JSON` — After you click “Sign in with Google” once, the app will show a token. Copy the **entire** JSON and add it here so you don’t have to sign in again.

**Optional:**
- `SERPER_API_KEY` — Serper API key  
- `GOOGLE_DRIVE_FOLDER_NAME` — e.g. `SEO-Health-Tekspot` (default)  
- `GOOGLE_CREDENTIALS_DRIVE_JSON` — Not required if you use one client for both; only if you ever split Docs vs Drive clients later.

### Example format (Secrets box)

```toml
GOOGLE_PAGESPEED_API_KEY = "your-pagespeed-key"
GEMINI_API_KEY = "your-gemini-key"
REDIRECT_URI = "https://yourapp-username.streamlit.app/"

# Paste the full JSON content (one line or multi-line string)
GOOGLE_CREDENTIALS_JSON = """
{"web":{"client_id":"...","client_secret":"...","redirect_uris":[]}}
"""
```

For `GOOGLE_TOKEN_JSON`, paste the token JSON the app shows after the first “Sign in with Google” (same format: string with the whole JSON).

## 3. Google Cloud Console

1. Create (or use) an OAuth 2.0 Client ID of type **Web application**.  
2. Under **Authorized redirect URIs** add exactly: your Streamlit app URL, e.g. `https://yourapp-username.streamlit.app/`.  
3. Download the client secret JSON; its full content is what you put in `GOOGLE_CREDENTIALS_JSON` (or `GOOGLE_CREDENTIALS_DOCS_JSON`).  
4. Ensure the OAuth consent screen includes scopes for Google Docs and Drive (or use the default scope set the app requests).

## 4. First-time sign-in

1. Deploy the app and open it.  
2. If `GOOGLE_TOKEN_JSON` is not set, the app shows **“Sign in with Google”**.  
3. Click it, complete sign-in in the new tab, and you’ll be redirected back to the app.  
4. The app will show a token; copy the **entire** JSON.  
5. In Streamlit Cloud: **Settings → Secrets**, add (or update) `GOOGLE_TOKEN_JSON` with that JSON.  
6. Save and reload the app. Future runs will use this token and won’t ask to sign in again.

After that, running an audit will create two Google Docs (report + gap analysis) and store them in your Drive folder (e.g. **SEO-Health-Tekspot**).
