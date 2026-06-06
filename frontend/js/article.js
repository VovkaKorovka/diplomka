const API = "https://diplomka-5mob.onrender.com";

const params = new URLSearchParams(window.location.search);
const articleId = Number(params.get("id"));

/* =====================
   SAFE HELPERS
===================== */

function getToken() {
  return localStorage.getItem("token");
}

function safeText(v, fallback = "") {
  if (v === null || v === undefined) return fallback;
  const s = String(v).trim();
  return s.length ? s : fallback;
}

function safeNumber(v, fallback = 0) {
  const n = Number(v);
  return isNaN(n) ? fallback : n;
}

function isValidArray(v) {
  return Array.isArray(v);
}

/* =====================
   AUTH CHECK
===================== */

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

/* =====================
   ARTICLE
===================== */

async function loadArticle() {
  const box = document.getElementById("articleContainer");

  if (!box) return;

  if (!articleId) {
    box.innerHTML = "<h2>Invalid article ID</h2>";
    return;
  }

  try {
    const res = await fetch(`${API}/articles/${articleId}`);

    if (!res.ok) {
      box.innerHTML = "<h2>Article not found</h2>";
      return;
    }

    const article = await res.json();

    if (!article || typeof article !== "object") {
      box.innerHTML = "<h2>Invalid article data</h2>";
      return;
    }

    const title = safeText(article.title, "Untitled");
    const content = safeText(article.content, "No content");
    const views = safeNumber(article.views, 0);
    const id = safeNumber(article.id, articleId);

    box.innerHTML = `
      <img src="https://picsum.photos/1000/400?random=${id || Math.random()}" />
      <h1>${title}</h1>
      <p>👁 Views: ${views}</p>
      <p>${content}</p>
    `;

  } catch (e) {
    console.error(e);
    box.innerHTML = `<h2>Failed to load article</h2>`;
  }
}

/* =====================
   🎵 MUSIC
===================== */

async function loadMusic() {

  const box = document.getElementById("musicContainer");
  if (!box) return;

  try {
    const res = await fetch(`${API}/articles/${articleId}/music`);

    if (!res.ok) {
      box.innerHTML = "";
      return;
    }

    const data = await res.json();

    if (!isValidArray(data) || data.length === 0) {
      box.innerHTML = "";
      return;
    }

    box.innerHTML = `
      <h2>🎵 Playlist</h2>
      ${data.map(t => {
        const title = safeText(t?.title, "Untitled track");
        const url = safeText(t?.youtube_url, "");

        return `
          <div class="track">
            <div>
              <strong>${title}</strong>
              <br>
              ${
                url
                  ? `<a href="${url}" target="_blank">▶ YouTube</a>`
                  : `<span style="color:red;">Broken link</span>`
              }
            </div>

            ${
              url
                ? `<button onclick="playTrack('${url}')">▶ Play</button>`
                : ""
            }
          </div>
        `;
      }).join("")}
    `;

  } catch (e) {
    console.error("music error", e);
  }
}

/* =====================
   ▶ PLAYER (SAFE)
===================== */

function extractYouTubeID(url) {
  if (!url) return "";

  const match = url.match(/(?:youtube\.com.*v=|youtu\.be\/)([^&?/]+)/);
  return match ? match[1] : "";
}

function playTrack(url) {

  const box = document.getElementById("musicContainer");
  if (!box) return;

  const id = extractYouTubeID(url);

  if (!id) {
    alert("Invalid YouTube link");
    return;
  }

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

/* =====================
   COMMENTS
===================== */

async function loadComments() {

  const box = document.getElementById("commentsList");
  if (!box) return;

  try {
    const res = await fetch(`${API}/comments/${articleId}`);

    if (!res.ok) {
      box.innerHTML = "<p>No comments</p>";
      return;
    }

    const data = await res.json();

    if (!Array.isArray(data) || data.length === 0) {
      box.innerHTML = "<p>No comments yet</p>";
      return;
    }

    box.innerHTML = "";

    data.forEach(c => {

      const username = c?.user?.username || "User";
      const avatar = c?.user?.avatar_url || null;
      const text = c?.content || "Empty comment";

      const comment = document.createElement("div");
      comment.className = "comment";

      /* AVATAR */
      const avatarBox = document.createElement("div");
      avatarBox.className = "comment-avatar";

      if (avatar) {
        const img = document.createElement("img");
        img.src = avatar;
        img.alt = username;
        avatarBox.appendChild(img);
      } else {
        avatarBox.textContent = "👤";
      }

      /* BODY */
      const body = document.createElement("div");
      body.className = "comment-body";

      const name = document.createElement("div");
      name.className = "comment-username";
      name.textContent = username;

      const textEl = document.createElement("div");
      textEl.className = "comment-text";
      textEl.textContent = text;

      body.appendChild(name);
      body.appendChild(textEl);

      comment.appendChild(avatarBox);
      comment.appendChild(body);

      box.appendChild(comment);
    });

  } catch (e) {
    console.error(e);
    box.innerHTML = "<p>Error loading comments</p>";
  }
}

/* =====================
   ADD COMMENT
===================== */

async function addComment() {
  if (!requireAuth()) return;

  const token = getToken();
  const input = document.getElementById("commentText");

  if (!input) return;

  const text = input.value;

  if (!text || text.trim().length < 2) {
    alert("Comment too short");
    return;
  }

  try {
    await fetch(`${API}/comments/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({
        content: text.trim(),
        article_id: articleId
      })
    });

    input.value = "";
    loadComments();

  } catch (e) {
    console.error(e);
    alert("Failed to send comment");
  }
}

/* =====================
   LIKE
===================== */

async function likeArticle() {
  if (!requireAuth()) return;

  const token = getToken();

  try {
    await fetch(`${API}/reactions/like?article_id=${articleId}`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });
  } catch (e) {
    console.error(e);
  }
}

/* =====================
   RATE
===================== */

async function rateArticle() {
  if (!requireAuth()) return;

  const token = getToken();
  const ratingEl = document.getElementById("rating");

  if (!ratingEl) return;

  const rating = Number(ratingEl.value);

  if (isNaN(rating) || rating < 1 || rating > 5) {
    alert("Rating must be 1–5");
    return;
  }

  try {
    await fetch(`${API}/reactions/rate?article_id=${articleId}&rating=${rating}`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });
  } catch (e) {
    console.error(e);
  }
}

/* =====================
   RATING STATS
===================== */

async function loadRatingStats() {

  const box = document.getElementById("ratingStats");
  if (!box) return;

  try {
    const res = await fetch(`${API}/reactions/rating-stats?article_id=${articleId}`);

    if (!res.ok) {
      box.innerHTML = "";
      return;
    }

    const data = await res.json();

    const count = safeNumber(data?.count, 0);
    const avg = safeNumber(data?.avg, 0);

    const stars =
      "⭐".repeat(Math.round(avg)) +
      "☆".repeat(5 - Math.round(avg));

    box.innerHTML = `
      <div>${stars}</div>
      <div>${avg.toFixed(1)} / 5 (${count})</div>
    `;

  } catch (e) {
    console.error(e);
    box.innerHTML = "";
  }
}

/* =====================
   INIT
===================== */

loadArticle();
loadMusic();
loadComments();
loadRatingStats();
requireAuth();