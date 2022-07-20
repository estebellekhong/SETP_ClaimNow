const container         = document.querySelector(".container"),
      pwShowHide        = document.querySelectorAll(".showHidePw"),
      pwFields          = document.querySelectorAll(".password"),
      signUp            = document.querySelector(".signup-link"),
      login             = document.querySelector(".login-link");
    


    //   js code to show/hide password and change icon
    pwShowHide.forEach(eyeIcon =>{
        eyeIcon.addEventListener("click", ()=>{
            pwFields.forEach(pwField =>{
                if(pwField.type ==="password"){
                    pwField.type = "text";

                    pwShowHide.forEach(icon =>{
                        icon.classList.replace("uil-eye-slash", "uil-eye");
                    })
                }else{
                    pwField.type = "password";

                    pwShowHide.forEach(icon =>{
                        icon.classList.replace("uil-eye", "uil-eye-slash");
                    })
                }
            }) 
        })
    })

    $(document).ready(function()
{
     $("Login").click(myFunction);

});

function myFunction()
{

$.ajax({
    url: "login.py",
    type: "post",
    datatype: "data",
    data: {name: $("user_id").val(), pass: $("user_password").val()},
    success: function(response){
        console.log(response.message);
        console.log(response.keys);
        console.log(response.data);
    }
 });
}

    // js code to appear signup and login form
    signUp.addEventListener("click", ( )=>{
        container.classList.add("active");
    });
    login.addEventListener("click", ( )=>{
        container.classList.remove("active");
    });
  