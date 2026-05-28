function safeGet(key) {
  try {
    const val = localStorage.getItem(key);
    if (!val || val === "null" || val === "undefined") return null;
    return val;
  } catch {
    return null;
  }
}

function getToken() {
  return safeGet("token");
}

function getRole() {
  return safeGet("role");
}

// ===============================
// 🔥 AUTH RENDER
// ===============================
function renderAuth() {
  const box = document.getElementById("authButtons");
  if (!box) return;

  const token = getToken();
  const role = getRole();

  // ❌ NOT LOGGED IN
  if (!token) {
    box.innerHTML = `
      <button onclick="location.href='login.html'">Login</button>
      <button onclick="location.href='register.html'">Register</button>
    `;
    return;
  }

  // 👤 PROFILE BUTTON
  const profileBtn = `
    <button onclick="location.href='profile.html'">
      My Profile
    </button>
  `;

  // 👑 ADMIN BUTTON
  const adminBtn = role === "admin"
    ? `<button onclick="location.href='admin.html'">Admin Panel</button>`
    : "";

  // 🚪 LOGOUT BUTTON
  const logoutBtn = `
    <button onclick="logout()">Logout</button>
  `;

  box.innerHTML = `
    ${profileBtn}
    ${adminBtn}
    ${logoutBtn}
  `;
}

// ===============================
// 🚪 LOGOUT
// ===============================
function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("role");

  // UX CLEAN
  window.location.href = "index.html";
}

// ===============================
// 🚀 NAV ACTION
// ===============================
function goExplore() {
  location.href = "albums.html";
}

// ===============================
// 🎯 ACTIVE NAV HIGHLIGHT
// ===============================
function setActiveNav() {
  const path = window.location.pathname.split("/").pop();

  document.querySelectorAll("nav a").forEach(a => {
    if (a.getAttribute("href") === path) {
      a.classList.add("active");
    }
  });
}
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("contactForm");
  if (!form) return;

  const status = document.getElementById("contactStatus");
  const btn = document.getElementById("contactBtn");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value;
    const message = document.getElementById("message").value;

    try {
      btn.disabled = true;
      btn.innerText = "Sending...";

      const API_URL = "https://diplomka-production-a099.up.railway.app";

      const res = await fetch(`${API_URL}/contact/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          email,
          message
        })
      });

      const data = await res.json();

      if (res.ok) {
        status.innerText = "✅ Message sent!";
        form.reset();
      } else {
        status.innerText = "❌ Error sending message";
      }

    } catch (err) {
      console.error(err);
      status.innerText = "❌ Server not responding";
    } finally {
      btn.disabled = false;
      btn.innerText = "Send";
    }
  });
});

// ===============================
// 🚀 INIT
// ===============================
document.addEventListener("DOMContentLoaded", () => {
  renderAuth();
  setActiveNav();
});