# Troubleshooting Guide

## Common Issues and Solutions

### 1. PageSpeed API 400 Bad Request Error

**Error Message:**
```
PageSpeed (desktop) failed: 400 Client Error: Bad Request
```

**Possible Causes:**

1. **API Key Restrictions**
   - Your API key might have IP address or HTTP referrer restrictions
   - **Solution**: Go to [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials
   - Edit your API key and remove IP/referrer restrictions, or add Streamlit Cloud's IP ranges

2. **API Quota Exceeded**
   - You may have exceeded the free tier quota (25,000 requests/day)
   - **Solution**: Check your quota usage in Google Cloud Console → APIs & Services → Dashboard

3. **Invalid URL Format**
   - The URL might not be accessible or properly formatted
   - **Solution**: Ensure the URL is publicly accessible and includes `http://` or `https://`

4. **API Not Enabled**
   - PageSpeed Insights API might not be enabled for your project
   - **Solution**: Enable it in Google Cloud Console → APIs & Services → Library → Search "PageSpeed Insights API" → Enable

**Note**: The app will continue to work with mobile results even if desktop fails. This is expected behavior.

### 2. Google Doc Creation Failed - No Credentials

**Error Message:**
```
Google Doc creation failed: No Google credentials (credentials.json not found or invalid)
```

**Solution Steps:**

1. **Verify Streamlit Secrets are Added**
   - Go to https://share.streamlit.io/ → Your app → Settings → Secrets
   - Ensure these secrets exist:
     - `GOOGLE_CREDENTIALS_JSON`
     - `GOOGLE_TOKEN_JSON`

2. **Check Secret Format**
   - `GOOGLE_CREDENTIALS_JSON` should contain the **entire JSON** from your Docs client secret file
   - `GOOGLE_TOKEN_JSON` should contain the **entire JSON** from `token_docs.json`
   - Both should be valid JSON (can be pasted as-is or formatted as TOML)

3. **Generate Token (if missing)**
   - If you don't have `token_docs.json`, you need to generate it locally:
   ```bash
   # On your local machine
   streamlit run app.py
   # Sign in with Google when prompted
   # Copy the entire content of token_docs.json
   ```

4. **Verify Secret Names**
   - Secret names are case-sensitive
   - Must be exactly: `GOOGLE_CREDENTIALS_JSON` and `GOOGLE_TOKEN_JSON`

5. **Redeploy After Adding Secrets**
   - After adding/updating secrets, the app should auto-redeploy
   - If not, manually trigger a redeploy

**Example Secret Format:**

In Streamlit Secrets (TOML format):
```toml
GOOGLE_CREDENTIALS_JSON = '''
{"web":{"client_id":"...","project_id":"...","auth_uri":"...","token_uri":"...","auth_provider_x509_cert_url":"...","client_secret":"..."}}
'''

GOOGLE_TOKEN_JSON = '''
{"token":"...","refresh_token":"...","token_uri":"...","client_id":"...","client_secret":"...","scopes":[...],"expiry":"..."}
'''
```

Or paste the JSON directly (Streamlit will parse it automatically).

### 3. Token Expired Error

**Error Message:**
```
Failed to use token from secrets: Token expired
```

**Solution:**
1. Regenerate `token_docs.json` locally (follow steps in `STREAMLIT_CLOUD_SECRETS.md`)
2. Update `GOOGLE_TOKEN_JSON` secret with the new token content
3. Redeploy the app

### 4. App Works Locally But Not on Streamlit Cloud

**Checklist:**
- ✅ All secrets are added correctly
- ✅ Secret names match exactly (case-sensitive)
- ✅ JSON content is valid (no missing braces/quotes)
- ✅ `GOOGLE_TOKEN_JSON` contains a valid refresh token
- ✅ Google account used to generate token has access to Drive folder
- ✅ API keys are added as secrets (not just in `.env`)

### 5. Getting More Detailed Error Messages

The updated code now provides more detailed error messages. If you see an error, check:
1. The full error message in the Streamlit app
2. Streamlit Cloud logs (Settings → Logs)
3. Verify each secret individually

## Still Having Issues?

1. **Check Streamlit Cloud Logs**
   - Go to your app → Settings → Logs
   - Look for detailed error messages

2. **Test Secrets Locally**
   - Create a test script to verify secrets are readable
   - Use `st.secrets.get("SECRET_NAME")` to test

3. **Verify API Keys**
   - Test your PageSpeed API key directly:
     ```bash
     curl "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://example.com&key=YOUR_KEY&strategy=mobile"
     ```

4. **Check Google Cloud Console**
   - Verify APIs are enabled
   - Check quota limits
   - Review API key restrictions

## Quick Reference

| Issue | Check | Solution |
|-------|-------|----------|
| PageSpeed 400 | API key restrictions | Remove IP/referrer restrictions |
| No credentials | Secrets added? | Add `GOOGLE_CREDENTIALS_JSON` and `GOOGLE_TOKEN_JSON` |
| Token expired | Token valid? | Regenerate `token_docs.json` |
| App not deploying | Secrets format? | Verify JSON is valid |

For detailed setup instructions, see [STREAMLIT_CLOUD_SECRETS.md](STREAMLIT_CLOUD_SECRETS.md).
