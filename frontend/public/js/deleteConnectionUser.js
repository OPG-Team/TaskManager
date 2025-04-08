document.addEventListener("DOMContentLoaded", () => {
    attachDeleteHandlers()
});

export function attachDeleteHandlers() {
    const removeParticipantButtons = document.querySelectorAll(".remove-participant");

    removeParticipantButtons.forEach(button => {
        button.addEventListener("click", async (event) => {
            const taskId = event.target.dataset.taskId;
            const userEmail = event.target.dataset.userEmail;

            try {
                const response = await fetch(`/delete-connection/${taskId}?email_user=${userEmail}`, {
                    method: "DELETE",
                    headers: {
                        "Content-Type": "application/json",
                    },
                });

                if (response.ok) {
                    // Обновите список участников на странице
                    const participantItem = event.target.closest("li");
                    participantItem.remove();
                } else {
                    const data = await response.json();
                    console.error("Error:", data.error);
                }
            } catch (error) {
                console.error("Error:", error);
            }
        });
    });
}