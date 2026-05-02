"""
database.py - SQLite database setup and operations for Smart Farming Hub
Handles sensor readings, irrigation logs, and disease detection records
"""

import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

# Database file path
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'smart_farming.db')


@contextmanager
def get_db():
    """Context manager for database connections - ensures proper cleanup"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_db():
    """Initialize database and create all required tables"""
    with get_db() as conn:
        cursor = conn.cursor()

        # Table: sensor_readings - stores simulated sensor data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                temperature REAL NOT NULL,
                humidity REAL NOT NULL,
                soil_moisture REAL NOT NULL
            )
        ''')

        # Table: irrigation_logs - tracks irrigation ON/OFF status
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS irrigation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL,
                soil_moisture REAL,
                reason TEXT,
                prediction_confidence REAL
            )
        ''')

        # Table: disease_detections - stores capture results and predictions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS disease_detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                image_path TEXT,
                disease_name TEXT NOT NULL,
                confidence REAL NOT NULL,
                health_status TEXT NOT NULL,
                recommendation TEXT
            )
        ''')

        # Migration: Add prediction_confidence to irrigation_logs if missing
        try:
            cursor.execute('ALTER TABLE irrigation_logs ADD COLUMN prediction_confidence REAL')
        except sqlite3.OperationalError:
            # Column already exists
            pass

        conn.commit()


def insert_sensor_reading(temperature, humidity, soil_moisture):
    """Insert a new sensor reading into the database"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO sensor_readings (temperature, humidity, soil_moisture) VALUES (?, ?, ?)',
            (temperature, humidity, soil_moisture)
        )


def insert_irrigation_log(status, soil_moisture=None, reason=None, confidence=None):
    """Insert irrigation status change"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO irrigation_logs (status, soil_moisture, reason, prediction_confidence) VALUES (?, ?, ?, ?)',
            (status, soil_moisture, reason, confidence)
        )


def insert_disease_detection(image_path, disease_name, confidence, health_status, recommendation=""):
    """Insert disease detection result"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO disease_detections 
               (image_path, disease_name, confidence, health_status, recommendation) 
               VALUES (?, ?, ?, ?, ?)''',
            (image_path, disease_name, confidence, health_status, recommendation)
        )


def get_latest_sensor_reading():
    """Get the most recent sensor reading"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT temperature, humidity, soil_moisture, timestamp 
               FROM sensor_readings 
               ORDER BY timestamp DESC LIMIT 1'''
        )
        row = cursor.fetchone()
        if row:
            return {
                'temperature': row['temperature'],
                'humidity': row['humidity'],
                'soil_moisture': row['soil_moisture'],
                'timestamp': row['timestamp']
            }
    return None


def get_latest_irrigation_status():
    """Get the most recent irrigation status"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT status, soil_moisture, timestamp 
               FROM irrigation_logs 
               ORDER BY timestamp DESC LIMIT 1'''
        )
        row = cursor.fetchone()
        if row:
            return {
                'status': row['status'],
                'soil_moisture': row['soil_moisture'],
                'timestamp': row['timestamp']
            }
    return None


def get_disease_history(limit=50):
    """Retrieve historical disease detection results"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT id, timestamp, image_path, disease_name, confidence, health_status, recommendation 
               FROM disease_detections 
               ORDER BY timestamp DESC LIMIT ?''',
            (limit,)
        )
        rows = cursor.fetchall()
        
        history = []
        for row in rows:
            history.append({
                'id': row['id'],
                'timestamp': row['timestamp'],
                'image_path': row['image_path'],
                'disease_name': row['disease_name'],
                'confidence': row['confidence'],
                'health_status': row['health_status'],
                'recommendation': row['recommendation']
            })
        return history
