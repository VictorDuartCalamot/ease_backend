const functions = require('firebase-functions');
const admin = require('firebase-admin');
const serviceAccount = require('../firebase/firebase_key.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: 'https://ease-8d84a-default-rtdb.europe-west1.firebasedatabase.app', // replace with your database URL
});

const express = require('express');
const cors = require('cors');   

//Main app
const app = express();
app.use(cors({origin:true}));

//Routes
app.get("/",(req,res) => {
    return res.status(200).send("Operation successful");
});

//Create -> post()

//get -> get()

//Update -> update()

//Delete -> delete()


//exports the api route to firebase cloud functions

exports.app = functions.https.onRequest(app);


