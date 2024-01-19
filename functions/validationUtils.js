//Check if the password contains the minimum requirements
function isPasswordValid(password) {
  const hasNumber = /\d/;
  const hasUppercase = /[A-Z]/;
  const hasLowercase = /[a-z]/;
  const hasSymbol = /[$;._\-*]/;
  const longEnough = /^.{8,}$/;
  return (
    hasNumber.test(password) &&
    hasUppercase.test(password) &&
    hasLowercase.test(password) &&
    hasSymbol.test(password) &&
    longEnough.test(password)
  );
}

//Funcion to check if the email follows a certain pattern
function isValidEmail(email) {
  // Use a regular expression to check if the email format is valid
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}
//Function to check if the NIF contains exactly 9 digits
function isValidNIF(nif){
  const nifRegex = /^[0-9]{9}$/;
  return nifRegex.test(nif);
};


module.exports = {
  isPasswordValid,
  isValidEmail,
  isValidNIF

};