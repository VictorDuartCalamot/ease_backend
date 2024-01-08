  // Import the functions you need from the SDKs you need
require('dotenv').config();
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
//import { getFirestore } from 'firebase/firestore';
import firebase from 'firebase/compat/app';
import 'firebase/compat/auth';
import 'firebase/compat/firestore';
import { initializeFirestore, getFirestore } from "firebase/firestore";
import Constants from "expo-constants";
//import { getAnalytics } from "firebase/analytics";

// TODO: Add SDKs for Firebase prºoducts that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: process.env.API_KEY,
  authDomain: process.env.AUTH_DOMAIN,
  projectId: process.env.PROJECT_ID,
  storageBucket: process.env.STORAGE_BUCKET,
  messagingSenderId: process.env.MESSAGING_SENDER_ID,
  appId: process.env.APP_ID,
  measurementId: process.env.MEASUREMENT_ID,
  databaseUrl: process.env.DATABASE_URL,
};

// Initialize Firebase
//const analytics = getAnalytics(app);
if (!firebase.apps.length){
  firebase.initializeApp(firebaseConfig);
}
export {firebase};

const firebaseApp = initializeApp(firebaseConfig);
export const firebaseAuth = getAuth(firebaseApp);
export const database = getFirestore(firebaseApp);
/*export const database = initializeFirestore(firebaseApp, {
  experimentalForceLongPolling: true,
});

*/

