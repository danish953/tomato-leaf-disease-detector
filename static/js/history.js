const historyList = document.querySelector("#historyList");

loadHistory();

async function loadHistory() {
  try {
    const response = await fetch("/api/history");
    const data = await response.json();
    const items = data.items || [];

    if (!items.length) {
      historyList.innerHTML = '<div class="loading-card">No predictions yet. Upload a tomato leaf image to begin.</div>';
      return;
    }

    historyList.innerHTML = items.map(renderHistoryItem).join("");
  } catch (error) {
    historyList.innerHTML = '<div class="error-card">Could not load history right now.</div>';
  }
}

function renderHistoryItem(item) {
  return `
    <a class="history-item" href="/result/${escapeHtml(item.session_id)}">
      <img src="/static/${escapeHtml(item.image_path)}" alt="Leaf prediction thumbnail">
      <div>
        <h3>${escapeHtml(item.disease)}</h3>
        <div class="history-meta">
          ${escapeHtml(item.severity)} severity - ${formatDate(item.created_at)} - ${Number(item.prediction_time).toFixed(3)}s
        </div>
      </div>
      <div class="history-confidence">${Number(item.confidence).toFixed(1)}%</div>
    </a>
  `;
}

function formatDate(value) {
  if (!value) return "Unknown date";
  return new Date(value).toLocaleString();
}

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
