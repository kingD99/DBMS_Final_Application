from flask import Flask, render_template, request, redirect, url_for
from models import db, PatientRecord
from ml_engine import get_prediction, train_model
import os

app = Flask(__name__)

# Configure local SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cardio_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Connect DB to app
db.init_app(app)

# Create tables if they don't exist and train ML model
with app.app_context():
    db.create_all() 
    if not os.path.exists('cardio_model.pkl'):
        train_model() 

@app.route('/')
def index():
    """Landing page with input form."""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Handles form submission, runs ML, and saves to DB."""
    if request.method == 'POST':
        
        # 1. Extract data from form and prepare for ML and DB
        patient_name = request.form['patient_name']
        age_in_years = int(request.form['age']) 
        age_for_ml_days = age_in_years * 365 

        data_for_ml = {
            'age': age_for_ml_days,  
            'gender': int(request.form['gender']),
            'height': float(request.form['height']),
            'weight': float(request.form['weight']),
            'ap_hi': int(request.form['ap_hi']),
            'ap_lo': int(request.form['ap_lo']),
            'cholesterol': int(request.form['cholesterol']),
            'gluc': int(request.form['gluc']),
            'smoke': int(request.form['smoke']),
            'alco': int(request.form['alco']),
            'active': int(request.form['active'])
        }

        # 2. Get ML Insight (now returns binary risk AND probability)
        binary_risk, probability = get_prediction(data_for_ml)
        
        # Format probability for display and storage (e.g., 0.754 -> "75.4%")
        probability_string = f"{probability * 100:.1f}%"

        # 3. Derive Business Outcome: Insurance Premium (3-Tier System)
        if probability < 0.40:
            insurance_status = "Standard"
        elif 0.40 <= probability < 0.70:
            insurance_status = "Moderate"
        else:
            insurance_status = "High"

        # 4. Save to Database (OLTP Update)
        new_record = PatientRecord(
            name=patient_name,
            age=age_in_years, 
            gender=data_for_ml['gender'],
            height=data_for_ml['height'],
            weight=data_for_ml['weight'],
            ap_hi=data_for_ml['ap_hi'],
            ap_lo=data_for_ml['ap_lo'],
            cholesterol=data_for_ml['cholesterol'],
            gluc=data_for_ml['gluc'],
            smoke=data_for_ml['smoke'],
            alco=data_for_ml['alco'],
            active=data_for_ml['active'],
            risk_probability=probability_string, # <-- NOW STORING PERCENTAGE
            insurance_premium=insurance_status
        )
        db.session.add(new_record)
        db.session.commit()

        # 5. Show Result (Updated to display probability)
        # We display the probability but use the binary outcome for the summary text
        result_text = f"Risk: {probability_string} (Premium: {insurance_status})"
        return render_template('index.html', result=result_text)

@app.route('/dashboard')
def dashboard():
    """View stored data (Analytical/Reporting View)."""
    records = PatientRecord.query.order_by(PatientRecord.created_at.desc()).all()
    return render_template('dashboard.html', records=records)

@app.route('/retrain')
def retrain():
    """Endpoint to trigger model retraining manually."""
    train_model()
    return "Model Retrained Successfully using latest data."

if __name__ == '__main__':
    app.run(debug=True, port=5000)