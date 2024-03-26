// signup.js
function signup(event) {
    event.preventDefault(); // Stop the form from submitting normally

    // Gather the data from the form
    const userData = {
        username: document.getElementById('username').value,
        email: document.getElementById('email').value,
        password: document.getElementById('password').value,
        confirmPassword: document.getElementById('confirmPassword').value,
        university: document.getElementById('university').value
    };

    // Basic validation for example purposes
    if(userData.password !== userData.confirmPassword) {
        alert("Passwords do not match!");
        return;
    }

    // Send the data to the server
    fetch('http://localhost:3000/signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
    })
    .then(response => response.json()) // Assume the server always returns JSON.
    .then(data => {
        if (data.message === 'User created') {
            console.log(data.message); // "User created"
            alert(`Signup complete: ${data.message}`);
            window.location.href = 'index.html';
        } else {
            console.error('Signup failed:', data.message);
            alert(`Signup failed: ${data.message}`);
        }
    })
.catch(error => {
    console.error('Error during fetch:', error);
    alert('Error during signup. Please try again.');
});
}

document.addEventListener('DOMContentLoaded', (event) => {
    document.getElementById('signup-form').addEventListener('submit', signup);
});
