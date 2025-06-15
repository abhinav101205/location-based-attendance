# streamlit_attendance.py
import streamlit as st
import sqlite3
from datetime import datetime
from math import radians, cos, sin, asin, sqrt

# Constants
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

def mark_attendance(roll_no, lat, lng):
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

# Streamlit UI
st.set_page_config(page_title="Location Attendance", layout="centered")
st.title("📍 Location-Based Attendance")

roll_no = st.text_input("Enter Roll Number")

with st.expander("📍 Get Your Current Location"):
    st.markdown("Use your phone or browser to get your current latitude and longitude.")
    lat = st.number_input("Latitude", format="%.6f")
    lng = st.number_input("Longitude", format="%.6f")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"📌 College Lat: `{college_lat}`")
    with col2:
        st.write(f"📌 College Lng: `{college_lng}`")

if st.button("Mark Attendance"):
    if not roll_no or lat == 0.0 or lng == 0.0:
        st.warning("Please fill in all fields.")
    else:
        distance = haversine(lat, lng, college_lat, college_lng)
        if distance <= allowed_radius:
            mark_attendance(roll_no, lat, lng)
            st.success(f"✅ Attendance marked successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.error("❌ You are not within the allowed location radius.")

# Optional: Show last few entries
with st.expander("🗂 View Attendance Log"):
    conn = sqlite3.connect("attendance.db")
    df = None
    try:
        df = conn.execute("SELECT roll_no, latitude, longitude, timestamp FROM attendance ORDER BY id DESC LIMIT 10").fetchall()
        if df:
            st.table(df)
        else:
            st.info("No attendance records found.")
    except:
        st.warning("Database not initialized yet.")
    conn.close()
