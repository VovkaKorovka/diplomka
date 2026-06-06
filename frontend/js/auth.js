const API = "https://diplomka-5mob.onrender.com";

/* ======================
   VALIDATION
====================== */

function isEmail(email) {
  return /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email);
}

/* username нормальний (без обмеження тільки letters) */
function isUsername(str) {
  return /^[a-zA-Z0-9_]{3,20}$/.test(str);
}

function isPassword(p) {
  return typeof p === "string" && p.length >= 6;
}

function notEmpty(v) {
  return v && v.trim().length > 0;
}

/* ======================
   HELPERS
====================== */

function setLoading(btn, state) {
  if (!btn) return;
  btn.disabled = state;
  btn.textContent = state ? "Loading..." : btn.dataset.original || "Submit";
}

/* ======================
   LOGIN
====================== */

async function login() {
  const btn = document.querySelector("#loginBtn");

  try {
    const email = document.getElementById("email")?.value?.trim();
    const password = document.getElementById("password")?.value?.trim();

    if (!notEmpty(email)) return alert("Email required");
    if (!notEmpty(password)) return alert("Password required");

    if (!isEmail(email)) return alert("Invalid email format");
    if (!isPassword(password)) return alert("Password min 6 chars");

    setLoading(btn, true);

    const res = await fetch(`${API}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      return alert(data.detail || "Login failed");
    }

    const token = data.access_token;
    localStorage.setItem("token", token);

    const meRes = await fetch(`${API}/users/me`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

    const me = await meRes.json().catch(() => null);

    if (!meRes.ok || !me) {
      localStorage.clear();
      return alert("Failed to load user");
    }

    /* ⚠️ STILL CLIENT CHECK (server must also enforce this) */
    if (me.is_active === false) {
      localStorage.clear();
      return alert("Account banned");
    }

    localStorage.setItem("role", me.role || "user");

    window.location.href = "index.html";

  } catch (err) {
    console.error(err);
    alert("Server error");
  } finally {
    setLoading(btn, false);
  }
}

/* ======================
   REGISTER
====================== */

async function register() {
  const btn = document.querySelector("#registerBtn");

  try {
    const username = document.getElementById("username")?.value?.trim();
    const email = document.getElementById("email")?.value?.trim();
    const password = document.getElementById("password")?.value?.trim();

    if (!notEmpty(username)) return alert("Username required");
    if (!notEmpty(email)) return alert("Email required");
    if (!notEmpty(password)) return alert("Password required");

    if (!isUsername(username)) {
      return alert("Username 3–20 chars (letters, numbers, _)");
    }

    if (!isEmail(email)) return alert("Invalid email");
    if (!isPassword(password)) return alert("Password min 6 chars");

    setLoading(btn, true);

    const res = await fetch(`${API}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, email, password })
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      return alert(data.detail || "Register failed");
    }

    const token = data.access_token;

    localStorage.setItem("token", token);
    localStorage.setItem("role", data.role || "user");

    alert("Account created!");

    window.location.href = "index.html";

  } catch (err) {
    console.error(err);
    alert("Server error");
  } finally {
    setLoading(btn, false);
  }
}