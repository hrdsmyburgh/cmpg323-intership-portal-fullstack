document.addEventListener('DOMContentLoaded', function() {
    const userRole = localStorage.getItem('userRole');

    if (userRole === 'employer') {
        document.getElementById('nav-myapplications')?.remove();
    }
    if (userRole === 'student') {
        document.getElementById('nav-employeradmin')?.remove();
    }

    // Optional: show username in field
    const usernameField = document.getElementById('inputUsername');
    if (usernameField) {
        usernameField.value = localStorage.getItem('username') || '';
    }
});