// Show form based on visitor type
function showSection() {
  const type = document.getElementById("visitorType").value;
  document.getElementById("touristForm").classList.add("hidden");
  document.getElementById("transitForm").classList.add("hidden");
  document.getElementById("studentForm").classList.add("hidden");

  if (type === "tourist")
    document.getElementById("touristForm").classList.remove("hidden");
  if (type === "transit")
    document.getElementById("transitForm").classList.remove("hidden");
  if (type === "student")
    document.getElementById("studentForm").classList.remove("hidden");
}

// Show "Other" accommodation field
function checkOtherAccommodation(select) {
  const input = document.getElementById("otherAccommodation");
  input.classList.toggle("hidden", select.value !== "Other");
}

// Tour companies (sample)
const tourCompanies = [
  "Matoke Tours Ltd",
  "Take Off Safaris Uganda Ltd",
  "Tulavo",
  "Go Gorilla Trekking",
  "Wild Frontiers Safaris",
  "Marasa Safari Lodge",
  "Murchison River Lodge"
];

// Handle tour company option
function onCompanyOptionChange() {
  const opt = document.getElementById("companyOption").value;
  const div = document.getElementById("companySelectDiv");

  if (opt === "Company") {
    div.style.display = "block";
    document.getElementById("companySelect").required = true;
  } else {
    div.style.display = "none";
    document.getElementById("companySelect").required = false;
    document.getElementById("companySelect").value = "";
    document.getElementById("companyOptionsList").innerHTML = "";
  }
}

// Autocomplete company field
document.getElementById("companySelect").addEventListener("input", (e) => {
  const val = e.target.value.toLowerCase();
  const listDiv = document.getElementById("companyOptionsList");
  listDiv.innerHTML = "";
  if (val.length < 2) return;

  const matches = tourCompanies.filter((c) => c.toLowerCase().includes(val));
  matches.forEach((match) => {
    const el = document.createElement("div");
    el.textContent = match;
    el.onclick = () => {
      document.getElementById("companySelect").value = match;
      listDiv.innerHTML = "";
    };
    listDiv.appendChild(el);
  });
});