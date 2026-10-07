const API_BASE = "http://127.0.0.1:5000/api";
const SESSION_KEY = "campuscrave_session";
const USER_KEY = "campuscrave_user";

let selectedPayment = null;
let currentUser = null;
let upiPaymentCompleted = false;
let isSubmittingOrder = false;


/* ================================
   GET CURRENT USER
================================ */

function getCurrentUser() {

    const sessionId = localStorage.getItem(SESSION_KEY);

    if (!sessionId) {
        alert("Please login first.");
        window.location.href = "login.html";
        return null;
    }

    const user = JSON.parse(localStorage.getItem(USER_KEY) || "null");

    if (!user || String(user.id) !== String(sessionId)) {
        localStorage.removeItem(SESSION_KEY);

        alert("Please login again.");

        window.location.href = "login.html";

        return null;
    }

    return user;
}


/* ================================
   SAVE USER
================================ */

function saveUser(user) {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
}


/* ================================
   LOAD ORDER SUMMARY
================================ */

function loadOrder() {

    if (!currentUser) return;

    const cart = currentUser.cart || [];

    const orderItems =
        document.getElementById("orderItems");

    const placeOrderBtn =
        document.getElementById("placeOrderBtn");

    let subtotal = 0;

    orderItems.innerHTML = "";


    if (cart.length === 0) {

        orderItems.innerHTML = `
            <p class="empty-cart-message">
                Your cart is empty.
            </p>
        `;

        placeOrderBtn.disabled = true;

        return;
    }


    cart.forEach(item => {

        const quantity =
            Number(item.quantity) || 1;

        const price =
            Number(item.price) || 0;

        const itemTotal =
            price * quantity;

        subtotal += itemTotal;


        const div =
            document.createElement("div");

        div.className = "order-item";

        div.innerHTML = `
            <span>
                ${item.name} × ${quantity}
            </span>

            <span>
                ₹${itemTotal}
            </span>
        `;

        orderItems.appendChild(div);

    });


    /*
       Delivery is FREE when subtotal
       is ₹300 or more.
    */

    const deliveryFee =
        subtotal >= 300 ? 0 : 20;

    const total =
        subtotal + deliveryFee;


    document.getElementById("subtotal")
        .textContent = `₹${subtotal}`;

    document.getElementById("deliveryFee")
        .textContent =
            deliveryFee === 0
                ? "FREE"
                : `₹${deliveryFee}`;

    document.getElementById("totalAmount")
        .textContent = `₹${total}`;
}


/* ================================
   SELECT PAYMENT METHOD
================================ */

function selectPayment(method) {

    selectedPayment = method;

    upiPaymentCompleted = false;


    const cashOption =
        document.getElementById("cashOption");

    const upiOption =
        document.getElementById("upiOption");

    const cashPayment =
        document.getElementById("cashPayment");

    const upiPayment =
        document.getElementById("upiPayment");

    const placeOrderBtn =
        document.getElementById("placeOrderBtn");


    /* Reset */

    cashOption.classList.remove("selected");

    upiOption.classList.remove("selected");

    cashPayment.classList.remove("show");

    upiPayment.classList.remove("show");


    /* ================================
       CASH
    ================================ */

    if (method === "cash") {

        cashOption.classList.add("selected");

        cashPayment.classList.add("show");

        placeOrderBtn.disabled = false;

        placeOrderBtn.textContent =
            "🛍️ Place Order - Cash on Delivery";
    }


    /* ================================
       UPI
    ================================ */

    if (method === "upi") {

        upiOption.classList.add("selected");

        upiPayment.classList.add("show");

        placeOrderBtn.disabled = true;

        placeOrderBtn.textContent =
            "Complete UPI Payment First";
    }
}


/* ================================
   UPI PAYMENT COMPLETED
================================ */

function paymentCompleted() {

    if (selectedPayment !== "upi") {
        return;
    }


    upiPaymentCompleted = true;


    const placeOrderBtn =
        document.getElementById("placeOrderBtn");


    placeOrderBtn.disabled = false;

    placeOrderBtn.textContent =
        "🛍️ Place Order - UPI Paid";


    const button =
        document.querySelector(".payment-done-btn");


    button.textContent =
        "✓ Payment Completed";

    button.classList.add("completed");
}


/* ================================
   CROWD MANAGEMENT
================================ */

function getCrowdPrediction() {

    const hour =
        new Date().getHours();


    /*
       This is currently a DEMO
       crowd prediction.

       Later this can be replaced
       with your ML model prediction.
    */


    /* Lunch peak */

    if (hour >= 12 && hour <= 14) {

        return {
            level: "High",
            emoji: "🔴",
            min: 25,
            max: 40,
            message:
                "The canteen is currently crowded during lunch peak hours."
        };
    }


    /* Morning / less crowded */

    if (hour >= 10 && hour < 12) {

        return {
            level: "Low",
            emoji: "🟢",
            min: 10,
            max: 15,
            message:
                "The canteen is currently less crowded."
        };
    }


    /* Other times */

    return {
        level: "Medium",
        emoji: "🟡",
        min: 15,
        max: 25,
        message:
            "The canteen has a moderate crowd."
    };
}


/* ================================
   CALCULATE READY TIME
================================ */

function calculateReadyTime(minMinutes, maxMinutes) {

    const now = new Date();

    const minimumReady =
        new Date(
            now.getTime() +
            minMinutes * 60 * 1000
        );

    const maximumReady =
        new Date(
            now.getTime() +
            maxMinutes * 60 * 1000
        );


    const formatTime = time => {

        return time.toLocaleTimeString(
            [],
            {
                hour: "numeric",
                minute: "2-digit"
            }
        );

    };


    return {
        start:
            formatTime(minimumReady),

        end:
            formatTime(maximumReady),

        text:
            `${formatTime(minimumReady)} - ${formatTime(maximumReady)}`
    };
}


/* ================================
   PLACE ORDER
================================ */

async function placeOrder() {

    if (!currentUser) return;
    if (isSubmittingOrder) return;


    /* Check payment */

    if (!selectedPayment) {

        alert(
            "Please select a payment method."
        );

        return;
    }


    /* UPI check */

    if (
        selectedPayment === "upi" &&
        !upiPaymentCompleted
    ) {

        alert(
            "Please complete the UPI payment first."
        );

        return;
    }


    const cart =
        currentUser.cart || [];


    if (cart.length === 0) {

        alert(
            "Your cart is empty."
        );

        window.location.href =
            "menu.html";

        return;
    }


    /* ================================
       CALCULATE TOTAL
    ================================ */

    let subtotal = 0;


    cart.forEach(item => {

        subtotal +=
            Number(item.price) *
            Number(item.quantity || 1);

    });


    const deliveryFee =
        subtotal >= 300 ? 0 : 20;


    const total =
        subtotal + deliveryFee;


    /* ================================
       GET CROWD PREDICTION
    ================================ */

    const crowd =
        getCrowdPrediction();


    /* ================================
       CALCULATE READY TIME
    ================================ */

    const readyTime =
        calculateReadyTime(
            crowd.min,
            crowd.max
        );


    const pendingKey = `campuscrave_pending_order_${currentUser.id}`;
    const cartSignature = JSON.stringify(
        cart.map(item => ({
            menuItemId: item.menu_item_id || item.item_id || item.name,
            quantity: Number(item.quantity) || 1
        })).sort((left, right) => String(left.menuItemId).localeCompare(String(right.menuItemId)))
    );
    const placeOrderButton = document.getElementById("placeOrderBtn");
    let backendOrder = null;

    isSubmittingOrder = true;
    placeOrderButton.disabled = true;
    placeOrderButton.textContent = "Placing order...";

    try {
        const savedPendingOrder = JSON.parse(localStorage.getItem(pendingKey) || "null");
        const pendingId = savedPendingOrder && savedPendingOrder.cartSignature === cartSignature
            ? savedPendingOrder.orderId
            : null;
        if (!pendingId) localStorage.removeItem(pendingKey);
        if (pendingId) {
            const existingResponse = await fetch(`${API_BASE}/orders/${pendingId}`);
            if (existingResponse.ok) {
                const existingOrder = await existingResponse.json();
                if (String(existingOrder.user_id) === String(currentUser.id)) {
                    backendOrder = existingOrder;
                }
            }
        }

        if (!backendOrder) {
            const orderResponse = await fetch(`${API_BASE}/orders`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    user_id: currentUser.id,
                    items: cart.map(item => ({
                        menu_item_id: item.menu_item_id || item.item_id,
                        name: item.name,
                        quantity: Number(item.quantity) || 1
                    }))
                })
            });
            const orderResult = await orderResponse.json();
            if (!orderResponse.ok) throw new Error(orderResult.error || "Unable to create the order.");
            backendOrder = orderResult.order;
            localStorage.setItem(pendingKey, JSON.stringify({ orderId: backendOrder.id, cartSignature }));
        }

        const paymentResponse = await fetch(`${API_BASE}/payment`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ order_id: backendOrder.id, method: selectedPayment })
        });
        const paymentResult = await paymentResponse.json();
        if (!paymentResponse.ok) throw new Error(paymentResult.error || "Unable to record payment.");
        backendOrder = paymentResult.order;
        localStorage.removeItem(pendingKey);
    } catch (error) {
        isSubmittingOrder = false;
        placeOrderButton.disabled = selectedPayment === "upi" && !upiPaymentCompleted;
        placeOrderButton.textContent = selectedPayment === "upi"
            ? (upiPaymentCompleted ? "🛍️ Place Order - UPI Paid" : "Complete UPI Payment First")
            : "🛍️ Place Order - Cash on Delivery";
        alert(`${error.message || "Unable to reach the backend."} Your cart is still saved.`);
        return;
    }

    const order = {
        id: backendOrder.order_code,
        databaseId: backendOrder.id,
        studentId: currentUser.id,
        studentName: currentUser.name || "",
        studentEmail: currentUser.email || "",
        items: JSON.parse(JSON.stringify(cart)),
        subtotal: backendOrder.subtotal,
        deliveryFee: backendOrder.delivery_fee,
        total: backendOrder.total,
        paymentMethod: backendOrder.payment_method,
        paymentStatus: backendOrder.payment_status,
        status: backendOrder.status,
        crowdLevel: crowd.level,
        crowdEmoji: crowd.emoji,
        crowdMessage: crowd.message,
        preparationTime: `${crowd.min}-${crowd.max} minutes`,
        readyTime: readyTime.text,
        readyTimeStart: readyTime.start,
        readyTimeEnd: readyTime.end,
        date: backendOrder.date,
        timestamp: Date.now(),
        demoStep: 1
    };


    /* ================================
       EMPTY CART
    ================================ */

    currentUser.cart = [];


    /* ================================
       SAVE USER
    ================================ */

    saveUser(currentUser);


    /* ================================
       SAVE LAST ORDER
    ================================ */

    localStorage.setItem(
        "campuscrave_last_order",
        JSON.stringify(order)
    );


    /* ================================
       GO TO CONFIRMATION
    ================================ */

    window.location.href =
        "order-confirmation.html";
}


/* ================================
   INITIALIZE
================================ */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        currentUser =
            getCurrentUser();

        if (!currentUser) return;

        loadOrder();

    }
);