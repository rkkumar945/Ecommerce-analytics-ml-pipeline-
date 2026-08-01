"""
analytics.py
Fetches product data from PostgreSQL, engineers a demand-score target,
trains a Linear Regression model with a proper train/test split, reports
evaluation metrics, and generates an inventory visualization chart.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from decouple import config
from sqlalchemy import create_engine
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error

# 1. Database Connection (credentials from environment, not hardcoded)
DB_USER = config('DB_USER', default='postgres')
DB_PASSWORD = config('DB_PASSWORD')
DB_HOST = config('DB_HOST', default='localhost')
DB_PORT = config('DB_PORT', default='5432')
DB_NAME = config('DB_NAME', default='ecommerce_db')

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

print("Connecting to database for ML forecasting...")

try:
    # 2. Data Fetching
    df_products = pd.read_sql("SELECT * FROM core_product", engine)

    print("\n--- PRODUCT FEATURES ---")
    print(df_products[['title', 'price', 'stock_quantity']])

    if len(df_products) < 5:
        print("\nNot enough rows for a meaningful train/test split "
              "(need at least 5). Add more products to the database.")
    else:
        # 3. Feature engineering
        # NOTE: predicted_demand_score is a synthetic label built from a
        # known formula plus noise, since we don't have real historical
        # sales data. This keeps the pipeline realistic (train/test split,
        # metrics) while being transparent that it is not live sales data.
        rng = np.random.default_rng(42)
        noise = rng.normal(loc=0, scale=2.0, size=len(df_products))
        df_products['predicted_demand_score'] = (
            df_products['price'].astype(float) * 0.1
            + df_products['stock_quantity'].astype(float) * 0.5
            + noise
        )

        X = df_products[['price', 'stock_quantity']].astype(float)
        y = df_products['predicted_demand_score']

        # 4. Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # 5. Model training
        model = LinearRegression()
        model.fit(X_train, y_train)

        # 6. Evaluation
        y_pred = model.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)

        print("\nModel trained successfully.")
        print(f"R^2 score on test set:  {r2:.3f}")
        print(f"MAE on test set:        {mae:.3f}")

        # 7. Prediction for a new hypothetical product
        new_product_features = pd.DataFrame(
            [[25000.0, 40.0]], columns=['price', 'stock_quantity']
        )
        prediction = model.predict(new_product_features)

        print("\n--- PREDICTION FOR A NEW PRODUCT ---")
        print("Price: 25,000 | Stock: 40 units")
        print(f"Predicted demand score: {prediction[0]:.2f}")

    # 8. Chart Generation
    plt.figure(figsize=(8, 5))
    plt.bar(
        df_products['title'],
        df_products['stock_quantity'].astype(int),
        color='skyblue',
        edgecolor='black',
    )
    plt.title('Product Inventory Levels', fontsize=14, fontweight='bold')
    plt.xlabel('Product Title', fontsize=12)
    plt.ylabel('Available Stock Quantity', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('product_stock_chart.png')
    print("\nChart saved to product_stock_chart.png")

except Exception as e:
    print(f"Error: {e}")
