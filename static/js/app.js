const imageInput = document.querySelector("#imageInput");
const dropZone = document.querySelector("#dropZone");
const previewImage = document.querySelector("#previewImage");
const emptyPreview = document.querySelector("#emptyPreview");
const validationMessage = document.querySelector("#validationMessage");
const detectButton = document.querySelector("#detectButton");
const detectButtonText = document.querySelector("#detectButtonText");
const clearButton = document.querySelector("#clearButton");
const inlineResult = document.querySelector("#inlineResult");

let selectedFile = null;

const allowedTypes = ["image/jpeg", "image/png", "image/webp"];

function setMessage(message) {
  validationMessage.textContent = message || "";
}

function setLoading(isLoading) {
  detectButton.disabled = isLoading || !selectedFile;
  detectButton.classList.toggle("loading", isLoading);
  detectButtonText.textContent = isLoading ? "Analyzing..." : "Run Detection";
}

function validateFile(file) {
  if (!file) {
    return "Please choose an image first.";
  }
  if (!allowedTypes.includes(file.type)) {
    return "Use a JPG, PNG, or WEBP image.";
  }
  return "";
}

function showPreview(file) {
  const reader = new FileReader();
  reader.onload = () => {
    previewImage.src = reader.result;
    previewImage.classList.add("visible");
    emptyPreview.classList.add("hidden");
  };
  reader.readAsDataURL(file);
}

function selectFile(file) {
  const error = validateFile(file);
  if (error) {
    setMessage(error);
    return;
  }

  selectedFile = file;
  setMessage("");
  showPreview(file);
  detectButton.disabled = false;
  clearButton.disabled = false;
  inlineResult.classList.add("hidden");
}

imageInput.addEventListener("change", (event) => {
  selectFile(event.target.files[0]);
});

["dragenter", "dragover"].forEach((eventName) => {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.add("dragging");
  });
});

["dragleave", "drop"].forEach((eventName) => {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.remove("dragging");
  });
});

dropZone.addEventListener("drop", (event) => {
  selectFile(event.dataTransfer.files[0]);
});

clearButton.addEventListener("click", () => {
  selectedFile = null;
  imageInput.value = "";
  previewImage.src = "";
  previewImage.classList.remove("visible");
  emptyPreview.classList.remove("hidden");
  detectButton.disabled = true;
  clearButton.disabled = true;
  inlineResult.classList.add("hidden");
  setMessage("");
});

detectButton.addEventListener("click", async () => {
  const error = validateFile(selectedFile);
  if (error) {
    setMessage(error);
    return;
  }

  const formData = new FormData();
  formData.append("image", selectedFile);
  setLoading(true);
  setMessage("");

  try {
    const response = await fetch("/api/detect", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();

    if (!response.ok || !data.success) {
      setMessage(data.error || "Detection failed. Please try again.");
      return;
    }

    renderInlineResult(data);
    window.setTimeout(() => {
      window.location.href = `/result/${data.session_id}`;
    }, 900);
  } catch (error) {
    setMessage("Network error. Please check the server and try again.");
  } finally {
    setLoading(false);
  }
});

function renderInlineResult(data) {
  inlineResult.classList.remove("hidden");
  inlineResult.innerHTML = `
    <p class="eyebrow">Prediction ready</p>
    <h3>${escapeHtml(data.disease)}</h3>
    <p>${Number(data.confidence).toFixed(2)}% confidence - ${escapeHtml(data.severity)} severity</p>
    <div class="confidence-list">
      ${renderConfidenceRows(data.top_predictions)}
    </div>
  `;
}

function renderConfidenceRows(items) {
  return (items || []).map((item) => `
    <div class="confidence-row">
      <strong>${escapeHtml(cleanLabel(item.label))}</strong>
      <div class="bar"><span style="width:${Number(item.confidence).toFixed(2)}%"></span></div>
      <span>${Number(item.confidence).toFixed(2)}%</span>
    </div>
  `).join("");
}

function cleanLabel(label) {
  return String(label || "").replace("Tomato___", "").replaceAll("_", " ");
}

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
