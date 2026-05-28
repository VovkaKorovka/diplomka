const API = "https://diplomka-production-a099.up.railway.app";

function token() {
  return localStorage.getItem("token");
}

// ======================
// 🔒 CHECK AUTH
// ======================
if (!token()) {
  window.location.href = "login.html";
}

/* ======================
   👤 LOAD PROFILE
====================== */
async function loadProfile() {
  try {
    const res = await fetch(`${API}/users/me`, {
      headers: {
        Authorization: "Bearer " + token()
      }
    });

    if (!res.ok) {
      console.log("PROFILE ERROR:", await res.text());
      return;
    }

    const user = await res.json();

    const box = document.getElementById("profileBox");

    box.innerHTML = `
      <div class="profile-card">

        <div class="avatar-box">
          <img 
            id="avatarPreview"
            src="${user.avatar_url || 'https://i.imgur.com/1X5Z1ZQ.png'}"
            class="avatar"
          />

          <input 
            type="file" 
            accept="image/*"
            id="avatarInput"
          />
        </div>

        <h2>${user.username ?? "Unknown user"}</h2>
        <p>📧 ${user.email ?? "No email"}</p>
        <p>🔑 Role: ${user.role ?? "user"}</p>

      </div>
    `;

    setupAvatarUpload();

  } catch (err) {
    console.error("PROFILE ERROR:", err);
  }
}

/* ======================
   🖼️ UPDATE AVATAR
====================== */
async function updateAvatar(base64) {
  await fetch(`${API}/users/avatar`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: "Bearer " + token()
    },
    body: JSON.stringify({
      avatar_url: base64
    })
  });
}

/* ======================
   📤 AVATAR UPLOAD
====================== */
function setupAvatarUpload() {
  const input = document.getElementById("avatarInput");
  const preview = document.getElementById("avatarPreview");

  if (!input || !preview) return;

  input.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();

    reader.onload = async () => {
      const base64 = reader.result;

      preview.src = base64;

      await updateAvatar(base64);
    };

    reader.readAsDataURL(file);
  });
}

/* ======================
   ❤️ LOAD LIKED ARTICLES (FIXED)
====================== */
async function loadLikedArticles() {
  try {
    const res = await fetch(`${API}/reactions/my-likes`, {
      headers: {
        Authorization: "Bearer " + token()
      }
    });

    if (!res.ok) {
      console.log("LIKES ERROR:", await res.text());
      return;
    }

    const articles = await res.json();

    const grid = document.getElementById("likedGrid");
    grid.innerHTML = "";

    if (!Array.isArray(articles) || articles.length === 0) {
      grid.innerHTML = `
        <div class="empty-state">
          ❤️ 0 likes yet. Explore and like some articles!
        </div>
      `;
      return;
    }

    articles.forEach(article => {
      const title = article.title?.trim() || "Untitled album";
      const content = article.content?.trim() || "No description";

      const card = document.createElement("div");
      card.className = "card";

      card.innerHTML = `
        <img src="https://picsum.photos/400/300?random=${article.id}" />

        <div class="card-content">
          <h3>${title}</h3>
          <p>${content.length > 120 ? content.slice(0, 120) + "..." : content}</p>
        </div>
      `;

      card.onclick = () => {
        window.location.href = `article.html?id=${article.id}`;
      };

      grid.appendChild(card);
    });

  } catch (err) {
    console.error("LIKES ERROR:", err);
  }
}

/* ======================
   🚀 INIT
====================== */
loadProfile();
loadLikedArticles();