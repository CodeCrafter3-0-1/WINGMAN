const form = document.getElementById("loginForm");
const errorEl = document.getElementById("loginError");
const loginBtn = document.getElementById("loginBtn");
const emailEl = document.getElementById("email");
const passEl = document.getElementById("password");
const passwordToggle = document.getElementById("passwordToggle");

// Password visibility toggle
passwordToggle.addEventListener("click", () => {
  const isPassword = passEl.type === "password";
  passEl.type = isPassword ? "text" : "password";
  passwordToggle.innerHTML = isPassword ? '<i class="fas fa-eye-slash"></i>' : '<i class="fas fa-eye"></i>';
});

// Demo account fillers
document.getElementById("fillAdmin").addEventListener("click", () => {
  emailEl.value = "admin@example.com";
  passEl.value = "admin123";
  errorEl.textContent = "";
  emailEl.focus();
});

document.getElementById("fillDoctor").addEventListener("click", () => {
  emailEl.value = "doctor@example.com";
  passEl.value = "doctor123";
  errorEl.textContent = "";
  emailEl.focus();
});

// Form submission
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  errorEl.textContent = "";
  loginBtn.disabled = true;
  loginBtn.innerHTML = '<span>Signing in...</span><i class="fas fa-spinner fa-spin"></i>';

  const email = emailEl.value.trim();
  const password = passEl.value;

  try {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    if (!res.ok) {
      let msg = "Login failed";
      try {
        const body = await res.json();
        msg = body.detail || msg;
      } catch (_) {
        // Keep default message.
      }
      errorEl.textContent = msg;
      loginBtn.innerHTML = '<span>Sign In</span><i class="fas fa-arrow-right"></i>';
      return;
    }

    // Success - redirect
    loginBtn.innerHTML = '<span>Success!</span><i class="fas fa-check"></i>';
    setTimeout(() => {
      window.location.href = "/introduction";
    }, 500);

  } catch (_) {
    errorEl.textContent = "Network error. Please try again.";
    loginBtn.innerHTML = '<span>Sign In</span><i class="fas fa-arrow-right"></i>';
  } finally {
    loginBtn.disabled = false;
  }
});

// Auto-focus email field on page load
document.addEventListener("DOMContentLoaded", () => {
  emailEl.focus();
});

