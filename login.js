const API_BASE = "http://127.0.0.1:5000/api";
const SESSION_KEY = "campuscrave_session";
const USER_KEY = "campuscrave_user";

document.getElementById("loginForm").addEventListener("submit", async function(event) {

    event.preventDefault();

    const email = document.getElementById("email").value.trim().toLowerCase();
    const password = document.getElementById("password").value;

    try {
        const response = await fetch(`${API_BASE}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });
        const result = await response.json();

        if (!response.ok) {
            alert(result.error || "Invalid email or password.");
            return;
        }

        localStorage.setItem(SESSION_KEY, String(result.user.id));
        localStorage.setItem(USER_KEY, JSON.stringify(result.user));
        alert("Login successful!");
        window.location.href = "dashboard.html";
    } catch (error) {
        alert("Unable to reach CampusCrave. Make sure the backend is running.");
    }
});


function togglePassword() {

    const password = document.getElementById("password");

    if (password.type === "password") {
        password.type = "text";
    } else {
        password.type = "password";
    }
}


function forgotPassword() {
    alert("Password reset is not available. Please contact the canteen administrator.");
}