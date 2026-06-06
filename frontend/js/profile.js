const API = "https://diplomka-5mob.onrender.com";

function token() {
  return localStorage.getItem("token");
}

/* ======================
   🔒 SAFE REDIRECT
====================== */

if (!token()) {
  window.location.href = "login.html";
}

/* ======================
   SAFE HELPERS
====================== */

function safeText(v, fallback = "") {
  if (v === null || v === undefined) return fallback;
  const s = String(v).trim();
  return s.length ? s : fallback;
}

function safeArray(v) {
  return Array.isArray(v) ? v : [];
}

function isValidUrl(v) {
  if (!v) return false;
  try {
    new URL(v);
    return true;
  } catch {
    return false;
  }
}

/* ======================
   👤 LOAD PROFILE
====================== */

async function loadProfile() {

  const box = document.getElementById("profileBox");
  if (!box) return;

  try {
    const res = await fetch(`${API}/users/me`, {
      headers: {
        Authorization: "Bearer " + token()
      }
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => "");
      console.log("PROFILE ERROR:", errText);
      box.innerHTML = "<h3>Failed to load profile</h3>";
      return;
    }

    const user = await res.json();

    if (!user || typeof user !== "object") {
      box.innerHTML = "<h3>Invalid user data</h3>";
      return;
    }

    const username = safeText(user.username, "Unknown user");
    const email = safeText(user.email, "No email");
    const role = safeText(user.role, "user");

    const avatar =
      isValidUrl(user.avatar_url)
        ? user.avatar_url
        : "https://i.imgur.com/1X5Z1ZQ.png";

    box.innerHTML = `
      <div class="profile-card">

        <div class="avatar-box">
          <img 
            id="avatarPreview"
            src="${avatar}"
            class="avatar"
          />

          <input 
            type="file" 
            accept="image/*"
            id="avatarInput"
          />
        </div>

        <h2>${username}</h2>
        <p>📧 ${email}</p>
        <p>🔑 Role: ${role}</p>

      </div>
    `;

    setupAvatarUpload();

  } catch (err) {
    console.error("PROFILE ERROR:", err);
    box.innerHTML = "<h3>Server error</h3>";
  }
}

/* ======================
   🖼️ UPDATE AVATAR
====================== */

async function updateAvatar(base64) {
  if (!base64) return;

  try {
    const res = await fetch(`${API}/users/avatar`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token()
      },
      body: JSON.stringify({
        avatar_url: base64
      })
    });

    if (!res.ok) {
      console.log("Avatar update failed");
    }

  } catch (e) {
    console.error("AVATAR ERROR:", e);
  }
}

/* ======================
   📤 AVATAR UPLOAD
====================== */

function setupAvatarUpload() {

  const input = document.getElementById("avatarInput");
  const preview = document.getElementById("avatarPreview");

  if (!input || !preview) return;

  input.addEventListener("change", (e) => {

    const file = e.target.files?.[0];
    if (!file) return;

    /* size check (5MB max) */
    if (file.size > 5 * 1024 * 1024) {
      alert("Image too large (max 5MB)");
      return;
    }

    const reader = new FileReader();

    reader.onload = async () => {

      const base64 = reader.result;

      if (!base64 || typeof base64 !== "string") {
        alert("Invalid image");
        return;
      }

      preview.src = base64;

      await updateAvatar(base64);
    };

    reader.onerror = () => {
      alert("Failed to read image");
    };

    reader.readAsDataURL(file);
  });
}

/* ======================
   ❤️ LIKED ARTICLES
====================== */

async function loadLikedArticles() {

  const grid = document.getElementById("likedGrid");
  if (!grid) return;

  try {
    const res = await fetch(`${API}/reactions/my-likes`, {
      headers: {
        Authorization: "Bearer " + token()
      }
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => "");
      console.log("LIKES ERROR:", errText);
      grid.innerHTML = "<div>Failed to load likes</div>";
      return;
    }

    const articles = await res.json();
    const list = safeArray(articles);

    grid.innerHTML = "";

    if (list.length === 0) {
      grid.innerHTML = `
        <div class="empty-state">
          ❤️ No liked articles yet
        </div>
      `;
      return;
    }

    list.forEach(article => {

      const id = article?.id;
      const title = safeText(article?.title, "Untitled album");
      const content = safeText(article?.content, "No description");

      const card = document.createElement("div");
      card.className = "card";

      const img = document.createElement("img");
      img.src = `https://picsum.photos/400/300?random=${id || Math.random()}`;

      const contentDiv = document.createElement("div");
      contentDiv.className = "card-content";

      const h3 = document.createElement("h3");
      h3.textContent = title;

      const p = document.createElement("p");
      p.textContent =
        content.length > 120 ? content.slice(0, 120) + "..." : content;

      contentDiv.appendChild(h3);
      contentDiv.appendChild(p);

      card.appendChild(img);
      card.appendChild(contentDiv);

      card.addEventListener("click", () => {
        if (!id) return;
        window.location.href = `article.html?id=${id}`;
      });

      grid.appendChild(card);
    });

  } catch (err) {
    console.error("LIKES ERROR:", err);
    grid.innerHTML = "<div>Error loading likes</div>";
  }
}

/* ======================
   🚀 INIT
====================== */

loadProfile();
loadLikedArticles();