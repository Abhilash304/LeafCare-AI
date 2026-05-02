"""
irrigation_predictor.py - Machine Learning module for predictive irrigation
Uses RandomForestClassifier to predict irrigation needs based on sensor data.
"""

import os
from datetime import datetime

# Model storage path
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'irrigation_model_v2.pkl')

class IrrigationPredictor:
    """
    ML-based irrigation predictor using Random Forest
    """
    
    def __init__(self):
        self.model = None
        # Create models directory if not exists
        if not os.path.exists(MODEL_DIR):
            os.makedirs(MODEL_DIR)

    def _ensure_model(self):
        """Ensure model is loaded or trained"""
        if self.model is None:
            self.load_or_train()

    def generate_synthetic_data(self, samples=1000):
        """
        Generate synthetic training data based on defined rules
        """
        import numpy as np
        import pandas as pd
        
        print(f"[Irrigation ML] Generating {samples} synthetic training samples...")
        
        temperature = np.random.uniform(15, 45, samples)
        humidity = np.random.uniform(20, 95, samples)
        hour = np.random.randint(0, 24, samples)
        
        data = pd.DataFrame({
            'temperature': temperature,
            'humidity': humidity,
            'hour': hour
        })
        
        # New Rule: ON if Temp > 32 OR (Temp > 28 AND Humidity < 50)
        data['irrigation_needed'] = ((data['temperature'] > 32) | 
                                    ((data['temperature'] > 28) & (data['humidity'] < 50))).astype(int)
        
        return data

    def train_model(self):
        """Train the Random Forest model on synthetic data"""
        from sklearn.ensemble import RandomForestClassifier
        import joblib
        
        data = self.generate_synthetic_data()
        
        X = data[['temperature', 'humidity', 'hour']]
        y = data['irrigation_needed']
        
        print("[Irrigation ML] Training Random Forest Classifier...")
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X, y)
        
        # Save the model
        joblib.dump(self.model, MODEL_PATH)
        print(f"[Irrigation ML] Model saved to {MODEL_PATH}")

    def load_or_train(self):
        """Load model from file or train new one if missing"""
        import joblib
        
        if os.path.exists(MODEL_PATH):
            try:
                print(f"[Irrigation ML] Loading existing model from {MODEL_PATH}")
                self.model = joblib.load(MODEL_PATH)
            except Exception as e:
                print(f"[Irrigation ML] Error loading model: {e}. Re-training...")
                self.train_model()
        else:
            print("[Irrigation ML] No pre-trained model found.")
            self.train_model()

    def predict(self, temperature, humidity, hour=None):
        """
        Predict irrigation need
        Returns: { 'irrigation_needed': bool, 'confidence': float }
        """
        self._ensure_model()
        import numpy as np
            
        if hour is None:
            hour = datetime.now().hour
            
        # Prepare input
        X_input = np.array([[temperature, humidity, hour]])
        
        # Predict class and probability
        prediction = self.model.predict(X_input)[0]
        probabilities = self.model.predict_proba(X_input)[0]
        
        # Confidence is the probability of the predicted class
        confidence = float(probabilities[prediction])
        
        return {
            "irrigation_needed": bool(prediction == 1),
            "confidence": round(confidence, 2)
        }

# Singleton instance
irrigation_predictor = IrrigationPredictor()
