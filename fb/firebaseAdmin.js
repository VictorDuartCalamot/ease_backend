const admin = require('react-admin-firebase');
const serviceAccount = require('./firebase_key.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: 'https://ease-8d84a-default-rtdb.europe-west1.firebasedatabase.app', // replace with your database URL
});

