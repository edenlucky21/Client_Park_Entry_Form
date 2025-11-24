document.addEventListener("DOMContentLoaded", ()=> {
  const visitorType = document.getElementById("visitorType");
  const touristForm = document.getElementById("touristForm");
  const transitForm = document.getElementById("transitForm");
  const studentForm = document.getElementById("studentForm");

  visitorType.addEventListener("change", () => {
    [touristForm, transitForm, studentForm].forEach(f => f.classList.add("hidden"));
    if (visitorType.value === "tourist") touristForm.classList.remove("hidden");
    if (visitorType.value === "transit") transitForm.classList.remove("hidden");
    if (visitorType.value === "student") studentForm.classList.remove("hidden");
  });

  // dynamic clients
  let clientCount = 1;
  document.getElementById("addClientBtn").addEventListener("click", ()=>{
    if (clientCount >= 10) return alert("Maximum 10 clients allowed");
    clientCount++;
    const div = document.createElement("div");
    div.className = "client";
    div.innerHTML = `
      <label>Full Name:</label><input type="text" name="client_name[]" required />
      <label>Contact:</label><input type="tel" name="client_contact[]" required />
      <label>Nationality:</label><select name="client_nationality[]" class="nationality-dropdown" required><option value="">--Select Nationality--</option></select>
    `;
    document.getElementById("clientList").appendChild(div);
    populateCountriesFor(div.querySelector('.nationality-dropdown'));
  });

  // dynamic vehicles
  let vehicleCount = 1;
  document.getElementById("addVehicleBtn").addEventListener("click", ()=>{
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

  // Countries populate
  const countries = [ "Afghanistan","Albania","Algeria","Andorra","Angola","Argentina","Armenia","Australia","Austria","Azerbaijan","Bahamas","Bahrain","Bangladesh","Barbados","Belarus","Belgium","Belize","Benin","Bhutan","Bolivia","Botswana","Brazil","Brunei","Bulgaria","Burkina Faso","Burundi","Cambodia","Cameroon","Canada","Cape Verde","Central African Republic","Chad","Chile","China","Colombia","Comoros","Congo (Brazzaville)","Congo (Kinshasa)","Costa Rica","Croatia","Cuba","Cyprus","Czech Republic","Denmark","Djibouti","Dominica","Dominican Republic","Ecuador","Egypt","El Salvador","Equatorial Guinea","Eritrea","Estonia","Eswatini","Ethiopia","Fiji","Finland","France","Gabon","Gambia","Georgia","Germany","Ghana","Greece","Grenada","Guatemala","Guinea","Guinea-Bissau","Guyana","Haiti","Honduras","Hungary","Iceland","India","Indonesia","Iran","Iraq","Ireland","Israel","Italy","Jamaica","Japan","Jordan","Kazakhstan","Kenya","Kiribati","Kuwait","Kyrgyzstan","Laos","Latvia","Lebanon","Lesotho","Liberia","Libya","Lithuania","Luxembourg","Madagascar","Malawi","Malaysia","Maldives","Mali","Malta","Marshall Islands","Mauritania","Mauritius","Mexico","Micronesia","Moldova","Monaco","Mongolia","Montenegro","Morocco","Mozambique","Myanmar","Namibia","Nauru","Nepal","Netherlands","New Zealand","Nicaragua","Niger","Nigeria","North Korea","North Macedonia","Norway","Oman","Pakistan","Palau","Panama","Papua New Guinea","Paraguay","Peru","Philippines","Poland","Portugal","Qatar","Romania","Russia","Rwanda","Saint Kitts and Nevis","Saint Lucia","Saint Vincent and the Grenadines","Samoa","San Marino","Sao Tome and Principe","Saudi Arabia","Senegal","Serbia","Seychelles","Sierra Leone","Singapore","Slovakia","Slovenia","Solomon Islands","Somalia","South Africa","South Korea","South Sudan","Spain","Sri Lanka","Sudan","Suriname","Sweden","Switzerland","Syria","Taiwan","Tajikistan","Tanzania","Thailand","Togo","Tonga","Trinidad and Tobago","Tunisia","Turkey","Turkmenistan","Tuvalu","Uganda","Ukraine","United Arab Emirates","United Kingdom","United States","Uruguay","Uzbekistan","Vanuatu","Vatican City","Venezuela","Vietnam","Yemen","Zambia","Zimbabwe" ];

  function populateCountriesFor(select){
    countries.forEach(c=>{
      const opt = document.createElement("option");
      opt.value = c; opt.textContent = c;
      select.appendChild(opt);
    });
  }

  // initially populate all nationality-dropdowns on page
  document.querySelectorAll('.nationality-dropdown').forEach(s => populateCountriesFor(s));

  // submit handlers for forms - return PDF and auto-open print
  document.querySelectorAll('form').forEach(f => {
    f.addEventListener('submit', async (e)=>{
      e.preventDefault();
      const form = e.target;
      const fd = new FormData(form);
      try {
        const resp = await fetch('/submit_form', { method: 'POST', body: fd });
        if (!resp.ok) {
          const txt = await resp.text();
          alert('Submit failed: ' + resp.status + ' - ' + txt);
          return;
        }
        const blob = await resp.blob();
        const url = URL.createObjectURL(blob);
        // open in new tab and auto-print
        const w = window.open(url, "_blank");
        // Attempt to auto-print by injecting print command after load
        // Note: Some browsers block programmatic print on cross-origin blobs, but most allow.
        w.focus();
        // Give the new window some time to load the PDF
        setTimeout(()=> {
          try { w.print(); } catch (err) { console.warn("Auto print blocked", err); }
        }, 1000);
        form.reset();
        // cleanup client/vehicle extras if tourist form
        if (form.id === 'touristForm') {
          const clientList = document.getElementById('clientList');
          while (clientList.children.length > 1) clientList.removeChild(clientList.lastChild);
          clientCount = 1;
          const vehicleList = document.getElementById('vehicleList');
          while (vehicleList.children.length > 1) vehicleList.removeChild(vehicleList.lastChild);
          vehicleCount = 1;
        }
        alert('Submitted — PDF opened for printing.');
      } catch (err) {
        console.error('Submit error', err);
        alert('Error submitting form. See console.');
      }
    });
  });

});