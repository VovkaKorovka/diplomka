const API_URL = "https://my-backend-production-7cd2.up.railway.app";

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