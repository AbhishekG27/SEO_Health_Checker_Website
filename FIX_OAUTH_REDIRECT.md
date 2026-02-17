# Fix OAuth Redirect URI Mismatch Error

## Problem
Error: `redirect_uri_mismatch` - This happens when the redirect URI in Google Cloud Console doesn't match what the OAuth flow is trying to use.

## Solution: Configure Redirect URIs in Google Cloud Console

### Step 1: Go to Google Cloud Console

1. Open [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project: **seo-health-checker-487011**
3. Go to **APIs & Services** → **Credentials**

### Step 2: Edit Your OAuth 2.0 Client

Find your OAuth 2.0 Client ID (the one ending in `_docs.json`):
- `623612593951-paaqhoeija3o1ceqo0ve0r2vibnbivd5.apps.googleusercontent.com`

Click **Edit** (pencil icon).

### Step 3: Add Authorized Redirect URIs

In the **Authorized redirect URIs** section, add these URIs:

```
http://localhost:8080/
http://localhost:8080
http://127.0.0.1:8080/
http://127.0.0.1:8080
http://localhost:8081/
http://localhost:8081
http://127.0.0.1:8081/
http://127.0.0.1:8081
```

**Note**: The code uses `port=0` which picks a random port, but common ports are 8080-8090. Add multiple ports to cover most cases.

### Step 4: Save Changes

Click **Save** at the bottom of the page.

### Step 5: Alternative - Use Fixed Port (Recommended)

Instead of adding many ports, we can modify the code to use a fixed port. This is more reliable.

## Alternative Solution: Use Fixed Port

If you want to avoid adding multiple redirect URIs, we can modify the code to use a fixed port (e.g., 8080).

Would you like me to update the code to use a fixed port? This way you only need to add `http://localhost:8080/` and `http://127.0.0.1:8080/` to your redirect URIs.

## Quick Fix: Add Common Ports

For now, add these redirect URIs to your OAuth client:

1. `http://localhost:8080/`
2. `http://localhost:8080`
3. `http://127.0.0.1:8080/`
4. `http://127.0.0.1:8080`
5. `http://localhost:8081/`
6. `http://localhost:8081`
7. `http://127.0.0.1:8081/`
8. `http://127.0.0.1:8081`

This should cover most cases. After saving, try running the app again.

## Verify Your Setup

After adding redirect URIs:

1. **Wait 1-2 minutes** for changes to propagate
2. **Run the app locally**: `streamlit run app.py`
3. **Try the Google Docs export** feature
4. The OAuth flow should now work without the redirect_uri_mismatch error

## Still Having Issues?

If you're still getting the error:

1. Check which port the app is trying to use (it will show in the terminal)
2. Add that specific port to your redirect URIs
3. Make sure you're editing the **correct OAuth client** (the Docs one, not Drive)
