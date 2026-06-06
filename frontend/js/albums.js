document.addEventListener("DOMContentLoaded", loadAlbums);

/* =========================
   HELPERS
========================= */

function safeText(v, fallback = "") {
  if (v === null || v === undefined) return fallback;
  const str = String(v).trim();
  return str.length ? str : fallback;
}

function safeNumber(v, fallback = 0) {
  const n = Number(v);
  return isNaN(n) ? fallback : n;
}

function safeSlice(v, len = 120) {
  const text = safeText(v);
  return text.length > len ? text.slice(0, len) + "..." : text;
}

/* 👇 URL CHECK */
function isValidUrl(url) {
  if (!url) return false;
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/* =========================
   MAIN
========================= */

async function loadAlbums() {

  const grid = document.getElementById("albumsGrid");
  if (!grid) return;

  grid.innerHTML = "<p>Loading...</p>";

  try {

    const articles = await getArticles();

    if (!Array.isArray(articles)) {
      grid.innerHTML = `<p class="error">Invalid server response</p>`;
      return;
    }

    if (articles.length === 0) {
      grid.innerHTML = "<p>No albums found</p>";
      return;
    }

    grid.innerHTML = "";

    articles.forEach(article => {

      const id = safeNumber(article?.id, 0);
      const title = safeText(article?.title, "Untitled Album");
      const content = safeSlice(article?.content, 120);

      /* 👇 POSSIBLE LINK (if backend has it) */
      const link = article?.link || article?.url || article?.image || null;

      const hasValidLink = isValidUrl(link);

      const card = document.createElement("div");
      card.className = "card";

      /* IMAGE */
      const img = document.createElement("img");
      img.src = hasValidLink
        ? link
        : `https://picsum.photos/400/300?random=${id || Math.random()}`;

      img.alt = title;

      /* CONTENT */
      const contentDiv = document.createElement("div");
      contentDiv.className = "card-content";

      const h3 = document.createElement("h3");
      h3.textContent = title;

      const p = document.createElement("p");

      /* 👇 IMPORTANT MESSAGE IF BROKEN LINK */
      if (!hasValidLink && link) {
        p.textContent = `${content} — ⚠ Link is broken, album still exists`;
        p.style.color = "#ff6b6b";
      } else {
        p.textContent = content;
      }

      const status = document.createElement("span");
      status.className = "views";

      status.textContent = hasValidLink
        ? `👁 ${safeNumber(article?.views, 0)}`
        : `⚠ Album exists but link is broken`;

      contentDiv.appendChild(h3);
      contentDiv.appendChild(p);
      contentDiv.appendChild(status);

      /* CLICK */
      card.addEventListener("click", () => {

        if (!id) return;

        /* 👇 if link broken → no redirect */
        if (!hasValidLink) {
          alert("This album has no valid link");
          return;
        }

        window.location.href = `article.html?id=${id}`;
      });

      card.appendChild(img);
      card.appendChild(contentDiv);

      /* 👇 visual indicator */
      if (!hasValidLink) {
        card.style.opacity = "0.7";
        card.style.border = "1px solid #ff6b6b";
      }

      grid.appendChild(card);
    });

  } catch (error) {

    console.error(error);

    grid.innerHTML = `
      <p class="error">
        Failed to load albums
      </p>
    `;
  }
}