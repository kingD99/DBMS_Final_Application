import pandas as pd
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Path to data and model
DATA_PATH = 'data/cardio_train.csv'
MODEL_PATH = 'cardio_model.pkl'

def train_model():
    """Reads CSV, preprocesses data, trains model, and saves it."""
    print("Starting model training...")
    
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Could not find {DATA_PATH}")
        
    df = pd.read_csv(DATA_PATH, sep=';')
    
    X = df.drop(['id', 'cardio'], axis=1)
    y = df['cardio']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    clf = RandomForestClassifier(n_estimators=100)
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Model trained. Accuracy: {acc:.2f}")
    
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(clf, f)
    print("Model saved to disk.")

def get_prediction(data_dict):
    """
    Loads model and returns both the binary prediction and the probability 
    of High Risk (class 1).
    """
    if not os.path.exists(MODEL_PATH):
        train_model()
        
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
        
    df = pd.DataFrame([data_dict])
    
    # 1. Get Probability array: [[Prob_LowRisk, Prob_HighRisk]]
    probability_array = model.predict_proba(df)
    
    # 2. Get Binary Prediction (0 or 1)
    binary_prediction = model.predict(df)[0]
    
    # 3. Get Probability of High Risk (class 1)
    prob_high_risk = probability_array[0][1]
    
    # Return both binary prediction (for business logic) and the probability
    return int(binary_prediction), float(prob_high_risk)