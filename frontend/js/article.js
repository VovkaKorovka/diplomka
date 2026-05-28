const API = "https://diplomka-production-a099.up.railway.app";

const params = new URLSearchParams(window.location.search);
const articleId = params.get("id");

function getToken() {
  return localStorage.getItem("token");
}

// =====================
// AUTH CHECK
// =====================
function requireAuth() {
  const token = getToken();

  if (!token) {
    const actions = document.querySelector(".actions");
    const comments = document.querySelector(".comments");

    if (actions) actions.style.display = "none";

    if (comments) {
      comments.innerHTML = `
        <div style="text-align:center;padding:40px;">
          <h2>🔒 Login required</h2>
          <a href="login.html">Login</a>
        </div>
      `;
    }

    return false;
  }

  return true;
}

// =====================
// ARTICLE
// =====================
async function loadArticle() {
  try {
    const res = await fetch(`${API}/articles/${articleId}`);
    const article = await res.json();

    document.getElementById("articleContainer").innerHTML = `
      <img src="https://picsum.photos/1000/400?random=${article.id}" />
      <h1>${article.title}</h1>
      <p>👁 Views: ${article.views}</p>
      <p>${article.content}</p>
    `;
  } catch (e) {
    document.getElementById("articleContainer").innerHTML = `<h2>Not found</h2>`;
  }
}

// =====================
// 🎵 MUSIC
// =====================
async function loadMusic() {
  try {
    const res = await fetch(`${API}/articles/${articleId}/music`);
    const data = await res.json();

    const box = document.getElementById("musicContainer");

    if (!data.length) {
      box.innerHTML = "";
      return;
    }

    box.innerHTML = `
      <h2>🎵 Playlist</h2>
      ${data.map(t => `
        <div class="track">
          <div>
            <strong>${t.title}</strong>
            <br>
            <a href="${t.youtube_url}" target="_blank">▶ YouTube</a>
          </div>

          <button onclick="playTrack('${t.youtube_url}')">
            ▶ Play
          </button>
        </div>
      `).join("")}
    `;
  } catch (e) {
    console.error("music error", e);
  }
}

// =====================
// ▶ PLAYER
// =====================
function playTrack(url) {
  const box = document.getElementById("musicContainer");
  const id = extractYouTubeID(url);

  box.innerHTML = `
    <button onclick="loadMusic()">⬅ Back</button>

    <div style="margin-top:15px;">
      <iframe width="100%" height="400"
        src="https://www.youtube.com/embed/${id}"
        frameborder="0"
        allowfullscreen>
      </iframe>
    </div>
  `;
}

// =====================
// YOUTUBE ID
// =====================
function extractYouTubeID(url) {
  const match = url.match(/(?:youtube\.com.*v=|youtu\.be\/)([^&?/]+)/);
  return match ? match[1] : "";
}

// =====================
// COMMENTS
// =====================
async function loadComments() {
  const res = await fetch(`${API}/comments/${articleId}`);
  const data = await res.json();

  const box = document.getElementById("commentsList");
  box.innerHTML = data.map(c => `<div class="comment">${c.content}</div>`).join("");
}

async function addComment() {
  if (!requireAuth()) return;

  const token = getToken();
  const text = document.getElementById("commentText").value;

  await fetch(`${API}/comments/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({
      content: text,
      article_id: Number(articleId)
    })
  });

  document.getElementById("commentText").value = "";
  loadComments();
}

// =====================
// LIKE
// =====================
async function likeArticle() {
  if (!requireAuth()) return;

  const token = getToken();

  await fetch(`${API}/reactions/like?article_id=${articleId}`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`
    }
  });
}

// =====================
// RATE
// =====================
async function rateArticle() {
  if (!requireAuth()) return;

  const token = getToken();
  const rating = document.getElementById("rating").value;

  await fetch(`${API}/reactions/rate?article_id=${articleId}&rating=${rating}`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`
    }
  });
}

// =====================
// RATING STATS
// =====================
async function loadRatingStats() {
  const res = await fetch(`${API}/reactions/rating-stats?article_id=${articleId}`);
  const data = await res.json();

  const count = data.count || 0;
  const avg = data.avg || 0;

  const stars = "⭐".repeat(Math.round(avg)) + "☆".repeat(5 - Math.round(avg));

  document.getElementById("ratingStats").innerHTML = `
    <div>${stars}</div>
    <div>${avg.toFixed(1)} / 5 (${count})</div>
  `;
}

// =====================
// INIT
// =====================
loadArticle();
loadMusic();
loadComments();
loadRatingStats();
requireAuth();