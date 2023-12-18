const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');

const app = express();

// Middleware
app.use(bodyParser.json());
app.use(cors());

// Routes
app.post('/api/data', (req, res) => {
  // Handle your data here
  const data = req.body;
  // Save to Firebase or perform other backend logic
  // Respond to the client
  res.json({ message: 'Data received successfully' });
});

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
