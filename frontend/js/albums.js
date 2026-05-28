document.addEventListener("DOMContentLoaded", loadAlbums);

async function loadAlbums() {

  const grid = document.getElementById("albumsGrid");

  if (!grid) return;

  try {

    const articles = await getArticles();

    grid.innerHTML = "";

    if (articles.length === 0) {
      grid.innerHTML = "<p>No albums found</p>";
      return;
    }

    articles.forEach(article => {

      const card = document.createElement("div");

      card.className = "card";

      card.innerHTML = `
        <img 
          src="https://picsum.photos/400/300?random=${article.id}" 
          alt="${article.title}"
        />

        <div class="card-content">
          <h3>${article.title}</h3>

          <p>
            ${article.content.slice(0, 120)}...
          </p>

          <span class="views">
            👁 ${article.views}
          </span>
        </div>
      `;

      card.addEventListener("click", () => {
        window.location.href = `article.html?id=${article.id}`;
      });

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