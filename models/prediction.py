from __future__ import annotations

from datetime import datetime, timezone

from database.extensions import db


class Prediction(db.Model):
    __tablename__ = "predictions"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    image_path = db.Column(db.String(255), nullable=False)
    gradcam_path = db.Column(db.String(255), nullable=True)
    disease_name = db.Column(db.String(120), nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    severity = db.Column(db.String(32), nullable=False)
    treatment = db.Column(db.Text, nullable=False)
    solution = db.Column(db.Text, nullable=False)
    top_predictions = db.Column(db.JSON, nullable=False, default=list)
    prediction_time = db.Column(db.Float, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "image_path": self.image_path,
            "gradcam_image": self.gradcam_path,
            "disease": self.disease_name,
            "disease_name": self.disease_name,
            "confidence": round(self.confidence_score, 2),
            "confidence_score": round(self.confidence_score, 2),
            "severity": self.severity,
            "treatment": self.treatment,
            "solution": self.solution,
            "top_predictions": self.top_predictions or [],
            "prediction_time": round(self.prediction_time, 4),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
