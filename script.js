
document.addEventListener("DOMContentLoaded", () => {
  const visitorType = document.getElementById("visitorType");
  const touristForm = document.getElementById("touristForm");
  const transitForm = document.getElementById("transitForm");
  const studentForm = document.getElementById("studentForm");

  // ---------- CATEGORY SWITCH ----------
  if (visitorType) {
    visitorType.addEventListener("change", () => {
      [touristForm, transitForm, studentForm].forEach(f => f.classList.add("hidden"));
      if (visitorType.value === "tourist") touristForm.classList.remove("hidden");
      if (visitorType.value === "transit") transitForm.classList.remove("hidden");
      if (visitorType.value === "student") studentForm.classList.remove("hidden");
    });
  }

  // ---------- COUNTRIES LIST ----------
  const countries = [
    "Afghanistan","Albania","Algeria","Andorra","Angola","Argentina","Armenia","Australia",
    "Austria","Azerbaijan","Bahamas","Bahrain","Bangladesh","Barbados","Belarus","Belgium",
    "Belize","Benin","Bhutan","Bolivia","Bosnia and Herzegovina","Botswana","Brazil","Brunei",
    "Bulgaria","Burkina Faso","Burundi","Cabo Verde","Cambodia","Cameroon","Canada",
    "Central African Republic","Chad","Chile","China","Colombia","Comoros",
    "Congo, Democratic Republic of","Congo, Republic of","Costa Rica","Croatia","Cuba",
    "Cyprus","Czech Republic","Denmark","Djibouti","Dominica","Dominican Republic",
    "Ecuador","Egypt","El Salvador","Equatorial Guinea","Eritrea","Estonia","Eswatini",
    "Ethiopia","Fiji","Finland","France","Gabon","Gambia","Georgia","Germany","Ghana",
    "Greece","Grenada","Guatemala","Guinea","Guinea-Bissau","Guyana","Haiti","Honduras",
    "Hungary","Iceland","India","Indonesia","Iran","Iraq","Ireland","Israel","Italy",
    "Jamaica","Japan","Jordan","Kazakhstan","Kenya","Kiribati","Korea, North",
    "Korea, South","Kuwait","Kyrgyzstan","Laos","Latvia","Lebanon","Lesotho","Liberia",
    "Libya","Liechtenstein","Lithuania","Luxembourg","Madagascar","Malawi","Malaysia",
    "Maldives","Mali","Malta","Marshall Islands","Mauritania","Mauritius","Mexico",
    "Micronesia","Moldova","Monaco","Mongolia","Montenegro","Morocco","Mozambique",
    "Myanmar","Namibia","Nauru","Nepal","Netherlands","New Zealand","Nicaragua","Niger",
    "Nigeria","North Macedonia","Norway","Oman","Pakistan","Palau","Panama",
    "Papua New Guinea","Paraguay","Peru","Philippines","Poland","Portugal","Qatar",
    "Romania","Russia","Rwanda","Saint Kitts and Nevis","Saint Lucia",
    "Saint Vincent and the Grenadines","Samoa","San Marino","Sao Tome and Principe",
    "Saudi Arabia","Senegal","Serbia","Seychelles","Sierra Leone","Singapore","Slovakia",
    "Slovenia","Solomon Islands","Somalia","South Africa","Spain","Sri Lanka","Sudan",
    "South Sudan","Suriname","Sweden","Switzerland","Syria","Taiwan","Tajikistan",
    "Tanzania","Thailand","Timor-Leste","Togo","Tonga","Trinidad and Tobago","Tunisia",
    "Turkey","Turkmenistan","Tuvalu","Uganda","Ukraine","United Arab Emirates",
    "United Kingdom","United States","Uruguay","Uzbekistan","Vanuatu","Vatican City",
    "Venezuela","Vietnam","Yemen","Zambia","Zimbabwe"
  ];

  // ---------- FUNCTION TO POPULATE NATIONALITIES ----------
  function populateCountriesFor(selectElement) {
    selectElement.innerHTML = '<option value="">--Select Nationality--</option>';
    countries.forEach(country => {
      const option = document.createElement("option");
      option.value = country;
      option.textContent = country;
      selectElement.appendChild(option);
    });
  }

  // ---------- INITIAL FILL FOR ALL STATIC DROPDOWNS ----------
  document.querySelectorAll(".nationality-dropdown")
    .forEach(drop => populateCountriesFor(drop));

  // ---------- DYNAMIC CLIENTS ----------
  let clientCount = 1;
  document.getElementById("addClientBtn").addEventListener("click", () => {
    if (clientCount >= 10) return alert("Maximum 10 clients allowed");
    clientCount++;

    const div = document.createElement("div");
    div.className = "client";
    div.innerHTML = `
      <label>Full Name:</label><input type="text" name="client_name[]" required />
      <label>Contact:</label><input type="tel" name="client_contact[]" required />
      <label>Nationality:</label>
      <select name="client_nationality[]" class="nationality-dropdown" required></select>
    `;

    document.getElementById("clientList").appendChild(div);

    populateCountriesFor(div.querySelector(".nationality-dropdown"));
  });

  // ---------- DYNAMIC VEHICLES ----------
  let vehicleCount = 1;
  document.getElementById("addVehicleBtn").addEventListener("click", () => {
    if (vehicleCount >= 10) return alert("Maximum 10 vehicles allowed");
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
  });
});
