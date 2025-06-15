const collegeLat = 17.4931;
const collegeLng = 78.3915;
const allowedRadius = 1000; // meters

function getDistanceFromLatLonInMeters(lat1, lon1, lat2, lon2) {
  const R = 6371000;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) ** 2;
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

navigator.geolocation.getCurrentPosition(
  (position) => {
    const lat = position.coords.latitude;
    const lng = position.coords.longitude;
    const distance = getDistanceFromLatLonInMeters(lat, lng, collegeLat, collegeLng);

    const status = document.getElementById("status");
    const button = document.getElementById("markBtn");

    if (distance <= allowedRadius) {
      status.textContent = "You are within campus. Attendance can be marked.";
      button.disabled = false;
    } else {
      status.textContent = "You are outside the allowed range.";
    }

    button.addEventListener("click", () => {
      fetch("/mark-attendance", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ lat, lng }),
      })
        .then((res) => res.json())
        .then((data) => {
          alert(data.message);
        });
    });
  },
  () => {
    document.getElementById("status").textContent =
      "Location access denied. Please enable it to mark attendance.";
  }
);
