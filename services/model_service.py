from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np
import onnxruntime as ort


@dataclass(frozen=True)
class ModelPrediction:
    label: str
    class_index: int
    confidence: float
    top_predictions: list[dict]
    probabilities: np.ndarray
    prediction_time: float


class ModelService:
    def __init__(self, config: dict):
        self.model_path = config["MODEL_PATH"]
        self.class_names = list(config["CLASS_NAMES"])
        self.providers = config["ONNX_PROVIDERS"]
        self.session: ort.InferenceSession | None = None
        self.input_name = ""
        self.input_layout = "NCHW"
        self.load_error = ""
        self._load_model()

    @property
    def is_ready(self) -> bool:
        return self.session is not None

    def _load_model(self) -> None:
        if not self.model_path.exists():
            self.load_error = f"Model file not found at {self.model_path}. Copy your trained ONNX file to ai_model/model.onnx."
            return

        try:
            options = ort.SessionOptions()
            options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            options.intra_op_num_threads = 1
            self.session = ort.InferenceSession(
                str(self.model_path),
                sess_options=options,
                providers=self.providers,
            )
            model_input = self.session.get_inputs()[0]
            self.input_name = model_input.name
            shape = model_input.shape
            if len(shape) == 4 and shape[-1] == 3:
                self.input_layout = "NHWC"
        except Exception as exc:
            self.session = None
            self.load_error = f"Could not load ONNX model: {exc}"

    def predict(self, tensor: np.ndarray) -> ModelPrediction:
        start = time.perf_counter()
        probabilities = self.predict_probabilities(tensor)
        elapsed = time.perf_counter() - start

        class_index = int(np.argmax(probabilities))
        confidence = float(probabilities[class_index] * 100.0)
        top_indices = np.argsort(probabilities)[::-1][:3]
        top_predictions = [
            {
                "label": self.class_names[int(index)] if int(index) < len(self.class_names) else f"Class {int(index)}",
                "confidence": round(float(probabilities[int(index)] * 100.0), 2),
            }
            for index in top_indices
        ]

        return ModelPrediction(
            label=self.class_names[class_index] if class_index < len(self.class_names) else f"Class {class_index}",
            class_index=class_index,
            confidence=confidence,
            top_predictions=top_predictions,
            probabilities=probabilities,
            prediction_time=elapsed,
        )

    def predict_probabilities(self, tensor: np.ndarray) -> np.ndarray:
        if self.session is None:
            raise RuntimeError(self.load_error or "Model is not loaded.")

        model_tensor = self._fit_layout(tensor)
        outputs = self.session.run(None, {self.input_name: model_tensor})
        logits = np.asarray(outputs[0])
        if logits.ndim > 1:
            logits = logits[0]
        logits = logits.astype(np.float32)

        if np.all(logits >= 0) and np.isclose(float(np.sum(logits)), 1.0, atol=1e-3):
            probabilities = logits
        else:
            shifted = logits - np.max(logits)
            exp = np.exp(shifted)
            probabilities = exp / np.sum(exp)

        return probabilities

    def predict_batch_probabilities(self, tensors: np.ndarray) -> np.ndarray:
        if self.session is None:
            raise RuntimeError(self.load_error or "Model is not loaded.")

        model_tensor = self._fit_layout(tensors)
        outputs = self.session.run(None, {self.input_name: model_tensor})
        logits = np.asarray(outputs[0]).astype(np.float32)
        if logits.ndim == 1:
            logits = np.expand_dims(logits, axis=0)

        if np.all(logits >= 0) and np.allclose(np.sum(logits, axis=1), 1.0, atol=1e-3):
            return logits

        shifted = logits - np.max(logits, axis=1, keepdims=True)
        exp = np.exp(shifted)
        return exp / np.sum(exp, axis=1, keepdims=True)

    def _fit_layout(self, tensor: np.ndarray) -> np.ndarray:
        if self.input_layout == "NHWC" and tensor.ndim == 4 and tensor.shape[1] == 3:
            return np.transpose(tensor, (0, 2, 3, 1)).astype(np.float32)
        return tensor.astype(np.float32)
