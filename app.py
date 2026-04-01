import os
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template, send_file, flash, redirect, url_for, session
from werkzeug.utils import secure_filename
from flask_cors import CORS
import joblib
from datetime import datetime
import logging
import json
from werkzeug.security import generate_password_hash, check_password_hash

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")

# ─── Configuration ────────────────────────────────────────────────────────────
UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'
USER_DATA_FILE = 'users.json'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16 MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

if not os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump({}, f)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# ─── Ecommerce Feature Columns (must match model training order) ──────────────
EXPECTED_COLUMNS = [
    'Age',
    'Gender',
    'Tenure',
    'Usage Frequency',
    'Support Calls',
    'Payment Delay',
    'Subscription Type',
    'Contract Length',
    'Total Spend',
    'Last Interaction',
    'AnnualIncome',
    'NumOrders',
    'LastLoginDaysAgo',
]

# ─── Load Model ───────────────────────────────────────────────────────────────
try:
    dt_model = joblib.load('models/nate_decision_tree.sav')
    logging.info("Ecommerce Decision Tree model loaded successfully.")
    model_loaded = True
except Exception as e:
    logging.error(f"Error loading model: {e}")
    dt_model = None
    model_loaded = False


# ─── Helpers ──────────────────────────────────────────────────────────────────
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def decode(pred):
    return 'Customer Churns' if pred == 1 else 'Customer Stays'


def get_confidence(pred_proba):
    confidence = max(pred_proba) * 100
    if confidence >= 80:
        return "High"
    elif confidence >= 60:
        return "Medium"
    return "Low"


def validate_data(df):
    errors = []
    # Normalize expected and actual columns to ignore spaces, underscores, and case
    norm_expected = [c.replace(' ', '').replace('_', '').lower() for c in EXPECTED_COLUMNS]
    norm_actual = [str(c).replace(' ', '').replace('_', '').lower() for c in df.columns]
    
    missing = []
    for i, exp in enumerate(norm_expected):
        if exp not in norm_actual:
            missing.append(EXPECTED_COLUMNS[i])

    if missing:
        errors.append(f"Missing columns: {', '.join(missing)}")
    if df.empty:
        errors.append("File is empty.")

    return errors


def preprocess_data(df):
    try:
        # Build normalized column mapping for flexible matching
        norm_map = {str(c).replace(' ', '').replace('_', '').lower(): c for c in df.columns}
        
        # Build DataFrame with correct column order for model
        processed_data = []
        for exp in EXPECTED_COLUMNS:
            norm_exp = exp.replace(' ', '').replace('_', '').lower()
            orig_col = norm_map.get(norm_exp)
            if orig_col:
                processed_data.append(pd.to_numeric(df[orig_col], errors='coerce'))
            else:
                # If optional but missing, fallback to 0
                processed_data.append(pd.Series([0] * len(df)))
                
        processed = pd.concat(processed_data, axis=1)
        processed.columns = EXPECTED_COLUMNS
        processed = processed.fillna(0)
        return processed.astype(float).values
    except Exception as e:
        logging.error(f"Preprocessing error: {e}")
        raise


# ─── File reading helper (robust, magic-byte aware) ───────────────────────────
def read_uploaded_file(file_path, ext):
    """
    Read a CSV or Excel file robustly.
    Detects the actual file format from magic bytes rather than trusting
    the extension, so renamed or re-uploaded files still work correctly.
    Also strips any extra prediction columns (from previous output files)
    so re-uploading a predictions file works cleanly.
    """
    # 1. Read magic bytes to detect real format
    with open(file_path, 'rb') as f:
        magic = f.read(8)

    # PK header = ZIP = xlsx/xlsm
    is_zip  = magic[:2] == b'PK'
    # D0 CF 11 E0 = Compound Document = old-format xls
    is_biff = magic[:8] == b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'
    # Check for HTML
    is_html = magic.startswith(b'<!DOCTYP') or magic.startswith(b'<html>') or magic.startswith(b'<html')

    if is_html:
        raise ValueError("The uploaded file is an HTML (web) page, not an Excel or CSV file. "
                         "This usually happens when a download link fails and returns an error page instead of the file.")

    def _strip_extra_cols(df):
        """Drop any columns added by previous prediction runs."""
        extra = {'Churn_Prediction', 'Prediction_Confidence', 'Churn_Probability_%'}
        return df.drop(columns=[c for c in extra if c in df.columns], errors='ignore')

    if is_zip or ext == 'xlsx':
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            return _strip_extra_cols(df)
        except Exception as e1:
            logging.warning(f"openpyxl failed ({e1}), trying xlrd …")
            try:
                df = pd.read_excel(file_path, engine='xlrd')
                return _strip_extra_cols(df)
            except Exception as e2:
                raise ValueError(
                    f"Could not read Excel file. openpyxl: {e1} | xlrd: {e2}"
                )

    elif is_biff or ext == 'xls':
        try:
            df = pd.read_excel(file_path, engine='xlrd')
            return _strip_extra_cols(df)
        except Exception as e:
            try:
                df = pd.read_excel(file_path, engine='openpyxl')
                return _strip_extra_cols(df)
            except Exception:
                raise ValueError(f"Could not read .xls file: {e}")

    else:
        # CSV or unknown — try CSV first, then Excel engines
        for enc in ('utf-8-sig', 'utf-8', 'latin-1', 'cp1252'):
            try:
                df = pd.read_csv(file_path, encoding=enc)
                return _strip_extra_cols(df)
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue

        # Last resort: might be an xlsx file with wrong extension
        for engine in ('openpyxl', 'xlrd'):
            try:
                df = pd.read_excel(file_path, engine=engine)
                return _strip_extra_cols(df)
            except Exception:
                continue

        raise ValueError(
            "Could not read the file. Please upload a valid .xlsx, .xls, or .csv file."
        )


# ─── Auth Helpers ──────────────────────────────────────────────────────────────
def get_users():
    with open(USER_DATA_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f, indent=4)


# ─── Routes ───────────────────────────────────────────────────────────────────
@app.route('/')
def home():
    """Simple API status or basic entry page."""
    return jsonify({
        'status': 'online',
        'service': 'Ecommerce Churn Prediction Backend',
        'model_loaded': model_loaded,
        'endpoints': {
            'predict': '/predict_json [POST]',
            'batch': '/batch_predict_json [POST]',
            'template': '/download_template/<format> [GET]'
        }
    })


# ─── Auth API ──────────────────────────────────────────────────────────────────
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    users = get_users()
    if username in users:
        return jsonify({'error': 'User already exists'}), 409

    users[username] = generate_password_hash(password)
    save_users(users)
    return jsonify({'success': 'User registered successfully'}), 200


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    users = get_users()
    if username not in users or not check_password_hash(users[username], password):
        return jsonify({'error': 'Invalid credentials'}), 401

    session['user'] = username
    return jsonify({'success': 'Logged in', 'username': username}), 200


@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'success': 'Logged out'}), 200


@app.route('/api/check_auth')
def check_auth():
    if 'user' in session:
        return jsonify({'authenticated': True, 'username': session['user']}), 200
    return jsonify({'authenticated': False}), 200


@app.route('/predict', methods=['POST'])
def predict():
    """Single record ecommerce churn prediction."""
    try:
        if not model_loaded:
            flash('Model is not available. Please check model files.', 'error')
            return redirect(url_for('home'))

        values = [x for x in request.form.values()]
        numeric_values = []
        for val in values:
            try:
                fv = float(val)
                numeric_values.append(fv)
            except ValueError:
                numeric_values.append(0.0)

        new_array = np.array(numeric_values, dtype=float).reshape(1, -1)
        logging.debug(f"Input array: {new_array}")

        custd = dict(zip(EXPECTED_COLUMNS, values))
        # Convert binary fields for display
        custd['UsesDiscounts'] = 'Yes' if custd.get('UsesDiscounts') == '1' else 'No'
        device_map = {'0': 'Mobile', '1': 'Desktop', '2': 'Tablet'}
        custd['DeviceType'] = device_map.get(custd.get('DeviceType', '0'), 'Mobile')

        prediction = dt_model.predict(new_array)[0]
        prediction_text = decode(prediction)

        try:
            proba = dt_model.predict_proba(new_array)[0]
            confidence = get_confidence(proba)
            probability = round(max(proba) * 100, 1)
        except Exception:
            confidence = "Unknown"
            probability = 0

        result = {
            'prediction': prediction_text,
            'confidence': confidence,
            'probability': probability,
            'customer': custd
        }

        flash('Prediction completed successfully!', 'success')
        return render_template('index.html', result=result, model_loaded=model_loaded)

    except Exception as e:
        logging.error(f"Single prediction error: {e}")
        flash(f'Error making prediction: {str(e)}', 'error')
        return redirect(url_for('home'))


@app.route('/predict_json', methods=['POST'])
def predict_json():
    """JSON API endpoint for React frontend single prediction."""
    try:
        if not model_loaded:
            return jsonify({'error': 'Model not loaded'}), 503

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        row = [float(data.get(col, 0)) for col in EXPECTED_COLUMNS]
        new_array = np.array(row, dtype=float).reshape(1, -1)

        global dt_model
        try:
            prediction = dt_model.predict(new_array)[0]
            proba = dt_model.predict_proba(new_array)[0]
        except ValueError as ve:
            if "expecting" in str(ve) or "features" in str(ve):
                logging.warning("Model mismatch! Reloading model...")
                dt_model = joblib.load('models/nate_decision_tree.sav')
                prediction = dt_model.predict(new_array)[0]
                proba = dt_model.predict_proba(new_array)[0]
            else: raise ve

        prediction_text = decode(prediction)
        confidence = get_confidence(proba)
        probability = round(max(proba) * 100, 1)

        return jsonify({
            'prediction': prediction_text,
            'churns': bool(prediction == 1),
            'confidence': confidence,
            'probability': probability,
        })

    except Exception as e:
        logging.error(f"JSON prediction error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/batch_predict_json', methods=['POST'])
def batch_predict_json():
    """Batch prediction returning full JSON for React graphical dashboard."""
    try:
        if not model_loaded:
            return jsonify({'error': 'Model not loaded'}), 503

        if 'excel_file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['excel_file']
        if not file or file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        filename = secure_filename(file.filename or 'upload')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{timestamp}_{filename}")
        file.save(file_path)

        ext = filename.lower().rsplit('.', 1)[-1]
        try:
            df = read_uploaded_file(file_path, ext)
        except Exception as e:
            return jsonify({'error': f'Error reading file: {str(e)}'}), 400
        finally:
            try: os.remove(file_path)
            except: pass

        errors = validate_data(df)
        if errors:
            return jsonify({'error': '; '.join(errors)}), 400

        processed = preprocess_data(df)
        
        # Self-healing reload if feature mismatch
        global dt_model
        try:
            predictions = dt_model.predict(processed)
            probas = dt_model.predict_proba(processed)
        except ValueError as ve:
            if "expecting" in str(ve) or "features" in str(ve):
                logging.warning("Batch model mismatch! Hot-reloading...")
                dt_model = joblib.load('models/nate_decision_tree.sav')
                predictions = dt_model.predict(processed)
                probas = dt_model.predict_proba(processed)
            else: raise ve

        # Build per-row results
        rows = []
        for i, (pred, proba) in enumerate(zip(predictions, probas)):
            churn_prob = round(float(max(proba)) * 100, 1) if pred == 1 else round(float(proba[1]) * 100, 1)
            rows.append({
                'id': i + 1,
                'customerID': int(df.iloc[i].get('CustomerID', 0)),
                'prediction': decode(pred),
                'churns': bool(pred == 1),
                'probability': round(float(proba[1]) * 100, 1),
                'confidence': get_confidence(proba),
                'age': int(df.iloc[i].get('Age', 0)),
                'tenure': int(df.iloc[i].get('Tenure', 0)),
                'totalSpend': float(df.iloc[i].get('Total Spend', 0)),
                'annualIncome': float(df.iloc[i].get('AnnualIncome', 0)),
                'numOrders': int(df.iloc[i].get('NumOrders', 0)),
                'lastLogin': int(df.iloc[i].get('LastLoginDaysAgo', 0)),
            })

        total = len(rows)
        churned = sum(1 for r in rows if r['churns'])
        stays = total - churned
        avg_prob = round(sum(r['probability'] for r in rows) / total, 1) if total else 0

        # Confidence breakdown
        conf_counts = {'High': 0, 'Medium': 0, 'Low': 0}
        for r in rows:
            conf_counts[r['confidence']] = conf_counts.get(r['confidence'], 0) + 1

        # Risk buckets (0-25, 25-50, 50-75, 75-100)
        buckets = [0, 0, 0, 0]
        for r in rows:
            p = r['probability']
            if p < 25: buckets[0] += 1
            elif p < 50: buckets[1] += 1
            elif p < 75: buckets[2] += 1
            else: buckets[3] += 1

        # Feature averages for churned vs stayed
        churn_rows = [r for r in rows if r['churns']]
        stay_rows  = [r for r in rows if not r['churns']]

        def avg(lst, key):
            return round(sum(r[key] for r in lst) / len(lst), 1) if lst else 0

        feature_comparison = {
            'labels': ['Income', 'Orders', 'Login (Days)', 'Spend'],
            'churned': [
                avg(churn_rows, 'annualIncome'),
                avg(churn_rows, 'numOrders'),
                avg(churn_rows, 'lastLogin'),
                avg(churn_rows, 'totalSpend'),
            ],
            'stayed': [
                avg(stay_rows, 'annualIncome'),
                avg(stay_rows, 'numOrders'),
                avg(stay_rows, 'lastLogin'),
                avg(stay_rows, 'totalSpend'),
            ],
        }

        return jsonify({
            'summary': {
                'total': total,
                'churned': churned,
                'stays': stays,
                'churnRate': round(churned / total * 100, 1) if total else 0,
                'avgChurnProbability': avg_prob,
            },
            'confidenceBreakdown': conf_counts,
            'riskBuckets': {
                'labels': ['Low (0-25%)', 'Moderate (25-50%)', 'High (50-75%)', 'Critical (75-100%)'],
                'values': buckets,
            },
            'featureComparison': feature_comparison,
            'rows': rows[:200],  # cap at 200 for performance
        })

    except Exception as e:
        logging.error(f"Batch JSON error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/batch_predict', methods=['POST'])
def batch_predict():
    """Batch prediction from uploaded Excel/CSV file."""
    try:
        if not model_loaded:
            flash('Model is not available.', 'error')
            return redirect(url_for('home'))

        if 'excel_file' not in request.files:
            flash('No file selected', 'error')
            return redirect(url_for('home'))

        file = request.files['excel_file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('home'))

        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload .xlsx, .xls, or .csv files.', 'error')
            return redirect(url_for('home'))

        filename = secure_filename(file.filename or 'upload')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_fn = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_fn)
        file.save(file_path)

        ext = filename.lower().rsplit('.', 1)[-1]
        try:
            df = read_uploaded_file(file_path, ext)
            logging.info(f"Loaded file: {len(df)} rows, {len(df.columns)} cols")
        except Exception as e:
            flash(f'Error reading file: {str(e)}', 'error')
            return redirect(url_for('home'))

        errors = validate_data(df)
        if errors:
            flash(f'Validation errors: {"; ".join(errors)}', 'error')
            return redirect(url_for('home'))

        processed = preprocess_data(df)
        results_df = df.copy()

        predictions = dt_model.predict(processed)
        results_df['Churn_Prediction'] = [decode(p) for p in predictions]

        try:
            probas = dt_model.predict_proba(processed)
            results_df['Prediction_Confidence'] = [get_confidence(p) for p in probas]
            results_df['Churn_Probability_%'] = [round(max(p) * 100, 1) for p in probas]
        except Exception:
            results_df['Prediction_Confidence'] = 'Unknown'
            results_df['Churn_Probability_%'] = 0

        output_fn = f"predictions_{timestamp}_{filename}"
        output_path = os.path.join(app.config['DOWNLOAD_FOLDER'], output_fn)

        if ext == 'csv':
            results_df.to_csv(output_path, index=False)
        else:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                results_df.to_excel(writer, index=False, sheet_name='Predictions')

        try:
            os.remove(file_path)
        except Exception:
            pass

        flash(f'Batch prediction completed! Processed {len(df)} records.', 'success')
        return send_file(output_path, as_attachment=True, download_name=output_fn)

    except Exception as e:
        logging.error(f"Batch prediction error: {e}")
        flash(f'Error processing file: {str(e)}', 'error')
        return redirect(url_for('home'))


@app.route('/download_template')
@app.route('/download_template/<format>')
def download_template(format='excel'):
    """Download an ecommerce data template."""
    try:
        template_data = {
            'CustomerID':            [1001, 1002, 1003, 1004, 1005],
            'Age':                   [25, 42, 19, 31, 55],
            'Gender':                [1, 0, 1, 1, 0], # 1=Female, 0=Male
            'AnnualIncome':          [45000, 80000, 22000, 110000, 65000],
            'SpendingScore':         [80, 50, 95, 20, 60],
            'TenureMonths':          [12, 48, 2, 72, 36],
            'NumOrders':             [5, 20, 1, 35, 12],
            'AvgOrderValue':         [65.50, 120.00, 15.75, 450.00, 85.00],
            'LastLoginDaysAgo':      [2, 30, 0, 45, 15],
            'IsActiveMember':        [1, 1, 0, 0, 1],
        }

        df = pd.DataFrame(template_data)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if format.lower() == 'csv':
            filename = f'ecommerce_template_{timestamp}.csv'
            filepath = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
            df.to_csv(filepath, index=False)
        else:
            filename = f'ecommerce_template_{timestamp}.xlsx'
            filepath = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Customer_Data')

        return send_file(filepath, as_attachment=True, download_name=filename)

    except Exception as e:
        logging.error(f"Template error: {e}")
        return jsonify({'error': f'Error creating template: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
