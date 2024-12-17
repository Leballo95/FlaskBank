function openSignupForm() {
    document.getElementById("signupForm").style.display = "block";
    closeLoginForm();


  }
  
  function closeSignupForm() {
    document.getElementById("signupForm").style.display = "none";
  }

  function openLoginForm(){
    document.getElementById("loginForm").style.display="block";
    closeSignupForm();
  }

  function closeLoginForm(){
    document.getElementById("loginForm").style.display="none";
  }


  function showPayMenu(){
    document.getElementById("transaction-form").style.display="block"

  }

  function closePayMenu(){
    document.getElementById("transaction-form").style.display="none"
  }


/******Controls transaction form radio buttons******/
document.addEventListener("DOMContentLoaded", function () {
    const option1 = document.getElementById("transferRadio");
    const option2 = document.getElementById("buyRadio");
    const fieldsOption1 = document.getElementById("fields-transfer");
    const fieldsOption2 = document.getElementById("fields-buy");

    function toggleFields() {
        if (option1.checked) {
            fieldsOption1.style.display = "block";
            fieldsOption2.style.display = "none";
        } else if (option2.checked) {
            fieldsOption1.style.display = "none";
            fieldsOption2.style.display = "block";
        }
    }

    option1.addEventListener("change", toggleFields);
    option2.addEventListener("change", toggleFields);
});
