// ==========================================
// CAMPUSCRAVE MENU.JS
// ==========================================

const API_BASE = "http://127.0.0.1:5000/api";
const SESSION_KEY = "campuscrave_session";
const USER_KEY = "campuscrave_user";
const menuItemsByName = {};


// ==========================================
// GET CURRENT USER
// ==========================================

function getCurrentUser() {

    const sessionId = localStorage.getItem(SESSION_KEY);

    if (!sessionId) {

        alert("Please login first.");

        window.location.href = "login.html";

        return null;
    }

    const user = JSON.parse(localStorage.getItem(USER_KEY) || "null");

    if (!user || String(user.id) !== String(sessionId)) {

        alert("User session not found.");

        localStorage.removeItem(SESSION_KEY);

        window.location.href = "login.html";

        return null;
    }

    // Make sure cart exists
    if (!user.cart) {
        user.cart = [];
    }

    return user;
}


// ==========================================
// SAVE CURRENT USER
// ==========================================

function saveCurrentUser(updatedUser) {
    localStorage.setItem(USER_KEY, JSON.stringify(updatedUser));
}


async function loadMenuItems() {
    try {
        const response = await fetch(`${API_BASE}/menu`);
        if (!response.ok) throw new Error("Menu request failed");
        const items = await response.json();

        items.forEach(item => {
            menuItemsByName[item.name] = item;
            const card = [...document.querySelectorAll(".food-card")]
                .find(element => element.querySelector("h3")?.innerText.trim() === item.name);
            if (!card) return;
            card.dataset.menuItemId = item.id;
            const price = card.querySelector("p");
            if (price) price.textContent = `₹${item.price}`;
        });
    } catch (error) {
        console.error("Unable to load the menu API:", error);
    }
}


async function loadRecommendations() {
    const currentUser = getCurrentUser();
    if (!currentUser) return;
    try {
        const response = await fetch(`${API_BASE}/recommendations/${currentUser.id}`);
        if (response.ok) {
            localStorage.setItem("campuscrave_recommendations", JSON.stringify(await response.json()));
        }
    } catch (error) {
        console.error("Unable to load recommendations:", error);
    }
}


// ==========================================
// SEARCH FOOD
// ==========================================

function searchFood() {

    const input =
        document
            .getElementById("search")
            .value
            .toLowerCase()
            .trim();

    const foods =
        document.querySelectorAll(".food-card");

    foods.forEach(food => {

        const name =
            food
                .querySelector("h3")
                .innerText
                .toLowerCase();

        if (name.includes(input)) {

            food.style.display = "block";

        } else {

            food.style.display = "none";

        }

    });

}


// ==========================================
// CATEGORY FILTER
// ==========================================

function filterFood(category) {

    const foods =
        document.querySelectorAll(".food-card");

    foods.forEach(food => {

        if (category === "all") {

            food.style.display = "block";

        }

        else if (
            food.classList.contains(category)
        ) {

            food.style.display = "block";

        }

        else {

            food.style.display = "none";

        }

    });

}


// ==========================================
// ADD TO CART
// ==========================================

function addToCart(name, price, image, itemId) {

    const currentUser = getCurrentUser();

    if (!currentUser) return;


    // If image wasn't passed, find it from menu card
    if (!image) {

        const cards =
            document.querySelectorAll(".food-card");

        cards.forEach(card => {

            const cardName =
                card.querySelector("h3").innerText.trim();

            if (cardName === name) {

                const img =
                    card.querySelector("img");

                if (img) {

                    image = img.src;

                }

            }

        });

    }


    // Check if item already exists
    const found =
        currentUser.cart.find(
            item => item.name === name
        );


    if (found) {

        found.quantity++;

    }

    else {

        currentUser.cart.push({

            id: Date.now(),

            menu_item_id: Number(itemId || menuItemsByName[name]?.id) || null,

            name: name,

            price: Number(price),

            image: image || "",

            quantity: 1

        });

    }


    // Save user
    saveCurrentUser(currentUser);


    // Update cart count
    updateCartCount();


    // Small success message
    showAddedMessage(name);

}


// ==========================================
// AUTOMATICALLY CONNECT ALL ADD TO CART
// ==========================================

function setupAddToCartButtons() {

    const cards =
        document.querySelectorAll(".food-card");


    cards.forEach(card => {

        const button =
            card.querySelector("button");

        const nameElement =
            card.querySelector("h3");

        const priceElement =
            card.querySelector("p");

        const imageElement =
            card.querySelector("img");


        if (
            !button ||
            !nameElement ||
            !priceElement
        ) {

            return;

        }


        const name =
            nameElement.innerText.trim();


        const priceText =
            priceElement.innerText
                .replace("₹", "")
                .trim();


        const price =
            parseFloat(priceText);


        const image =
            imageElement
                ? imageElement.src
                : "";


        // Remove old inline onclick if present
        button.removeAttribute("onclick");


        // Prevent duplicate event listeners
        button.onclick = function () {

            addToCart(
                name,
                price,
                image,
                card.dataset.menuItemId
            );

        };

    });

}


// ==========================================
// SHOW ADDED MESSAGE
// ==========================================

function showAddedMessage(name) {

    const message =
        document.createElement("div");

    message.className = "cart-message";

    message.innerHTML =
        `✓ ${name} added to cart`;


    document.body.appendChild(message);


    setTimeout(() => {

        message.classList.add("show");

    }, 10);


    setTimeout(() => {

        message.classList.remove("show");

        setTimeout(() => {

            message.remove();

        }, 300);

    }, 1800);

}


// ==========================================
// UPDATE CART COUNT
// ==========================================

function updateCartCount() {

    const currentUser =
        getCurrentUser();

    if (!currentUser) return;


    let count = 0;


    if (currentUser.cart) {

        currentUser.cart.forEach(item => {

            count +=
                Number(item.quantity) || 0;

        });

    }


    // Font Awesome cart icon
    const cartIcon =
        document.querySelector(
            ".fa-cart-shopping"
        );


    if (cartIcon) {

        cartIcon.setAttribute(
            "data-count",
            count
        );

    }


    // If a cart count element exists
    const cartCount =
        document.getElementById("cartCount");


    if (cartCount) {

        cartCount.innerText = count;

    }

}


// ==========================================
// CART ICON
// ==========================================

function goToCart() {

    window.location.href =
        "cart.html";

}


// ==========================================
// USER PROFILE
// ==========================================

function loadUserProfile() {

    const currentUser =
        getCurrentUser();

    if (!currentUser) return;


    console.log(
        "Welcome " + currentUser.name
    );

}


// ==========================================
// LOGOUT
// ==========================================

function logout() {

    const confirmLogout =
        confirm(
            "Do you want to logout?"
        );


    if (confirmLogout) {

        localStorage.removeItem(
            SESSION_KEY
        );

        localStorage.removeItem(USER_KEY);

        window.location.href =
            "login.html";

    }

}


// ==========================================
// PAGE LOAD
// ==========================================

document.addEventListener(
    "DOMContentLoaded",
    async function () {

        await loadMenuItems();

        setupAddToCartButtons();

        updateCartCount();

        loadUserProfile();

        loadRecommendations();


        // Cart icon click
        const cartIcon =
            document.querySelector(
                ".fa-cart-shopping"
            );


        if (cartIcon) {

            cartIcon.addEventListener(
                "click",
                goToCart
            );

        }

    }
);