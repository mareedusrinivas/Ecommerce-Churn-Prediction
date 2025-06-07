import os
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import joblib
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")

# Configuration
UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB max file size

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Load saved models
try:
    dt_model = joblib.load('models/nate_decision_tree.sav')
    knn_model = joblib.load('models/nate_knn.sav')
    lr_model = joblib.load('models/nate_logistic_regression.sav')
    rf_model = joblib.load('models/nate_random_forest.sav')
    svm_model = joblib.load('models/SVM_model.sav')
    
    # Dictionary of all loaded models
    loaded_models = {
        'dt': dt_model,
        'knn': knn_model,
        'lr': lr_model,
        'rf': rf_model,
        'svm': svm_model,
    }
    
    model_names = {
        'dt': 'Decision Tree',
        'knn': 'K-nearest Neighbors',
        'lr': 'Logistic Regression',
        'rf': 'Random Forest',
        'svm': 'SVM'
    }
    
    logging.info("All models loaded successfully")
except Exception as e:
    logging.error(f"Error loading models: {e}")
    loaded_models = {}
    model_names = {}

# Expected column order for the models
EXPECTED_COLUMNS = [
    'CreditScore', 'Geography', 'Gender', 'Age', 'Tenure', 
    'Balance', 'NumOfProducts', 'HasCrCard', 'IsActiveMember', 'EstimatedSalary'
]

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def decode(pred):
    """Function to decode predictions"""
    if pred == 1: 
        return 'Customer Exits'
    else: 
        return 'Customer Stays'

def validate_excel_data(df):
    """Validate Excel data structure"""
    errors = []
    
    # Check if all required columns are present
    missing_cols = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing_cols:
        errors.append(f"Missing required columns: {', '.join(missing_cols)}")
    
    # Check for empty dataframe
    if df.empty:
        errors.append("Excel file is empty")
    
    # Check data types and ranges
    try:
        if 'CreditScore' in df.columns:
            if not df['CreditScore'].between(300, 850).all():
                errors.append("CreditScore must be between 300 and 850")
        
        if 'Age' in df.columns:
            if not df['Age'].between(18, 100).all():
                errors.append("Age must be between 18 and 100")
        
        if 'Geography' in df.columns:
            valid_geo = ['France', 'Germany', 'Spain']
            if not df['Geography'].isin(valid_geo).all():
                errors.append(f"Geography must be one of: {', '.join(valid_geo)}")
        
        if 'Gender' in df.columns:
            valid_gender = ['Male', 'Female']
            if not df['Gender'].isin(valid_gender).all():
                errors.append(f"Gender must be one of: {', '.join(valid_gender)}")
                
    except Exception as e:
        errors.append(f"Data validation error: {str(e)}")
    
    return errors

def preprocess_batch_data(df):
    """Preprocess batch data for model prediction"""
    try:
        # Create a copy to avoid modifying original
        processed_df = df.copy()
        
        # Handle geography encoding - check if already numeric or needs mapping
        if processed_df['Geography'].dtype == 'object':
            geo_map = {'France': 0, 'Germany': 1, 'Spain': 2}
            processed_df['Geography'] = processed_df['Geography'].map(geo_map)
        
        # Handle gender encoding - check if already numeric or needs mapping
        if processed_df['Gender'].dtype == 'object':
            gender_map = {'Female': 0, 'Male': 1}
            processed_df['Gender'] = processed_df['Gender'].map(gender_map)
        
        # Ensure correct column order
        processed_df = processed_df[EXPECTED_COLUMNS]
        
        # Convert all columns to numeric, handling any remaining string values
        for col in processed_df.columns:
            processed_df[col] = pd.to_numeric(processed_df[col], errors='coerce')
        
        # Fill any NaN values with 0 (fallback for conversion errors)
        processed_df = processed_df.fillna(0)
        
        # Convert to numpy array with float dtype
        return processed_df.astype(float).values
    
    except Exception as e:
        logging.error(f"Error preprocessing data: {e}")
        raise

@app.route('/')
def home():
    """Home page with both single and batch prediction options"""
    # Initial rendering for single prediction
    result = []
    for key, name in model_names.items():
        result.append({'model': name, 'prediction': ' '})
    
    # Create main dictionary
    maind = {
        'customer': {},
        'predictions': result
    }

    return render_template('index.html', maind=maind)

@app.route('/predict', methods=['POST'])
def predict():
    """Single record prediction (existing functionality)"""
    try:
        # List values received from form
        values = [x for x in request.form.values()]

        # Convert string values to appropriate numeric types
        numeric_values = []
        for i, val in enumerate(values):
            try:
                # Convert to float first, then to int if it's a whole number
                float_val = float(val)
                if float_val.is_integer() and i in [0, 1, 2, 3, 4, 6, 7, 8]:  # Integer columns
                    numeric_values.append(int(float_val))
                else:
                    numeric_values.append(float_val)
            except ValueError:
                numeric_values.append(0)  # Default fallback
        
        # new_array - input to models
        new_array = np.array(numeric_values, dtype=float).reshape(1, -1)
        logging.debug(f"Input array: {new_array}")
        logging.debug(f"Input values: {values}")
        
        # Create customer dictionary for display
        custd = {}
        for k, v in zip(EXPECTED_COLUMNS, values):
            custd[k] = v

        # Convert 1 or 0 to Yes or No for display   
        yn_val = ['HasCrCard', 'IsActiveMember']
        for val in yn_val:
            if custd[val] == '1': 
                custd[val] = 'Yes'
            else: 
                custd[val] = 'No'

        # Loop through loaded models and save predictions
        predl = []
        for key in ['dt', 'knn', 'lr', 'rf', 'svm']:
            if key in loaded_models:
                pred = loaded_models[key].predict(new_array)[0]
                predl.append(decode(pred))
            else:
                predl.append('Model not available')

        result = []
        for i, (key, name) in enumerate(model_names.items()):
            result.append({
                'model': name, 
                'prediction': predl[i] if i < len(predl) else 'N/A'
            })

        # Create main dictionary
        maind = {
            'customer': custd,
            'predictions': result
        }

        flash('Prediction completed successfully!', 'success')
        return render_template('index.html', maind=maind)
        
    except Exception as e:
        logging.error(f"Error in single prediction: {e}")
        flash(f'Error making prediction: {str(e)}', 'error')
        return redirect(url_for('home'))

@app.route('/batch_predict', methods=['POST'])
def batch_predict():
    """Batch prediction from Excel file"""
    try:
        # Check if file was uploaded
        if 'excel_file' not in request.files:
            flash('No file selected', 'error')
            return redirect(url_for('home'))
        
        file = request.files['excel_file']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('home'))
        
        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload .xlsx, .xls, or .csv files only.', 'error')
            return redirect(url_for('home'))
        
        # Save uploaded file
        original_filename = file.filename if file.filename else 'uploaded_file'
        filename = secure_filename(original_filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Read file based on extension
        try:
            file_extension = filename.lower().split('.')[-1]
            if file_extension == 'csv':
                df = pd.read_csv(file_path)
                logging.info(f"Loaded CSV file with {len(df)} rows and {len(df.columns)} columns")
            else:
                df = pd.read_excel(file_path)
                logging.info(f"Loaded Excel file with {len(df)} rows and {len(df.columns)} columns")
        except Exception as e:
            flash(f'Error reading file: {str(e)}', 'error')
            return redirect(url_for('home'))
        
        # Validate data
        validation_errors = validate_excel_data(df)
        if validation_errors:
            flash(f'Validation errors: {"; ".join(validation_errors)}', 'error')
            return redirect(url_for('home'))
        
        # Preprocess data
        try:
            processed_data = preprocess_batch_data(df)
            logging.info(f"Preprocessed data shape: {processed_data.shape}")
        except Exception as e:
            flash(f'Error preprocessing data: {str(e)}', 'error')
            return redirect(url_for('home'))
        
        # Make predictions with all models
        results_df = df.copy()
        
        for key, model in loaded_models.items():
            try:
                predictions = model.predict(processed_data)
                decoded_predictions = [decode(pred) for pred in predictions]
                results_df[f'{model_names[key]}_Prediction'] = decoded_predictions
                logging.info(f"Completed predictions for {model_names[key]}")
            except Exception as e:
                logging.error(f"Error with {model_names[key]}: {e}")
                results_df[f'{model_names[key]}_Prediction'] = 'Error'
        
        # Save results to same format as input file
        file_extension = filename.lower().split('.')[-1]
        if file_extension == 'csv':
            output_filename = f"predictions_{timestamp}_{filename}"
            output_path = os.path.join(app.config['DOWNLOAD_FOLDER'], output_filename)
            try:
                results_df.to_csv(output_path, index=False)
                logging.info(f"Results saved to {output_path}")
            except Exception as e:
                flash(f'Error saving results: {str(e)}', 'error')
                return redirect(url_for('home'))
        else:
            output_filename = f"predictions_{timestamp}_{filename}"
            output_path = os.path.join(app.config['DOWNLOAD_FOLDER'], output_filename)
            try:
                with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                    results_df.to_excel(writer, index=False, sheet_name='Predictions')
                logging.info(f"Results saved to {output_path}")
            except Exception as e:
                flash(f'Error saving results: {str(e)}', 'error')
                return redirect(url_for('home'))
        
        # Clean up uploaded file
        try:
            os.remove(file_path)
        except:
            pass
        
        flash(f'Batch prediction completed! Processed {len(df)} records.', 'success')
        return send_file(output_path, as_attachment=True, download_name=output_filename)
        
    except Exception as e:
        logging.error(f"Error in batch prediction: {e}")
        flash(f'Error processing file: {str(e)}', 'error')
        return redirect(url_for('home'))

@app.route('/download_template')
@app.route('/download_template/<format>')
def download_template(format='excel'):
    """Download template file in Excel or CSV format"""
    try:
        # Create template DataFrame with more realistic sample data
        template_data = {
            'CreditScore': [619, 608, 502, 699, 850, 645, 822, 376, 501, 684],
            'Geography': ['France', 'Spain', 'France', 'Germany', 'Spain', 'Germany', 'France', 'Germany', 'Spain', 'France'],
            'Gender': ['Female', 'Female', 'Female', 'Female', 'Male', 'Male', 'Male', 'Female', 'Male', 'Male'],
            'Age': [42, 41, 42, 39, 43, 44, 50, 29, 44, 27],
            'Tenure': [2, 1, 8, 1, 4, 8, 7, 4, 4, 2],
            'Balance': [0.00, 83807.86, 159660.80, 0.00, 125510.82, 113755.78, 0.00, 12551.72, 142051.07, 134603.88],
            'NumOfProducts': [1, 1, 3, 2, 1, 2, 2, 4, 2, 1],
            'HasCrCard': [1, 0, 1, 0, 1, 1, 1, 1, 0, 1],
            'IsActiveMember': [1, 1, 0, 0, 1, 0, 1, 0, 1, 1],
            'EstimatedSalary': [101348.88, 112542.58, 113931.57, 93826.63, 79084.10, 149756.71, 10062.80, 119346.88, 74940.50, 71725.73]
        }
        
        template_df = pd.DataFrame(template_data)
        
        if format.lower() == 'csv':
            # Save CSV template
            template_filename = 'customer_data_template.csv'
            template_path = os.path.join(app.config['DOWNLOAD_FOLDER'], template_filename)
            template_df.to_csv(template_path, index=False)
            
            return send_file(template_path, as_attachment=True, download_name=template_filename)
        else:
            # Save Excel template
            template_filename = 'customer_data_template.xlsx'
            template_path = os.path.join(app.config['DOWNLOAD_FOLDER'], template_filename)
            
            with pd.ExcelWriter(template_path, engine='openpyxl') as writer:
                template_df.to_excel(writer, index=False, sheet_name='Template')
                
                # Add instructions sheet
                instructions = pd.DataFrame({
                    'Instructions': [
                        'Fill in customer data using the template format',
                        'CreditScore: 300-850 (credit score)',
                        'Geography: France, Germany, or Spain',
                        'Gender: Male or Female',
                        'Age: 18-100 (customer age)',
                        'Tenure: 0-10 (years with bank)',
                        'Balance: Account balance (can be 0)',
                        'NumOfProducts: 1-4 (number of bank products)',
                        'HasCrCard: 1 for Yes, 0 for No',
                        'IsActiveMember: 1 for Yes, 0 for No',
                        'EstimatedSalary: Annual salary estimate',
                        '',
                        'Save as CSV or Excel file for batch processing'
                    ]
                })
                instructions.to_excel(writer, index=False, sheet_name='Instructions')
            
            return send_file(template_path, as_attachment=True, download_name=template_filename)
        
    except Exception as e:
        logging.error(f"Error creating template: {e}")
        flash(f'Error creating template: {str(e)}', 'error')
        return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
