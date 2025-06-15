// script.js
const collegeLat = 17.4931;
const collegeLng = 78.3915;
const allowedRadius = 1000; // in meters

function getDistanceFromLatLonInMeters(lat1, lon1, lat2, lon2) {
  const R = 6371000; // Radius of the earth in m
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const d = R * c; // Distance in meters
  return d;
}

navigator.geolocation.getCurrentPosition(
  (position) => {
    const lat = position.coords.latitude;
    const lng = position.coords.longitude;
    const distance = getDistanceFromLatLonInMeters(lat, lng, collegeLat, collegeLng);

    const status = document.getElementById("status");
    const button = document.getElementById("markBtn");
    const rollInput = document.getElementById("rollNo");

    if (distance <= allowedRadius) {
      status.textContent = "You are within the campus. Attendance can be marked.";
      button.disabled = false;
    } else {
      status.textContent = "You are outside the allowed range. Attendance cannot be marked.";
    }

    button.addEventListener("click", () => {
      const rollNo = rollInput.value.trim();
      if (!rollNo) {
        alert("Please enter your Roll Number.");
        return;
      }
      fetch("/mark-attendance", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ lat, lng, roll_no: rollNo }),
      })
        .then((res) => res.json())
        .then((data) => {
          alert(data.message);
        });
    });
  },
  (err) => {
    document.getElementById("status").textContent =
      "Location access denied. Please enable location to mark attendance.";
  }
);
