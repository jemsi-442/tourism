document.addEventListener("DOMContentLoaded", function () {
  var modal = document.getElementById("img-zoom-modal");
  var zoomedImage = document.getElementById("img-zoomed");
  var closeButton = document.getElementById("img-zoom-close");

  if (!modal || !zoomedImage || !closeButton) {
    return;
  }

  document.querySelectorAll(".zoomable-img").forEach(function (image) {
    image.addEventListener("click", function () {
      zoomedImage.src = image.src;
      modal.classList.add("active");
    });
  });

  closeButton.addEventListener("click", function () {
    modal.classList.remove("active");
    zoomedImage.src = "";
  });

  modal.addEventListener("click", function (event) {
    if (event.target === modal) {
      modal.classList.remove("active");
      zoomedImage.src = "";
    }
  });
});
