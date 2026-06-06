const API = "https://diplomka-5mob.onrender.com";

/* =========================
   AUTH
========================= */

function token() {
  return localStorage.getItem("token");
}

function role() {
  return localStorage.getItem("role");
}

function logout() {
  localStorage.clear();
  location.href = "index.html";
}

/* =========================
   SAFE API
========================= */

async function api(url, options = {}) {
  try {
    const res = await fetch(API + url, {
      ...options,
      headers: {
        Authorization: "Bearer " + token(),
        "Content-Type": "application/json",
        ...(options.headers || {})
      }
    });

    if (res.status === 401) {
      alert("Session expired");
      logout();
      return null;
    }

    if (res.status === 403) {
      alert("No permission");
      return null;
    }

    return res;
  } catch (err) {
    console.error("API ERROR:", err);
    return null;
  }
}

/* =========================
   SECURITY
========================= */

if (role() !== "admin") {
  alert("Access denied");
  location.href = "index.html";
}

/* =========================
   CACHE
========================= */

let cache = {
  users: null,
  countries: null,
  cultures: null,
  albums: null
};

/* =========================
   STATE
========================= */

let state = { tab: "dashboard" };
let selectedAlbumId = null;

/* =========================
   UI HELPERS
========================= */

function render(html) {
  document.getElementById("adminGrid").innerHTML = html;
}

function loader() {
  render(`<div class="card">Loading...</div>`);
}

function selectHTML(id, items, labelKey = "name") {
  return `
    <select id="${id}">
      <option value="">Select...</option>
      ${items.map(i => `
        <option value="${i.id}">${i[labelKey]}</option>
      `).join("")}
    </select>
  `;
}

/* =========================
   CACHE FETCH
========================= */

async function fetchCached(key, url) {
  if (cache[key]) return cache[key];

  const res = await api(url);
  if (!res) return [];

  const data = await res.json();
  cache[key] = data;

  return data;
}

/* =========================
   TAB SWITCH
========================= */

function switchTab(tab) {
  state.tab = tab;

  const actions = {
    dashboard: loadDashboard,
    articles: loadArticles,
    users: loadUsers,
    comments: loadComments,
    contact: loadContact,
    countries: loadCountries,
    cultures: loadCultures,
    genres: loadGenres,
    instruments: loadInstruments,
    music: loadMusicPanel
  };

  (actions[tab] || loadDashboard)();
}

/* =========================
   DASHBOARD
========================= */

async function loadDashboard() {
  loader();

  const [aRes, uRes] = await Promise.all([
    api("/articles/"),
    api("/users/")
  ]);

  if (!aRes || !uRes) return;

  const articles = await aRes.json();
  const users = await uRes.json();

  render(`
    <div class="card">
      <h2>📊 Dashboard</h2>
      <p>Articles: ${articles.length}</p>
      <p>Users: ${users.length}</p>
    </div>
  `);
}

/* =========================
   ARTICLES
========================= */

async function loadArticles() {
  loader();

  const [aRes, users, cultures] = await Promise.all([
    api("/articles/"),
    fetchCached("users", "/users/"),
    fetchCached("cultures", "/cultures/")
  ]);

  const articles = aRes ? await aRes.json() : [];

  render(`
    <div class="card">
      <h2>Create Article</h2>

      <input id="title" placeholder="Title">
      <textarea id="content" placeholder="Content"></textarea>

      <label>Author</label>
      ${selectHTML("author_id", users, "email")}

      <label>Culture</label>
      ${selectHTML("culture_id", cultures)}

      <button onclick="createArticle()">Create</button>
    </div>

    ${articles.map(a => `
      <div class="card">
        <h3>${a.title}</h3>
        <p>Status: ${a.status || "draft"}</p>
        <button onclick="publish(${a.id})">Publish</button>
        <button onclick="deleteArticle(${a.id})">Delete</button>
      </div>
    `).join("")}
  `);
}

async function createArticle() {
  if (!confirm("Створити статтю?")) return;

  const title = document.getElementById("title").value;
  const content = document.getElementById("content").value;

  const authorVal = document.getElementById("author_id").value;
  const cultureVal = document.getElementById("culture_id").value;

  if (isEmpty(title)) return showError("Title is required");
  if (!minLen(title, 3)) return showError("Title min 3 symbols");

  if (isEmpty(content)) return showError("Content is required");
  if (!minLen(content, 10)) return showError("Content min 10 symbols");

  const author_id = authorVal ? Number(authorVal) : null;
  const culture_id = cultureVal ? Number(cultureVal) : null;

  if (!author_id) return showError("Select author");
  if (!culture_id) return showError("Select culture");

  const res = await api("/admin/articles", {
    method: "POST",
    body: JSON.stringify({
      title: title.trim(),
      content: content.trim(),
      author_id,
      culture_id,
      is_album: true
    })
  });

  const data = await res?.json().catch(() => ({}));

  if (!res || !res.ok) {
    return showError(data.detail || "Create failed");
  }

  loadArticles();
}

async function publish(id) {
  if (!confirm("Опублікувати?")) return;

  await api(`/articles/${id}/publish`, { method: "PATCH" });
  loadArticles();
}

async function deleteArticle(id) {
  if (!confirm("Видалити?")) return;

  await api(`/admin/articles/${id}`, { method: "DELETE" });
  loadArticles();
}

/* =========================
   USERS
========================= */

async function loadUsers() {
  loader();

  const res = await api("/users/");
  if (!res) return;

  const data = await res.json();

  render(data.map(u => `
    <div class="card">
      <h3>${u.email}</h3>
      <p>${u.role}</p>

      <p>Status: ${u.is_active ? "ACTIVE" : "BANNED"}</p>

      ${
        u.is_active
          ? `<button onclick="banUser(${u.id})">Ban</button>`
          : `<button onclick="unbanUser(${u.id})">Unban</button>`
      }
    </div>
  `).join(""));
}

async function unbanUser(id) {
  if (!confirm("Unban user?")) return;

  await api(`/users/${id}/unban`, {
    method: "PATCH"
  });

  loadUsers();
}

async function banUser(id) {
  if (!confirm("Ban user?")) return;

  await api(`/users/${id}/ban`, { method: "PATCH" });
  loadUsers();
}

/* =========================
   COMMENTS
========================= */

async function loadComments() {
  loader();

  const res = await api("/comments/1");
  if (!res) return;

  const data = await res.json();

  render(data.map(c => `
    <div class="card">
      <p>${c.content || c.text || ""}</p>

      <button onclick="deleteComment(${c.id})">
        Delete
      </button>
    </div>
  `).join(""));
}

async function deleteComment(id) {
  if (!confirm("Delete comment?")) return;

  await api(`/comments/${id}`, {
    method: "DELETE"
  });

  loadComments();
}

/* =========================
   CONTACT
========================= */

async function loadContact() {
  loader();

  const res = await api("/contact/");
  if (!res) return;

  const data = await res.json();

  render(data.map(m => `
    <div class="card">
      <h3>${m.email}</h3>
      <p>${m.message}</p>

      <button onclick="deleteContact(${m.id})">
        Delete
      </button>
    </div>
  `).join(""));
}

async function deleteContact(id) {
  if (!id) return;

  if (!confirm("Delete message?")) return;

  await api(`/contact/${id}`, {
    method: "DELETE"
  });

  loadContact();
}

function safeString(v, min = 0, field = "Field") {
  if (isEmpty(v)) return showError(field + " is required");
  if (!minLen(v, min)) return showError(field + ` min ${min} symbols`);
  return true;
}

/* =========================
   COUNTRIES
========================= */

async function loadCountries() {
  loader();

  const res = await api("/countries/");
  if (!res) return;

  const data = await res.json();

  render(`
    <div class="card">
      <h2>Add Country</h2>
      <input id="countryName" placeholder="Country name">
      <button onclick="createCountry()">Create</button>
    </div>

    ${data.map(c => `
      <div class="card">
        <h3>🌍 ${c.name}</h3>

        <button onclick="deleteCountry(${c.id})">
          Delete
        </button>
      </div>
    `).join("")}
  `);
}

async function deleteCountry(id) {
  if (!confirm("Delete country?")) return;

  const res = await api(`/countries/${id}`, {
    method: "DELETE"
  });

  if (!res || !res.ok) {
    const data = await res?.json().catch(() => ({}));
    alert(data.detail || "Delete failed");
    return;
  }

  loadCountries();
}

async function createCountry() {
  if (!confirm("Create country?")) return;

  const name = document.getElementById("countryName").value;

  const res = await api("/countries/", {
    method: "POST",
    body: JSON.stringify({ name })
  });

  const data = await res?.json().catch(() => ({}));

  if (!res || !res.ok) {
    console.log("ERROR:", data);
    alert(data.detail || "Create failed");
    return;
  }

  cache.countries = null;
  loadCountries();
}

/* =========================
   CULTURES
========================= */

async function loadCultures() {
  loader();

  const [cultures, countries] = await Promise.all([
    api("/cultures/").then(r => r.json()),
    fetchCached("countries", "/countries/")
  ]);

  render(`
    <div class="card">
      <h2>Add Culture</h2>

      <input id="cultureName" placeholder="Culture name">

      <label>Country</label>
      ${selectHTML("country_id", countries)}

      <button onclick="createCulture()">Create</button>
    </div>

    ${cultures.map(c => `
      <div class="card">
        <h3>🎶 ${c.name}</h3>

        <button onclick="deleteCulture(${c.id})">
          Delete
        </button>
      </div>
    `).join("")}
  `);
}

async function deleteCulture(id) {
  if (!confirm("Delete culture?")) return;

  const res = await api(`/cultures/${id}`, {
    method: "DELETE"
  });

  if (!res || !res.ok) {
    const data = await res?.json().catch(() => ({}));
    alert(data.detail || "Delete failed");
    return;
  }

  loadCultures();
}

async function createCulture() {
  if (!confirm("Create culture?")) return;

  const name = document.getElementById("cultureName").value;
  const country_id = Number(document.getElementById("country_id").value);

  if (isEmpty(name)) return showError("Culture name required");
  if (!minLen(name, 2)) return showError("Min 2 symbols");

  if (!country_id) return showError("Select country");

  await api("/cultures/", {
    method: "POST",
    body: JSON.stringify({
      name: name.trim(),
      country_id
    })
  });

  cache.cultures = null;
  loadCultures();
}

/* =========================
   GENRES
========================= */

async function loadGenres() {
  loader();

  const res = await api("/genres/");
  if (!res) return;

  const data = await res.json();

  render(`
    <div class="card">
      <h2>Add Genre</h2>
      <input id="genreName" placeholder="Genre name">
      <button onclick="createGenre()">Create</button>
    </div>

    ${data.map(g => `
      <div class="card">
        <h3>🎧 ${g.name}</h3>
      </div>
    `).join("")}
  `);
}

async function createGenre() {
  if (!confirm("Create genre?")) return;

  const name = document.getElementById("genreName").value;

  if (isEmpty(name)) return showError("Genre name required");
  if (!minLen(name, 2)) return showError("Min 2 symbols");

  await api("/genres/", {
    method: "POST",
    body: JSON.stringify({ name: name.trim() })
  });

  loadGenres();
}

/* =========================
   INSTRUMENTS
========================= */

async function loadInstruments() {
  loader();

  const res = await api("/instruments/");
  if (!res) return;

  const data = await res.json();

  render(`
    <div class="card">
      <h2>Add Instrument</h2>
      <input id="instrumentName" placeholder="Instrument name">
      <button onclick="createInstrument()">Create</button>
    </div>

    ${data.map(i => `
      <div class="card">
        <h3>🎹 ${i.name}</h3>
      </div>
    `).join("")}
  `);
}

async function createInstrument() {
  if (!confirm("Create instrument?")) return;

  const name = document.getElementById("instrumentName").value;

  if (isEmpty(name)) return showError("Instrument name required");
  if (!minLen(name, 2)) return showError("Min 2 symbols");

  await api("/instruments/", {
    method: "POST",
    body: JSON.stringify({ name: name.trim() })
  });

  loadInstruments();
}

/* =========================
   🎵 MUSIC PANEL
========================= */

async function loadMusicPanel() {
  loader();

  const articles = await api("/articles/").then(r => r.json());

  const albums = articles.filter(a =>
    a.is_album === true ||
    a.is_album === 1 ||
    a.is_album === "true"
  );

  if (!albums.length) {
    render(`<div class="card">No albums found</div>`);
    return;
  }

  if (!selectedAlbumId) {
    selectedAlbumId = albums[0].id;
  }

  const music = await api(`/music/${selectedAlbumId}`)
    .then(r => r.json())
    .catch(() => []);

  render(`
    <div class="music-wrapper">

      <!-- LEFT PANEL -->
      <div class="music-albums">
        <h3>📀 Albums</h3>

        ${albums.map(a => `
          <button class="action"
            onclick="selectAlbum(${a.id})"
            style="background:${selectedAlbumId === a.id ? '#444' : '#2a2a35'}; width:100%">
            ${a.title}
          </button>
        `).join("")}
      </div>

      <!-- RIGHT PANEL -->
      <div class="music-content">

        <div class="card">
          <h3>🎵 Music</h3>

          ${music.map(m => `
            <div class="music-item">
              <b>${m.title}</b><br>
              <a href="${m.youtube_url}" target="_blank">YouTube</a>
              <p>Position: ${m.position}</p>
              <button onclick="deleteMusic(${m.id})">Delete</button>
            </div>
          `).join("")}
        </div>

        <div class="card">
          <h3>➕ Add Music</h3>

          <input id="musicTitle" placeholder="Title">
          <input id="musicUrl" placeholder="YouTube URL">
          <input id="musicPos" type="number" value="0">

          <button onclick="addMusic()">Add</button>
        </div>

      </div>

    </div>
  `);
}

function selectAlbum(id) {
  selectedAlbumId = id;
  loadMusicPanel();
}

async function addMusic() {
  if (!selectedAlbumId) return showError("Select album");

  const title = document.getElementById("musicTitle").value;
  const youtube_url = document.getElementById("musicUrl").value;
  const position = Number(document.getElementById("musicPos").value);

  if (isEmpty(title)) return showError("Title required");
  if (!minLen(title, 2)) return showError("Title min 2 symbols");

  if (isEmpty(youtube_url)) return showError("YouTube URL required");
  if (!youtube_url.includes("http")) return showError("Invalid URL");

  if (isNaN(position) || position < 0) {
    return showError("Position must be 0 or higher");
  }

  await api(`/music/${selectedAlbumId}`, {
    method: "POST",
    body: JSON.stringify({
      title: title.trim(),
      youtube_url: youtube_url.trim(),
      position
    })
  });

  loadMusicPanel();
}

async function deleteMusic(id) {
  if (!confirm("Delete track?")) return;

  await api(`/music/${id}`, { method: "DELETE" });

  loadMusicPanel();
}

/* =========================
   INIT
========================= */

loadDashboard();

function isEmpty(v) {
  return v === null || v === undefined || String(v).trim().length === 0;
}

function minLen(v, len) {
  return String(v).trim().length >= len;
}

function showError(msg) {
  alert(msg);
  return false;
}