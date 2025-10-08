document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('registrationForm');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const password = document.getElementById('password').value;
    const confirm = document.getElementById('confirm_password').value;

    if (password !== confirm) {
      alert("Passwords do not match!");
      return;
    }

    const formData = {
      username: document.querySelector('input[name="email"]').value,
      email: document.querySelector('input[name="email"]').value,
      password: password,
      role: document.querySelector('input[name="user_type"]:checked').value
    };

    try {
      const response = await fetch(
        "https://placement-portal-e0cggsa9gfg6ghg5.southafricanorth-01.azurewebsites.net/users/register/",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(formData)
        }
      );

      if (response.ok) {
        alert("Registration successful!");
        localStorage.setItem('userType', formData.role);
        window.location.href = "{% url 'login' %}";
      } else {
        const err = await response.json();
        alert("Registration failed: " + JSON.stringify(err));
      }
    } catch (err) {
      alert("Request failed: " + err);
    }
  });
});
