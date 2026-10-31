#!/usr/bin/env python
"""Minimal HTTPS static server for P1.03 handset testing.

Run from repo root with venv active:
    python scripts/serve-https.py

The script locates the repo from __file__ and resolves cert/key paths to
absolute before any chdir, so it works regardless of cwd.
"""
import http.server
import os
import ssl
import sys

if "WindowsApps" in sys.executable:
    sys.exit(f"error: Store stub interpreter ({sys.executable}). "
             f"Activate the venv: source .venv/Scripts/activate")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(REPO, "out", "leaf.crt")
KEY  = os.path.join(REPO, "out", "leaf.key")
DIR  = os.path.join(REPO, "frontend", "dist")
PORT = int(os.environ.get("PORT", "4443"))

for label, path in (("cert", CERT), ("key", KEY)):
    if not os.path.isfile(path):
        sys.exit(f"missing {label}: {path}")
if not os.path.isdir(DIR):
    sys.exit(f"missing dist dir: {DIR} (run: cd frontend && npm run build)")

os.chdir(DIR)
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.load_cert_chain(CERT, KEY)
srv = http.server.HTTPServer(("0.0.0.0", PORT), http.server.SimpleHTTPRequestHandler)
srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
print(f"serving {DIR} on https://0.0.0.0:{PORT}", flush=True)
srv.serve_forever()
