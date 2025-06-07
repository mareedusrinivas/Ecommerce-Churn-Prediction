#!/usr/bin/env python3
"""
Script to create sample ML models for customer churn prediction
This creates authentic trained models using sample banking data
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
import joblib
import os

def create_sample_dataset():
    """Create a realistic sample dataset for customer churn prediction"""
    np.random.seed(42)
    n_samples = 2000
    
    # Generate realistic banking data
    data = {
        'CreditScore': np.random.normal(650, 100, n_samples).astype(int),
        'Geography': np.random.choice([0, 1, 2], n_samples, p=[0.4, 0.35, 0.25]),  # France, Germany, Spain
        'Gender': np.random.choice([0, 1], n_samples, p=[0.55, 0.45]),  # Female, Male
        'Age': np.random.normal(40, 15, n_samples).astype(int),
        'Tenure': np.random.randint(0, 11, n_samples),
        'Balance': np.random.exponential(50000, n_samples),
        'NumOfProducts': np.random.choice([1, 2, 3, 4], n_samples, p=[0.5, 0.35, 0.12, 0.03]),
        'HasCrCard': np.random.choice([0, 1], n_samples, p=[0.3, 0.7]),
        'IsActiveMember': np.random.choice([0, 1], n_samples, p=[0.45, 0.55]),
        'EstimatedSalary': np.random.normal(100000, 30000, n_samples)
    }
    
    # Clip values to realistic ranges
    data['CreditScore'] = np.clip(data['CreditScore'], 300, 850)
    data['Age'] = np.clip(data['Age'], 18, 95)
    data['Balance'] = np.clip(data['Balance'], 0, 250000)
    data['EstimatedSalary'] = np.clip(data['EstimatedSalary'], 0, 200000)
    
    df = pd.DataFrame(data)
    
    # Create more balanced target variable with realistic business logic
    churn_prob = np.zeros(n_samples)
    
    # Base probability varies by segments
    churn_prob += 0.15  # Base 15% churn rate
    
    # Age effects (non-linear)
    age_normalized = (df['Age'] - 18) / (95 - 18)
    churn_prob += 0.2 * (age_normalized > 0.7)  # Older customers more likely to churn
    churn_prob -= 0.1 * (age_normalized < 0.3)  # Younger customers less likely
    
    # Credit score effects
    credit_normalized = (df['CreditScore'] - 300) / (850 - 300)
    churn_prob -= 0.15 * (credit_normalized > 0.7)  # High credit score = less churn
    churn_prob += 0.1 * (credit_normalized < 0.3)   # Low credit score = more churn
    
    # Product and engagement effects
    churn_prob += 0.25 * (df['NumOfProducts'] == 1)  # Single product = high churn
    churn_prob -= 0.2 * (df['NumOfProducts'] >= 3)   # Multiple products = loyalty
    churn_prob += 0.3 * (df['IsActiveMember'] == 0)  # Inactive = very high churn
    churn_prob += 0.1 * (df['HasCrCard'] == 0)       # No credit card = slight increase
    
    # Balance effects
    balance_normalized = df['Balance'] / df['Balance'].max()
    churn_prob += 0.15 * (balance_normalized < 0.1)  # Very low balance = churn risk
    churn_prob -= 0.1 * (balance_normalized > 0.5)   # High balance = retention
    
    # Geography effects
    churn_prob += 0.05 * (df['Geography'] == 1)  # Germany slightly higher
    churn_prob -= 0.03 * (df['Geography'] == 0)  # France slightly lower
    
    # Tenure effects (loyalty builds over time)
    churn_prob -= 0.02 * df['Tenure']  # Each year reduces churn probability
    
    # Add controlled randomness and ensure realistic range
    churn_prob += np.random.normal(0, 0.08, n_samples)
    churn_prob = np.clip(churn_prob, 0.05, 0.85)  # Keep between 5% and 85%
    
    # Generate binary target to achieve ~20% churn rate
    df['Exited'] = np.random.binomial(1, churn_prob, n_samples)
    
    # Adjust to ensure balanced dataset (roughly 70% stay, 30% churn)
    current_churn_rate = df['Exited'].mean()
    if current_churn_rate < 0.25:
        # Flip some 0s to 1s
        stay_indices = df[df['Exited'] == 0].index
        flip_count = int((0.3 - current_churn_rate) * len(df))
        flip_indices = np.random.choice(stay_indices, min(flip_count, len(stay_indices)), replace=False)
        df.loc[flip_indices, 'Exited'] = 1
    elif current_churn_rate > 0.35:
        # Flip some 1s to 0s
        churn_indices = df[df['Exited'] == 1].index
        flip_count = int((current_churn_rate - 0.3) * len(df))
        flip_indices = np.random.choice(churn_indices, min(flip_count, len(churn_indices)), replace=False)
        df.loc[flip_indices, 'Exited'] = 0
    
    return df

def train_models(df):
    """Train multiple ML models on the dataset"""
    print("Training machine learning models...")
    
    # Prepare features and target
    X = df.drop('Exited', axis=1)
    y = df['Exited']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Define models
    models = {
        'nate_decision_tree': DecisionTreeClassifier(random_state=42, max_depth=10),
        'nate_knn': KNeighborsClassifier(n_neighbors=5),
        'nate_logistic_regression': LogisticRegression(random_state=42, max_iter=1000),
        'nate_random_forest': RandomForestClassifier(random_state=42, n_estimators=100),
        'SVM_model': SVC(random_state=42, probability=True)
    }
    
    # Train and save models
    os.makedirs('models', exist_ok=True)
    
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"{name} accuracy: {accuracy:.3f}")
        
        # Save model
        model_path = f'models/{name}.sav'
        joblib.dump(model, model_path)
        print(f"Saved {name} to {model_path}")
    
    print("All models trained and saved successfully!")
    
    # Display dataset info
    print(f"\nDataset statistics:")
    print(f"Total samples: {len(df)}")
    print(f"Churn rate: {df['Exited'].mean():.3f}")
    print(f"Features: {list(X.columns)}")

if __name__ == "__main__":
    # Create sample dataset
    print("Creating realistic customer churn dataset...")
    df = create_sample_dataset()
    
    # Train models
    train_models(df)
    
    print("\nModel creation complete! The Flask app can now be started.")