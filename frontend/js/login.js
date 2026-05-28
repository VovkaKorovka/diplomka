async function login(email, password) {
  const res = await fetch("https://diplomka-production-a099.up.railway.app/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ email, password })
  });

  const data = await res.json();

  if (!res.ok) {
    alert("Login failed");
    return;
  }

  localStorage.setItem("token", data.access_token);

  const meRes = await fetch("https://diplomka-production-a099.up.railway.app/users/me", {
    headers: {
      "Authorization": `Bearer ${data.access_token}`
    }
  });

  const me = await meRes.json();

  localStorage.setItem("role", me.role);

  window.location.href = "index.html";
}