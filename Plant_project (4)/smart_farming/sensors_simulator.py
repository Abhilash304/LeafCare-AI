import random
import urllib.request
import json
from datetime import datetime
import database
from weather_service import WeatherService


class SensorSimulator:
    """
    Simulates DHT (temperature/humidity) and soil moisture sensors.
    Hybrid: Uses real-time weather APIs for Temp/Hum, and simulates Soil Moisture.
    """

    def __init__(self):
        # API Configuration
        self.api_key = "de926f822eae3b4a53fe4dd46c944505"
        self.weather_service = WeatherService(self.api_key)
        self.city = "Mangalore"

        # State variables for fallback simulation (if API fails)
        self.temp_min = 25.0
        self.temp_max = 40.0
        self.humidity_min = 40.0
        self.humidity_max = 95.0
        
        self.current_temp = random.uniform(self.temp_min, self.temp_max)
        self.current_humidity = random.uniform(self.humidity_min, self.humidity_max)
        self.current_moisture = random.uniform(40.0, 70.0)
        
        self.manual_override = False
        self.manual_status = "OFF"
        self.last_irrigation_status = "OFF"

    def get_temperature(self):
        """Fallback simulation for temperature"""
        self.current_temp += random.uniform(-0.3, 0.3)
        self.current_temp = max(self.temp_min, min(self.temp_max, self.current_temp))
        return round(self.current_temp, 2)

    def get_humidity(self):
        """Fallback simulation for humidity"""
        self.current_humidity += random.uniform(-0.5, 0.5)
        self.current_humidity = max(self.humidity_min, min(self.humidity_max, self.current_humidity))
        return round(self.current_humidity, 2)

    def get_soil_moisture(self):
        """
        Simulate soil moisture.
        Decreases slowly over time, increases if irrigation is ON.
        """
        if self.last_irrigation_status == "ON":
            self.current_moisture += random.uniform(1.0, 3.0) 
        else:
            self.current_moisture -= random.uniform(0.1, 0.3) 
            
        self.current_moisture = max(20.0, min(95.0, self.current_moisture))
        return round(self.current_moisture, 2)

    def set_manual_override(self, mode, status="OFF"):
        if mode == 'manual':
            self.manual_override = True
            self.manual_status = status.upper()
        else:
            self.manual_override = False

    def read_all(self):
        """
        Read all sensors and return as dict.
        Hybrid: Real weather for Temp/Hum, Simulation for Moisture.
        """
        # 1. Fetch real weather data (No manual offsets applied)
        weather = self.weather_service.get_weather_data(self.city)
        
        if weather:
            temperature = weather['temperature']
            humidity = weather['humidity']
            data_source = f"Weather API ({weather['city']})"
            
            # Print to terminal for debugging
            print(f"[Sensors] Real-time Data: {temperature}°C, {humidity}% Humidity (Source: {weather['city']})")
            
            # Update internal state for fallback continuity
            self.current_temp = temperature
            self.current_humidity = humidity
        else:
            # Fallback to simulation
            temperature = self.get_temperature()
            humidity = self.get_humidity()
            data_source = "Simulated (Fallback)"
            print(f"[Sensors] Fallback Simulation: {temperature}°C, {humidity}% Humidity")

        # 2. Get soil moisture (always simulated)
        soil_moisture = self.get_soil_moisture()

        # 3. Store in database (non-critical — don't crash if DB fails)
        try:
            database.insert_sensor_reading(temperature, humidity, soil_moisture)
        except Exception as e:
            print(f"[Sensors] DB write error (sensor_reading): {e}")

        # 4. ML-Based Irrigation Prediction (lazy import to speed up startup)
        irrigation_needed = False
        confidence = 0.0
        try:
            from irrigation_predictor import irrigation_predictor
            prediction = irrigation_predictor.predict(temperature, humidity)
            irrigation_needed = prediction['irrigation_needed']
            confidence = prediction['confidence']
        except Exception as e:
            print(f"[Sensors] Irrigation prediction error: {e}")

        if self.manual_override:
            irrigation_status = self.manual_status
            reason = f"Manual Override: {self.manual_status}"
        else:
            irrigation_status = "ON" if irrigation_needed else "OFF"
            reason = f"ML Prediction ({int(confidence*100)}%): " + ("Needed" if irrigation_needed else "Not Needed")

        self.last_irrigation_status = irrigation_status

        # 5. Log irrigation status change (non-critical)
        try:
            database.insert_irrigation_log(
                status=irrigation_status, 
                soil_moisture=soil_moisture, 
                reason=reason,
                confidence=confidence
            )
        except Exception as e:
            print(f"[Sensors] DB write error (irrigation_log): {e}")

        return {
            'temperature': temperature,
            'humidity': humidity,
            'soil_moisture': soil_moisture,
            'irrigation_prediction': irrigation_needed,
            'irrigation_confidence': confidence,
            'irrigation_status': irrigation_status,
            'manual_mode': self.manual_override,
            'data_source': data_source,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }


# Singleton instance
sensor_simulator = SensorSimulator()
