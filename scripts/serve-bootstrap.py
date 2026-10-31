#!/usr/bin/env python
"""Serve the bootstrap page over HTTP with {{HTTPS_URL}} substituted.

Development only. The Pi's nginx performs the equivalent role with
sub_filter or a pre-substituted file (P5).

Reads:
  frontend/public/bootstrap/index.html   (template, contains {{HTTPS_URL}})
  frontend/public/bootstrap/bootstrap.css
  out/ca.crt                             (public CA cert only; never ca.key)
"""
import http.server
import os
import sys

if "WindowsApps" in sys.executable:
    sys.exit(f"error: Store stub interpreter ({sys.executable}). "
             f"Activate the venv: source .venv/Scripts/activate")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOT = os.path.join(REPO, "frontend", "public", "bootstrap")
CA   = os.path.join(REPO, "out", "ca.crt")
PORT = int(os.environ.get("BOOTSTRAP_PORT", "8080"))
HTTPS_URL = os.environ.get("BOOTSTRAP_HTTPS_URL", "https://agelgil.internal/")

for p, label in ((os.path.join(BOOT, "index.html"), "index.html"),
                 (os.path.join(BOOT, "bootstrap.css"), "bootstrap.css"),
                 (CA, "out/ca.crt")):
    if not os.path.isfile(p):
        sys.exit(f"missing {label}: {p}")

with open(os.path.join(BOOT, "index.html"), "r", encoding="utf-8") as f:
    HTML = f.read().replace("{{HTTPS_URL}}", HTTPS_URL).encode("utf-8")

with open(os.path.join(BOOT, "bootstrap.css"), "rb") as f:
    CSS = f.read()

with open(CA, "rb") as f:
    CACERT = f.read()

ROUTES = {
    "/":              (HTML,   "text/html; charset=utf-8"),
    "/index.html":    (HTML,   "text/html; charset=utf-8"),
    "/bootstrap.css": (CSS,    "text/css; charset=utf-8"),
    "/ca.crt":        (CACERT, "application/x-x509-ca-cert"),
}

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        hit = ROUTES.get(path)
        if hit is None:
            self.send_error(404)
            return
        body, ctype = hit
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

print(f"serving {BOOT} on http://0.0.0.0:{PORT} (HTTPS_URL={HTTPS_URL})", flush=True)
http.server.HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
