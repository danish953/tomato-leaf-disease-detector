from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _path_env(name: str, default: Path) -> Path:
    value = os.getenv(name)
    if not value:
        return default
    path = Path(value)
    return path if path.is_absolute() else BASE_DIR / path


TOMATO_CLASSES = [
    "Bacterial_spot",
    "Early_blight",
    "Late_blight",
    "Leaf_Mold",
    "Septoria_leaf_spot",
    "Spider_mites Two-spotted_spider_mite",
    "Target_Spot",
    "Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato_mosaic_virus",
    "healthy",
    "powdery_mildew",
]


def _csv_env(name: str, default: list[str]) -> list[str]:
    value = os.getenv(name)
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
    ENV = os.getenv("FLASK_ENV", "production")

    DATABASE_FOLDER = BASE_DIR / "database"
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{(DATABASE_FOLDER / 'plant_disease.db').as_posix()}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
    GRADCAM_FOLDER = BASE_DIR / "static" / "gradcam"
    LOG_FOLDER = BASE_DIR / "logs"
    MODEL_PATH = _path_env("MODEL_PATH", BASE_DIR / "ai_model" / "model.onnx")
    CLASS_NAMES = _csv_env("CLASS_NAMES", TOMATO_CLASSES)

    MAX_CONTENT_LENGTH = int(os.getenv("MAX_UPLOAD_MB", "8")) * 1024 * 1024
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
    IMAGE_SIZE = int(os.getenv("IMAGE_SIZE", "224"))
    NORMALIZATION_MODE = os.getenv("NORMALIZATION_MODE", "imagenet")
    ONNX_PROVIDERS = ["CPUExecutionProvider"]

    REQUIRE_API_KEY = os.getenv("REQUIRE_API_KEY", "0") == "1"
    API_KEY = os.getenv("API_KEY", "")
    GRADCAM_GRID_SIZE = int(os.getenv("GRADCAM_GRID_SIZE", "7"))


class DevelopmentConfig(Config):
    DEBUG = True
    ENV = "development"


class ProductionConfig(Config):
    DEBUG = False
    ENV = "production"


def get_config() -> type[Config]:
    if os.getenv("FLASK_ENV") == "development":
        return DevelopmentConfig
    return ProductionConfig
