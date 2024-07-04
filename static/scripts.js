let currentEmployeeId;
let selectedBox;
let sortState = 0;
let currentPage = 1;
const itemsPerPage = 10;
let totalEmployees = 0;

function loading() {
    document.body.classList.add('hidden-content');
    const loadingScreen = document.getElementById('loading-screen');
    loadingScreen.style.display = 'flex';
    loadingScreen.classList.add('fade-in');

    setTimeout(() => {
        loadingScreen.classList.remove('fade-in');
        loadingScreen.classList.add('fade-out');

        loadingScreen.addEventListener('animationend', () => {
            loadingScreen.style.display = 'none';
            document.body.classList.remove('hidden-content');
            localStorage.setItem('loadingScreenShown', 'true');
        }, { once: true });
    }, 1000);
}

document.addEventListener('DOMContentLoaded', function() {
    if (!localStorage.getItem('loadingScreenShown')) {
        loading();
    } else {
        document.body.classList.remove('hidden-content');
    }

    const form = document.getElementById('company-filter-form');
    form.addEventListener('change', filterEmployees);

    const searchBox = document.getElementById('search-box');
    searchBox.addEventListener('input', filterEmployees);
});

function filterEmployees(reset = false) {
    const selectedCompanies = Array.from(document.querySelectorAll('input[name="company"]:checked'))
        .map(checkbox => checkbox.value);
    const searchText = document.getElementById('search-box').value.toLowerCase();

    if(reset){ currentPage = 1 }

    fetch('/filter_employees', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ companies: selectedCompanies, searchText: searchText, sortState: sortState, page: currentPage, itemsPerPage: itemsPerPage })
    })
    .then(response => response.json())
    .then(data => {
        totalEmployees = data.totalEmployees;
        updateGrid(data.employees);
        updatePaginationButtons();
    });
}

function updateGrid(employees) {
    const employeeGrid = document.querySelector('.grid-container');
    employeeGrid.innerHTML = '';

    employees.forEach(employee => {
        const gridItem = document.createElement('div');
        gridItem.classList.add('grid-item');
        gridItem.onclick = () => showDetails(employee.id, gridItem);

        const img = document.createElement('img');
        img.alt = 'Employee Photo';
        img.width = 100;
        img.src = employee.photo ? `data:image/jpeg;base64,${employee.photo}` : '/static/images/noProfile.jpg';

        const employeeInfo = document.createElement('div');
        employeeInfo.classList.add('employee-info');

        const employeeName = document.createElement('p');
        employeeName.classList.add('employee-name');
        employeeName.textContent = `${employee.fname} ${employee.lname}`;

        const employeeCompany = document.createElement('p');
        employeeCompany.classList.add('employee-company');
        employeeCompany.textContent = employee.company;

        employeeInfo.appendChild(employeeName);
        employeeInfo.appendChild(employeeCompany);

        const employeeColor = document.createElement('div');
        employeeColor.classList.add('employee-color');
        employeeColor.style.backgroundColor = employee.color;

        gridItem.appendChild(img);
        gridItem.appendChild(employeeInfo);
        gridItem.appendChild(employeeColor);

        employeeGrid.appendChild(gridItem);
    });
}

function updatePaginationButtons() {
    const totalPages = Math.ceil(totalEmployees / itemsPerPage);
    const paginationButtons = document.getElementById('pagination-buttons');
    paginationButtons.innerHTML = '';

    for (let i = 1; i <= totalPages; i++) {
        const button = document.createElement('button');
        button.textContent = i;
        button.onclick = () => changePage(i);
        button.className = 'page-button';
        if (i === currentPage) {
            button.classList.add('active');
        }
        paginationButtons.appendChild(button);
    }

    document.getElementById('prev-page').disabled = currentPage === 1;
    document.getElementById('next-page').disabled = currentPage === totalPages;
}

function changePage(page) {
    if (page === 'prev' && currentPage > 1) {
        currentPage--;
    } else if (page === 'next' && currentPage < Math.ceil(totalEmployees / itemsPerPage)) {
        currentPage++;
    } else if (typeof page === 'number') {
        currentPage = page;
    }
    filterEmployees();
}

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('company-filter-form');
    form.addEventListener('change', filterEmployees(true));

    const searchBox = document.getElementById('search-box');
    searchBox.addEventListener('input', filterEmployees(true));
    
    filterEmployees();
});

function toggleSort() {
    sortState = (sortState + 1) % 3;

    const sortIcon = document.getElementById('sort-icon');
    if (sortState === 0) {
        sortIcon.src = "/static/images/sort-regular.png";
    } else if (sortState === 1) {
        sortIcon.src = "/static/images/sort-asc.png";
    } else {
        sortIcon.src = "/static/images/sort-desc.png";
    }

    filterEmployees();
}

function showDetails(employeeId, boxElement) {
    currentEmployeeId = employeeId;

    if (selectedBox) {
        selectedBox.classList.remove('selected');
    }

    boxElement.classList.add('selected');
    selectedBox = boxElement;

    document.querySelector('.grid-container').style.gridTemplateColumns = 'repeat(2, 1fr)';
    document.querySelector('.grid-container').style.width = '55%';

    fetch(`/employee/${employeeId}`)
        .then(response => response.json())
        .then(employee => {
            document.getElementById('details-name').innerText = `${employee.fname} ${employee.lname}`;
            document.getElementById('details-name').style.color = employee.color;
            document.getElementById('details-company').innerText = employee.company;
            document.getElementById('details-address').innerText = employee.address;
            document.getElementById('details-city').innerText = employee.city;
            document.getElementById('details-county').innerText = employee.county;
            document.getElementById('details-color').style.backgroundColor = employee.color;
            if (employee.photo) {
                const photoData = `data:image/jpeg;base64,${employee.photo}`;
                document.getElementById('details-photo').src = photoData;
            }
            else{
                document.getElementById('details-photo').src = "/static/images/noProfile.jpg"
            }
            document.getElementById('employee-details').style.display = 'flex';
            document.getElementById('employee-details').style.borderColor = employee.color;
        });
}

function closeDetails() {
    document.getElementById('employee-details').style.display = 'none';

    if (selectedBox) {
        selectedBox.classList.remove('selected');
    }

    document.querySelector('.grid-container').style.gridTemplateColumns = 'repeat(3, 1fr)';
    document.querySelector('.grid-container').style.width = '78%';
}

function confirmDelete() {
    document.getElementById('delete-employee-modal').style.display = 'block';
}

function closeDeleteModal() {
    document.getElementById('delete-employee-modal').style.display = 'none';
}

function deleteEmployee() {
    fetch(`/delete_employee/${currentEmployeeId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closeDeleteModal();
            closeDetails();
            location.reload();
        } else {
            alert('Error deleting employee');
        }
    });
}

function showEditModal() {
    fetch(`/employee/${currentEmployeeId}`)
    .then(response => response.json())
    .then(employee => {
        document.getElementById('edit-employee-id').value = employee.id;
        document.getElementById('edit-fname').value = employee.fname;
        document.getElementById('edit-lname').value = employee.lname;
        document.getElementById('edit-address').value = employee.address;
        document.getElementById('edit-city').value = employee.city;
        document.getElementById('edit-county').value = employee.county;
        document.getElementById('edit-company').value = employee.company;
    
        document.getElementById('edit-employee-modal').style.display = 'block';
    });
}

function closeEditModal() {
    document.getElementById('edit-employee-modal').style.display = 'none';
    document.querySelectorAll('.error-message').forEach(el => el.textContent = '');
}
function showEditConfirmationModal() {
    document.getElementById('edit-confirmation-modal').style.display = 'block';
}

function closeEditConfirmationModal() {
    document.getElementById('edit-confirmation-modal').style.display = 'none';
}

function saveEmployeeChanges() {
    const form = document.getElementById('edit-employee-form');
    const formData = new FormData(form);
    let isValid = true;

    document.querySelectorAll('.error-message').forEach(el => el.textContent = '');
    for (let [key, value] of formData.entries()) {
        if (!value && key !== 'photo') {
            document.getElementById(`edit-${key}-error`).textContent = '*Required';
            isValid = false;
        }
    }
    if (!isValid) return;

    const companyColors = {
        'Benton': '#8bc447',
        'Chanay': '#8a3b93',
        'Chemel': '#1473bb',
        'Feltz Printing': '#c32482',
        'Commercial Press': '#dde553'
    };

    formData.append('color', companyColors[formData.get('company')]);

    fetch('/update_employee', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closeEditModal();
            location.reload();
        } else {
            alert('Error updating employee');
        }
    });
}

function shareEmployee() {
    const employeeName = document.getElementById('details-name').innerText;
    const employeeCompany = document.getElementById('details-company').innerText;
    const employeeAddress = document.getElementById('details-address').innerText;
    const employeeCity = document.getElementById('details-city').innerText;
    const employeeCounty = document.getElementById('details-county').innerText;

    const employeeDetails = `Name: ${employeeName}\nCompany: ${employeeCompany}\nAddress: ${employeeAddress}\nCity: ${employeeCity}\nCounty: ${employeeCounty}`;

    navigator.clipboard.writeText(employeeDetails).then(() => {
        alert('Employee details copied to clipboard');
    }).catch(err => {
        console.error('Error copying text: ', err);
    });
}

function showAddModal() {
    document.getElementById('add-employee-modal').style.display = 'block';
}

function closeAddModal() {
    document.getElementById('add-employee-modal').style.display = 'none';
    document.querySelectorAll('.error-message').forEach(el => el.textContent = '');
}

function submitAddEmployee() {
    const form = document.getElementById('add-employee-form');
    const formData = new FormData(form);
    let isValid = true;

    document.querySelectorAll('.error-message').forEach(el => el.textContent = '');
    for (let [key, value] of formData.entries()) {
        if (!value && key !== 'photo') {
            document.getElementById(`add-${key}-error`).textContent = '*Required';
            isValid = false;
        }
    }
    if (!isValid) return;

    const companyColors = {
        'Benton': '#8bc447',
        'Chanay': '#8a3b93',
        'Chemel': '#1473bb',
        'Feltz Printing': '#c32482',
        'Commercial Press': '#dde553'
    };

    formData.append('color', companyColors[formData.get('company')]);

    fetch('/add_employee', {
        method: 'POST',
        body: formData
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              closeAddModal();
              location.reload();
          } else {
              alert('Failed to add employee.');
          }
      });
}

let editCompanyId = null;
let deleteCompanyId = null;

function showManageCompaniesModal() {
    document.getElementById('manage-companies-modal').style.display = 'block';
    fetchCompanies();
}

function closeManageCompaniesModal() {
    document.getElementById('manage-companies-modal').style.display = 'none';
    document.querySelectorAll('.error-message').forEach(el => el.textContent = '');
    location.reload();
}

function fetchCompanies() {
    fetch('/companies')
        .then(response => response.json())
        .then(data => {
            const companyList = document.getElementById('company-list');
            companyList.innerHTML = '';
            data.forEach(company => {
                const companyItem = document.createElement('div');
                companyItem.style.borderLeft = `10px solid ${company.color}`;
                companyItem.style.display = 'flex';
                companyItem.style.alignItems = 'center';
                companyItem.style.marginBottom = '10px';

                const companyName = document.createElement('span');
                companyName.textContent = company.name;
                companyName.style.marginRight = '10px';
                companyName.style.marginLeft = '10px';

                const editButton = document.createElement('button');
                editButton.textContent = 'Edit';
                editButton.style.marginRight = '10px';
                editButton.onclick = () => showEditCompanyModal(company.id, company.name, company.color, companyName, editButton);

                const deleteButton = document.createElement('button');
                deleteButton.textContent = 'Delete';
                deleteButton.style.marginRight = '10px';
                deleteButton.onclick = () => showDeleteCompanyModal(company.id);

                companyItem.appendChild(companyName);
                companyItem.appendChild(editButton);
                companyItem.appendChild(deleteButton);
                companyList.appendChild(companyItem);
            });
        });
}

function addCompany() {
    const name = document.getElementById('company-name').value;
    const color = document.getElementById('company-color').value;

    document.querySelectorAll('.error-message').forEach(el => el.textContent = '');

    if (!name || !color) {
        if (!name) document.getElementById('company-name-error').textContent = '*Required';
        if (!color) document.getElementById('company-color-error').textContent = '*Required';
        return;
    }

    fetch('/add_company', {
        method: 'POST',
        body: new URLSearchParams(new FormData(document.getElementById('add-company-form')))
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            fetchCompanies();
            document.getElementById('add-company-form').reset();
        } else {
            alert('Failed to add company.');
        }
    });
}

function showEditCompanyModal(id, name, color, companyNameElement, editButton) {
    editCompanyId = id;
    companyNameElement.innerHTML = `<input type="text" id="edit-company-name" value="${name}" required>
                                    <input type="color" id="edit-company-color" value="${color}" required>`;
    editButton.textContent = 'Save';
    editButton.onclick = () => editCompany(id, companyNameElement, editButton);
}

function editCompany(id, companyNameElement, editButton) {
    const name = document.getElementById('edit-company-name').value;
    const color = document.getElementById('edit-company-color').value;

    if (!name || !color) {
        if (!name) document.getElementById('company-name-error').textContent = '*Required';
        if (!color) document.getElementById('company-color-error').textContent = '*Required';
        return;
    }

    fetch('/update_company', {
        method: 'POST',
        body: new URLSearchParams({id, name, color})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            companyNameElement.textContent = name;
            companyNameElement.style.borderLeft = `10px solid ${color}`;
            editButton.textContent = 'Edit';
            editButton.onclick = () => showEditCompanyModal(id, name, color, companyNameElement, editButton);
            fetchCompanies();
        } else {
            alert('Failed to edit company.');
        }
    });
}

function showDeleteCompanyModal(id) {
    deleteCompanyId = id;
    document.getElementById('delete-company-modal').style.display = 'block';
}

function closeDeleteCompanyModal() {
    document.getElementById('delete-company-modal').style.display = 'none';
}

function deleteCompany() {
    fetch('/delete_company', {
        method: 'POST',
        body: new URLSearchParams({id: deleteCompanyId})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closeDeleteCompanyModal();
            fetchCompanies();
        } else {
            alert('Failed to delete company.');
        }
    });
}