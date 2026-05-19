from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
import timm


DEFAULT_CLASSES = [
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


def strip_parallel_prefixes(state_dict: dict) -> dict:
    state = state_dict
    if any(key.startswith("_orig_mod.") for key in state):
        state = {key.replace("_orig_mod.", "", 1): value for key, value in state.items()}
    if any(key.startswith("module.") for key in state):
        state = {key.replace("module.", "", 1): value for key, value in state.items()}
    return state


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export the notebook's PyTorch checkpoint best.pt to ai_model/model.onnx."
    )
    parser.add_argument(
        "--checkpoint",
        default="outputs_mobilenetv4_android_final/best.pt",
        help="Path to best.pt downloaded from Kaggle.",
    )
    parser.add_argument(
        "--output",
        default="ai_model/model.onnx",
        help="Where to write the exported ONNX model.",
    )
    parser.add_argument("--opset", type=int, default=18)
    args = parser.parse_args()

    checkpoint_path = Path(args.checkpoint)
    output_path = Path(args.output)

    if not checkpoint_path.exists():
        raise FileNotFoundError(
            f"Checkpoint not found: {checkpoint_path}\n"
            "Download best.pt from Kaggle output first, then run this script again."
        )

    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    config = checkpoint.get("config", {})
    model_name = config.get("model_name", "mobilenetv4_conv_medium")
    image_size = int(config.get("img_size", 224))
    class_names = checkpoint.get("class_names", DEFAULT_CLASSES)

    model = timm.create_model(
        model_name,
        pretrained=False,
        num_classes=len(class_names),
    ).cpu().eval()
    model.load_state_dict(strip_parallel_prefixes(checkpoint["model_state"]), strict=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    dummy = torch.randn(1, 3, image_size, image_size, dtype=torch.float32)

    torch.onnx.export(
        model,
        dummy,
        output_path.as_posix(),
        input_names=["input"],
        output_names=["logits"],
        opset_version=args.opset,
        do_constant_folding=True,
    )

    metadata = {
        "model_name": model_name,
        "input_size": [1, 3, image_size, image_size],
        "class_names": class_names,
        "mean": [0.485, 0.456, 0.406],
        "std": [0.229, 0.224, 0.225],
        "input_tensor_name": "input",
        "output_tensor_name": "logits",
        "onnx": output_path.name,
    }
    metadata_path = output_path.parent / "metadata.json"
    labels_path = output_path.parent / "labels.txt"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    labels_path.write_text("\n".join(class_names) + "\n", encoding="utf-8")

    print("Export complete")
    print(f"ONNX: {output_path.resolve()}")
    print(f"Metadata: {metadata_path.resolve()}")
    print(f"Labels: {labels_path.resolve()}")


if __name__ == "__main__":
    main()
