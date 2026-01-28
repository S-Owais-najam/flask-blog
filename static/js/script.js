const elements = document.querySelectorAll('.reveal');

window.addEventListener('scroll', () => {
  elements.forEach(el => {
    const top = el.getBoundingClientRect().top;
    const windowHeight = window.innerHeight;

    if (top < windowHeight - 100) {
      el.classList.add('active');
    }
  });
});
// Scroll reveal
document.addEventListener("scroll", () => {
  document.querySelectorAll(".reveal").forEach(el => {
    if (el.getBoundingClientRect().top < window.innerHeight - 100) {
      el.classList.add("active");
    }
  });
});

// Dark mode
const toggle = document.getElementById("darkToggle");
if (toggle) {
  toggle.onclick = () => {
    document.body.classList.toggle("dark");
    localStorage.setItem("dark", document.body.classList.contains("dark"));
  };
}
if (localStorage.getItem("dark") === "true") {
  document.body.classList.add("dark");
}

// Search suggestions
const searchInput = document.querySelector(".search-box input");
if (searchInput) {
  searchInput.addEventListener("input", async () => {
    const q = searchInput.value;
    if (q.length < 2) return;
    const res = await fetch(`/search-suggest?q=${q}`);
    const data = await res.json();
    console.log(data); // You can render dropdown easily
  });
}

