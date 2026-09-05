const loginForm =
    document.getElementById(
        "admin-login-form"
    );

const loginError =
    document.getElementById(
        "login-error"
    );


loginForm.addEventListener(
    "submit",
    async event => {
        event.preventDefault();

        loginError.style.display =
            "none";


        const email =
            document.getElementById(
                "email"
            ).value.trim();


        const password =
            document.getElementById(
                "password"
            ).value;


        try {
            await loginUser(
                email,
                password
            );


            await apiRequest(
                "/admin/test",
                {},
                true
            );


            window.location.href =
                "dashboard.html";


        } catch (error) {
            clearTokens();

            loginError.textContent =
                error.message;

            loginError.style.display =
                "block";
        }
    }
);