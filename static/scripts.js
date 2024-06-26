let currentUserId;
let selectedBox;
let sortState = 0;

function loading() {
    const loadingScreen = document.getElementById('loading-screen');
    loadingScreen.classList.add('fade-in');
    loadingScreen.style.display = 'flex';

    setTimeout(() => {
        loadingScreen.classList.remove('fade-in');
        loadingScreen.classList.add('fade-out');

        loadingScreen.addEventListener('animationend', () => {
            loadingScreen.style.display = 'none';
        }, { once: true });
    }, 1000);
}
document.addEventListener('DOMContentLoaded', loading);

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('company-filter-form');
    form.addEventListener('change', filterUsers);

    const searchBox = document.getElementById('search-box');
    searchBox.addEventListener('input', filterUsers);
});

function filterUsers() {
    const selectedCompanies = Array.from(document.querySelectorAll('input[name="company"]:checked'))
        .map(checkbox => checkbox.value);
    const searchText = document.getElementById('search-box').value.toLowerCase();

    fetch('/filter_users', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ companies: selectedCompanies, searchText: searchText, sortState: sortState })
    })
    .then(response => response.json())
    .then(data => {
        const employeeGrid = document.querySelector('.grid-container');
        employeeGrid.innerHTML = '';

        data.forEach(user => {
            const gridItem = document.createElement('div');
            gridItem.classList.add('grid-item');
            gridItem.onclick = () => showDetails(user.id, gridItem);

            const img = document.createElement('img');
            img.alt = 'User Photo';
            img.width = 100;
            img.src = user.photo ? `data:image/jpeg;base64,${user.photo}` : '/static/images/noProfile.jpg';

            const employeeInfo = document.createElement('div');
            employeeInfo.classList.add('employee-info');

            const employeeName = document.createElement('p');
            employeeName.classList.add('employee-name');
            employeeName.textContent = `${user.fname} ${user.lname}`;

            const employeeCompany = document.createElement('p');
            employeeCompany.classList.add('employee-company');
            employeeCompany.textContent = user.company;

            employeeInfo.appendChild(employeeName);
            employeeInfo.appendChild(employeeCompany);

            const employeeColor = document.createElement('div');
            employeeColor.classList.add('employee-color');
            employeeColor.style.backgroundColor = user.color;

            gridItem.appendChild(img);
            gridItem.appendChild(employeeInfo);
            gridItem.appendChild(employeeColor);

            employeeGrid.appendChild(gridItem);
        });
    });
}

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

    filterUsers();
}

function showDetails(userId, boxElement) {
    currentUserId = userId;

    if (selectedBox) {
        selectedBox.classList.remove('selected');
    }

    boxElement.classList.add('selected');
    selectedBox = boxElement;

    document.querySelector('.grid-container').style.gridTemplateColumns = 'repeat(2, 1fr)';
    document.querySelector('.grid-container').style.width = '55%';

    fetch(`/user/${userId}`)
        .then(response => response.json())
        .then(user => {
            document.getElementById('details-name').innerText = `${user.fname} ${user.lname}`;
            document.getElementById('details-name').style.color = user.color;
            document.getElementById('details-company').innerText = user.company;
            document.getElementById('details-address').innerText = user.address;
            document.getElementById('details-city').innerText = user.city;
            document.getElementById('details-county').innerText = user.county;
            document.getElementById('details-color').style.backgroundColor = user.color;
            if (user.photo) {
                const photoData = `data:image/jpeg;base64,${user.photo}`;
                document.getElementById('details-photo').src = photoData;
            }
            else{
                document.getElementById('details-photo').src = "/static/images/noProfile.jpg"
            }
            document.getElementById('user-details').style.display = 'flex';
            document.getElementById('user-details').style.borderColor = user.color;
        });
}

function closeDetails() {
    document.getElementById('user-details').style.display = 'none';

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
    fetch(`/delete_user/${currentUserId}`, {
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
            alert('Error deleting user');
        }
    });
}

function showEditModal() {
    fetch(`/user/${currentUserId}`)
    .then(response => response.json())
    .then(user => {
        document.getElementById('edit-user-id').value = user.id;
        document.getElementById('edit-fname').value = user.fname;
        document.getElementById('edit-lname').value = user.lname;
        document.getElementById('edit-address').value = user.address;
        document.getElementById('edit-city').value = user.city;
        document.getElementById('edit-county').value = user.county;
        document.getElementById('edit-company').value = user.company;
    
        document.getElementById('edit-employee-modal').style.display = 'block';
    });
}

function closeEditModal() {
    document.getElementById('edit-employee-modal').style.display = 'none';
    document.querySelectorAll('.error-message').forEach(el => el.textContent = '');
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

    fetch('/update_user', {
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
    const userName = document.getElementById('details-name').innerText;
    const userCompany = document.getElementById('details-company').innerText;
    const userAddress = document.getElementById('details-address').innerText;
    const userCity = document.getElementById('details-city').innerText;
    const userCounty = document.getElementById('details-county').innerText;

    const userDetails = `Name: ${userName}\nCompany: ${userCompany}\nAddress: ${userAddress}\nCity: ${userCity}\nCounty: ${userCounty}`;

    navigator.clipboard.writeText(userDetails).then(() => {
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

    fetch('/add_user', {
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