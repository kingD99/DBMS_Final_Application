from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

# Initialize the database instance
db = SQLAlchemy()

# Define the Patient Record table
class PatientRecord(db.Model):
    __tablename__ = 'patient_records'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) 
    age = db.Column(db.Integer, nullable=False)  
    gender = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    ap_hi = db.Column(db.Integer, nullable=False) 
    ap_lo = db.Column(db.Integer, nullable=False) 
    cholesterol = db.Column(db.Integer, nullable=False)
    gluc = db.Column(db.Integer, nullable=False)
    smoke = db.Column(db.Integer, nullable=False)
    alco = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Integer, nullable=False)
    
    # UPDATED COLUMN: Stores probability percentage string (e.g., "75.4%")
    risk_probability = db.Column(db.String(10), nullable=True) 
    
    # Business outcome (Standard or High premium)
    insurance_premium = db.Column(db.String(10), nullable=True) 
    
    created_at = db.Column(db.DateTime, server_default=func.now())

    def __repr__(self):
        return f'<PatientRecord {self.id} - Probability: {self.risk_probability}>'