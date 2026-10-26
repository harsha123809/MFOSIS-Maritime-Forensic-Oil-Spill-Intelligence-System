"""Vercel serverless entry point: exposes the FastAPI app from backend/.

vercel.json rewrites /api/<path> to /api/index?__path=<path>. Depending on the
Vercel runtime version, the function sees either the original URL or the
rewritten one, so the original path is restored from __path before FastAPI
routes the request. That makes routing correct under both behaviours.
"""
import sys
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlencode

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.main import app as fastapi_app  # noqa: E402


async def app(scope, receive, send):
    if scope["type"] == "http":
        query = parse_qsl(scope.get("query_string", b"").decode(), keep_blank_values=True)
        original = [v for k, v in query if k == "__path"]
        if original:
            path = "/api/" + unquote(original[0]).lstrip("/")
            rest = urlencode([(k, v) for k, v in query if k != "__path"])
            scope = {**scope, "path": path, "raw_path": path.encode(), "query_string": rest.encode()}
    await fastapi_app(scope, receive, send)
