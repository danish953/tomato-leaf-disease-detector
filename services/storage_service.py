from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from utils.errors import AppError


@dataclass(frozen=True)
class SavedUpload:
    absolute_path: Path
    static_path: str


def save_upload(file: FileStorage, session_id: str, upload_folder: Path) -> SavedUpload:
    original = secure_filename(file.filename or "leaf.jpg")
    extension = original.rsplit(".", 1)[-1].lower()
    filename = f"{session_id}.{extension}"
    absolute_path = upload_folder / filename

    try:
        file.save(absolute_path)
    except Exception as exc:
        raise AppError("Could not save uploaded image. Please try again.") from exc

    return SavedUpload(absolute_path=absolute_path, static_path=f"uploads/{filename}")
