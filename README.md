# CampusCrave

CampusCrave is a campus canteen ordering project. The existing HTML, CSS, and JavaScript frontend remains at the project root; this work adds the Flask API, SQLite persistence, and small machine-learning demonstrations that it can use.

## Components

- `backend/app.py` provides the REST API and creates `database/canteen.db` and its schema on startup. It seeds menu items when the menu table is empty.
- `ml/demand_prediction.py` trains a Random Forest regression pipeline from item, weekday, hour, weekend, and price features.
- `ml/recommendation.py` recommends items from popularity and a user's past order/category frequency.
- `ml/sentiment_analysis.py` uses TF-IDF and Logistic Regression to classify feedback as Positive, Negative, or Neutral.
- `data/` contains compact demonstration datasets. Trained pipelines are saved under `ml/models/` when first needed.

## Technologies

Python, Flask, Flask-CORS, SQLite, pandas, scikit-learn, and joblib. Passwords are stored as Werkzeug password hashes, and database values are passed using parameterized SQL.

## Installation and Running

Python 3.9 or newer is required. From the project root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python backend/app.py
```

The API runs at `http://127.0.0.1:5000`. On its first start it creates `database/canteen.db`, tables, and sample menu entries. To serve the existing root-level frontend, open another terminal in the project root and run:

```sh
python3 -m http.server 8000
```

Then visit `http://127.0.0.1:8000`. Flask-CORS is enabled for local frontend development. The frontend JavaScript uses the local API at `http://127.0.0.1:5000`.

## API

All request and response bodies are JSON unless noted.

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/signup` | Create an account from `name`, `email`, `password` |
| POST | `/api/login` | Verify `email` and `password` |
| GET | `/api/menu` | List available menu items; optional `?category=pizza` |
| GET | `/api/menu/<id>` | Read one menu item |
| POST | `/api/orders` | Create an order from `user_id` and `items` (`menu_item_id`, `quantity`) |
| GET | `/api/orders/user/<user_id>` | List a user's orders |
| GET | `/api/orders/<order_id>` | Read one order; accepts numeric ID or `CC` order code |
| GET | `/api/orders/<order_id>/tracking` | Demo rider coordinates, route progress, status, and ETA |
| GET | `/api/orders/<order_id>/tracking` | Demo courier coordinates, route progress, status, and ETA |
| POST | `/api/payment` | Record demo UPI or cash payment for `order_id` |
| POST | `/api/feedback` | Analyze and store `comment`, optional `user_id`, `menu_item_id`, and `rating` |
| GET | `/api/feedback` | List stored feedback with detected sentiment |
| GET | `/api/recommendations/<user_id>` | List recommendations based on order history/popularity |
| GET | `/api/demand-prediction` | Predict item quantities; optional `item_name`, `hour`, `day_of_week` |
| GET | `/api/dashboard` | Aggregate counts; optional `?user_id=<id>` returns that user's orders and recommendations |

The UPI option is a local demonstration and does not contact a payment processor. The frontend's "Payment Done" action records the demo payment in SQLite; it must not be treated as a real payment confirmation.

The order-confirmation page shows a Leaflet/OpenStreetMap demo route and polls the tracking endpoint every 15 seconds. Rider coordinates and ETA are simulated from order creation time and a sample route; real driver tracking requires a rider app or device to send GPS updates.

The order-confirmation page shows a Leaflet/OpenStreetMap demo route and polls the tracking endpoint every 15 seconds. Rider coordinates and ETA are simulated from order creation time and a sample route; real driver tracking requires a rider app or device to send GPS updates.

## Database Tables

`users`, `menu_items`, `orders`, `order_items`, `payments`, `feedback`, and `recommendations`. Foreign keys are enabled on each SQLite connection; order items and related records reference their owning rows.

## Machine Learning

Demand predictions use the small `data/food_demand.csv` history and are saved as `ml/models/demand_model.pkl`. If the demand file is missing, the module creates a small demonstration dataset. Recommendations combine personal item/category frequency with overall order popularity; new users receive popular items. Feedback predictions use `data/feedback.csv` and persist the TF-IDF/logistic-regression pipeline as `ml/models/sentiment_model.pkl`.

The sample datasets and resulting models are for demonstration and coursework, not production forecasting, recommendations, or payment processing.