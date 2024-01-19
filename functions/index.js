//#################
//#####  API  #####
//#### NodeJS #####
//#################
//
const functions = require("firebase-functions");
const admin = require("firebase-admin");
const cors = require("cors");
const express = require("express");
//
const serviceAccount = require("../fb/firebase_key.json");// Will need to secure later on
const { getAuth } = require("firebase-admin/auth");
admin.initializeApp({
  credential: admin.credential.cert(serviceAccount), databaseURL: "https://ease-8d84a-default-rtdb.europe-west1.firebasedatabase.app",
});
//
//
const app = express();  
const db = admin.firestore();
const dbAuth = admin.auth()
app.use(cors({origin: true}));
//
//
const validation = require("./validationUtils");



//
//
// Routes
app.get("/", (req, res) => {
  return res.status(200).send("Operation successful");
});
// Create -> post()

app.post("/api/createUser", async (req, res) => {
  let userUid;
  try {
    //Transaction to rollback in case of errors
    await db.runTransaction(async (transaction) => {
      // Create user in firebase authentication
      if(validation.isValidEmail(req.body.email) && validation.isPasswordValid(req.body.password)){
        const userRecord = await dbAuth.createUser({
          email: req.body.email,
          password: req.body.password,
        });
        // Capture user UID
        userUid = userRecord.uid;      
        const userRoleDocRef = db.collection("role").doc("user");
        const userRoleDocSnapshot = await transaction.get(userRoleDocRef);
        const userRoleData = userRoleDocSnapshot.data().roleName;
  
        const userData = {
          username: req.body.username,
          surname: req.body.surname,
          email: req.body.email,
          role: userRoleData,
          signUpDate: new Date(),
          isPremiumAccount: false,
        };
  
        // Use transaction.set for each document
        transaction.set(db.collection("email").doc(req.body.email), { blocked: false });
        transaction.set(db.collection("user").doc(userUid), userData);
      }
      else{
        return res.status(500).send("Email or password does not meet the requirements");
      }}
      );
      
      

    return res.status(200).send();
  } catch (error) {
    console.error("Error creating user: ", error);

    // If an error occurs, the transaction will automatically be rolled back,
    // and the user won't be created.
    if (userUid) {
      // If user was created, delete the user to roll back authentication
      await dbAuth.deleteUser(userUid);
      console.log("RollBack successfully: " + userUid + " was deleted");
    }
    return res.status(500).send(error);
  }
});


// get -> get()
// Update -> update()
// Delete -> delete()
app.post("/api/deleteUser", async (req, res) => {
  try {
    if (req.body.uid) {
      // If user was created, delete the user to roll back authentication
      await dbAuth.deleteUser(req.body.uid);
       
    }
    return res.status(200).send();
  } catch (error) {
    return res.status(500).send(error);
    
  }

});
// exports the api route to firebase cloud functions
exports.app = functions.https.onRequest(app);