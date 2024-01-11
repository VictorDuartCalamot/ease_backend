//#################
//#####  API  #####
//#################
//
const functions = require("firebase-functions");
const admin = require("firebase-admin");
const cors = require("cors");
const express = require("express");
const { doc, getDoc, setDoc, collection } = require('firebase/firestore'); // Import getDoc from @firebase/firestore
const { createUserWithEmailAndPassword} = require('firebase/auth');
//
const serviceAccount = require("../fb/firebase_key.json");// Will need to secure later on
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
// Routes
app.get("/", (req, res) => {
  return res.status(200).send("Operation successful");
});
// Create -> post()
app.post("/api/createUser", async (req, res) => {
  try {
    // Create user in firebase authentication    
    await dbAuth.createUser({
      email: req.body.email, 
      password: req.body.password    
    }).then(async (UserRec) => {
      const user = UserRec;
    // Depending on account type the user will be given a role or other
    let roleName;
    if (req.body.isBusinessAccount) {
      try {
        const businessRoleCollectionRef = collection(db,"business_role");
        const businessRoleDocRef = doc(businessRoleCollectionRef, "accountManager");
        const BuesinessRoleDocSnap = await getDoc(businessRoleDocRef);
        if (BuesinessRoleDocSnap.exists()){
          roleName = BuesinessRoleDocSnap.get("roleName");
        }else{
          console.error("Document 'accountManager' does not exist in the 'business_role' collection");
        }        
      } catch (e) {
        console.error("Error checking the role accountManager " + e);
      }
    } else {
      try {
        const userRoleCollectionRef = collection(db,"role");
        const userRoleDocRef = doc(userRoleCollectionRef, "user");
        const userRoleDocSnap = await getDoc(userRoleDocRef);
        if (userRoleDocSnap.exists()){
          roleName = userRoleDocSnap.get("roleName");
        }else{
          console.error("Document 'user' does not exist in the 'role' collection");
        } 
        
      } catch (e) {
        console.error("Error checking the role user " + e);
      }
    }
    // Create the json
    const userData = {
      username: req.body.username,
      surname: req.body.surname,
      email: req.body.email,
      role: roleName,
      signUpDate: new Date(),
      isBusinessAccount: req.body.isBusinessAccount,
      isPremiumAccount: false,
    };
    // Add field to the json in case it"s a business account
    if (req.body.isBusinessAccount) {
      userData.companyName = req.body.companyName;
      userData.role = { roleName };
    }  
    // Create promises for each asynchronous operation
    const createEmailDocPromise = setDoc(doc(db, "email", req.body.email), { blocked: false });
    const createUserDocPromise = setDoc(doc(db, "user", user.uid), userData);           
    const promises = [createEmailDocPromise,createUserDocPromise];
    if (req.body.isBusinessAccount) {
      // First create the company name document like if it was a user
      const createCompanyDocPromise = setDoc(doc(db, "company", req.body.companyName), {
        companyName: req.body.companyName,
        signUpDate: new Date(),
        nif: req.body.nif,
      });
      promises.push(createCompanyDocPromise);
    }
    // Wait for all promises to complete
    await Promise.all(promises);
      
    });
    
    return res.status(200).send();
  } catch (error) {
    console.error("Error adding document: ", error);
    return res.status(500).send(error);
  }
});
// get -> get()
// Update -> update()
// Delete -> delete()
// exports the api route to firebase cloud functions
exports.app = functions.https.onRequest(app);