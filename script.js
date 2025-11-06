// script.js
document.addEventListener("DOMContentLoaded", () => {
  const visitorType = document.getElementById("visitorType");
  visitorType.addEventListener("change", showSection);

  document.getElementById("addClientBtn").addEventListener("click", addClient);
  document.getElementById("addVehicleBtn").addEventListener("click", addVehicle);

  // Attach submit handlers for all forms
  document.querySelectorAll("form").forEach(f => {
    f.addEventListener("submit", submitForm);
  });

  loadCountries();
});

function showSection() {
  const type = document.getElementById("visitorType").value;
  const tourist = document.getElementById("touristForm");
  const transit = document.getElementById("transitForm");
  const student = document.getElementById("studentForm");

  tourist.classList.add("hidden");
  transit.classList.add("hidden");
  student.classList.add("hidden");

  if (type === "tourist") tourist.classList.remove("hidden");
  if (type === "transit") transit.classList.remove("hidden");
  if (type === "student") student.classList.remove("hidden");

  // refresh countries when a form becomes visible
  loadCountries();
}

// CLIENTS
let clientCount = 1;
function addClient() {
  if (clientCount >= 10) return alert("Maximum 10 clients allowed!");
  clientCount++;
  const div = document.createElement("div");
  div.className = "client";
  div.innerHTML = `
    <label>Full Name:</label><input type="text" name="client_name[]" required />
    <label>Contact:</label><input type="tel" name="client_contact[]" required />
    <label>Nationality:</label>
    <select name="client_nationality[]" class="nationality"><option value="">Select Country</option></select>
  `;
  document.getElementById("clientList").appendChild(div);
  loadCountries();
}

// VEHICLES
let vehicleCount = 1;
function addVehicle() {
  if (vehicleCount >= 10) return alert("Maximum 10 vehicles allowed!");
  vehicleCount++;
  const div = document.createElement("div");
  div.className = "vehicle";
  div.innerHTML = `
    <label>Type of Car:</label><input type="text" name="car_type[]" />
    <label>Registration Number:</label><input type="text" name="car_reg[]" />
    <label>Driver Name:</label><input type="text" name="driver_name[]" />
    <label>Driver Phone:</label><input type="tel" name="driver_phone[]" />
  `;
  document.getElementById("vehicleList").appendChild(div);
}

// Load countries (cached)
let countriesCache = null;
async function loadCountries() {
  try {
    if (!countriesCache) {
      const res = await fetch("https://restcountries.com/v3.1/all");
      const data = await res.json();
      countriesCache = data.map(c => c.name.common).sort((a,b)=>a.localeCompare(b));
    }
    document.querySelectorAll(".nationality").forEach(select => {
      // avoid re-adding options
      if (select.dataset.populated === "1") return;
      countriesCache.forEach(country => {
        const opt = document.createElement("option");
        opt.value = country;
        opt.textContent = country;
        select.appendChild(opt);
      });
      select.dataset.populated = "1";
    });
  } catch (err) {
    console.error("Error loading countries:", err);
  }
}

// Submit form handler (works for all three forms)
async function submitForm(e) {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);

  // For tourist form: ensure single-valued fields are present if empty (avoid server confusion)
  // (No extra action needed if left empty — server handles lists.)

  try {
    const resp = await fetch("http://127.0.0.1:5000/submit", {
      method: "POST",
      body: formData
    });

    if (!resp.ok) {
      const txt = await resp.text();
      alert("Submission failed: " + resp.status + " — " + txt);
      return;
    }

    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    window.open(url, "_blank");
    form.reset();

    // Reset client/vehicle counters and DOM (if tourist)
    if (form.querySelector("#clientList")) {
      // remove extra client nodes (keep first)
      const clientList = document.getElementById("clientList");
      while (clientList.children.length > 1) clientList.removeChild(clientList.lastChild);
      clientCount = 1;
    }
    if (form.querySelector("#vehicleList")) {
      const vehicleList = document.getElementById("vehicleList");
      while (vehicleList.children.length > 1) vehicleList.removeChild(vehicleList.lastChild);
      vehicleCount = 1;
    }

    alert("Submitted successfully — PDF opened in new tab.");
  } catch (err) {
    console.error("Submit error:", err);
    alert("Error submitting form. See console for details.");
  }
}