from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import HTTPException, RequestEntityTooLarge

from utils.errors import AppError


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "error": error.message}), error.status_code
        return render_template("error.html", message=error.message, status_code=error.status_code), error.status_code

    @app.errorhandler(RequestEntityTooLarge)
    def handle_large_file(error):
        message = "The uploaded image is too large. Please upload a smaller file."
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "error": message}), 413
        return render_template("error.html", message=message, status_code=413), 413

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        message = error.description or "Something went wrong."
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "error": message}), error.code
        return render_template("error.html", message=message, status_code=error.code), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        app.logger.exception("Unhandled application error")
        message = "Something went wrong while processing your request."
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "error": message}), 500
        return render_template("error.html", message=message, status_code=500), 500
