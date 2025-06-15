import streamlit as st
import sqlite3
import datetime
import math
import streamlit.components.v1 as components
import folium

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

# Haversine function
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

# Title
st.title("📍 Location-Based Student Attendance")

# Input
roll_no = st.text_input("Enter your Roll Number")

# Button: Get location
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

# Fetch lat/lng from query
lat = st.query_params.get("lat", [None])[0]
lng = st.query_params.get("lng", [None])[0]

# Store in session
if lat and lng:
    st.session_state.lat = float(lat)
    st.session_state.lng = float(lng)

# Proceed if location fetched
if "lat" in st.session_state and "lng" in st.session_state:
    user_lat = st.session_state.lat
    user_lng = st.session_state.lng

    st.success(f"📌 Location: Lat: {user_lat:.5f}, Lng: {user_lng:.5f}")

    distance = haversine(user_lat, user_lng, COLLEGE_LAT, COLLEGE_LNG)

    # Display Map with markers
    m = folium.Map(location=[COLLEGE_LAT, COLLEGE_LNG], zoom_start=15)
    folium.Marker([COLLEGE_LAT, COLLEGE_LNG], popup="College", icon=folium.Icon(color="green")).add_to(m)
    folium.Circle([COLLEGE_LAT, COLLEGE_LNG], radius=ALLOWED_RADIUS, color="blue", fill=True, fill_opacity=0.1).add_to(m)
    folium.Marker([user_lat, user_lng], popup="You", icon=folium.Icon(color="red")).add_to(m)

    folium_static_html = "map_with_user.html"
    m.save(folium_static_html)
    with open(folium_static_html, "r", encoding="utf-8") as f:
        html_data = f.read()
    st.components.v1.html(html_data, height=500)

    # Mark attendance
    if distance <= ALLOWED_RADIUS:
        if st.button("✅ Mark Attendance"):
            if not roll_no:
                st.warning("Please enter your Roll Number.")
            else:
                c.execute("INSERT INTO attendance (roll_no, latitude, longitude, status) VALUES (?, ?, ?, ?)",
                          (roll_no, user_lat, user_lng, "Inside Zone"))
                conn.commit()
                st.success("🎉 Attendance marked successfully.")
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
    st.info("📡 Please click 'Get My Location' to fetch your coordinates.")
