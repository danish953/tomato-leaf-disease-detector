# Tomato Leaf Disease Detector

Production-ready beginner-friendly Flask web app for tomato leaf disease detection using a trained MobileNetV4 ONNX model.

## What This Project Includes

- Flask backend with modular routes, services, utilities, and SQLAlchemy models
- ONNX Runtime inference with the model loaded once at startup
- OpenCV/Pillow preprocessing: CLAHE, bilateral filtering, HSV leaf segmentation, resize, normalization
- Confidence score and top-3 predictions
- Grad-CAM-style heatmap generation saved under `static/gradcam`
- SQLite prediction history
- Responsive HTML/CSS/vanilla JavaScript frontend
- Render/Railway compatible deployment files

## Folder Structure

```text
plant-disease-detector/
|-- app.py                  # Flask application factory and startup
|-- config.py               # Environment-based configuration
|-- requirements.txt        # Python dependencies
|-- Procfile                # Gunicorn web command for Render/Railway
|-- runtime.txt             # Python runtime for supported hosts
|-- .env                    # Local development environment variables
|-- .env.example            # Safe production environment template
|-- ai_model/
|   `-- model.onnx          # Put your trained MobileNetV4 ONNX model here
|-- database/
|   |-- extensions.py       # SQLAlchemy extension instance
|   `-- init_db.py          # Optional manual database initialization
|-- models/
|   `-- prediction.py       # Prediction history table schema
|-- routes/
|   |-- api.py              # JSON APIs
|   `-- pages.py            # HTML page routes
|-- services/
|   |-- disease_service.py  # Disease metadata and treatment suggestions
|   |-- gradcam_service.py  # Heatmap generation
|   |-- image_service.py    # Image validation and preprocessing pipeline
|   |-- model_service.py    # ONNX Runtime model loading and inference
|   `-- storage_service.py  # Secure upload saving
|-- utils/
|   |-- error_handlers.py   # Sanitized API/page errors
|   |-- errors.py           # Custom exceptions
|   |-- logging_config.py   # Rotating file logging
|   |-- security.py         # Security headers and optional API key
|   `-- validators.py       # Upload validation
|-- static/
|   |-- css/styles.css      # Responsive agriculture-themed UI
|   |-- js/app.js           # Upload and detection behavior
|   |-- js/result.js        # Result page rendering
|   |-- js/history.js       # History page rendering
|   |-- uploads/            # Saved user uploads
|   `-- gradcam/            # Saved heatmap overlays
`-- templates/
    |-- base.html
    |-- index.html
    |-- result.html
    |-- history.html
    `-- error.html
```

## Local Setup

1. Create and activate a virtual environment.

```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Copy your trained ONNX model to:

```text
ai_model/model.onnx
```

Your notebook exported the model on Kaggle to:

```text
/kaggle/working/outputs_mobilenetv4_android_final/android_export/mobilenetv4_conv_medium.onnx
```

Download that file from the Kaggle notebook output, place it in `ai_model`, and rename it to `model.onnx`.

If ONNX export creates a second file named `model.onnx.data`, keep it beside `model.onnx`. ONNX Runtime needs both files.

If you download the PyTorch checkpoint instead, put `best.pt` at:

```text
outputs_mobilenetv4_android_final/best.pt
```

Then install export-only packages and run:

```bash
pip install torch timm onnx
python scripts/export_checkpoint_to_onnx.py
```

4. Confirm `.env` settings. Most projects can keep:

```text
MODEL_PATH=ai_model/model.onnx
IMAGE_SIZE=224
NORMALIZATION_MODE=imagenet
```

If your model was trained with `0..1` normalization instead of ImageNet normalization, set:

```text
NORMALIZATION_MODE=zero_one
```

5. Run the app.

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## API Endpoints

### `POST /api/detect`

Multipart form upload:

```text
image=<leaf image>
```

Response:

```json
{
  "success": true,
  "disease": "Late Blight",
  "confidence": 97.52,
  "severity": "High",
  "top_predictions": [],
  "gradcam_image": "gradcam/session_gradcam.jpg",
  "treatment": "Urgent fungicide",
  "solution": "Remove badly infected plants..."
}
```

### `GET /api/result/<session_id>`

Fetch one saved prediction.

### `GET /api/history`

Fetch the latest 50 predictions.

### `GET /api/health`

Check model and database readiness.

## Database

SQLite is configured through SQLAlchemy and created automatically on startup at:

```text
database/plant_disease.db
```

Stored fields include:

- `id`
- `session_id`
- `image_path`
- `disease_name`
- `confidence_score`
- `severity`
- `treatment`
- `solution`
- `top_predictions`
- `gradcam_path`
- `prediction_time`
- `created_at`

## Deployment on Render

1. Push this project to GitHub.
2. Create a new Render Web Service.
3. Use these settings:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120`
4. Add environment variables from `.env.example`.
5. Upload/include `ai_model/model.onnx` in your repository or use a private deployment artifact.
6. Deploy.

## Deployment on Railway

1. Create a Railway project from your GitHub repo.
2. Railway will detect the `Procfile`.
3. Add environment variables from `.env.example`.
4. Ensure `ai_model/model.onnx` is available in the deployed project.
5. Deploy and open the generated Railway URL.

## Production Notes

- Set `FLASK_ENV=production` and `FLASK_DEBUG=0`.
- Replace `SECRET_KEY` with a long random value.
- Keep `.env` out of git. Use host environment variables in production.
- For basic API protection, set `REQUIRE_API_KEY=1` and provide `API_KEY`; clients must send `X-API-Key`.
- Use `opencv-python-headless` for smaller server deployments.
- The app uses one Gunicorn worker by default so the ONNX model is loaded once per process and RAM stays low.

## Grad-CAM Note

Plain ONNX Runtime does not expose training gradients from most exported classification models. This app generates a class-specific heatmap using a fast occlusion-based Grad-CAM-style method that works with standard ONNX classifiers. If you export a model with feature-map outputs or keep a PyTorch/TensorFlow training graph, you can swap `services/gradcam_service.py` for true gradient Grad-CAM.
