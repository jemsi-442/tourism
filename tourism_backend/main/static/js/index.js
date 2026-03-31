const slides = document.querySelectorAll(".slide");
let currentSlide = 0;
const landingMenuToggle = document.querySelector(".landing-menu-toggle");
const landingMenuPanel = document.querySelector(".landing-menu-panel");

function closeLandingMenu() {
  if (!landingMenuToggle || !landingMenuPanel) {
    return;
  }

  landingMenuToggle.classList.remove("is-open");
  landingMenuToggle.setAttribute("aria-expanded", "false");
  landingMenuPanel.classList.remove("is-open");
  landingMenuPanel.setAttribute("aria-hidden", "true");
}

if (landingMenuToggle && landingMenuPanel) {
  landingMenuToggle.addEventListener("click", function toggleLandingMenu() {
    const isOpen = landingMenuToggle.classList.toggle("is-open");
    landingMenuToggle.setAttribute("aria-expanded", String(isOpen));
    landingMenuPanel.classList.toggle("is-open", isOpen);
    landingMenuPanel.setAttribute("aria-hidden", String(!isOpen));
  });

  document.addEventListener("click", function handleDocumentClick(event) {
    if (
      landingMenuToggle.classList.contains("is-open") &&
      !landingMenuToggle.contains(event.target) &&
      !landingMenuPanel.contains(event.target)
    ) {
      closeLandingMenu();
    }
  });

  document.addEventListener("keydown", function handleEscape(event) {
    if (event.key === "Escape") {
      closeLandingMenu();
    }
  });

  landingMenuPanel.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", closeLandingMenu);
  });
}

function showSlide(index) {
  slides.forEach((slide, idx) => {
    slide.classList.toggle("active", idx === index);
  });
}

if (slides.length > 0) {
  setInterval(() => {
    currentSlide = (currentSlide + 1) % slides.length;
    showSlide(currentSlide);
  }, 3500);
}

window.scrollToExplore = function scrollToExplore() {
  const gallery = document.getElementById("gallery");
  if (gallery) {
    gallery.scrollIntoView({ behavior: "smooth" });
  } else {
    window.scrollTo({ top: window.innerHeight, behavior: "smooth" });
  }
};

const filterButtons = document.querySelectorAll(".filter-btn");
const cards = document.querySelectorAll(".card");

filterButtons.forEach((button) => {
  button.addEventListener("click", function handleFilterClick() {
    filterButtons.forEach((btn) => btn.classList.remove("active"));
    this.classList.add("active");

    const filter = this.getAttribute("data-filter");
    cards.forEach((card) => {
      card.style.display =
        filter === "all" || card.getAttribute("data-category") === filter ? "" : "none";
    });
  });
});
