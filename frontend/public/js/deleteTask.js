document.addEventListener("DOMContentLoaded", () => {
    const deleteTaskButtons = document.querySelectorAll(".delete-task");

    deleteTaskButtons.forEach(button => {
        button.addEventListener("click", async (event) => {
            const taskId = event.target.dataset.taskId;

            try {
                const response = await fetch(`/delete-task/${taskId}`, {
                    method: "DELETE",
                    headers: {
                        "Content-Type": "application/json",
                    },
                });

                if (response.ok) {
                    const taskItem = event.target.closest(".task-item");
                    taskItem.remove();
                    alert("Задача успешно удалена");
                } else {
                    const data = await response.json();
                    console.error("Error:", data.error);
                    alert("Ошибка при удалении задачи");
                }
            } catch (error) {
                console.error("Error:", error);
                alert("Произошла ошибка");
            }
        });
    });
});
