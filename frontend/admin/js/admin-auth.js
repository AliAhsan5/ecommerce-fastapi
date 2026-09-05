async function verifyAdmin() {
    if (
        !getAccessToken() &&
        !getRefreshToken()
    ) {
        window.location.href =
            "login.html";

        return false;
    }

    try {
        await apiRequest(
            "/admin/test",
            {},
            true
        );

        return true;

    } catch (error) {
        clearTokens();

        window.location.href =
            "login.html";

        return false;
    }
}


async function adminLogout() {
    try {
        await logoutUser();
    } finally {
        window.location.href =
            "login.html";
    }
}