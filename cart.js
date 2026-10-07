const SESSION_KEY = "campuscrave_session";
const USER_KEY = "campuscrave_user";


// ================= GET CURRENT USER =================

function getCurrentUser() {

    const sessionId = localStorage.getItem(SESSION_KEY);

    if (!sessionId) {
        window.location.href = "login.html";
        return null;
    }

    const user = JSON.parse(localStorage.getItem(USER_KEY) || "null");

    if (!user || String(user.id) !== String(sessionId)) {
        localStorage.removeItem(SESSION_KEY);
        window.location.href = "login.html";
        return null;
    }

    return user;
}


// ================= SAVE USER =================

function saveUser(updatedUser) {
    localStorage.setItem(USER_KEY, JSON.stringify(updatedUser));
}


// ================= LOAD CART =================

function loadCart() {

    const currentUser = getCurrentUser();

    if (!currentUser) return;

    if (!currentUser.cart) {
        currentUser.cart = [];
    }

    const cartItems = document.getElementById("cartItems");
    const cartContent = document.getElementById("cartContent");
    const emptyCart = document.getElementById("emptyCart");

    cartItems.innerHTML = "";

    if (currentUser.cart.length === 0) {

        cartContent.style.display = "none";
        emptyCart.style.display = "block";

        updateCartCount(0);

        return;
    }

    cartContent.style.display = "grid";
    emptyCart.style.display = "none";


    let totalItems = 0;
    let subtotal = 0;


    currentUser.cart.forEach((item, index) => {

        const quantity = Number(item.quantity) || 1;
        const price = Number(item.price) || 0;

        totalItems += quantity;
        subtotal += price * quantity;


        const itemElement = document.createElement("div");

        itemElement.className = "cart-item";


        itemElement.innerHTML = `

            <div class="item-left">

                <div class="item-image">
                    ${item.emoji || "🍴"}
                </div>

                <div class="item-info">

                    <h3>${item.name}</h3>

                    <p class="item-price">
                        ₹${price.toFixed(2)}
                    </p>

                </div>

            </div>


            <div class="quantity-box">

                <button onclick="decreaseQuantity(${index})">
                    −
                </button>

                <span class="quantity">
                    ${quantity}
                </span>

                <button onclick="increaseQuantity(${index})">
                    +
                </button>

            </div>


            <div class="item-total">
                ₹${(price * quantity).toFixed(2)}
            </div>


            <button
                class="remove-btn"
                onclick="removeItem(${index})">

                Remove

            </button>

        `;

        cartItems.appendChild(itemElement);

    });


    // Delivery fee
    const deliveryFee = subtotal >= 300 ? 0 : 20;

    const total = subtotal + deliveryFee;


    document.getElementById("summaryItems").textContent =
        totalItems;

    document.getElementById("subtotal").textContent =
        subtotal.toFixed(2);

    document.getElementById("deliveryFee").textContent =
        deliveryFee.toFixed(2);

    document.getElementById("totalPrice").textContent =
        total.toFixed(2);


    updateCartCount(totalItems);
}


// ================= CART COUNT =================

function updateCartCount(count) {

    const cartCount = document.getElementById("cartCount");

    if (cartCount) {
        cartCount.textContent = count;
    }
}


// ================= INCREASE =================

function increaseQuantity(index) {

    const currentUser = getCurrentUser();

    if (!currentUser) return;

    currentUser.cart[index].quantity++;

    saveUser(currentUser);

    loadCart();
}


// ================= DECREASE =================

function decreaseQuantity(index) {

    const currentUser = getCurrentUser();

    if (!currentUser) return;


    if (currentUser.cart[index].quantity > 1) {

        currentUser.cart[index].quantity--;

    } else {

        const confirmRemove =
            confirm("Remove this item from your cart?");

        if (confirmRemove) {

            currentUser.cart.splice(index, 1);

        } else {

            return;
        }
    }


    saveUser(currentUser);

    loadCart();
}


// ================= REMOVE ITEM =================

function removeItem(index) {

    const currentUser = getCurrentUser();

    if (!currentUser) return;


    const itemName =
        currentUser.cart[index].name;


    const confirmRemove =
        confirm(`Remove ${itemName} from your cart?`);


    if (!confirmRemove) return;


    currentUser.cart.splice(index, 1);

    saveUser(currentUser);

    loadCart();
}


// ================= CLEAR CART =================

function clearCart() {

    const currentUser = getCurrentUser();

    if (!currentUser) return;


    if (currentUser.cart.length === 0) {
        return;
    }


    const confirmClear =
        confirm("Are you sure you want to clear your cart?");


    if (!confirmClear) return;


    currentUser.cart = [];

    saveUser(currentUser);

    loadCart();
}


// ================= PAYMENT =================

function proceedToPayment() {

    const currentUser = getCurrentUser();

    if (!currentUser) return;


    if (!currentUser.cart ||
        currentUser.cart.length === 0) {

        alert("Your cart is empty!");

        return;
    }


    window.location.href = "payment.html";
}


// ================= MENU =================

function goToMenu() {

    window.location.href = "menu.html";
}


// ================= LOGOUT =================

function logout() {

    localStorage.removeItem(SESSION_KEY);
    localStorage.removeItem(USER_KEY);

    window.location.href = "login.html";
}


// ================= START =================

document.addEventListener(
    "DOMContentLoaded",
    loadCart
);