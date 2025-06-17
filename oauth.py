import os
import webbrowser
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

# ─── Config & Constants ───────────────────────────────────────────────────────
load_dotenv()
CLIENT_ID     = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI  = os.getenv("REDIRECT_URI", "http://localhost:8000/callback")
SCOPE         = "openid profile w_member_social"  # must match exactly your app’s scopes

AUTH_URL      = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL     = "https://www.linkedin.com/oauth/v2/accessToken"
ME_URL        = "https://api.linkedin.com/v2/me"

if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError("CLIENT_ID and CLIENT_SECRET must be set in .env")

# ─── Tiny HTTP Server to Catch the Redirect ──────────────────────────────────
class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        qs = parse_qs(urlparse(self.path).query)
        if "code" in qs:
            self.server.auth_code = qs["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h2>Authorization complete. You can close this window.</h2>")
        else:
            self.send_response(400)
            self.end_headers()

# ─── Step 1: Open Browser & Fetch the Auth Code ──────────────────────────────
def fetch_auth_code():
    server = HTTPServer(("localhost", 8000), OAuthHandler)
    params = {
        "response_type": "code",
        "client_id":     CLIENT_ID,
        "redirect_uri":  REDIRECT_URI,
        "scope":         SCOPE
    }
    url = AUTH_URL + "?" + "&".join(f"{k}={requests.utils.quote(v)}" for k,v in params.items())
    print("Opening browser for LinkedIn login…")
    webbrowser.open(url)
    server.handle_request()    # wait for a single incoming request
    return getattr(server, "auth_code", None)

# ─── Step 2: Exchange Auth Code for Access Token ─────────────────────────────
def exchange_token(code: str) -> str:
    resp = requests.post(TOKEN_URL, data={
        "grant_type":   "authorization_code",
        "code":         code,
        "redirect_uri": REDIRECT_URI,
        "client_id":    CLIENT_ID,
        "client_secret":CLIENT_SECRET
    })
    resp.raise_for_status()
    return resp.json()["access_token"]

# ─── Step 3: Fetch Your Member ID & Build URN ────────────────────────────────
def fetch_member_urn(token: str) -> str:
    """
    Uses the OIDC UserInfo endpoint to retrieve the member's subject ID
    and build their LinkedIn URN.
    """
    resp = requests.get(
        "https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {token}"}
    )
    resp.raise_for_status()
    sub = resp.json()["sub"]
    return f"urn:li:person:{sub}"


# ─── Step 4: Update .env with ACCESS_TOKEN and AUTHOR_URN ────────────────────
def update_env(token: str, author_urn: str):
    path = ".env"
    lines = []
    seen_token = seen_urn = False

    with open(path, "r") as f:
        for L in f:
            if L.startswith("ACCESS_TOKEN="):
                lines.append(f"ACCESS_TOKEN={token}\n")
                seen_token = True
            elif L.startswith("AUTHOR_URN="):
                lines.append(f"AUTHOR_URN={author_urn}\n")
                seen_urn = True
            else:
                lines.append(L)

    if not seen_token:
        lines.append(f"\nACCESS_TOKEN={token}\n")
    if not seen_urn:
        lines.append(f"AUTHOR_URN={author_urn}\n")

    with open(path, "w") as f:
        f.writelines(lines)

# ─── Main Flow ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    code = fetch_auth_code()
    if not code:
        print("No code received; check your redirect URI and scopes.")
        exit(1)

    print("Exchanging code for access token…")
    token = exchange_token(code)

    print("Fetching your LinkedIn URN…")
    urn = fetch_member_urn(token)

    update_env(token, urn)
    print(f".env updated:\n  ACCESS_TOKEN={token}\n  AUTHOR_URN={urn}")
