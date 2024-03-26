function validateForm() {
    var username = document.getElementById('username').value.trim();
    var password = document.getElementById('password').value.trim();
    var usernameError = document.getElementById('usernameError');
    var passwordError = document.getElementById('passwordError');
    var isValid = true;

    // Reset error messages
    usernameError.textContent = '';
    passwordError.textContent = '';

    // Validate username/email
    if (username === '') {
      usernameError.textContent = 'Username/Email is required';
      isValid = false;
    }

    // Validate password
    if (password === '') {
      passwordError.textContent = 'Password is required';
      isValid = false;
    } else if (password.length < 8) {
      passwordError.textContent = 'Password must be at least 8 characters long';
      isValid = false;
    }

    // Additional password validation rules can be added here

    return isValid;
  }

  function login() {
    // Gather the data from the form
    const userData = {
        username: document.getElementById('username').value,
        password: document.getElementById('password').value,
    };

    // Send the data to the server for authentication
    fetch('http://localhost:3000/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Login failed');
        }
    })
    .then(data => {
        console.log(data.message); // Message from server
        alert(`Login successful: ${data.message}`);
        // Redirect to the dashboard or homepage after successful login
        window.location.href = 'dashboard.html'; // Replace 'dashboard.html' with the actual URL of your dashboard page
    })
    .catch(error => {
        console.error('Login failed:', error.message);
        alert('Login failed. Please check your credentials and try again.');
    });
}

