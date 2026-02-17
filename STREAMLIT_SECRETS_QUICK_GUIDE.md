# Quick Guide: Add Google Credentials to Streamlit Cloud Secrets

## Step 1: Generate Token Locally (One-time)

Before adding secrets, you need to generate a Google OAuth token locally:

1. **Run the app locally**:
   ```bash
   streamlit run app.py
   ```

2. **Sign in with Google** when prompted (this will create `token_docs.json`)

3. **Copy the token content**:
   - Open `token_docs.json` in a text editor
   - Copy ALL its content (entire JSON)

## Step 2: Add Secrets to Streamlit Cloud

Go to your Streamlit Cloud app → **Settings** → **Secrets**

Add these secrets in **TOML format**:

### 1. GOOGLE_CREDENTIALS_JSON

Add the **Docs** client secret JSON content:

```toml
GOOGLE_CREDENTIALS_JSON = '''
{"web":{"client_id":"YOUR_CLIENT_ID.apps.googleusercontent.com","project_id":"your-project-id","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"YOUR_CLIENT_SECRET"}}
'''
```

**Note**: The Docs client secret works for both Docs AND Drive APIs (it has the necessary scopes).

### 2. GOOGLE_TOKEN_JSON

Add the token content from `token_docs.json` (generated in Step 1):

```toml
GOOGLE_TOKEN_JSON = '''
{"token":"YOUR_TOKEN_HERE","refresh_token":"YOUR_REFRESH_TOKEN_HERE","token_uri":"https://oauth2.googleapis.com/token","client_id":"YOUR_CLIENT_ID.apps.googleusercontent.com","client_secret":"YOUR_CLIENT_SECRET","scopes":["https://www.googleapis.com/auth/documents","https://www.googleapis.com/auth/drive.file"],"expiry":"YOUR_EXPIRY_HERE"}
'''
```

**Important**: Replace the example token above with your actual `token_docs.json` content!

### 3. Optional: GOOGLE_DRIVE_FOLDER_NAME

```toml
GOOGLE_DRIVE_FOLDER_NAME = "SEO Health Checker"
```

## Complete Example (All Secrets Together)

```toml
GOOGLE_PAGESPEED_API_KEY = "YOUR_PAGESPEED_API_KEY"
SERPER_API_KEY = "YOUR_SERPER_API_KEY"
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

GOOGLE_CREDENTIALS_JSON = '''
{"web":{"client_id":"YOUR_CLIENT_ID.apps.googleusercontent.com","project_id":"your-project-id","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"YOUR_CLIENT_SECRET"}}
'''

GOOGLE_TOKEN_JSON = '''
{"token":"YOUR_TOKEN_HERE","refresh_token":"YOUR_REFRESH_TOKEN_HERE","token_uri":"https://oauth2.googleapis.com/token","client_id":"YOUR_CLIENT_ID.apps.googleusercontent.com","client_secret":"YOUR_CLIENT_SECRET","scopes":["https://www.googleapis.com/auth/documents","https://www.googleapis.com/auth/drive.file"],"expiry":"YOUR_EXPIRY_HERE"}
'''

GOOGLE_DRIVE_FOLDER_NAME = "SEO Health Checker"
```

## Important Notes

1. **Use Docs Client Secret Only**: The Docs client secret (`client_secret_...docs.json`) works for both Docs and Drive APIs. You don't need to add the Drive client secret separately.

2. **Token Must Be Generated Locally**: You MUST generate `token_docs.json` locally first by running the app and signing in. This token contains your authorized access.

3. **Format**: Use triple quotes `'''` for multi-line JSON strings in TOML.

4. **Wait for Propagation**: Changes take about 1 minute to propagate after saving.

5. **Don't Commit Secrets**: Never commit `client_secret*.json` or `token_docs.json` files to git (they're already in `.gitignore`).

## After Adding Secrets

1. **Save** the secrets in Streamlit Cloud
2. **Wait 1-2 minutes** for changes to propagate
3. **Redeploy** your app (or it will auto-redeploy)
4. **Test** the Google Docs export feature

## Troubleshooting

- **"No Google credentials" error**: Make sure both `GOOGLE_CREDENTIALS_JSON` and `GOOGLE_TOKEN_JSON` are added
- **"Token expired" error**: Regenerate `token_docs.json` locally and update `GOOGLE_TOKEN_JSON`
- **"Invalid JSON" error**: Make sure the JSON is valid and properly escaped in TOML format
