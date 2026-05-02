"""
weather_service.py - Handles real-time weather data fetching
Uses OpenWeatherMap with Latitude/Longitude for maximum precision.
"""

import urllib.request
import json

class WeatherService:
    def __init__(self, api_key):
        self.api_key = api_key
        # Precise coordinates for Mangalore, India
        self.lat = 12.9141
        self.lon = 74.8560
        self.owm_url = "http://api.openweathermap.org/data/2.5/weather"

    def get_weather_data(self, city="Mangalore"):
        """
        Fetch real-time temperature (Celsius) and humidity (%) using exact coordinates.
        This is more accurate than city-name lookup.
        """
        try:
            # Using precise Lat/Lon coordinates for your location
            url = f"{self.owm_url}?lat={self.lat}&lon={self.lon}&appid={self.api_key}&units=metric"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                
                if data.get("cod") == 200:
                    main = data.get("main", {})
                    temp = main.get("temp")
                    humidity = main.get("humidity")
                    
                    if temp is not None and humidity is not None:
                        # Return raw data from the API as requested
                        return {
                            "temperature": round(float(temp), 2),
                            "humidity": round(float(humidity), 2),
                            "city": data.get("name", "Mangalore"),
                            "country": data.get("sys", {}).get("country", "IN")
                        }
        except Exception as e:
            print(f"[WeatherService] API Error: {e}")
        
        return None
