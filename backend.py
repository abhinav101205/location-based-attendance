# backend.py (Flask)
from flask import Flask, request, jsonify
from flask_cors import CORS
from math import radians, cos, sin, asin, sqrt
import sqlite3
import datetime

app = Flask(__name__)
CORS(app)

college_lat = 17.4931
college_lng = 78.3915
allowed_radius = 1000  # in meters

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    a = sin(dLat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dLon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

@app.route("/mark-attendance", methods=["POST"])
def mark_attendance():
    data = request.get_json()
    lat = data.get("lat")
    lng = data.get("lng")
    roll_no = data.get("roll_no")
    distance = haversine(lat, lng, college_lat, college_lng)

    if distance <= allowed_radius:
        conn = sqlite3.connect("attendance.db")
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roll_no TEXT,
                latitude REAL,
                longitude REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        c.execute("INSERT INTO attendance (roll_no, latitude, longitude) VALUES (?, ?, ?)", (roll_no, lat, lng))
        conn.commit()
        conn.close()
        return jsonify({"message": "Attendance marked successfully."})
    else:
        return jsonify({"message": "You are not in the allowed location."})

if __name__ == "__main__":
    app.run(debug=True)
