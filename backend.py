import streamlit as st
import sqlite3
import math
import streamlit.components.v1 as components

# Constants
COLLEGE_LAT = 17.4931
COLLEGE_LNG = 78.3915
ALLOWED_RADIUS = 1000  # in meters

# DB Setup
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

# Distance function
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

# Title
st.title("📍 Location-Based Student Attendance")

# Initialize session state
if "lat" not in st.session_state:
    st.session_state.lat = None
    st.session_state.lng = None
    st.session_state.location_checked = False
    st.session_state.within_range = False

# Location Button
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

# Get location from query params
lat = st.query_params.get("lat", None)
lng = st.query_params.get("lng", None)

if lat and lng:
    try:
        st.session_state.lat = float(lat)
        st.session_state.lng = float(lng)
        st.session_state.location_checked = True

        distance = haversine(st.session_state.lat, st.session_state.lng, COLLEGE_LAT, COLLEGE_LNG)

        if distance <= ALLOWED_RADIUS:
            st.session_state.within_range = True
            st.success(f"✅ You are within the allowed area.\n📌 Lat: {st.session_state.lat:.5f}, Lng: {st.session_state.lng:.5f}")
        else:
            st.session_state.within_range = False
            st.error("❌ You are outside the 1 km radius of the college.")
            st.stop()

    except ValueError:
        st.error("Invalid latitude or longitude data.")

# Show roll input & mark attendance only if in range
if st.session_state.within_range:
    roll_no = st.text_input("🎓 Enter your Roll Number")
    if st.button("✅ Mark Attendance"):
        if not roll_no.strip():
            st.warning("⚠️ Please enter your Roll Number.")
        else:
            c.execute("INSERT INTO attendance (roll_no, latitude, longitude) VALUES (?, ?, ?)",
                      (roll_no.strip(), st.session_state.lat, st.session_state.lng))
            conn.commit()
            st.success("🎉 Attendance marked successfully.")
