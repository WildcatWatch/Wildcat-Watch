// Select elements
const nameInput = document.getElementById("nameInput");
const placeInput = document.getElementById("placeInput");
const statusInput = document.getElementById("statusInput");
const addBtn = document.getElementById("addBtn");
const dutyTableBody = document.querySelector("#dutyTable tbody");

// Add new duty row
addBtn.addEventListener("click", () => {
  const name = nameInput.value.trim();
  const place = placeInput.value;
  const status = statusInput.value;

  if (name === "" || place === "") {
    alert("Please fill out all fields.");
    return;
  }

  // Create table row
  const row = document.createElement("tr");

  row.innerHTML = `
    <td>${name}</td>
    <td>${place}</td>
    <td>${status}</td>
    <td>
      <button class="action-btn edit-btn">Edit</button>
      <button class="action-btn delete-btn">Delete</button>
    </td>
  `;

  dutyTableBody.appendChild(row);

  // Clear inputs after adding
  nameInput.value = "";
  placeInput.selectedIndex = 0;
  statusInput.selectedIndex = 0;

  attachActionEvents(row);
});

// Attach edit & delete events
function attachActionEvents(row) {
  const editBtn = row.querySelector(".edit-btn");
  const deleteBtn = row.querySelector(".delete-btn");

  // DELETE ROW
  deleteBtn.addEventListener("click", () => {
    if (confirm("Are you sure you want to delete this assignment?")) {
      row.remove();
    }
  });

  // EDIT ROW
  editBtn.addEventListener("click", () => {
    const nameCell = row.children[0];
    const placeCell = row.children[1];
    const statusCell = row.children[2];

    const newName = prompt("Edit Name:", nameCell.textContent);
    const newPlace = prompt("Edit Location:", placeCell.textContent);
    const newStatus = prompt("Edit Status:", statusCell.textContent);

    if (newName && newPlace && newStatus) {
      nameCell.textContent = newName;
      placeCell.textContent = newPlace;
      statusCell.textContent = newStatus;
    }
  });
}
