import streamlit as st
import sqlite3
import datetime
import math
import streamlit.components.v1 as components

# Constants
COLLEGE_LAT = 17.4931
COLLEGE_LNG = 78.3915
ALLOWED_RADIUS = 1000  # meters

# DB Setup
conn = sqlite3.connect("attendance.db", check_same_thread=False)
c = conn.cursor()
c.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_no TEXT,
        latitude REAL,
        longitude REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        status TEXT
    )
""")
conn.commit()

# Haversine distance function
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

st.title("📍 Location-Based Student Attendance")

roll_no = st.text_input("Enter your Roll Number")

# Button to get location
if st.button("📍 Get My Location"):
    components.html(
        f"""
        <script>
        navigator.geolocation.getCurrentPosition(
            function(pos) {{
                const lat = pos.coords.latitude;
                const lng = pos.coords.longitude;
                const query = new URLSearchParams(window.location.search);
                query.set("lat", lat);
                query.set("lng", lng);
                window.location.search = query.toString();
            }},
            function(err) {{
                alert("Location access denied or unavailable.");
            }}
        );
        </script>
        """,
        height=0,
    )

# Retrieve coordinates from query
lat = st.query_params.get("lat", [None])[0]
lng = st.query_params.get("lng", [None])[0]

if lat and lng:
    st.session_state.lat = float(lat)
    st.session_state.lng = float(lng)

if "lat" in st.session_state and "lng" in st.session_state:
    user_lat = st.session_state.lat
    user_lng = st.session_state.lng

    st.success(f"📌 Location Captured: Latitude {user_lat:.5f}, Longitude {user_lng:.5f}")
    distance = haversine(user_lat, user_lng, COLLEGE_LAT, COLLEGE_LNG)

    if distance <= ALLOWED_RADIUS:
        if st.button("✅ Mark Attendance"):
            if not roll_no:
                st.warning("Please enter your Roll Number.")
            else:
                c.execute("INSERT INTO attendance (roll_no, latitude, longitude, status) VALUES (?, ?, ?, ?)",
                          (roll_no, user_lat, user_lng, "Inside Zone"))
                conn.commit()
                st.success("🎉 Attendance marked successfully!")
    else:
        st.error("❌ You are outside the allowed 1 km zone.")
        if st.button("📝 Log Attendance (Outside Zone)"):
            if not roll_no:
                st.warning("Please enter your Roll Number.")
            else:
                c.execute("INSERT INTO attendance (roll_no, latitude, longitude, status) VALUES (?, ?, ?, ?)",
                          (roll_no, user_lat, user_lng, "Outside Zone"))
                conn.commit()
                st.success("🗒️ Logged your location as outside the campus.")
else:
    st.info("📡 Click the 'Get My Location' button to fetch your coordinates.")
