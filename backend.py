import streamlit as st
import sqlite3
import math
import streamlit.components.v1 as components

# Constants
COLLEGE_LAT = 17.4931
COLLEGE_LNG = 78.3915
ALLOWED_RADIUS = 1000  # meters

# Database setup
conn = sqlite3.connect("attendance.db", check_same_thread=False)
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
conn.commit()

# Haversine distance
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

st.title("📍 Location-Based Student Attendance")

# Session storage for coordinates
if "lat" not in st.session_state:
    st.session_state.lat = None
    st.session_state.lng = None

# Get location
if st.button("📍 Get My Location"):
    components.html(
        """
        <script>
        navigator.geolocation.getCurrentPosition(
            function(pos) {
                const lat = pos.coords.latitude;
                const lng = pos.coords.longitude;
                const query = new URLSearchParams(window.location.search);
                query.set("lat", lat);
                query.set("lng", lng);
                window.location.search = query.toString();
            },
            function(err) {
                alert("Location access denied or unavailable.");
            }
        );
        </script>
        """,
        height=0,
    )

# Handle query params from JS
query_params = st.query_params
lat = query_params.get("lat", [None])[0]
lng = query_params.get("lng", [None])[0]

if lat and lng:
    st.session_state.lat = float(lat)
    st.session_state.lng = float(lng)

# If location is captured
if st.session_state.lat and st.session_state.lng:
    distance = haversine(st.session_state.lat, st.session_state.lng, COLLEGE_LAT, COLLEGE_LNG)
    st.success(f"📌 Your Location: Lat: {st.session_state.lat:.5f}, Lng: {st.session_state.lng:.5f}")
    
    if distance <= ALLOWED_RADIUS:
        st.success("✅ You are inside the college zone.")
        roll_no = st.text_input("Enter your Roll Number")
        if st.button("✅ Mark Attendance"):
            if not roll_no:
                st.warning("Please enter your Roll Number.")
            else:
                c.execute("INSERT INTO attendance (roll_no, latitude, longitude) VALUES (?, ?, ?)",
                          (roll_no, st.session_state.lat, st.session_state.lng))
                conn.commit()
                st.success("🎉 Attendance marked successfully.")
    else:
        st.error("❌ You are *not in the desired zone*. You must be within 1 km of the college to mark attendance.")
else:
    st.info("📍 Please click 'Get My Location' to check your eligibility.")
