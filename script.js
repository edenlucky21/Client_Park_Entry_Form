function showSection() {
  const type = document.getElementById("visitorType").value;

  document.getElementById("touristForm").classList.add("hidden");
  document.getElementById("transitForm").classList.add("hidden");
  document.getElementById("studentForm").classList.add("hidden");

  if (type === "tourist") document.getElementById("touristForm").classList.remove("hidden");
  if (type === "transit") document.getElementById("transitForm").classList.remove("hidden");
  if (type === "student") document.getElementById("studentForm").classList.remove("hidden");

  // Always refresh country lists when a form opens
  loadCountries();
}

// Add client
let clientCount = 1;
function addClient() {
  if (clientCount >= 10) return alert("Maximum 10 clients allowed!");
  clientCount++;

  const div = document.createElement("div");
  div.className = "client";
  div.innerHTML = `
    <label>Full Name:</label>
    <input type="text" name="client_name[]" required />
    <label>Contact:</label>
    <input type="tel" name="client_contact[]" required />
    <label>Nationality:</label>
    <select name="client_nationality[]" class="nationality">
      <option value="">Select Country</option>
    </select>
  `;
  document.getElementById("clientList").appendChild(div);
  loadCountries();
}

// Add vehicle
let vehicleCount = 1;
function addVehicle() {
  if (vehicleCount >= 10) return alert("Maximum 10 vehicles allowed!");
  vehicleCount++;

  const div = document.createElement("div");
  div.className = "vehicle";
  div.innerHTML = `
    <label>Type of Car:</label>
    <input type="text" name="car_type[]" />
    <label>Registration Number:</label>
    <input type="text" name="car_reg[]" />
    <label>Driver Name:</label>
    <input type="text" name="driver_name[]" />
    <label>Driver Phone:</label>
    <input type="tel" name="driver_phone[]" />
  `;
  document.getElementById("vehicleList").appendChild(div);
}

// Load countries into dropdowns
async function loadCountries() {
  try {
    const response = await fetch("https://restcountries.com/v3.1/all");
    const data = await response.json();
    const countries = data.map(c => c.name.common).sort();

    document.querySelectorAll(".nationality").forEach(select => {
      if (select.options.length <= 1) {
        countries.forEach(country => {
          const opt = document.createElement("option");
          opt.value = country;
          opt.textContent = country;
          select.appendChild(opt);
        });
      }
    });
  } catch (err) {
    console.error("Failed to load countries:", err);
  }
}
loadCountries();

// Submit form
async function submitForm(event) {
  event.preventDefault();
  const form = event.target;
  const formData = new FormData(form);

  const response = await fetch("http://localhost:5000/submit", {
    method: "POST",
    body: formData
  });

  if (response.ok) {
    const blob = await response.blob();
    const pdfUrl = URL.createObjectURL(blob);
    window.open(pdfUrl, "_blank");
    form.reset();
  } else {
    alert("Error submitting form.");
  }
}