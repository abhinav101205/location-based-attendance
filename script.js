const collegeLat = 17.4931;
const collegeLng = 78.3915;
const allowedRadius = 1000; // in meters

function getDistanceFromLatLonInMeters(lat1, lon1, lat2, lon2) {
  const R = 6371000; // Earth's radius in meters
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

const status = document.getElementById("status");
const button = document.getElementById("markBtn");
const rollInput = document.getElementById("rollNo");

// Automatically request current location
window.onload = () => {
  if (!navigator.geolocation) {
    status.textContent = "Geolocation is not supported by your browser.";
    return;
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const lat = position.coords.latitude;
      const lng = position.coords.longitude;

      const distance = getDistanceFromLatLonInMeters(lat, lng, collegeLat, collegeLng);

      if (distance <= allowedRadius) {
        status.textContent = "✅ You are within campus. Attendance can be marked.";
        button.disabled = false;

        // Event listener for button
        button.onclick = () => {
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
            })
            .catch(() => {
              alert("Error marking attendance. Please try again.");
            });
        };
      } else {
        status.textContent = "❌ You are outside the allowed range. Attendance not permitted.";
        button.disabled = true;
      }
    },
    (err) => {
      status.textContent =
        "⚠️ Location access denied or unavailable. Please enable location and reload.";
    }
  );
};
