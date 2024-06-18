let currentUserId;
let selectedBox;

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
    form.addEventListener('change', function() {
        const selectedCompanies = Array.from(form.querySelectorAll('input[name="company"]:checked'))
            .map(checkbox => checkbox.value);

        fetch('/filter_users', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ companies: selectedCompanies })
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
    });
});

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
    if (confirm("Are you sure you want to delete this employee?")) {
        fetch(`/delete_user/${currentUserId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('User deleted successfully');
                closeDetails();
                location.reload();
            } else {
                alert('Error deleting user');
            }
        });
    }
}
