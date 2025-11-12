document.addEventListener("DOMContentLoaded", () => {
  const addBtn = document.getElementById("addBtn");
  const nameInput = document.getElementById("nameInput");
  const placeInput = document.getElementById("placeInput");
  const statusInput = document.getElementById("statusInput");
  const dutyTable = document.querySelector("#dutyTable tbody");

  function createRow(name, place, status) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${name}</td>
      <td>${place}</td>
      <td>${status}</td>
      <td>
        <button class="btn btn-edit">Edit</button>
        <button class="btn btn-delete">Delete</button>
      </td>
    `;

    // Edit
    row.querySelector(".btn-edit").addEventListener("click", () => editRow(row));
    // Delete
    row.querySelector(".btn-delete").addEventListener("click", () => row.remove());

    dutyTable.appendChild(row);
  }

  function editRow(row) {
    const nameCell = row.children[0];
    const placeCell = row.children[1];
    const statusCell = row.children[2];

    const name = nameCell.textContent;
    const place = placeCell.textContent;
    const status = statusCell.textContent;

    nameCell.innerHTML = `<input type="text" value="${name}" />`;
    placeCell.innerHTML = `
      <select>
        <option>Front Gate</option>
        <option>Back Gate</option>
        <option>Library</option>
        <option>RTL Building</option>
        <option>NGE Building</option>
        <option>ALLIED Building</option>
        <option>GLE Building</option>
      </select>
    `;
    statusCell.innerHTML = `
      <select>
        <option>Unassigned</option>
        <option>On Duty</option>
        <option>On Break</option>
        <option>Off Duty</option>
        <option>Absent</option>
      </select>
    `;

    placeCell.querySelector("select").value = place;
    statusCell.querySelector("select").value = status;

    const editBtn = row.querySelector(".btn-edit");
    editBtn.textContent = "Save";
    editBtn.classList.add("btn-save");

    editBtn.onclick = () => {
      const newName = nameCell.querySelector("input").value;
      const newPlace = placeCell.querySelector("select").value;
      const newStatus = statusCell.querySelector("select").value;

      nameCell.textContent = newName;
      placeCell.textContent = newPlace;
      statusCell.textContent = newStatus;

      editBtn.textContent = "Edit";
      editBtn.classList.remove("btn-save");
      editBtn.onclick = () => editRow(row);
    };
  }

  addBtn.addEventListener("click", () => {
    const name = nameInput.value.trim();
    const place = placeInput.value;
    const status = statusInput.value;

    if (!name || !place) {
      alert("Please fill in all fields.");
      return;
    }

    createRow(name, place, status);
    nameInput.value = "";
    placeInput.value = "";
    statusInput.value = "Unassigned";
  });
});
