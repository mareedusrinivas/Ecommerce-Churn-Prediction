# 🛒 ShopChurn AI: Ecommerce Customer Retention Platform

ShopChurn AI is a powerful machine learning application designed to predict customer churn based on behavioral profiles. It features a Flask backend using Scikit-Learn and a modern, high-performance React frontend.

---

## 🚀 Step-by-Step Execution Guide

### 1. Prerequisite: Virtual Environment
First, ensure you have a Python virtual environment set up and all dependencies installed.

```powershell
# Create environment (if not already done)
python -m venv .venv

# Activate environment
.\.venv\Scripts\activate

# Install dependencies
pip install flask flask-cors pandas scikit-learn joblib openpyxl xlrd
```

### 2. Prepare the ML Model
Before running the app, you need to generate the predictive model based on the behavioral features.

```powershell
python create_models.py
```
*This script trains the model and generates `models/nate_decision_tree.sav`.*

### 3. Start the Backend Server (Flask)
Run the main Flask application to handle API requests.

```powershell
python main.py
```
*The backend will be available at `http://127.0.0.1:5000`.*

### 4. Start the Frontend Application (React)
Open a **new terminal window**, navigate to the frontend directory, and start the development server.

```powershell
cd frontend
npm install  # (Only the first time)
npm run dev
```
*The frontend will be available at `http://localhost:5173`.*

---

## 📊 How to Use

### 👤 Individual Customer Analysis
1.  Open the dashboard in your browser.
2.  Fill in the "Customer Behaviour Profile" (Age, Income, Orders, etc.).
3.  Click **"Run Churn Analysis"** to see the churn probability and retention insight.

### 📋 Batch Prediction Engine (Excel/CSV)
1.  Go to the **"Batch Engine"** tab.
2.  Click **"Excel"** or **"CSV"** under "Need sample templates?" to download a correctly formatted data file.
3.  Fill the template with your real customer data (ensuring headers match).
4.  Drag and drop the file into the upload zone.
5.  Click **"Run Batch Churn Analysis"**.
6.  Explore the interactive charts, risk distribution, and sortable prediction table.
7.  Click **"Download CSV"** to export your results back to your local machine.

---

## 🛠️ Tech Stack
- **Backend:** Python, Flask, Pandas, Scikit-Learn
- **Frontend:** React.js, Vite, Vanilla CSS
- **ML Model:** Decision Tree Classifier (trained on behavioral datasets)
