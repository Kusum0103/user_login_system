function switchTab(mode) {
    const loginTab = document.getElementById("login-tab");
    const registerTab = document.getElementById("register-tab");
    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form");
    const verifyForm = document.getElementById("verify-form");
    const messageBox = document.getElementById("message-box");

    messageBox.style.display = "none";

    if (verifyForm) {
        verifyForm.classList.add("hidden");
    }

    if (mode === "login") {
        loginTab.classList.add("active");
        registerTab.classList.remove("active");
        loginForm.classList.remove("hidden");
        registerForm.classList.add("hidden");
    } else {
        registerTab.classList.add("active");
        loginTab.classList.remove("active");
        registerForm.classList.remove("hidden");
        loginForm.classList.add("hidden");
    }
}


async function handleAuth(event, endpoint) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    const messageBox = document.getElementById("message-box");

    messageBox.style.display = "none";
    messageBox.className = "message-box";

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.success) {
            messageBox.textContent = data.message;
            messageBox.classList.add("success");
            messageBox.style.display = "block";

            if (endpoint === '/login') {
                setTimeout(() => {
                    window.location.href = "/dashboard";
                }, 500);
            } else {
                setTimeout(() => {
                    form.reset();
                
                    document.getElementById("verify-username").value = data.username;
                    document.getElementById("register-form").classList.add("hidden");
                    document.getElementById("verify-form").classList.remove("hidden");
                }, 500);

            }
        } else {

            if (endpoint === '/login' && data.needs_verification){
              
                messageBox.textContent = data.error || "Something went wrong!! Try again";
                messageBox.classList.add("error");
                messageBox.style.display = "block";


                setTimeout(()=>{
                    form.reset();
                    document.getElementById("verify-username").value = data.username;
                    document.getElementById("login-form").classList.add("hidden");
                    document.getElementById("verify-form").classList.remove("hidden");
                },2000);
            } else {
                messageBox.textContent = data.error || "Something went wrong!! Try again";
                messageBox.classList.add("error");
                messageBox.style.display = "block";
            }
                    
        }
        
    } catch (error) {
        messageBox.textContent = "Could not connect to the server. Please check your internet connection.";
        messageBox.classList.add("error");
        messageBox.style.display = "block";
        console.error("Error during authentication:", error);
    }
}


async function handleVerifyOTP(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const messageBox = document.getElementById("message-box");

    messageBox.style.display = "none";
    messageBox.className = "message-box";

    try {
        const response = await fetch('/verify-otp', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        if (response.ok && data.success) {
            messageBox.textContent = data.message;
            messageBox.classList.add("success");
            messageBox.style.display = "block";
            
            // Success hone baad login tab par redirect karna
            setTimeout(() => {
                form.reset();
                switchTab("login");
            }, 500);
        } else {
            messageBox.textContent = data.error || "Verification failed.";
            messageBox.classList.add("error");
            messageBox.style.display = "block";
        }
    } catch (error) {
        messageBox.textContent = "Could not connect to the server.";
        messageBox.classList.add("error");
        messageBox.style.display = "block";
    }
}

// 2. Resend OTP link click handle karne ke liye
async function handleResendOTP(event) {
    event.preventDefault();
    // Hidden input se username read karna
    const username = document.getElementById("verify-username").value;
    const messageBox = document.getElementById("message-box");

    messageBox.style.display = "none";
    messageBox.className = "message-box";

    // Form data create karna taaki backend ko request.form mein data mile
    const formData = new FormData();
    formData.append("username", username);

    try {
        const response = await fetch('/resend-otp', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        
        if (response.ok && data.success) {
            messageBox.textContent = data.message;
            messageBox.classList.add("success");
            messageBox.style.display = "block";
        } else {
            messageBox.textContent = data.error || "Failed to resend OTP.";
            messageBox.classList.add("error");
            messageBox.style.display = "block";
        }
    } catch (error) {
        messageBox.textContent = "Could not connect to the server.";
        messageBox.classList.add("error");
        messageBox.style.display = "block";
    }
}


// Password ko show/hide karne ke liye custom function
function togglePasswordVisibility(inputId, element) {
    const input = document.getElementById(inputId);
    const icon = element.querySelector('i');
    
    if (input.type === "password") {
        input.type = "text";
        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");
    } else {
        input.type = "password";
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
  
    }
}
