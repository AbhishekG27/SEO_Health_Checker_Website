# Streamlit Cloud Secrets Setup Guide

This guide explains how to add your Google OAuth credentials and other API keys as secrets in Streamlit Cloud.

## Prerequisites

Before adding secrets, you need to generate a Google OAuth token. This must be done **once** on a local machine:

### Step 1: Generate Google OAuth Token (One-time setup)

1. **Clone your repository locally** (if not already done):
   ```bash
   git clone <your-repo-url>
   cd new-automation
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the credentials file**:
   - Copy your **Docs** client secret file (the one ending in `_docs.json`) to `credentials.json` in the project root
   - Or set the `GOOGLE_CREDENTIALS_FILE` environment variable to point to the file

4. **Run the app locally**:
   ```bash
   streamlit run app.py
   ```

5. **Sign in with Google**:
   - When the browser opens, sign in with the Google account that should own the Drive folder and Docs
   - After successful authentication, a file named `token_docs.json` will be created in your project folder

6. **Copy the token content**:
   - Open `token_docs.json` in a text editor
   - Copy **ALL** its content (the entire JSON)
   - You'll need this for Step 3 below

## Step 2: Add Secrets to Streamlit Cloud

1. **Go to your Streamlit Cloud dashboard**: https://share.streamlit.io/

2. **Select your app** (or create a new app if you haven't deployed yet)

3. **Open Secrets Manager**:
   - Click on your app
   - Go to **Settings** (⚙️ icon) or **Manage app**
   - Click on **Secrets** in the left sidebar

4. **Add the following secrets**:

### Required Secrets:

#### 1. `GOOGLE_CREDENTIALS_JSON`
- **Value**: Copy the **entire content** of your Docs client secret JSON file
  - File: `client_secret_...docs.json` (your actual file name)
- **How to add**:
  - Open the file in a text editor
  - Select all (Ctrl+A / Cmd+A)
  - Copy (Ctrl+C / Cmd+C)
  - Paste into the Streamlit secret value field
- **Example format** (replace with your actual values):
  ```json
  {"web":{"client_id":"YOUR_CLIENT_ID.apps.googleusercontent.com","project_id":"your-project-id","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"YOUR_CLIENT_SECRET"}}
  ```

#### 2. `GOOGLE_TOKEN_JSON`
- **Value**: Copy the **entire content** of `token_docs.json` (generated in Step 1)
- **How to add**:
  - Open `token_docs.json` in a text editor
  - Select all (Ctrl+A / Cmd+A)
  - Copy (Ctrl+C / Cmd+C)
  - Paste into the Streamlit secret value field
- **Note**: This is the authorized user token that allows the app to access Google Docs/Drive without requiring browser authentication

#### 3. `GOOGLE_PAGESPEED_API_KEY`
- **Value**: Your Google PageSpeed Insights API key
- **How to get**: 
  - Go to [Google Cloud Console](https://console.cloud.google.com/)
  - Enable PageSpeed Insights API
  - Create credentials → API Key
- **Example**: `AIzaSyAbCdEfGhIjKlMnOpQrStUvWxYz1234567`

### Optional Secrets:

#### 4. `GEMINI_API_KEY`
- **Value**: Your Google Gemini API key (for gap analysis feature)
- **How to get**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

#### 5. `SERPER_API_KEY`
- **Value**: Your Serper API key (for SERP data feature)
- **How to get**: Sign up at [serper.dev](https://serper.dev)

#### 6. `GOOGLE_DRIVE_FOLDER_NAME`
- **Value**: Name of the Drive folder where docs will be created
- **Default**: `SEO-Health-Tekspot`
- **Example**: `SEO-Health-Tekspot`

## Step 3: Format for Streamlit Secrets

When adding JSON secrets in Streamlit Cloud, you have two options:

### Option A: Paste as JSON string (Recommended)
Paste the entire JSON content as a single-line string. Streamlit will automatically parse it.

### Option B: Format as TOML (Alternative)
You can also format it as TOML in the secrets editor:

```toml
GOOGLE_CREDENTIALS_JSON = '''
{"web":{"client_id":"...","project_id":"...","auth_uri":"...","token_uri":"...","auth_provider_x509_cert_url":"...","client_secret":"..."}}
'''

GOOGLE_TOKEN_JSON = '''
{"token":"...","refresh_token":"...","token_uri":"...","client_id":"...","client_secret":"...","scopes":[...],"expiry":"..."}
'''
```

## Step 4: Verify Secrets

After adding secrets:

1. **Redeploy your app** (or wait for auto-deploy if enabled)
2. **Check the app logs** for any authentication errors
3. **Test the Google Docs export** feature in your app

## Troubleshooting

### Issue: "No Google credentials" error
- **Solution**: Make sure `GOOGLE_CREDENTIALS_JSON` is added correctly. Check that the entire JSON is copied (including all braces and quotes).

### Issue: "Token expired" or authentication errors
- **Solution**: 
  - Regenerate `token_docs.json` locally (follow Step 1 again)
  - Update `GOOGLE_TOKEN_JSON` secret with the new token content
  - Redeploy the app

### Issue: "Invalid JSON format"
- **Solution**: Make sure you're copying the entire JSON file content, not just part of it. The JSON should start with `{` and end with `}`.

### Issue: App works locally but not on Streamlit Cloud
- **Solution**: 
  - Verify all secrets are added correctly
  - Check that `GOOGLE_TOKEN_JSON` contains a valid refresh token
  - Ensure the Google account used to generate the token has access to the Drive folder

## Security Notes

⚠️ **Important**:
- Never commit `credentials.json`, `token_docs.json`, or any client secret files to your repository
- These files are already in `.gitignore`
- Secrets in Streamlit Cloud are encrypted and only accessible to your app
- If you suspect a secret has been compromised, regenerate it immediately

## Quick Reference

| Secret Name | Required | Description |
|------------|----------|-------------|
| `GOOGLE_CREDENTIALS_JSON` | ✅ Yes | Full content of Docs client secret JSON |
| `GOOGLE_TOKEN_JSON` | ✅ Yes | Full content of `token_docs.json` |
| `GOOGLE_PAGESPEED_API_KEY` | ✅ Yes | PageSpeed Insights API key |
| `GEMINI_API_KEY` | ⚠️ Optional | For gap analysis feature |
| `SERPER_API_KEY` | ⚠️ Optional | For SERP data feature |
| `GOOGLE_DRIVE_FOLDER_NAME` | ⚠️ Optional | Drive folder name (default: SEO-Health-Tekspot) |
