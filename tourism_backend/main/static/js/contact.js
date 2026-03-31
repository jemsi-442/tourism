const contactForm = document.getElementById("contactForm");

if (contactForm) {
  const fullNameInput = contactForm.querySelector('[name="full_name"]');
  const emailInput = contactForm.querySelector('[name="email"]');
  const phoneInput = contactForm.querySelector('[name="phone"]');
  const messageInput = contactForm.querySelector('[name="message"]');
  const errorDiv = document.getElementById("formError");
  const whatsappButton = document.getElementById("waBtn");
  const emailButton = document.getElementById("emailBtn");

  function validateForm() {
    const name = fullNameInput.value.trim();
    const email = emailInput.value.trim();
    const phone = phoneInput.value.trim();
    const message = messageInput.value.trim();

    errorDiv.style.display = "none";

    if (!name || !email || !phone || !message) {
      errorDiv.innerText = "Please complete all fields before sending your request.";
      errorDiv.style.display = "block";
      return null;
    }

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(email)) {
      errorDiv.innerText = "Please enter a valid email address so we can reply to you.";
      errorDiv.style.display = "block";
      return null;
    }

    return { name, email, phone, message };
  }

  [whatsappButton, emailButton].forEach((button) => {
    if (!button) {
      return;
    }

    button.addEventListener("click", (event) => {
      const data = validateForm();
      if (!data) {
        event.preventDefault();
      }
    });
  });
}
