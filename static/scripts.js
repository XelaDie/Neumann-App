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
    }, 2000);
}

document.addEventListener('DOMContentLoaded', loading);

function showDetails(userId, boxElement) {
    currentUserId = userId;

    if (selectedBox) {
        selectedBox.classList.remove('selected');
    }

    boxElement.classList.add('selected');
    selectedBox = boxElement;

    document.querySelector('.grid-container').style.gridTemplateColumns = 'repeat(2, 1fr)';
    document.querySelector('.grid-container').style.width = '75%';

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
    document.querySelector('.grid-container').style.width = '100%';
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
