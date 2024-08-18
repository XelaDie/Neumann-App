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

    document.getElementById('add-company-color').addEventListener('input', function() {
        document.getElementById('color-preview').style.backgroundColor = this.value;
    });

    document.getElementById('edit-company-color').addEventListener('input', function() {
        document.getElementById('color-preview').style.backgroundColor = this.value;
    });
});

function filterEmployees(reset = false) {
    const selectedCompanies = Array.from(document.querySelectorAll('input[name="company"]:checked'))
        .map(checkbox => checkbox.value);
    const searchText = document.getElementById('search-box').value.toLowerCase();

    if (reset) {
        currentPage = 1;
    }

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
        if (!employee.isDeleted) {
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
        }
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
            document.getElementById('details-date_account_created').innerText = employee.date_account_created;
            document.getElementById('details-salary').innerText = `${employee.salary} $`;
            document.getElementById('details-date_of_birth').innerText = employee.date_of_birth;
            document.getElementById('details-job_title').innerText = employee.job_title;
            document.getElementById('details-employment_status').innerText = employee.employment_status;
            if (employee.photo) {
                const photoData = `data:image/jpeg;base64,${employee.photo}`;
                document.getElementById('details-photo').src = photoData;
            } else {
                document.getElementById('details-photo').src = "/static/images/noProfile.jpg";
            }
            document.getElementById('employee-details').style.display = 'flex';
            document.getElementById('employee-details').style.borderColor = employee.color;
            document.getElementById('details-color').style.backgroundColor = employee.color;
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
            filterEmployees();
        } else {
            alert('Error deleting employee');
        }
    });
}

function transformDate(dateString) {
    const dateParts = dateString.split(' ');
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const monthIndex = months.indexOf(dateParts[1]);
    const month = String(monthIndex + 1).padStart(2, '0');
    const day = String(dateParts[0]).padStart(2, '0');
    const year = String(dateParts[2]);
    return `${year}-${month}-${day}`;
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
        document.getElementById('edit-job_title').value = employee.job_title;
        document.getElementById('edit-employment_status').value = employee.employment_status;
        document.getElementById('edit-salary').value = employee.salary;
        document.getElementById('edit-date_of_birth').value = transformDate(employee.date_of_birth);
        document.getElementById('edit-employee-modal').style.display = 'block';
    });
}

function closeEditModal() {
    document.getElementById('edit-employee-modal').style.display = 'none';
    document.querySelectorAll('.error-message').forEach(el => el.textContent = '');
}
function showEditConfirmationModal() {
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
    document.getElementById('edit-confirmation-modal').style.display = 'block';
}

function closeEditConfirmationModal() {
    document.getElementById('edit-confirmation-modal').style.display = 'none';
}

function saveEmployeeChanges() {
    const form = document.getElementById('edit-employee-form');
    const formData = new FormData(form);

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
    const employeeJobTitle = document.getElementById('details-job_title').innerText;
    const employeeEmploymentStatus = document.getElementById('details-employment_status').innerText;
    const employeeSalary = document.getElementById('details-salary').innerText;
    const employeeDateOfBirth = document.getElementById('details-date_of_birth').innerText;
    const employeeAddress = document.getElementById('details-address').innerText;
    const employeeCity = document.getElementById('details-city').innerText;
    const employeeCounty = document.getElementById('details-county').innerText;
    const employeeDateAccountCreated = document.getElementById('details-date_account_created').innerText;

    const employeeDetails = `Name: ${employeeName}\nCompany: ${employeeCompany}\nJob Title: ${employeeJobTitle}\nEmployment Status: ${employeeEmploymentStatus}\nSalary: ${employeeSalary}\nDate of Birth: ${employeeDateOfBirth}\nAddress: ${employeeAddress}\nCity: ${employeeCity}\nCounty: ${employeeCounty}\nDate Account Created: ${employeeDateAccountCreated}`;

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

let deleteCompanyId = null;

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

function showAddCompanyModal() {
    document.getElementById('add-company-modal').style.display = 'block';
    document.getElementById('add-company-error').textContent = '';
    const companyMaps = document.getElementsByClassName('company-map');
    Array.from(companyMaps).forEach(map => {
        map.style.zIndex = -1;
    });
}

function closeAddCompanyModal() {
    document.getElementById('add-company-modal').style.display = 'none';
    const companyMaps = document.getElementsByClassName('company-map');
    Array.from(companyMaps).forEach(map => {
        map.style.zIndex = 1;
    });
}

function showEditCompanyModal(id, name, color) {
    document.getElementById('edit-company-id').value = id;
    document.getElementById('edit-company-name').value = name;
    document.getElementById('edit-company-color').value = color;
    document.getElementById('edit-company-error').textContent = '';
    document.getElementById('edit-company-modal').style.display = 'block';
    const companyMaps = document.getElementsByClassName('company-map');
    Array.from(companyMaps).forEach(map => {
        map.style.zIndex = -1;
    });
}

function closeEditCompanyModal() {
    document.getElementById('edit-company-modal').style.display = 'none';
    const companyMaps = document.getElementsByClassName('company-map');
    Array.from(companyMaps).forEach(map => {
        map.style.zIndex = 1;
    });
}

function submitAddCompanyForm(event) {
    event.preventDefault();
    const form = event.target;
    fetch('/add_company', {
        method: 'POST',
        body: new FormData(form)
    }).then(response => response.json())
      .then(data => {
          if (!data.success) {
              document.getElementById('add-company-error').textContent = data.message;
          } else {
              closeAddCompanyModal();
              location.reload();
          }
      });
}

function submitEditCompanyForm(event) {
    event.preventDefault();
    const form = event.target;
    fetch('/update_company', {
        method: 'POST',
        body: new FormData(form)
    }).then(response => response.json())
      .then(data => {
          if (!data.success) {
              document.getElementById('edit-company-error').textContent = data.message;
          } else {
              closeEditCompanyModal();
              location.reload();
          }
      });
}

function showDeleteCompanyModal(id) {
    document.getElementById('delete-company-id').value = id;
    document.getElementById('delete-company-modal').style.display = 'block';
    const companyMaps = document.getElementsByClassName('company-map');
    Array.from(companyMaps).forEach(map => {
        map.style.zIndex = -1;
    });
}

function closeDeleteCompanyModal() {
    document.getElementById('delete-company-modal').style.display = 'none';
    const companyMaps = document.getElementsByClassName('company-map');
    Array.from(companyMaps).forEach(map => {
        map.style.zIndex = 1;
    });
}

let currentProjectId;

document.getElementById('statistic-select').addEventListener('change', updateChart);
document.getElementById('start-date').addEventListener('change', updateChart);
document.getElementById('end-date').addEventListener('change', updateChart);
document.getElementById('company-filter-form').addEventListener('change', updateChart);

function updateChart() {
    const startDate = document.getElementById('start-date').value || null;
    const endDate = document.getElementById('end-date').value || null;
    const companyIds = Array.from(document.querySelectorAll('#company-filter-form input[name="company"]:checked')).map(checkbox => checkbox.value);
    const statistic = document.getElementById('statistic-select').value;

    fetch('/fetch_filtered_projects', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ date_range: { start: startDate, end: endDate }, company_ids: companyIds, statistic })
    })
    .then(response => response.json())
    .then(data => {
        displayChart(data, statistic);
    });
}

let projectChart;

function displayChart(data, statistic) {
    const ctx = document.getElementById('project-chart').getContext('2d');

    if (projectChart) {
        projectChart.destroy();
    }

    let chartData;
    let label;
    let toolTipLabel;

    if (statistic === 'most_expensive') {
        label = 'Budget ($)';
        chartData = data.map(project => project.budget);
        toolTipLabel = (project) => `Budget: ${project.budget}$ - Companies: ${project.companies.join(', ')} - Time Estimation: ${project.time_estimation}d`;
    } else if (statistic === 'longest_duration') {
        label = 'Duration (days)';
        chartData = data.map(project => project.duration);
        toolTipLabel = (project) => `Duration: ${project.duration} days - Companies: ${project.companies.join(', ')} - Budget: ${project.budget}$`;
    } else if (statistic === 'most_employees') {
        label = 'Number of Employees';
        chartData = data.map(project => project.employee_count);
        toolTipLabel = (project) => `Employees: ${project.employee_count} - Companies: ${project.companies.join(', ')} - Budget: ${project.budget}$ - Time Estimation: ${project.time_estimation}d`;
    } else {
        label = 'Unknown Statistic';
        chartData = [];
        toolTipLabel = () => 'No data available';
    }

    const config = {
        type: 'bar',
        data: {
            labels: data.map(project => project.name),
            datasets: [{
                label: label,
                data: chartData,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const project = data[context.dataIndex];
                            return toolTipLabel(project);
                        }
                    }
                }
            }
        }
    };

    projectChart = new Chart(ctx, config);
    document.getElementById('project-chart').style.width = "100%"
    document.getElementById('project-chart').style.height = "270px"
}

document.addEventListener('DOMContentLoaded', function() {
    displayChart([], 'most_expensive');
});

function showAddProjectModal() {
    document.getElementById('add-project-modal').style.display = 'block';
}

function closeAddProjectModal() {
    document.getElementById('add-project-modal').style.display = 'none';
}

function submitAddProject() {
    const form = document.getElementById('add-project-form');
    const formData = new FormData(form);
    let isValid = true;

    document.querySelectorAll('.error-message').forEach(el => el.textContent = '');
    for (let [key, value] of formData.entries()) {
        if (!value) {
            document.getElementById(`add-${key}-error`).textContent = '*Required';
            isValid = false;
        }
    }
    if (!isValid) return;

    fetch('/add_project', {
        method: 'POST',
        body: formData
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              closeAddProjectModal();
              location.reload();
          } else {
              document.getElementById('add-project-error').textContent = data.message;
          }
      });
}

function showEditProjectModal(id, name, description, start_date, end_date, budget, time_estimation, companyIds) {
    console.log(end_date - start_date)
    document.getElementById('edit-project-id').value = id;
    document.getElementById('edit-project-name').value = name;
    document.getElementById('edit-project-description').value = description;
    document.getElementById('edit-project-start-date').value = start_date;
    document.getElementById('edit-project-end-date').value = end_date;
    document.getElementById('edit-project-budget').value = budget;
    document.getElementById('edit-project-time-estimation').value = time_estimation;

    const companySelect = document.getElementById('edit-project-companies');
    for (const option of companySelect.options) {
        option.selected = companyIds.includes(option.value);
    }

    document.getElementById('edit-project-modal').style.display = 'block';
}

function closeEditProjectModal() {
    document.getElementById('edit-project-modal').style.display = 'none';
}

function showEditConfirmationModal() {
    const form = document.getElementById('edit-project-form');
    const formData = new FormData(form);
    let isValid = true;

    document.querySelectorAll('.error-message').forEach(el => el.textContent = '');
    for (let [key, value] of formData.entries()) {
        if (!value) {
            document.getElementById(`edit-${key}-error`).textContent = '*Required';
            isValid = false;
        }
    }
    if (!isValid) return;

    document.getElementById('edit-confirmation-modal').style.display = 'block';
}

function closeEditConfirmationModal() {
    document.getElementById('edit-confirmation-modal').style.display = 'none';
}

function submitEditProject() {
    const form = document.getElementById('edit-project-form');
    const formData = new FormData(form);

    fetch('/update_project', {
        method: 'POST',
        body: formData
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              closeEditProjectModal();
              location.reload();
          } else {
              document.getElementById('edit-project-error').textContent = data.message;
          }
      });
}

function confirmDeleteProject(id) {
    currentProjectId = id;
    document.getElementById('delete-project-modal').style.display = 'block';
}

function closeDeleteProjectModal() {
    document.getElementById('delete-project-modal').style.display = 'none';
}

function deleteProject() {
    fetch(`/delete_project/${currentProjectId}`, {
        method: 'POST'
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              closeDeleteProjectModal();
              location.reload();
          } else {
              alert('Failed to delete project.');
          }
      });
}

function showLinkEmployeesModal(projectId, companyNames, selectedEmployeeIds = []) {
    const companyIds = getCompanyIdsByName(companyNames.split(', '));

    fetch(`/fetch_employees_by_companies`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ company_ids: companyIds })
    }).then(response => response.json())
      .then(data => {
          const employeeSelect = document.getElementById('link-project-employees');
          employeeSelect.innerHTML = '';
          data.employees.forEach(employee => {
              const option = document.createElement('option');
              option.value = employee.id;
              option.textContent = `${employee.fname} ${employee.lname}`;
              if (selectedEmployeeIds.includes(employee.id.toString())) {
                  option.selected = true;
              }
              employeeSelect.appendChild(option);
          });
          document.getElementById('link-project-id').value = projectId;
          document.getElementById('link-employees-modal').style.display = 'block';
      });
}

function closeLinkEmployeesModal() {
    document.getElementById('link-employees-modal').style.display = 'none';
}

function submitLinkEmployees() {
    const form = document.getElementById('link-employees-form');
    const formData = new FormData(form);

    fetch('/link_employees_to_project', {
        method: 'POST',
        body: formData
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              closeLinkEmployeesModal();
              location.reload();
          } else {
              alert('Failed to link employees.');
          }
      });
}

function getCompanyIdsByName(companyNames) {
    const companySelect = document.getElementById('project-companies');
    const companyIds = [];
    companyNames.forEach(name => {
        for (const option of companySelect.options) {
            if (option.textContent === name) {
                companyIds.push(option.value);
                break;
            }
        }
    });
    return companyIds;
}