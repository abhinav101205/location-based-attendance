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
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()

# Haversine distance function
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

st.title("📍 Location-Based Student Attendance")

roll_no = st.text_input("Enter your Roll Number")

# Display JavaScript to get location
st.markdown("Click the button below to fetch your location from your device.")
get_location_button = st.button("📍 Get My Location")

# Run JS to get location
location = components.html("""
    <script>
    const sendCoords = (lat, lng) => {
        const input = window.parent.document.querySelector('iframe[srcdoc]').contentWindow;
        input.postMessage({lat, lng}, "*");
    };

    navigator.geolocation.getCurrentPosition(
        (pos) => {
            const lat = pos.coords.latitude;
            const lng = pos.coords.longitude;
            sendCoords(lat, lng);
        },
        (err) => {
            alert("Location access denied.");
        }
    );
    </script>
""", height=0)

# Get location from JS
location_data = st.experimental_get_query_params()

if "lat" not in st.session_state:
    st.session_state.lat = None
    st.session_state.lng = None

def handle_js_response():
    import streamlit_javascript as stj  # optional: if you use streamlit-javascript package
    coords = stj.get_geolocation()
    if coords:
        st.session_state.lat = coords["latitude"]
        st.session_state.lng = coords["longitude"]

if get_location_button:
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

lat = st.experimental_get_query_params().get("lat", [None])[0]
lng = st.experimental_get_query_params().get("lng", [None])[0]

if lat and lng:
    st.session_state.lat = float(lat)
    st.session_state.lng = float(lng)

if st.session_state.lat and st.session_state.lng:
    st.success(f"📌 Location: Lat: {st.session_state.lat:.5f}, Lng: {st.session_state.lng:.5f}")
    distance = haversine(st.session_state.lat, st.session_state.lng, COLLEGE_LAT, COLLEGE_LNG)
    if distance <= ALLOWED_RADIUS:
        if st.button("✅ Mark Attendance"):
            if not roll_no:
                st.warning("Please enter your Roll Number.")
            else:
                c.execute("INSERT INTO attendance (roll_no, latitude, longitude) VALUES (?, ?, ?)",
                          (roll_no, st.session_state.lat, st.session_state.lng))
                conn.commit()
                st.success("🎉 Attendance marked successfully.")
    else:
        st.error("❌ You are outside the allowed 1 km radius of the college.")
else:
    st.info("Your location has not been captured yet.")

