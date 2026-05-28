const API_URL = "https://diplomka-5mob.onrender.com";

async function getArticles() {
  const response = await fetch(`${API_URL}/articles`);

  if (!response.ok) {
    throw new Error("Failed to fetch articles");
  }

  return await response.json();
}

function token() {
  return localStorage.getItem("token");
}

function authHeaders() {
  return {
    Authorization: "Bearer " + token(),
    "Content-Type": "application/json"
  };
}