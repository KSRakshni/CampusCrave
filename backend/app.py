"""CampusCrave REST API and SQLite persistence layer."""

from __future__ import annotations

import sqlite3
import sys
import math
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash


# =========================================================
# PROJECT PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[1]

DATABASE_PATH = ROOT / "database" / "canteen.db"

sys.path.insert(0, str(ROOT))


# =========================================================
# ML MODULES
# =========================================================

from ml.demand_prediction import predict_demand
from ml.recommendation import get_user_recommendations
from ml.sentiment_analysis import analyze_sentiment


# =========================================================
# MENU DATA
# =========================================================

MENU_SEED = [

    (
        "Margherita Pizza",
        "Classic tomato, basil, and mozzarella pizza",
        "pizza",
        180
    ),

    (
        "Veg Supreme Pizza",
        "Loaded vegetable and cheese pizza",
        "pizza",
        220
    ),

    (
        "Farmhouse Pizza",
        "Farm-fresh vegetables with mozzarella",
        "pizza",
        240
    ),

    (
        "Paneer Tikka Pizza",
        "Tandoori paneer with peppers and cheese",
        "pizza",
        260
    ),

    (
        "Cheese Burger",
        "Grilled patty with cheese and house sauce",
        "burger",
        120
    ),

    (
        "Veg Burger",
        "Crispy vegetable patty with fresh greens",
        "burger",
        100
    ),

    (
        "Crispy Burger",
        "Crispy patty with lettuce and sauce",
        "burger",
        140
    ),

    (
        "Double Patty Burger",
        "Two patties with cheese and vegetables",
        "burger",
        180
    ),

    (
        "South Indian Meals",
        "Rice, seasonal vegetables, and accompaniments",
        "meal",
        120
    ),

    (
        "Veg Fried Rice",
        "Wok-fried rice with vegetables",
        "meal",
        140
    ),

    (
        "Paneer Biryani",
        "Fragrant rice layered with paneer and spices",
        "meal",
        180
    ),

    (
        "Lemon Rice",
        "South Indian rice with lemon and tempered spices",
        "meal",
        100
    ),

    (
        "Curd Rice",
        "Cooling rice with yogurt and seasoning",
        "meal",
        90
    ),

    (
        "Veg Sandwich",
        "Fresh vegetables in toasted bread",
        "sandwich",
        90
    ),

    (
        "Grilled Cheese Sandwich",
        "Grilled bread with melted cheese",
        "sandwich",
        130
    ),

    (
        "Club Sandwich",
        "Layered sandwich with vegetables and sauces",
        "sandwich",
        150
    ),

    (
        "French Fries",
        "Crispy salted potato fries",
        "snack",
        80
    ),

    (
        "Samosa (2 pcs)",
        "Two crisp pastry parcels with spiced filling",
        "snack",
        40
    ),

    (
        "Veg Puff",
        "Flaky pastry filled with spiced vegetables",
        "snack",
        35
    ),

    (
        "Spring Rolls",
        "Crisp rolls filled with seasoned vegetables",
        "snack",
        120
    ),

    (
        "Cold Coffee",
        "Chilled coffee blended with milk",
        "drink",
        90
    ),

    (
        "Fresh Lime Juice",
        "Fresh lime juice, served chilled",
        "drink",
        60
    ),

    (
        "Mango Milkshake",
        "Mango blended with chilled milk",
        "drink",
        110
    ),

    (
        "Chocolate Brownie",
        "Rich chocolate brownie",
        "dessert",
        90
    ),

    (
        "Vanilla Ice Cream",
        "Classic vanilla ice cream",
        "dessert",
        70
    ),
]


# =========================================================
# DEMO DELIVERY ROUTE
# =========================================================

DEMO_ROUTE = [

    {
        "latitude": 12.9716,
        "longitude": 77.5946
    },

    {
        "latitude": 12.9724,
        "longitude": 77.5960
    },

    {
        "latitude": 12.9738,
        "longitude": 77.5975
    },

    {
        "latitude": 12.9752,
        "longitude": 77.5989
    },

    {
        "latitude": 12.9765,
        "longitude": 77.6008
    },

    {
        "latitude": 12.9774,
        "longitude": 77.6023
    },
]


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def initialize_database():

    """Create all tables and seed the menu only when it is empty."""

    with get_connection() as connection:

        connection.executescript(

            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS menu_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT NOT NULL DEFAULT '',
                category TEXT NOT NULL,
                price REAL NOT NULL CHECK (price >= 0),
                available INTEGER NOT NULL DEFAULT 1
                    CHECK (available IN (0, 1)),
                image_url TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subtotal REAL NOT NULL,
                delivery_fee REAL NOT NULL,
                total REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending Payment',
                payment_method TEXT NOT NULL DEFAULT '',
                payment_status TEXT NOT NULL DEFAULT 'Pending',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                menu_item_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL
                    CHECK (quantity > 0),
                unit_price REAL NOT NULL
                    CHECK (unit_price >= 0),

                FOREIGN KEY (order_id)
                    REFERENCES orders(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (menu_item_id)
                    REFERENCES menu_items(id)
            );

            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                menu_item_id INTEGER,
                rating INTEGER
                    CHECK (
                        rating IS NULL
                        OR rating BETWEEN 1 AND 5
                    ),
                comment TEXT NOT NULL,
                sentiment TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE SET NULL,

                FOREIGN KEY (menu_item_id)
                    REFERENCES menu_items(id)
                    ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                menu_item_id INTEGER NOT NULL,
                score REAL NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (menu_item_id)
                    REFERENCES menu_items(id)
                    ON DELETE CASCADE,

                UNIQUE (user_id, menu_item_id)
            );

            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL UNIQUE,
                method TEXT NOT NULL,
                status TEXT NOT NULL,
                amount REAL NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (order_id)
                    REFERENCES orders(id)
                    ON DELETE CASCADE
            );
            """
        )

        count = connection.execute(
            "SELECT COUNT(*) FROM menu_items"
        ).fetchone()[0]

        if count == 0:

            connection.executemany(

                """
                INSERT INTO menu_items
                (name, description, category, price)
                VALUES (?, ?, ?, ?)
                """,

                MENU_SEED
            )


# =========================================================
# USER JSON
# =========================================================

def user_json(row):

    return {

        "id": row["id"],

        "name": row["name"],

        "email": row["email"]

    }


# =========================================================
# MENU JSON
# =========================================================

def menu_item_json(row):

    return {

        "id": row["id"],

        "name": row["name"],

        "description": row["description"],

        "category": row["category"],

        "price": row["price"],

        "available": bool(
            row["available"]
        ),

        "image_url": row["image_url"],

    }


# =========================================================
# ORDER JSON
# =========================================================

def order_json(connection, order_id):

    row = connection.execute(

        """
        SELECT
            o.*,
            u.name AS user_name,
            u.email AS user_email

        FROM orders o

        JOIN users u
            ON u.id = o.user_id

        WHERE o.id = ?
        """,

        (order_id,)

    ).fetchone()


    if row is None:

        return None


    items = connection.execute(

        """
        SELECT
            oi.menu_item_id,
            m.name,
            m.category,
            oi.quantity,
            oi.unit_price

        FROM order_items oi

        JOIN menu_items m
            ON m.id = oi.menu_item_id

        WHERE oi.order_id = ?

        ORDER BY oi.id
        """,

        (order_id,)

    ).fetchall()


    return {

        "id": row["id"],

        "order_code":
            f"CC{row['id']:06d}",

        "user_id":
            row["user_id"],

        "user_name":
            row["user_name"],

        "user_email":
            row["user_email"],

        "items":
            [dict(item) for item in items],

        "subtotal":
            row["subtotal"],

        "delivery_fee":
            row["delivery_fee"],

        "total":
            row["total"],

        "status":
            row["status"],

        "payment_method":
            row["payment_method"],

        "payment_status":
            row["payment_status"],

        "date":
            row["created_at"],

    }


# =========================================================
# CREATE FLASK APP
# =========================================================

def create_app():

    application = Flask(__name__)

    CORS(application)

    initialize_database()


    # =====================================================
    # HEALTH
    # =====================================================

    @application.get("/api/health")
    def health():

        return jsonify({

            "status": "ok",

            "database":
                str(DATABASE_PATH)

        })


    # =====================================================
    # SIGNUP
    # =====================================================

    @application.post("/api/signup")
    def signup():

        data = request.get_json(
            silent=True
        ) or {}


        name = str(
            data.get("name", "")
        ).strip()


        email = str(
            data.get("email", "")
        ).strip().lower()


        password = str(
            data.get("password", "")
        )


        if (
            not name
            or not email
            or len(password) < 6
        ):

            return jsonify({

                "error":
                    "Name, email, and a password "
                    "of at least 6 characters are required."

            }), 400


        try:

            with get_connection() as connection:

                cursor = connection.execute(

                    """
                    INSERT INTO users
                    (name, email, password_hash)
                    VALUES (?, ?, ?)
                    """,

                    (
                        name,
                        email,
                        generate_password_hash(
                            password,
                            method="pbkdf2:sha256"
                        )
                    )
                )


                user_id = cursor.lastrowid


                row = connection.execute(

                    """
                    SELECT *
                    FROM users
                    WHERE id = ?
                    """,

                    (user_id,)

                ).fetchone()


            return jsonify({

                "message":
                    "Account created successfully.",

                "user":
                    user_json(row)

            }), 201


        except sqlite3.IntegrityError:

            return jsonify({

                "error":
                    "An account with this email already exists."

            }), 409


    # =====================================================
    # LOGIN
    # =====================================================

    @application.post("/api/login")
    def login():

        data = request.get_json(
            silent=True
        ) or {}


        email = str(
            data.get("email", "")
        ).strip().lower()


        password = str(
            data.get("password", "")
        )


        with get_connection() as connection:

            row = connection.execute(

                """
                SELECT *
                FROM users
                WHERE email = ?
                """,

                (email,)

            ).fetchone()


        if (
            row is None
            or not check_password_hash(
                row["password_hash"],
                password
            )
        ):

            return jsonify({

                "error":
                    "Invalid email or password."

            }), 401


        return jsonify({

            "message":
                "Login successful.",

            "user":
                user_json(row)

        })


    # =====================================================
    # GET MENU
    # =====================================================

    @application.get("/api/menu")
    def get_menu():

        category = request.args.get(
            "category"
        )


        with get_connection() as connection:

            if category:

                rows = connection.execute(

                    """
                    SELECT *
                    FROM menu_items

                    WHERE available = 1
                    AND category = ?

                    ORDER BY name
                    """,

                    (category,)

                ).fetchall()

            else:

                rows = connection.execute(

                    """
                    SELECT *
                    FROM menu_items

                    WHERE available = 1

                    ORDER BY id
                    """

                ).fetchall()


        return jsonify([

            menu_item_json(row)

            for row in rows

        ])


    # =====================================================
    # GET SINGLE MENU ITEM
    # =====================================================

    @application.get("/api/menu/<int:item_id>")
    def get_menu_item(item_id):

        with get_connection() as connection:

            row = connection.execute(

                """
                SELECT *
                FROM menu_items

                WHERE id = ?
                AND available = 1
                """,

                (item_id,)

            ).fetchone()


        if row is None:

            return jsonify({

                "error":
                    "Menu item not found."

            }), 404


        return jsonify(
            menu_item_json(row)
        )


    # =====================================================
    # CREATE ORDER
    # =====================================================

    @application.post("/api/orders")
    def create_order():

        data = request.get_json(
            silent=True
        ) or {}


        user_id = data.get(
            "user_id"
        )

        items = data.get(
            "items"
        )


        if (
            not user_id
            or not isinstance(items, list)
            or not items
        ):

            return jsonify({

                "error":
                    "user_id and a non-empty "
                    "items list are required."

            }), 400


        try:

            with get_connection() as connection:

                user_exists = connection.execute(

                    """
                    SELECT 1
                    FROM users
                    WHERE id = ?
                    """,

                    (user_id,)

                ).fetchone()


                if user_exists is None:

                    return jsonify({

                        "error":
                            "User not found."

                    }), 404


                resolved_items = []

                subtotal = 0.0


                for item in items:

                    item_id = item.get(
                        "menu_item_id",
                        item.get("item_id")
                    )


                    quantity = int(
                        item.get(
                            "quantity",
                            0
                        )
                    )


                    if (
                        quantity < 1
                        or quantity > 99
                    ):

                        return jsonify({

                            "error":
                                "Item quantities must "
                                "be between 1 and 99."

                        }), 400


                    if (
                        item_id is None
                        and item.get("name")
                    ):

                        menu_item = connection.execute(

                            """
                            SELECT
                                id,
                                name,
                                category,
                                price

                            FROM menu_items

                            WHERE name = ?
                            AND available = 1
                            """,

                            (item["name"],)

                        ).fetchone()

                    else:

                        menu_item = connection.execute(

                            """
                            SELECT
                                id,
                                name,
                                category,
                                price

                            FROM menu_items

                            WHERE id = ?
                            AND available = 1
                            """,

                            (item_id,)

                        ).fetchone()


                    if menu_item is None:

                        return jsonify({

                            "error":
                                "One or more menu "
                                "items are unavailable."

                        }), 400


                    resolved_items.append(
                        (
                            menu_item,
                            quantity
                        )
                    )


                    subtotal += (
                        menu_item["price"]
                        * quantity
                    )


                delivery_fee = (
                    0.0
                    if subtotal >= 300
                    else 20.0
                )


                cursor = connection.execute(

                    """
                    INSERT INTO orders
                    (
                        user_id,
                        subtotal,
                        delivery_fee,
                        total
                    )

                    VALUES (?, ?, ?, ?)
                    """,

                    (
                        user_id,
                        subtotal,
                        delivery_fee,
                        subtotal + delivery_fee
                    )
                )


                order_id = cursor.lastrowid


                connection.executemany(

                    """
                    INSERT INTO order_items
                    (
                        order_id,
                        menu_item_id,
                        quantity,
                        unit_price
                    )

                    VALUES (?, ?, ?, ?)
                    """,

                    [

                        (
                            order_id,
                            menu_item["id"],
                            quantity,
                            menu_item["price"]
                        )

                        for menu_item, quantity
                        in resolved_items

                    ]
                )


                result = order_json(
                    connection,
                    order_id
                )


            return jsonify({

                "message":
                    "Order created.",

                "order":
                    result

            }), 201


        except (
            TypeError,
            ValueError
        ):

            return jsonify({

                "error":
                    "Each order item must have "
                    "a valid menu item and quantity."

            }), 400


    # =====================================================
    # USER ORDERS
    # =====================================================

    @application.get("/api/orders/user/<int:user_id>")
    def get_user_orders(user_id):

        with get_connection() as connection:

            rows = connection.execute(

                """
                SELECT id
                FROM orders

                WHERE user_id = ?

                ORDER BY id DESC
                """,

                (user_id,)

            ).fetchall()


            orders = [

                order_json(
                    connection,
                    row["id"]
                )

                for row in rows

            ]


        return jsonify(orders)


    # =====================================================
    # SINGLE ORDER
    # =====================================================

    @application.get("/api/orders/<order_id>")
    def get_order(order_id):

        try:

            order_number = int(
                str(order_id).removeprefix("CC")
            )

        except ValueError:

            return jsonify({

                "error":
                    "Invalid order ID."

            }), 400


        with get_connection() as connection:

            order = order_json(
                connection,
                order_number
            )


        if order is None:

            return jsonify({

                "error":
                    "Order not found."

            }), 404


        return jsonify(order)


    # =====================================================
    # ORDER TRACKING
    # =====================================================

    @application.get("/api/orders/<order_id>/tracking")
    def track_order(order_id):

        try:

            order_number = int(
                str(order_id).removeprefix("CC")
            )

        except ValueError:

            return jsonify({

                "error":
                    "Invalid order ID."

            }), 400


        with get_connection() as connection:

            order = order_json(
                connection,
                order_number
            )


        if order is None:

            return jsonify({

                "error":
                    "Order not found."

            }), 404


        try:

            created_at = datetime.fromisoformat(
                order["date"]
            )

        except (
            TypeError,
            ValueError
        ):

            created_at = datetime.now()


        elapsed_seconds = max(

            0.0,

            (
                datetime.now()
                - created_at
            ).total_seconds()

        )


        preparation_seconds = 180

        delivery_seconds = 1800


        delivered = (
            order["status"]
            .strip()
            .lower()
            in {
                "delivered",
                "completed",
                "picked up"
            }
        )


        if delivered:

            stage = "Delivered"

            message = (
                "Your order has been marked delivered."
            )

            progress = 1.0

            eta_minutes = 0


        elif elapsed_seconds >= delivery_seconds:

            stage = "Rider near pickup"

            message = (
                "The demo rider is approaching "
                "the pickup point. Live delivery "
                "confirmation is not connected."
            )

            progress = 0.95

            eta_minutes = 1


        elif elapsed_seconds >= preparation_seconds:

            stage = "Rider on the way"

            message = (
                "Your order is moving along "
                "the demo route."
            )

            progress = (
                0.15
                + 0.8
                * (
                    elapsed_seconds
                    - preparation_seconds
                )
                / (
                    delivery_seconds
                    - preparation_seconds
                )
            )

            eta_minutes = max(

                1,

                math.ceil(
                    (
                        delivery_seconds
                        - elapsed_seconds
                    ) / 60
                )

            )


        else:

            stage = "Preparing your order"

            message = (
                "The canteen is preparing your order. "
                "The rider is waiting nearby."
            )

            progress = (
                0.15
                * elapsed_seconds
                / preparation_seconds
            )

            eta_minutes = math.ceil(

                (
                    delivery_seconds
                    - elapsed_seconds
                ) / 60

            )


        route_position = (
            progress
            * (len(DEMO_ROUTE) - 1)
        )


        segment_index = min(

            int(route_position),

            len(DEMO_ROUTE) - 2

        )


        segment_progress = (
            route_position
            - segment_index
        )


        start = DEMO_ROUTE[
            segment_index
        ]

        end = DEMO_ROUTE[
            segment_index + 1
        ]


        courier = {

            "latitude":
                start["latitude"]
                + (
                    end["latitude"]
                    - start["latitude"]
                )
                * segment_progress,

            "longitude":
                start["longitude"]
                + (
                    end["longitude"]
                    - start["longitude"]
                )
                * segment_progress,

        }


        return jsonify({

            "order_id":
                order["id"],

            "order_code":
                order["order_code"],

            "tracking_status":
                stage,

            "message":
                message,

            "eta_minutes":
                eta_minutes,

            "progress":
                round(progress, 4),

            "courier":
                courier,

            "origin": {

                "name":
                    "Campus Canteen",

                **DEMO_ROUTE[0]

            },

            "destination": {

                "name":
                    "Campus Pickup Point",

                **DEMO_ROUTE[-1]

            },

            "route":
                DEMO_ROUTE,

            "simulated":
                True,

        })


    # =====================================================
    # PAYMENT
    # =====================================================

    @application.post("/api/payment")
    def create_payment():

        data = request.get_json(
            silent=True
        ) or {}


        try:

            order_id = int(

                str(
                    data.get(
                        "order_id",
                        ""
                    )
                ).removeprefix("CC")

            )

        except ValueError:

            return jsonify({

                "error":
                    "A valid order_id is required."

            }), 400


        method = str(

            data.get(
                "method",
                ""
            )

        ).strip().lower()


        if method not in (
            "upi",
            "cash",
            "cash on delivery"
        ):

            return jsonify({

                "error":
                    "Payment method must be UPI or cash."

            }), 400


        payment_status = (
            "Paid"
            if method == "upi"
            else "Pay on Delivery"
        )


        display_method = (
            "UPI"
            if method == "upi"
            else "Cash on Delivery"
        )


        with get_connection() as connection:

            order = connection.execute(

                """
                SELECT *
                FROM orders
                WHERE id = ?
                """,

                (order_id,)

            ).fetchone()


            if order is None:

                return jsonify({

                    "error":
                        "Order not found."

                }), 404


            connection.execute(

                """
                INSERT INTO payments
                (
                    order_id,
                    method,
                    status,
                    amount
                )

                VALUES (?, ?, ?, ?)

                ON CONFLICT(order_id)

                DO UPDATE SET

                    method =
                        excluded.method,

                    status =
                        excluded.status,

                    amount =
                        excluded.amount
                """,

                (
                    order_id,
                    display_method,
                    payment_status,
                    order["total"]
                )

            )


            connection.execute(

                """
                UPDATE orders

                SET
                    payment_method = ?,
                    payment_status = ?,
                    status = 'Confirmed'

                WHERE id = ?
                """,

                (
                    display_method,
                    payment_status,
                    order_id
                )

            )


            result = order_json(
                connection,
                order_id
            )


        return jsonify({

            "message":
                "Payment recorded.",

            "order":
                result,

            "demo_payment":
                True

        })


    # =====================================================
    # FEEDBACK
    # =====================================================

    @application.post("/api/feedback")
    def create_feedback():

        data = request.get_json(
            silent=True
        ) or {}


        comment = str(

            data.get(
                "comment",
                data.get("text", "")
            )

        ).strip()


        if not comment:

            return jsonify({

                "error":
                    "Feedback comment is required."

            }), 400


        user_id = (
            data.get("user_id")
            or None
        )


        item_id = (
            data.get("menu_item_id")
            or None
        )


        rating = data.get(
            "rating"
        )


        if rating is not None:

            try:

                rating = int(
                    rating
                )

            except (
                TypeError,
                ValueError
            ):

                return jsonify({

                    "error":
                        "Rating must be an integer from 1 to 5."

                }), 400


            if not 1 <= rating <= 5:

                return jsonify({

                    "error":
                        "Rating must be an integer from 1 to 5."

                }), 400


        try:

            sentiment = analyze_sentiment(
                comment
            )

        except (
            FileNotFoundError,
            ValueError,
            OSError
        ):

            sentiment = "Neutral"


        try:

            with get_connection() as connection:

                cursor = connection.execute(

                    """
                    INSERT INTO feedback
                    (
                        user_id,
                        menu_item_id,
                        rating,
                        comment,
                        sentiment
                    )

                    VALUES (?, ?, ?, ?, ?)
                    """,

                    (
                        user_id,
                        item_id,
                        rating,
                        comment,
                        sentiment
                    )

                )


                result = connection.execute(

                    """
                    SELECT *
                    FROM feedback
                    WHERE id = ?
                    """,

                    (cursor.lastrowid,)

                ).fetchone()


            return jsonify({

                "message":
                    "Feedback saved.",

                "feedback":
                    dict(result)

            }), 201


        except sqlite3.IntegrityError:

            return jsonify({

                "error":
                    "The supplied user or "
                    "menu item does not exist."

            }), 400


    # =====================================================
    # GET FEEDBACK
    # =====================================================

    @application.get("/api/feedback")
    def get_feedback():

        with get_connection() as connection:

            rows = connection.execute(

                """
                SELECT
                    f.*,
                    u.name AS user_name,
                    m.name AS item_name

                FROM feedback f

                LEFT JOIN users u
                    ON u.id = f.user_id

                LEFT JOIN menu_items m
                    ON m.id = f.menu_item_id

                ORDER BY f.id DESC
                """

            ).fetchall()


        return jsonify([

            dict(row)

            for row in rows

        ])


    # =====================================================
    # RECOMMENDATIONS
    # =====================================================

    @application.get(
        "/api/recommendations/<int:user_id>"
    )
    def recommendations(user_id):

        return jsonify(
            get_user_recommendations(user_id)
        )


    # =====================================================
    # ML DEMAND PREDICTION
    # =====================================================

    @application.get("/api/demand-prediction")
    def demand_prediction():

        item_name = request.args.get(
            "item_name"
        )


        hour = request.args.get(
            "hour",
            type=int
        )


        day = request.args.get(
            "day_of_week"
        )


        # -------------------------------------------------
        # Validate hour
        # -------------------------------------------------

        if (
            hour is not None
            and not 0 <= hour <= 23
        ):

            return jsonify({

                "error":
                    "hour must be between 0 and 23."

            }), 400


        try:

            predictions = predict_demand(

                item_name=item_name,

                hour=hour,

                day_of_week=day

            )


        except ValueError as error:

            return jsonify({

                "error":
                    str(error)

            }), 400


        except FileNotFoundError as error:

            return jsonify({

                "error":
                    str(error)

            }), 500


        except Exception as error:

            print(
                "Demand prediction error:",
                error
            )

            return jsonify({

                "error":
                    "Unable to generate "
                    "demand prediction."

            }), 500


        # -------------------------------------------------
        # TOTAL EXPECTED DEMAND
        # -------------------------------------------------

        expected_total = round(

            sum(

                item["expected_quantity"]

                for item in predictions

            ),

            1

        )


        # -------------------------------------------------
        # CROWD LEVEL
        # -------------------------------------------------

        if expected_total >= 100:

            level = "High"

        elif expected_total >= 50:

            level = "Medium"

        else:

            level = "Low"


        # -------------------------------------------------
        # ESTIMATED QUEUE
        # -------------------------------------------------

        if level == "High":

            queue = "20 - 30 min"

        elif level == "Medium":

            queue = "10 - 15 min"

        else:

            queue = "5 - 10 min"


        # -------------------------------------------------
        # CURRENT HOUR
        # -------------------------------------------------

        current_hour = (

            datetime.now().hour

            if hour is None

            else hour

        )


        # -------------------------------------------------
        # CURRENT DAY
        # -------------------------------------------------

        current_day = (

            day

            if day

            else datetime.now().strftime("%A")

        )


        # -------------------------------------------------
        # PEAK HOUR
        # -------------------------------------------------
        #
        # The current Kaggle model does not contain an
        # "hour" feature. Therefore, it cannot calculate
        # a true ML-based hourly peak.
        #
        # For the current CampusCrave dashboard, we use
        # the normal college lunch peak as an estimate.
        #
        # -------------------------------------------------

        peak_hour = "12:30 PM"


        # -------------------------------------------------
        # API RESPONSE
        # -------------------------------------------------

        return jsonify({
    "crowd_level": level,
    "estimated_queue": queue,
    "expected_total": expected_total,
    "day_of_week": current_day,
    "peak_hour": peak_hour,
    "predictions": predictions
})

    # =====================================================
    # DASHBOARD
    # =====================================================

    @application.get("/api/dashboard")
    def dashboard():

        user_id = request.args.get(
            "user_id",
            type=int
        )


        # -------------------------------------------------
        # ADMIN / GENERAL DASHBOARD
        # -------------------------------------------------

        if user_id is None:

            with get_connection() as connection:

                user_count = connection.execute(

                    """
                    SELECT COUNT(*)
                    FROM users
                    """

                ).fetchone()[0]


                order_count = connection.execute(

                    """
                    SELECT COUNT(*)
                    FROM orders
                    """

                ).fetchone()[0]


                feedback_count = connection.execute(

                    """
                    SELECT COUNT(*)
                    FROM feedback
                    """

                ).fetchone()[0]


            return jsonify({

                "users":
                    user_count,

                "orders":
                    order_count,

                "feedback":
                    feedback_count

            })


        # -------------------------------------------------
        # USER DASHBOARD
        # -------------------------------------------------

        with get_connection() as connection:

            user_row = connection.execute(

                """
                SELECT *
                FROM users
                WHERE id = ?
                """,

                (user_id,)

            ).fetchone()


            if user_row is None:

                return jsonify({

                    "error":
                        "User not found."

                }), 404


            order_rows = connection.execute(

                """
                SELECT id
                FROM orders

                WHERE user_id = ?

                ORDER BY id DESC
                """,

                (user_id,)

            ).fetchall()


            orders = [

                order_json(
                    connection,
                    row["id"]
                )

                for row in order_rows

            ]


        return jsonify({

            "user":
                user_json(user_row),

            "orders":
                orders,

            "order_count":
                len(orders),

            "recommendations":
                get_user_recommendations(user_id)

        })


    # =====================================================
    # RETURN APPLICATION
    # =====================================================

    return application


# =========================================================
# CREATE APP
# =========================================================

app = create_app()


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )