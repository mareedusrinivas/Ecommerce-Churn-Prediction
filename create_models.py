#!/usr/bin/env python3
"""
Script to create an ecommerce customer churn prediction model.
Features: CustomerID, Age, Gender, AnnualIncome, SpendingScore, 
          TenureMonths, NumOrders, AvgOrderValue, LastLoginDaysAgo, IsActiveMember
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

def create_sample_dataset():
    """Create a dataset based on the user's requested features."""
    np.random.seed(42)
    n_samples = 5000

    # --- Feature Generation ---
    data = {
        'CustomerID': np.arange(1001, 1001 + n_samples),
        'Age': np.random.randint(18, 71, n_samples),
        'Gender': np.random.choice([0, 1], n_samples), # 0=Male, 1=Female
        'AnnualIncome': np.random.randint(20000, 150001, n_samples),
        'SpendingScore': np.random.randint(1, 101, n_samples),
        'TenureMonths': np.random.randint(0, 121, n_samples),
        'NumOrders': np.random.randint(1, 51, n_samples),
        'AvgOrderValue': np.random.uniform(10, 500, n_samples),
        'LastLoginDaysAgo': np.random.randint(0, 61, n_samples),
        'IsActiveMember': np.random.choice([0, 1], n_samples, p=[0.4, 0.6]),
    }

    df = pd.DataFrame(data)

    # --- Realistic Churn Logic ---
    # Churn probability calculation
    cp = np.zeros(n_samples)
    cp += 0.20 # Base churn

    # Low activity/engagement increases churn
    cp += 0.25 * (df['LastLoginDaysAgo'] > 30)
    cp += 0.15 * (df['IsActiveMember'] == 0)
    
    # Low tenure = higher risk (haven't formed habit)
    cp += 0.15 * (df['TenureMonths'] < 12)
    cp -= 0.10 * (df['TenureMonths'] > 60)

    # Low value / low loyalty
    cp += 0.10 * (df['NumOrders'] < 3)
    cp -= 0.10 * (df['SpendingScore'] > 80)
    
    # Younger users often have higher churn in some ecommerce segments
    cp += 0.05 * (df['Age'] < 25)
    
    # Add noise
    cp += np.random.normal(0, 0.1, n_samples)
    cp = np.clip(cp, 0, 1)

    df['Churn'] = np.random.binomial(1, cp, n_samples)

    # Final churn rate check (~25-30%)
    print(f"Initial Churn Rate: {df['Churn'].mean():.2%}")
    
    return df

def train_models(df):
    """Train the model excluding ID and Target."""
    print("Training Ecommerce Churn Model...")

    # Drop CustomerID for training as it's just an identifier
    X = df.drop(['CustomerID', 'Churn'], axis=1)
    y = df['Churn']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Use a simpler DT to avoid overfitting on synthetic data
    model = DecisionTreeClassifier(
        max_depth=10,
        min_samples_leaf=15,
        random_state=42
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.3f}")
    print(classification_report(y_test, y_pred))

    os.makedirs('models', exist_ok=True)
    joblib.dump(model, 'models/nate_decision_tree.sav')
    
    # Save a CSV with the headers for the user to use as a template
    df.head(100).to_csv('ecommerce_template.csv', index=False)
    print("Saved training model and 'ecommerce_template.csv'")

if __name__ == "__main__":
    df = create_sample_dataset()
    train_models(df)
