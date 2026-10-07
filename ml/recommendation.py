"""Explainable item recommendations using order frequency and category affinity."""

from __future__ import annotations

import csv
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ORDERS_CSV = ROOT / "data" / "orders.csv"
DATABASE_PATH = ROOT / "database" / "canteen.db"


def _csv_history():
    history = []
    if ORDERS_CSV.exists():
        with ORDERS_CSV.open(newline="", encoding="utf-8") as source:
            history.extend(csv.DictReader(source))
    return history


def get_user_recommendations(user_id, db_path: str | Path = DATABASE_PATH, limit: int = 5):
    """Rank available menu items using user category affinity and popularity."""
    popularity = Counter()
    item_categories = {}
    user_counts = Counter()
    category_counts = Counter()
    database = Path(db_path)
    if database.exists():
        with sqlite3.connect(database) as connection:
            connection.row_factory = sqlite3.Row
            items = connection.execute(
                "SELECT id, name, category FROM menu_items WHERE available = 1"
            ).fetchall()
            item_categories = {row["name"]: row["category"] for row in items}
            user_rows = connection.execute(
                "SELECT m.name, m.category, SUM(oi.quantity) AS quantity "
                "FROM orders o JOIN order_items oi ON oi.order_id = o.id "
                "JOIN menu_items m ON m.id = oi.menu_item_id "
                "WHERE o.user_id = ? GROUP BY m.id, m.category",
                (user_id,),
            ).fetchall()
            for row in user_rows:
                user_counts[row["name"]] += row["quantity"] or 0
                category_counts[row["category"]] += row["quantity"] or 0
            popular_rows = connection.execute(
                "SELECT m.name, m.category, COALESCE(SUM(oi.quantity), 0) AS quantity "
                "FROM menu_items m LEFT JOIN order_items oi ON oi.menu_item_id = m.id "
                "LEFT JOIN orders o ON o.id = oi.order_id "
                "WHERE m.available = 1 GROUP BY m.id"
            ).fetchall()
            for row in popular_rows:
                popularity[row["name"]] += row["quantity"] or 0
    else:
        for row in _csv_history():
            item_categories[row["item_name"]] = row["category"]
            popularity[row["item_name"]] += int(row.get("quantity", 1) or 1)
            if str(row.get("user_id")) == str(user_id):
                user_counts[row["item_name"]] += int(row.get("quantity", 1) or 1)
                category_counts[row["category"]] += int(row.get("quantity", 1) or 1)

    if not item_categories:
        for row in _csv_history():
            item_categories[row["item_name"]] = row["category"]
            popularity[row["item_name"]] += int(row.get("quantity", 1) or 1)

    if not any(popularity.values()):
        for row in _csv_history():
            item_categories.setdefault(row["item_name"], row["category"])
            popularity[row["item_name"]] += int(row.get("quantity", 1) or 1)

    affinity = defaultdict(float)
    for item, count in user_counts.items():
        affinity[item] += count * 2.0
    for item, category in item_categories.items():
        affinity[item] += category_counts[category] * 0.35
    ranked = sorted(
        (name for name in item_categories if name not in user_counts),
        key=lambda name: (affinity[name], popularity[name], name),
        reverse=True,
    )
    return [
        {"name": name, "category": item_categories[name], "popularity": int(popularity[name])}
        for name in ranked[:max(0, limit)]
    ]