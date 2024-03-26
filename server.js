const express = require('express');
const cors = require('cors');
const bcrypt = require('bcrypt');
const session = require('express-session');
const mongoose = require('./database'); // Import your database connection
const User = require('./user'); // Import your User model

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(session({
  secret: 'yourSecretKey',
  resave: true,
  saveUninitialized: false
}));

// Signup route
app.post('/signup', async (req, res) => {
  try {
    const { username, password } = req.body;
    const user = new User({ username, password });
    await user.save();
    res.status(201).json({ message: 'User created' });

  } catch (error) {
    res.status(500).json({ success: false, message: 'Error creating user' });
  }
});

// Login route
app.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    const user = await User.findOne({ username });
    if (!user || !await bcrypt.compare(password, user.password)) {
      return res.status(401).json({ message: 'Authentication failed' });
    }
    req.session.userId = user._id; // Save user id to session
    res.status(200).json({ message: 'Logged in successfully' }); 
  } catch (error) {
    res.status(500).json({ message: error.message }); 
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
