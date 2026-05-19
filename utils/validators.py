from __future__ import annotations

from pathlib import Path

from werkzeug.datastructures import FileStorage

from utils.errors import ValidationError


def validate_image_upload(file: FileStorage | None, config: dict) -> None:
    if file is None or not file.filename:
        raise ValidationError("Please upload a tomato leaf image.")

    extension = Path(file.filename).suffix.lower().replace(".", "")
    if extension not in config["ALLOWED_EXTENSIONS"]:
        allowed = ", ".join(sorted(config["ALLOWED_EXTENSIONS"]))
        raise ValidationError(f"Unsupported file type. Allowed formats: {allowed}.")

    content_type = (file.content_type or "").lower()
    if content_type and not content_type.startswith("image/"):
        raise ValidationError("The uploaded file does not look like an image.")
