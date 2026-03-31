const homeRoot = document.querySelector(".home-dashboard-content");

if (homeRoot) {
  const slideshowSlides = document.querySelectorAll("#slideshow-bg .slide");
  let currentSlide = 0;

  if (slideshowSlides.length > 0) {
    setInterval(() => {
      slideshowSlides[currentSlide].style.opacity = 0;
      currentSlide = (currentSlide + 1) % slideshowSlides.length;
      slideshowSlides[currentSlide].style.opacity = 1;
    }, 4000);
  }

  const photoBase = homeRoot.dataset.photoBase || "";
  const attractions = Array.isArray(window.homeAttractionsData) ? window.homeAttractionsData : [];
  const attractionsList = document.getElementById("attractions-list");
  const galleryImages = document.getElementById("gallery-images");
  const galleryModal = document.getElementById("gallery-modal");
  const closeGalleryButton = document.getElementById("close-gallery");
  const zoomModal = document.getElementById("img-zoom-modal");
  const zoomImage = document.getElementById("img-zoomed");
  const zoomCloseButton = document.getElementById("img-zoom-close");

  function enableImageZoom() {
    document.querySelectorAll(".dash-section section img, #attractions-list img, #gallery-images img").forEach((img) => {
      img.classList.add("zoomable-img", "home-zoomable");
      img.onclick = function handleImageZoom() {
        zoomImage.src = this.src;
        zoomModal.style.display = "flex";
      };
    });
  }

  function renderAttractions(group) {
    attractionsList.innerHTML = "";
    attractions.forEach((attr, idx) => {
      if (group === "all" || attr.group === group) {
        const imgSrc = attr.images[0] ? `${photoBase}${attr.images[0]}` : "";
        const card = document.createElement("div");
        card.className = "attraction-card home-attraction-card";
        card.innerHTML = `
          <img src="${imgSrc}" alt="${attr.name}" class="home-attraction-image">
          <h3 class="home-attraction-title">${attr.name}</h3>
          <p class="home-attraction-copy">${attr.knownFor}</p>
          <button class="view-more-btn home-view-more-btn" data-idx="${idx}">View More</button>
        `;
        attractionsList.appendChild(card);
      }
    });
    enableImageZoom();
  }

  document.querySelectorAll(".filter-btn").forEach((button) => {
    button.addEventListener("click", function handleFilterClick() {
      document.querySelectorAll(".filter-btn").forEach((btn) => btn.classList.remove("active"));
      this.classList.add("active");
      renderAttractions(this.dataset.group);
    });
  });

  renderAttractions("all");

  attractionsList.addEventListener("click", (event) => {
    if (event.target.classList.contains("view-more-btn")) {
      const attr = attractions[event.target.dataset.idx];
      galleryImages.innerHTML = "";
      attr.images.forEach((img) => {
        const imgElement = document.createElement("img");
        imgElement.src = `${photoBase}${img}`;
        imgElement.alt = attr.name;
        imgElement.className = "home-gallery-thumb";
        galleryImages.appendChild(imgElement);
      });
      galleryModal.style.display = "flex";
      enableImageZoom();
    }
  });

  closeGalleryButton.addEventListener("click", () => {
    galleryModal.style.display = "none";
  });

  galleryModal.addEventListener("click", (event) => {
    if (event.target === galleryModal) {
      galleryModal.style.display = "none";
    }
  });

  zoomCloseButton.addEventListener("click", () => {
    zoomModal.style.display = "none";
    zoomImage.src = "";
  });

  zoomModal.addEventListener("click", (event) => {
    if (event.target === zoomModal) {
      zoomModal.style.display = "none";
      zoomImage.src = "";
    }
  });
}
