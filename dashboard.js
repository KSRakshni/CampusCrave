const API_BASE = "http://127.0.0.1:5000/api";

const SESSION_KEY = "campuscrave_session";
const USER_KEY = "campuscrave_user";


// =========================================
// GET CURRENT USER
// =========================================

function getCurrentUser() {

    const sessionId = localStorage.getItem(SESSION_KEY);
    const storedUser = localStorage.getItem(USER_KEY);

    if (!sessionId || !storedUser) {
        return null;
    }

    try {

        const user = JSON.parse(storedUser);

        if (String(user.id) !== String(sessionId)) {
            return null;
        }

        return user;

    } catch (error) {

        console.error("Unable to read logged-in user:", error);

        return null;
    }
}


// =========================================
// CURRENT USER
// =========================================

const currentUser = getCurrentUser();


// =========================================
// CHECK LOGIN
// =========================================

if (!currentUser) {

    alert("Please login first.");

    window.location.href = "login.html";

}


// =========================================
// NAVIGATION
// =========================================

function openMenu() {

    window.location.href = "menu.html";
}


function goToCart() {

    window.location.href = "cart.html";
}


function viewOrders() {

    window.location.href = "orders.html";
}


// =========================================
// LOGOUT
// =========================================

function logout() {

    localStorage.removeItem(SESSION_KEY);
    localStorage.removeItem(USER_KEY);

    alert("You have been logged out.");

    window.location.href = "login.html";
}


// =========================================
// LOAD DASHBOARD
// =========================================

async function loadDashboard() {

    if (!currentUser) {
        return;
    }


    // -----------------------------------------
    // USER NAME
    // -----------------------------------------

    const welcomeName =
        document.getElementById("welcomeName");

    if (welcomeName) {

        welcomeName.textContent =
            currentUser.name || "Student";

    }


    const userName =
        document.getElementById("userName");

    if (userName) {

        userName.textContent =
            currentUser.name || "Student";

    }


    const profileName =
        document.getElementById("profileName");

    if (profileName) {

        profileName.textContent =
            currentUser.name || "Student";

    }


    // -----------------------------------------
    // EMAIL
    // -----------------------------------------

    const profileEmail =
        document.getElementById("profileEmail");

    if (profileEmail) {

        profileEmail.textContent =
            currentUser.email || "";

    }


    // -----------------------------------------
    // CART COUNT
    // -----------------------------------------

    const cart =
        currentUser.cart || [];


    const cartCount =
        cart.reduce(
            (total, item) =>
                total + Number(item.quantity || 1),
            0
        );


    const cartElement =
        document.getElementById("cartCount");

    if (cartElement) {

        cartElement.textContent =
            cartCount;

    }


    const dashboardCartElement =
        document.getElementById("dashboardCartCount");

    if (dashboardCartElement) {

        dashboardCartElement.textContent =
            cartCount;

    }


    // -----------------------------------------
    // LOAD DATA FROM FLASK
    // -----------------------------------------

    try {

        const response =
            await fetch(
                `${API_BASE}/dashboard?user_id=${currentUser.id}`
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.error || "Dashboard API error"
            );

        }


        console.log(
            "Dashboard data:",
            data
        );


        // -------------------------------------
        // ORDER COUNT
        // -------------------------------------

        const orderCount =
            document.getElementById("orderCount");

        if (orderCount) {

            orderCount.textContent =
                data.order_count || 0;

        }


        // -------------------------------------
        // RECENT ORDERS
        // -------------------------------------

        loadRecentOrders(
            data.orders || []
        );


        // -------------------------------------
        // RECOMMENDATIONS
        // -------------------------------------

        loadRecommendations(
            data.recommendations || []
        );


    } catch (error) {

        console.error(
            "Dashboard API error:",
            error
        );


        // Use local orders as fallback

        const orders =
            currentUser.orders || [];


        const orderCount =
            document.getElementById("orderCount");

        if (orderCount) {

            orderCount.textContent =
                orders.length;

        }


        loadRecentOrders(orders);

        loadRecommendations([]);

    }


    // -----------------------------------------
    // AI PREDICTION
    // -----------------------------------------

    generatePrediction();

}


// =========================================
// RECENT ORDERS
// =========================================

function loadRecentOrders(orders) {

    const container =
        document.getElementById("recentOrders");


    if (!container) {
        return;
    }


    container.innerHTML = "";


    if (!orders || orders.length === 0) {

        container.innerHTML = `

            <div class="quick-card">

                <div class="quick-icon">
                    📦
                </div>

                <h3>
                    No Recent Orders
                </h3>

                <p>
                    Your recent orders will appear here.
                </p>

                <button
                    type="button"
                    onclick="openMenu()"
                >
                    Order Food →
                </button>

            </div>

        `;

        return;
    }


    const recentOrders =
        [...orders]
            .reverse()
            .slice(0, 3);


    recentOrders.forEach(order => {

        const card =
            document.createElement("div");


        card.className =
            "quick-card";


        const itemNames =
            (order.items || [])
                .map(
                    item =>
                        `${item.name} × ${item.quantity || 1}`
                )
                .join(", ");


        card.innerHTML = `

            <div class="quick-icon">
                📦
            </div>

            <h3>
                Order #${order.id || ""}
            </h3>

            <p>
                ${itemNames || "Food order"}
            </p>

            <p>
                ${order.date || ""}
            </p>

            <p>
                ₹${Number(order.total || 0).toFixed(2)}
            </p>

            <p>
                Status:
                <strong>
                    ${order.status || "Confirmed"}
                </strong>
            </p>

        `;


        container.appendChild(card);

    });

}


// =========================================
// RECOMMENDATIONS
// =========================================

function loadRecommendations(recommendationList) {

    const container =
        document.getElementById("recommendations");


    if (!container) {

        console.error(
            "Recommendation container not found."
        );

        return;
    }


    if (
        !recommendationList ||
        recommendationList.length === 0
    ) {

        container.innerHTML = `

            <div class="quick-card">

                <div class="quick-icon">
                    🍽️
                </div>

                <h3>
                    No recommendations yet
                </h3>

                <p>
                    Order some food and we'll
                    recommend your favorites!
                </p>

                <button
                    type="button"
                    onclick="openMenu()"
                >
                    Browse Menu →
                </button>

            </div>

        `;

        return;
    }


    container.innerHTML = "";


    recommendationList.forEach(
        (item, index) => {

            const card =
                document.createElement("div");


            card.className =
                "quick-card";


            const icon =
                index % 3 === 0
                    ? "🍕"
                    : index % 3 === 1
                        ? "🍔"
                        : "🥪";


            card.innerHTML = `

                <div class="quick-icon">
                    ${icon}
                </div>

                <h3>
                    ${item.name || "Recommended Food"}
                </h3>

                <p>
                    Category:
                    ${item.category || "Food"}
                </p>

                <p>
                    Popularity:
                    ${item.popularity ?? 0}
                </p>

                <button
                    type="button"
                    class="recommendation-order-btn"
                >
                    Order Now →
                </button>

            `;


            const button =
                card.querySelector(
                    ".recommendation-order-btn"
                );


            if (button) {

                button.addEventListener(
                    "click",
                    function () {

                        openMenu();

                    }
                );

            }


            container.appendChild(card);

        }
    );

}


// =========================================
// AI DEMAND PREDICTION
// =========================================

async function generatePrediction() {

    try {

        const response =
            await fetch(
                `${API_BASE}/demand-prediction`
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.error || "Prediction failed"
            );

        }


        console.log(
            "AI Prediction:",
            data
        );


        // Crowd

        const crowdLevel =
            document.getElementById("crowdLevel");

        if (crowdLevel) {

            crowdLevel.textContent =
                data.crowd_level || "Medium";

        }


        // Queue

        const queueTime =
            document.getElementById("queueTime");

        if (queueTime) {

            queueTime.textContent =
                data.estimated_queue ||
                "10 - 15 min";

        }


        // Peak hour

        const peakHour =
            document.getElementById("peakHour");

        if (peakHour) {

            peakHour.textContent =
                data.peak_hour ||
                "12:30 PM";

        }


        // Smart message

        const smartMessage =
            document.getElementById("smartMessage");


        if (smartMessage) {

            if (
                data.crowd_level === "High"
            ) {

                smartMessage.textContent =
                    "The canteen is expected to be crowded. Consider ordering early to avoid longer queues.";

            }

            else if (
                data.crowd_level === "Low"
            ) {

                smartMessage.textContent =
                    "The canteen is expected to have a lower crowd. This is a good time to order.";

            }

            else {

                smartMessage.textContent =
                    "The canteen is expected to have a medium crowd. Consider ordering now to avoid longer queues.";

            }

        }


    } catch (error) {

        console.error(
            "Prediction API error:",
            error
        );


        // Fallback

        const hour =
            new Date().getHours();


        let crowd =
            "Medium";

        let queue =
            "10 - 15 min";


        if (
            hour >= 12 &&
            hour <= 14
        ) {

            crowd =
                "High";

            queue =
                "20 - 30 min";

        }

        else if (
            hour >= 10 &&
            hour < 12
        ) {

            crowd =
                "Low";

            queue =
                "5 - 10 min";

        }


        const crowdLevel =
            document.getElementById("crowdLevel");

        if (crowdLevel) {

            crowdLevel.textContent =
                crowd;

        }


        const queueTime =
            document.getElementById("queueTime");

        if (queueTime) {

            queueTime.textContent =
                queue;

        }

    }

}


// =========================================
// SHOW PREDICTION
// =========================================

function showPrediction(event) {

    if (event) {

        event.stopPropagation();

    }


    generatePrediction();


    const section =
        document.querySelector(
            ".smart-section"
        );


    if (section) {

        section.scrollIntoView({
            behavior: "smooth"
        });

    }

}


// =========================================
// MAKE FUNCTIONS AVAILABLE TO HTML
// =========================================

window.openMenu =
    openMenu;

window.goToCart =
    goToCart;

window.viewOrders =
    viewOrders;

window.logout =
    logout;

window.loadRecommendations =
    loadRecommendations;

window.generatePrediction =
    generatePrediction;

window.showPrediction =
    showPrediction;


// =========================================
// START
// =========================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        loadDashboard();

    }
);