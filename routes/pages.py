from flask import Blueprint, render_template

pages_bp = Blueprint("pages", __name__)


@pages_bp.get("/")
def index():
    return render_template("index.html")


@pages_bp.get("/history")
def history():
    return render_template("history.html")


@pages_bp.get("/result/<session_id>")
def result(session_id: str):
    return render_template("result.html", session_id=session_id)
