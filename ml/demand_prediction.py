"""CampusCrave food-demand prediction using the trained Random Forest model."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = ROOT / "data" / "CampusCrave_Food_Demand_Dataset copy.xlsx"
MODEL_PATH = ROOT / "ml" / "models" / "demand_model.pkl"

FEATURES = [
    "week",
    "center_id",
    "meal_id",
    "checkout_price",
    "base_price",
    "emailer_for_promotion",
    "homepage_featured",
]


def load_demand_model():
    """Load the trained CampusCrave Random Forest model."""

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained model not found: {MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


def predict_demand(
    item_name: str | None = None,
    hour: int | None = None,
    day_of_week: str | None = None,
):
    """Generate realistic demand predictions for CampusCrave."""

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}"
        )

    # Load dataset
    df = pd.read_excel(
        DATA_PATH,
        sheet_name="CampusCrave Data"
    )

    # Check required columns
    missing = set(FEATURES) - set(df.columns)

    if missing:
        raise ValueError(
            f"Dataset is missing columns: {missing}"
        )

    # Load trained model
    model = load_demand_model()

    # -------------------------------------------------
    # Select representative rows from the dataset
    # -------------------------------------------------

    # Use the most recent week available
    latest_week = df["week"].max()

    current_data = df[
        df["week"] == latest_week
    ].copy()

    # If there are too few rows, use the complete dataset
    if len(current_data) == 0:
        current_data = df.copy()

    # -------------------------------------------------
    # Generate predictions
    # -------------------------------------------------

    prediction_data = current_data[FEATURES].copy()

    predictions = model.predict(prediction_data)

    prediction_data["predicted_orders"] = predictions

    # -------------------------------------------------
    # Group demand by meal
    # -------------------------------------------------

    meal_demand = (
        prediction_data
        .groupby("meal_id")["predicted_orders"]
        .mean()
        .reset_index()
    )

    # Highest-demand meals
    meal_demand = meal_demand.sort_values(
        "predicted_orders",
        ascending=False
    ).head(10)

    results = []

    for _, row in meal_demand.iterrows():

        quantity = max(
            0,
            float(row["predicted_orders"])
        )

        results.append({
            "item_name": f"Meal ID {int(row['meal_id'])}",
            "expected_quantity": round(quantity, 1)
        })

    return results