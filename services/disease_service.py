from __future__ import annotations


DISEASE_LIBRARY = {
    "Bacterial_spot": {
        "name": "Bacterial Spot",
        "severity": "High",
        "treatment": "Copper-based bactericide",
        "solution": "Remove infected leaves, avoid overhead watering, and apply a copper-based bactericide following the product label.",
    },
    "Early_blight": {
        "name": "Early Blight",
        "severity": "Medium",
        "treatment": "Fungicide and pruning",
        "solution": "Prune lower infected leaves, improve airflow, mulch soil, and apply a chlorothalonil or copper fungicide if spread continues.",
    },
    "Late_blight": {
        "name": "Late Blight",
        "severity": "High",
        "treatment": "Urgent fungicide",
        "solution": "Remove badly infected plants, keep foliage dry, and apply a late-blight fungicide immediately to protect nearby plants.",
    },
    "Leaf_Mold": {
        "name": "Leaf Mold",
        "severity": "Medium",
        "treatment": "Humidity control and fungicide",
        "solution": "Increase ventilation, reduce humidity, remove affected leaves, and use a labeled fungicide when needed.",
    },
    "Septoria_leaf_spot": {
        "name": "Septoria Leaf Spot",
        "severity": "Medium",
        "treatment": "Fungicide and sanitation",
        "solution": "Remove spotted leaves, clean plant debris, water at soil level, and apply a protective fungicide.",
    },
    "Spider_mites Two-spotted_spider_mite": {
        "name": "Spider Mites",
        "severity": "Medium",
        "treatment": "Miticide or insecticidal soap",
        "solution": "Spray leaf undersides with water, use insecticidal soap or neem oil, and repeat treatment to control new mites.",
    },
    "Target_Spot": {
        "name": "Target Spot",
        "severity": "Medium",
        "treatment": "Fungicide and canopy management",
        "solution": "Remove infected foliage, improve spacing and airflow, and apply a broad-spectrum fungicide if symptoms progress.",
    },
    "Tomato_Yellow_Leaf_Curl_Virus": {
        "name": "Tomato Yellow Leaf Curl Virus",
        "severity": "High",
        "treatment": "Vector control",
        "solution": "Remove infected plants, control whiteflies with sticky traps or insecticidal soap, and use resistant varieties in future planting.",
    },
    "Tomato_mosaic_virus": {
        "name": "Tomato Mosaic Virus",
        "severity": "High",
        "treatment": "Sanitation",
        "solution": "Remove infected plants, disinfect tools and hands, and avoid handling healthy plants after touching infected foliage.",
    },
    "healthy": {
        "name": "Healthy Leaf",
        "severity": "None",
        "treatment": "No treatment required",
        "solution": "The leaf appears healthy. Continue regular watering, balanced nutrition, and routine field monitoring.",
    },
    "powdery_mildew": {
        "name": "Powdery Mildew",
        "severity": "Medium",
        "treatment": "Sulfur or potassium bicarbonate fungicide",
        "solution": "Remove heavily affected leaves, improve airflow, avoid wet foliage, and apply a labeled powdery mildew treatment.",
    },
}


def get_disease_details(label: str) -> dict:
    if label in DISEASE_LIBRARY:
        return DISEASE_LIBRARY[label]

    readable = label.replace("Tomato___", "").replace("_", " ").strip().title()
    return {
        "name": readable or "Unknown Tomato Condition",
        "severity": "Medium",
        "treatment": "Consult local extension guidance",
        "solution": "Isolate the plant, monitor symptom spread, and consult a local agriculture expert for confirmation.",
    }
