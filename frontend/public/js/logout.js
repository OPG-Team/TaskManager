document.addEventListener("DOMContentLoaded", () => {
    const logoutButton = document.getElementById("logoutButton");

    logoutButton.addEventListener("click", async (event) => {
        event.preventDefault();

        try {
            const response = await fetch("/logout", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                credentials: "include"
            });

            window.location.href = "/login";
        } catch (error) {
            console.error("Error:", error);
            alert("Произошла ошибка при выходе из системы");
        }
    });
});
