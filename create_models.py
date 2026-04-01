#!/usr/bin/env python3
"""
Script to create a subscription-based customer churn prediction model.
Final Version: Fully 13-feature model.
Features: Age, Gender, Tenure, Usage Frequency, Support Calls, 
          Payment Delay, Subscription Type, Contract Length, 
          Total Spend, Last Interaction, AnnualIncome, NumOrders, LastLoginDaysAgo
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

def load_and_prep_data():
    """Load from the enriched dataset or create synthetic if missing."""
    file_path = r'c:\Users\Srinivas\Downloads\customer_churn_dataset-testing-master.csv'
    if os.path.exists(file_path):
        print(f"Loading data from {file_path}...")
        df = pd.read_csv(file_path)
        # Encode categorical features if they are in string format
        if df['Gender'].dtype == object:
            df['Gender'] = df['Gender'].map({'Male': 0, 'Female': 1})
        if 'Subscription Type' in df.columns and df['Subscription Type'].dtype == object:
            df['Subscription Type'] = df['Subscription Type'].map({'Basic': 0, 'Standard': 1, 'Premium': 2})
        if 'Contract Length' in df.columns and df['Contract Length'].dtype == object:
            df['Contract Length'] = df['Contract Length'].map({'Monthly': 0, 'Quarterly': 1, 'Annual': 2})
        df = df.fillna(0)
    else:
        print("Dataset not found. Creating synthetic dataset...")
        np.random.seed(42)
        n_samples = 5000
        data = {
            'CustomerID': np.arange(1001, 1001 + n_samples),
            'Age': np.random.randint(18, 71, n_samples),
            'Gender': np.random.choice([0, 1], n_samples),
            'Tenure': np.random.randint(1, 61, n_samples),
            'Usage Frequency': np.random.randint(1, 31, n_samples),
            'Support Calls': np.random.randint(0, 11, n_samples),
            'Payment Delay': np.random.randint(0, 31, n_samples),
            'Subscription Type': np.random.choice([0, 1, 2], n_samples),
            'Contract Length': np.random.choice([0, 1, 2], n_samples),
            'Total Spend': np.random.uniform(100, 5000, n_samples),
            'Last Interaction': np.random.randint(0, 31, n_samples),
            'AnnualIncome': np.random.randint(20000, 150001, n_samples),
            'NumOrders': np.random.randint(1, 51, n_samples),
            'LastLoginDaysAgo': np.random.randint(0, 61, n_samples),
        }
        df = pd.DataFrame(data)
        cp = 0.2 + 0.2*(df['Payment Delay']>15) + 0.1*(df['Contract Length']==0) - 0.1*(df['AnnualIncome']>80000)
        df['Churn'] = np.random.binomial(1, np.clip(cp,0,1))
    
    return df

def train_models(df):
    """Train the model on all features except ID and Churn."""
    print("Training 13-feature Enhanced Model...")

    # Select features in the precise order for app.py compatibility
    X = df[['Age', 'Gender', 'Tenure', 'Usage Frequency', 'Support Calls', 
            'Payment Delay', 'Subscription Type', 'Contract Length', 
            'Total Spend', 'Last Interaction', 'AnnualIncome', 'NumOrders', 'LastLoginDaysAgo']]
    y = df['Churn']

    print(f"Training with {X.shape[1]} features: {X.columns.tolist()}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = DecisionTreeClassifier(max_depth=10, min_samples_leaf=15, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.3f}")
    
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, 'models/nate_decision_tree.sav')
    
    # Save 13-feature template
    df.head(100).to_csv('ecommerce_template.csv', index=False)
    print("Saved 'models/nate_decision_tree.sav' and 'ecommerce_template.csv'")

if __name__ == "__main__":
    df = load_and_prep_data()
    train_models(df)
