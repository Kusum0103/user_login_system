function switchTab(mode) {
    const loginTab = document.getElementById("login-tab")

    const registerTab = document.getElementById("register-tab")

    const loginForm = document.getElementById("login-form")

    const registerForm = document.getElementById("register-form")

    const messageBox = document.getElementById("message-box")

    messageBox.style.display = "none"

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
                }, 1000);
            }
            else {

                setTimeout(() => {
                    form.reset();
                    switchTab("login");
                }, 2000);
            }
        }
        else {
            messageBox.textContent = data.error || "Something went wrong!! Try again";
            messageBox.classList.add("error");
            messageBox.style.display = "block";
        }

    }
    catch (error) {
        messageBox.textContent = "Could not connect to the server. Please check your internet connection.";
        messageBox.classList.add("error");
        messageBox.style.display = "block";
        console.error("Error during authentication:", error);
    }

}
