document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("admin-confirm-modal");
  if (!modal) {
    return;
  }

  const title = document.getElementById("admin-confirm-title");
  const message = document.getElementById("admin-confirm-message");
  const acceptButton = modal.querySelector("[data-confirm-accept]");
  const cancelButton = modal.querySelector("[data-confirm-cancel]");
  const closeElements = modal.querySelectorAll("[data-confirm-close], [data-confirm-cancel]");
  const confirmForms = document.querySelectorAll("form[data-confirm-action]");

  let pendingForm = null;

  const closeModal = () => {
    modal.hidden = true;
    pendingForm = null;
  };

  const openModal = (form) => {
    pendingForm = form;
    title.textContent = form.dataset.confirmAction || "Confirm Action";
    message.textContent =
      form.dataset.confirmMessage || "Are you sure you want to continue?";
    modal.hidden = false;
  };

  confirmForms.forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (form.dataset.confirmed === "true") {
        form.dataset.confirmed = "false";
        return;
      }

      event.preventDefault();
      openModal(form);
    });
  });

  closeElements.forEach((element) => {
    element.addEventListener("click", closeModal);
  });

  acceptButton?.addEventListener("click", () => {
    if (!pendingForm) {
      return;
    }
    pendingForm.dataset.confirmed = "true";
    pendingForm.requestSubmit();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !modal.hidden) {
      closeModal();
    }
  });
});
