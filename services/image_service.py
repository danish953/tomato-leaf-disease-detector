from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

from utils.errors import ValidationError


@dataclass(frozen=True)
class ImageInput:
    original_rgb: np.ndarray
    processed_rgb: np.ndarray
    tensor: np.ndarray


class ImageService:
    def __init__(self, config: dict):
        self.image_size = int(config["IMAGE_SIZE"])
        self.normalization_mode = config["NORMALIZATION_MODE"]

    def load_and_preprocess(self, path: Path) -> ImageInput:
        try:
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                image = ImageOps.exif_transpose(image).convert("RGB")
                original_rgb = np.array(image)
        except (UnidentifiedImageError, OSError) as exc:
            raise ValidationError("The uploaded file is corrupted or is not a valid image.") from exc

        enhanced = self._enhance_leaf(original_rgb)
        cropped = self._resize_and_center_crop(enhanced)
        tensor = self.to_model_tensor(cropped)
        return ImageInput(original_rgb=original_rgb, processed_rgb=cropped, tensor=tensor)

    def to_model_tensor(self, rgb_image: np.ndarray) -> np.ndarray:
        array = rgb_image.astype(np.float32) / 255.0

        if self.normalization_mode == "imagenet":
            mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
            std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
            array = (array - mean) / std

        nchw = np.transpose(array, (2, 0, 1))
        return np.expand_dims(nchw, axis=0).astype(np.float32)

    def _enhance_leaf(self, rgb_image: np.ndarray) -> np.ndarray:
        # Mirrors the final notebook preprocessing: LAB histogram equalization,
        # then HSV leaf masking before resize/crop/normalization.
        lab = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)
        l_channel = cv2.equalizeHist(l_channel)
        enhanced = cv2.merge((l_channel, a_channel, b_channel))
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)
        return self._segment_leaf_region(enhanced)

    def _segment_leaf_region(self, rgb_image: np.ndarray) -> np.ndarray:
        hsv = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV)
        lower_green = np.array([25, 40, 40], dtype=np.uint8)
        upper_green = np.array([90, 255, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower_green, upper_green)
        return cv2.bitwise_and(rgb_image, rgb_image, mask=mask)

    def _resize_and_center_crop(self, rgb_image: np.ndarray) -> np.ndarray:
        resize_to = int(self.image_size * 1.14)
        height, width = rgb_image.shape[:2]
        scale = resize_to / min(height, width)
        new_width = max(self.image_size, int(round(width * scale)))
        new_height = max(self.image_size, int(round(height * scale)))
        resized = cv2.resize(rgb_image, (new_width, new_height), interpolation=cv2.INTER_AREA)

        y1 = max(0, (new_height - self.image_size) // 2)
        x1 = max(0, (new_width - self.image_size) // 2)
        return resized[y1 : y1 + self.image_size, x1 : x1 + self.image_size]
