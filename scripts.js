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
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const university = document.getElementById('university').value;

    if (university === 'university1' && email && password) {
      // Redirect to my.asu.edu
      window.location.href = 'https://my.asu.edu';
    } else {
      alert('Invalid credentials or university selection.');
    }
  }
