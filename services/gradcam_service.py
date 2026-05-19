from __future__ import annotations

import cv2
import numpy as np

from services.image_service import ImageInput, ImageService


class GradCAMService:
    def __init__(self, config: dict):
        self.gradcam_folder = config["GRADCAM_FOLDER"]
        self.grid_size = int(config["GRADCAM_GRID_SIZE"])
        self.image_service = ImageService(config)

    def generate(self, model_service, image_input: ImageInput, target_index: int, session_id: str) -> str:
        heatmap = self._occlusion_heatmap(model_service, image_input.processed_rgb, target_index)
        heatmap = cv2.resize(heatmap, (image_input.original_rgb.shape[1], image_input.original_rgb.shape[0]))
        heatmap_uint8 = np.uint8(255 * heatmap)
        color_map = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
        color_map = cv2.cvtColor(color_map, cv2.COLOR_BGR2RGB)
        overlay = cv2.addWeighted(image_input.original_rgb, 0.62, color_map, 0.38, 0)

        output_name = f"{session_id}_gradcam.jpg"
        output_path = self.gradcam_folder / output_name
        cv2.imwrite(str(output_path), cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 92])
        return f"gradcam/{output_name}"

    def _occlusion_heatmap(self, model_service, processed_rgb: np.ndarray, target_index: int) -> np.ndarray:
        baseline = model_service.predict_probabilities(self.image_service.to_model_tensor(processed_rgb))[target_index]
        height, width, _ = processed_rgb.shape
        patch_h = max(1, height // self.grid_size)
        patch_w = max(1, width // self.grid_size)

        occluded_tensors = []
        locations = []
        fill_color = np.mean(processed_rgb.reshape(-1, 3), axis=0).astype(np.uint8)

        for row in range(self.grid_size):
            for col in range(self.grid_size):
                y1 = row * patch_h
                x1 = col * patch_w
                y2 = height if row == self.grid_size - 1 else (row + 1) * patch_h
                x2 = width if col == self.grid_size - 1 else (col + 1) * patch_w
                modified = processed_rgb.copy()
                modified[y1:y2, x1:x2] = fill_color
                occluded_tensors.append(self.image_service.to_model_tensor(modified)[0])
                locations.append((y1, y2, x1, x2))

        try:
            batch = np.stack(occluded_tensors, axis=0)
            scores = model_service.predict_batch_probabilities(batch)[:, target_index]
        except Exception:
            scores = np.array(
                [
                    model_service.predict_probabilities(np.expand_dims(tensor, axis=0))[target_index]
                    for tensor in occluded_tensors
                ]
            )

        importance = np.maximum(0.0, baseline - scores)
        coarse = np.zeros((height, width), dtype=np.float32)
        for value, (y1, y2, x1, x2) in zip(importance, locations):
            coarse[y1:y2, x1:x2] = value

        if float(np.max(coarse)) <= 1e-8:
            gray = cv2.cvtColor(processed_rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
            coarse = cv2.GaussianBlur(gray, (0, 0), sigmaX=9)

        coarse = cv2.GaussianBlur(coarse, (0, 0), sigmaX=9)
        coarse -= float(np.min(coarse))
        max_value = float(np.max(coarse))
        if max_value > 0:
            coarse /= max_value
        return coarse
