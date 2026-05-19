from __future__ import annotations

from functools import wraps

from flask import current_app, jsonify, request


def apply_security_headers(app):
    @app.after_request
    def set_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response


def require_api_key(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_app.config["REQUIRE_API_KEY"]:
            provided = request.headers.get("X-API-Key", "")
            expected = current_app.config["API_KEY"]
            if not expected or provided != expected:
                return jsonify({"success": False, "error": "Unauthorized request."}), 401
        return view(*args, **kwargs)

    return wrapped
