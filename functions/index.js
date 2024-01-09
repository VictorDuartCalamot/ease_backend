import * as dbUtil from "./dbUtils";
const functions = require('firebase-functions');
const admin = require('firebase-admin');

var serviceAccount = require("../fb/firebase_key.json");

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: "https://ease-8d84a-default-rtdb.europe-west1.firebasedatabase.app"
});

const express = require('express');
const app = express();  

const cors = require('cors');
app.use(cors({origin:true}));

//Routes
app.get("/",(req,res) => {
    return res.status(200).send("Operation successful");
});

//Create -> post()
app.post("/api/createUser",(req,res) => {
    (async () => {
        try {
            await dbUtil.registerUser(req.body.nif,req.body.companyName, req.body.username, req.body.surname, req.body.email, req.body.password, req.body.isBusinessAccount);
            return res.status(200).send();
        } catch (error) {
            console.error("Error adding document: ", error);
        }
    })

    
});

//get -> get()

//Update -> update()

//Delete -> delete()


//exports the api route to firebase cloud functions

exports.app = functions.https.onRequest(app);


