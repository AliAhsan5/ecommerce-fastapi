const loginForm =
    document.getElementById(
        "login-form"
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


            const params =
                new URLSearchParams(
                    window.location.search
                );

            const next =
                params.get("next");


            window.location.href =
                next || "index.html";

        } catch (error) {
            loginError.textContent =
                error.message;

            loginError.style.display =
                "block";
        }
    }
);