"""
sensors_simulator.py - Simulates realistic sensor values for Smart Farming Hub
NO HARDWARE REQUIRED - generates random values within realistic agricultural ranges
"""

import random
from datetime import datetime
import database
from irrigation_predictor import irrigation_predictor


class SensorSimulator:
    """
    Simulates DHT (temperature/humidity) and soil moisture sensors
    with realistic value ranges for farming environments
    """

    def __init__(self):
        # Realistic ranges for Indian/global farming conditions
        self.temp_min = 25.0
        self.temp_max = 40.0
        self.humidity_min = 40.0
        self.humidity_max = 90.0
        
        # State variables for smooth realistic simulation
        self.current_temp = random.uniform(self.temp_min, self.temp_max)
        self.current_humidity = random.uniform(self.humidity_min, self.humidity_max)
        
        # Manual override state
        self.manual_override = False
        self.manual_status = "OFF"
        
        # Keep track of last irrigation status to drive soil moisture realism
        self.last_irrigation_status = "OFF"

    def get_temperature(self):
        """Simulate temperature sensor with realistic gradual drift (+/- 0.5 °C)"""
        self.current_temp += random.uniform(-0.5, 0.5)
        self.current_temp = max(self.temp_min, min(self.temp_max, self.current_temp))
        return round(self.current_temp, 2)

    def get_humidity(self):
        """Simulate humidity sensor with realistic gradual drift (+/- 1.0 %)"""
        self.current_humidity += random.uniform(-1.0, 1.0)
        self.current_humidity = max(self.humidity_min, min(self.humidity_max, self.current_humidity))
        return round(self.current_humidity, 2)


    def set_manual_override(self, mode, status="OFF"):
        """
        Set manual override
        mode: 'auto' or 'manual'
        status: 'ON' or 'OFF' (ignored if mode is 'auto')
        """
        if mode == 'manual':
            self.manual_override = True
            self.manual_status = status.upper()
        else:
            self.manual_override = False

    def read_all(self):
        """
        Read all sensors and return as dict
        Also stores in database and returns irrigation status
        """
        temperature = self.get_temperature()
        humidity = self.get_humidity()

        # Store in database, passing 0.0 for soil_moisture to maintain schema integrity
        database.insert_sensor_reading(temperature, humidity, 0.0)

        # ML-Based Irrigation Prediction (always run to show prediction to user)
        # We now only pass temperature and humidity
        prediction = irrigation_predictor.predict(temperature, humidity)
        irrigation_needed = prediction['irrigation_needed']
        confidence = prediction['confidence']
        
        # Determine actual status
        if self.manual_override:
            irrigation_status = self.manual_status
            reason = f"Manual Override: {self.manual_status}"
        else:
            irrigation_status = "ON" if irrigation_needed else "OFF"
            if irrigation_needed:
                reason = f"ML Predicts Irrigation Needed (Confidence: {int(confidence*100)}%)"
            else:
                reason = f"ML Predicts No Irrigation (Confidence: {int(confidence*100)}%)"

        # Keep track of last irrigation status
        self.last_irrigation_status = irrigation_status

        # Log irrigation status change (pass 0.0 for soil moisture backwards compatibility)
        database.insert_irrigation_log(
            status=irrigation_status, 
            soil_moisture=0.0, 
            reason=reason,
            confidence=confidence
        )

        return {
            'temperature': temperature,
            'humidity': humidity,
            'irrigation_prediction': irrigation_needed,
            'irrigation_confidence': confidence,
            'irrigation_status': irrigation_status,
            'manual_mode': self.manual_override,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }


# Singleton instance for easy import
sensor_simulator = SensorSimulator()
