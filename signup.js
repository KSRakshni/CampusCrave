const API_BASE = "http://127.0.0.1:5000/api";
const USER_KEY = "campuscrave_user";

document.getElementById("signupForm").addEventListener("submit", async function(event) {

    event.preventDefault();

    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim().toLowerCase();
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirmPassword").value;

    if (password !== confirmPassword) {
        alert("Passwords do not match.");
        return;
    }

    if (password.length < 6) {
        alert("Password must contain at least 6 characters.");
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/signup`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, email, password })
        });
        const result = await response.json();

        if (!response.ok) {
            alert(result.error || "Unable to create your account.");
            return;
        }

        localStorage.setItem(USER_KEY, JSON.stringify(result.user));
        alert("Account created successfully!");
        window.location.href = "login.html";
    } catch (error) {
        alert("Unable to reach CampusCrave. Make sure the backend is running.");
    }
});


function togglePassword(id) {

    const input = document.getElementById(id);

    if (input.type === "password") {
        input.type = "text";
    } else {
        input.type = "password";
    }
}