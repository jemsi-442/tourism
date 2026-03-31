const galleryModal = document.getElementById("gallery-modal-bg");
const galleryModalImage = document.getElementById("gallery-modal-img");
const galleryCloseButton = document.querySelector(".gallery-modal-close");

if (galleryModal && galleryModalImage) {
  function openGalleryModal(src, alt) {
    galleryModalImage.src = src;
    galleryModalImage.alt = alt;
    galleryModal.classList.add("active");
  }

  function closeGalleryModal() {
    galleryModalImage.src = "";
    galleryModalImage.alt = "";
    galleryModal.classList.remove("active");
  }

  document.querySelectorAll(".zoomable-photo").forEach((img) => {
    img.addEventListener("click", () => {
      openGalleryModal(img.src, img.alt);
    });
  });

  galleryModal.addEventListener("click", (event) => {
    if (event.target === galleryModal) {
      closeGalleryModal();
    }
  });

  if (galleryCloseButton) {
    galleryCloseButton.addEventListener("click", closeGalleryModal);
  }
}
