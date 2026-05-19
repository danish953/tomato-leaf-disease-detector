const resultPage = document.querySelector("#resultPage");
const sessionId = resultPage.dataset.sessionId;

loadResult();

async function loadResult() {
  try {
    const response = await fetch(`/api/result/${sessionId}`);
    const data = await response.json();
    if (!response.ok || !data.success) {
      resultPage.className = "error-card";
      resultPage.innerHTML = `<h1>Result not found</h1><p>${escapeHtml(data.error || "Unable to load this prediction.")}</p>`;
      return;
    }
    renderResult(data);
  } catch (error) {
    resultPage.className = "error-card";
    resultPage.innerHTML = "<h1>Could not load result</h1><p>Please refresh the page.</p>";
  }
}

function renderResult(data) {
  const isAlert = data.severity && data.severity !== "None";
  resultPage.className = "result-card";
  resultPage.innerHTML = `
    <div class="panel-heading">
      <div>
        <p class="eyebrow">Detection result</p>
        <h1>${escapeHtml(data.disease)}</h1>
      </div>
      <strong>${Number(data.confidence).toFixed(2)}%</strong>
    </div>

    <div class="result-layout">
      <div class="image-stack">
        <figure class="image-tile">
          <img src="/static/${escapeHtml(data.image_path)}" alt="Uploaded leaf">
          <span>Original Upload</span>
        </figure>
        <figure class="image-tile">
          <img src="/static/${escapeHtml(data.gradcam_image)}" alt="Grad-CAM heatmap">
          <span>Grad-CAM Heatmap</span>
        </figure>
      </div>

      <div>
        <div class="tag-row">
          <span class="tag ${isAlert ? "alert" : ""}">Severity: ${escapeHtml(data.severity)}</span>
          <span class="tag">Treatment: ${escapeHtml(data.treatment)}</span>
          <span class="tag">Inference: ${Number(data.prediction_time).toFixed(3)}s</span>
        </div>

        <div class="confidence-list">
          ${renderConfidenceRows(data.top_predictions)}
        </div>

        <div class="advice-box">
          <strong>Recommended Solution</strong>
          <p>${escapeHtml(data.solution)}</p>
        </div>

        <div class="result-actions">
          <a class="button primary" href="/">New Detection</a>
          <a class="button secondary" href="/history">View History</a>
        </div>
      </div>
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
