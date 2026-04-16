import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from utils.comparison import comparison_payload


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, status_code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/health":
            self._send_json(200, {"status": "OK", "message": "Backend is healthy"})
            return

        if parsed.path == "/compare":
            params = parse_qs(parsed.query)
            query = (params.get("query", [""])[0] or "").strip()
            category = (params.get("category", ["laptop"])[0] or "laptop").strip()
            try:
                limit = int(params.get("limit", ["20"])[0])
            except ValueError:
                limit = 20

            limit = max(1, min(limit, 50))

            try:
                payload = comparison_payload(query=query, limit=limit, category=category)
                self._send_json(200, payload)
            except Exception as error:
                self._send_json(500, {
                    "error": "Failed to compare products",
                    "detail": str(error),
                })
            return

        self._send_json(404, {"error": "Not found"})


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 5000), Handler)
    print("Server running on http://localhost:5000")
    server.serve_forever()
