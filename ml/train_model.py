import pandas as pd
import joblib
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# Project root folder
ROOT = Path(__file__).resolve().parent.parent


# 1. Load the Kaggle dataset
file_path = ROOT / "data" / "CampusCrave_Food_Demand_Dataset copy.xlsx"

df = pd.read_excel(
    file_path,
    sheet_name="CampusCrave Data"
)

print("Dataset loaded successfully!")
print("Number of rows:", len(df))
print("Columns:", list(df.columns))


# 2. Select the features
features = [
    "week",
    "center_id",
    "meal_id",
    "checkout_price",
    "base_price",
    "emailer_for_promotion",
    "homepage_featured"
]

X = df[features]

# Target variable
y = df["num_orders"]


# 3. Split the data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# 4. Create the Random Forest model
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)


# 5. Train the model
print("\nTraining CampusCrave model...")

model.fit(X_train, y_train)

print("Model training completed!")


# 6. Make predictions
predictions = model.predict(X_test)


# 7. Evaluate the model
mae = mean_absolute_error(y_test, predictions)
mse = mean_squared_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

print("\n-----------------------------")
print("CampusCrave Model Performance")
print("-----------------------------")
print("MAE:", round(mae, 2))
print("MSE:", round(mse, 2))
print("R2 Score:", round(r2, 2))


# 8. Save the trained model
model_path = ROOT / "ml" / "models" / "demand_model.pkl"

# Make sure the models folder exists
model_path.parent.mkdir(parents=True, exist_ok=True)

joblib.dump(model, model_path)

print("\nModel saved successfully!")
print("Saved as:", model_path)