const API = "https://my-backend-production-7cd2.up.railway.app";

/* ======================
   VALIDATION
====================== */

function isEmail(email) {
  return /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email);
}

function isText(str) {
  return /^[a-zA-Z0-9]+$/.test(str);
}

function isPassword(p) {
  return /^[a-zA-Z0-9]{6,}$/.test(p);
}

/* ======================
   LOGIN
====================== */

async function login() {
  try {
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!isEmail(email)) return alert("Invalid email");
    if (!isPassword(password)) return alert("Invalid password");

    const res = await fetch(`${API}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      return alert(data.detail || "Login failed");
    }

    localStorage.setItem("token", data.access_token);

    const meRes = await fetch(`${API}/users/me`, {
      headers: {
        Authorization: `Bearer ${data.access_token}`
      }
    });

    const me = await meRes.json().catch(() => null);

    if (!meRes.ok || !me) {
      localStorage.clear();
      return alert("Failed to load user");
    }

    // 🔥 BAN CHECK (CLIENT SIDE)
    if (me.is_active === false) {
      localStorage.clear();
      return alert("You are banned from system");
    }

    localStorage.setItem("role", me.role || "user");

    window.location.href = "index.html";

  } catch (err) {
    console.error(err);
    alert("Server error");
  }
}

/* ======================
   REGISTER
====================== */

async function register() {
  try {
    const username = document.getElementById("username").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    if (username.length < 3) return alert("Username too short");
    if (!isText(username)) return alert("Only English letters/numbers");
    if (!isEmail(email)) return alert("Invalid email");
    if (!isPassword(password)) return alert("Password min 6 chars");

    const res = await fetch(`${API}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, email, password })
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      return alert(data.detail || "Register failed");
    }

    localStorage.setItem("token", data.access_token);
    localStorage.setItem("role", data.role || "user");

    alert("Account created!");

    window.location.href = "index.html";

  } catch (err) {
    console.error(err);
    alert("Server error");
  }
}