from __future__ import annotations

import uuid
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request

from database.extensions import db
from models.prediction import Prediction
from services.disease_service import get_disease_details
from services.gradcam_service import GradCAMService
from services.image_service import ImageService
from services.storage_service import save_upload
from utils.errors import AppError, DatabaseError, ModelUnavailableError, ValidationError
from utils.security import require_api_key
from utils.validators import validate_image_upload

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.post("/detect")
@require_api_key
def detect():
    file = request.files.get("image")
    validate_image_upload(file, current_app.config)

    session_id = str(uuid.uuid4())
    saved = save_upload(file, session_id, current_app.config["UPLOAD_FOLDER"])

    model_service = current_app.extensions["model_service"]
    if not model_service.is_ready:
        raise ModelUnavailableError(model_service.load_error)

    image_service = ImageService(current_app.config)
    image_input = image_service.load_and_preprocess(saved.absolute_path)

    try:
        prediction = model_service.predict(image_input.tensor)
        details = get_disease_details(prediction.label)
        gradcam_path = GradCAMService(current_app.config).generate(
            model_service=model_service,
            image_input=image_input,
            target_index=prediction.class_index,
            session_id=session_id,
        )

        record = Prediction(
            session_id=session_id,
            image_path=saved.static_path,
            gradcam_path=gradcam_path,
            disease_name=details["name"],
            confidence_score=prediction.confidence,
            severity=details["severity"],
            treatment=details["treatment"],
            solution=details["solution"],
            top_predictions=prediction.top_predictions,
            prediction_time=prediction.prediction_time,
        )
        db.session.add(record)
        db.session.commit()
    except AppError:
        raise
    except Exception as exc:
        current_app.logger.exception("Prediction failed")
        raise AppError("Prediction failed. Please try another clear tomato leaf image.") from exc

    payload = record.to_dict()
    payload["success"] = True
    return jsonify(payload), 201


@api_bp.get("/result/<session_id>")
def api_result(session_id: str):
    record = Prediction.query.filter_by(session_id=session_id).first()
    if not record:
        raise ValidationError("Prediction result was not found.", status_code=404)

    payload = record.to_dict()
    payload["success"] = True
    return jsonify(payload)


@api_bp.get("/history")
def api_history():
    try:
        rows = Prediction.query.order_by(Prediction.created_at.desc()).limit(50).all()
    except Exception as exc:
        current_app.logger.exception("Could not fetch prediction history")
        raise DatabaseError("Could not load prediction history right now.") from exc

    return jsonify({"success": True, "items": [row.to_dict() for row in rows]})


@api_bp.get("/health")
def health():
    model_service = current_app.extensions["model_service"]
    return jsonify(
        {
            "success": True,
            "model_ready": model_service.is_ready,
            "model_path": str(Path(current_app.config["MODEL_PATH"])),
            "database": "ready",
        }
    )
