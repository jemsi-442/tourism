(function () {
  var navbarToggle = document.querySelector(".navbar-toggle");
  var navbarMenu = document.querySelector(".navbar-menu");

  if (!navbarToggle || !navbarMenu) {
    return;
  }

  function closeDropdowns(exceptContent) {
    document.querySelectorAll(".dropdown .dropdown-content").forEach(function (content) {
      if (content !== exceptContent) {
        content.style.display = "none";
      }
    });
  }

  navbarToggle.addEventListener("click", function () {
    navbarMenu.classList.toggle("open");
    if (!navbarMenu.classList.contains("open")) {
      closeDropdowns();
    }
  });

  document.addEventListener("click", function (event) {
    if (window.innerWidth < 768) {
      if (!navbarMenu.contains(event.target) && !navbarToggle.contains(event.target)) {
        navbarMenu.classList.remove("open");
        closeDropdowns();
      }
    }
  });

  document.querySelectorAll(".dropdown > a").forEach(function (dropLink) {
    dropLink.addEventListener("click", function (event) {
      var content;
      var shouldOpen;

      if (window.innerWidth < 768) {
        event.preventDefault();
        content = this.parentElement.querySelector(".dropdown-content");
        shouldOpen = content.style.display !== "block";
        closeDropdowns(content);
        content.style.display = shouldOpen ? "block" : "none";
      }
    });
  });
}());
