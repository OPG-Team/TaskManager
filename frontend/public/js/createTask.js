document.addEventListener("DOMContentLoaded", () => {
    const taskForm = document.getElementById("taskForm");

    taskForm.addEventListener("submit", async (event) => {
        event.preventDefault(); // Предотвращаем стандартную отправку формы

        const title = document.getElementById("title").value;
        const status = document.getElementById("status").value;
        const description = document.getElementById("description").value;

        const newTask = {
            title,
            status,
            description
        }

        try {
            const response = await fetch("/create-task", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(newTask)
            });

            if (response.ok) {
                alert("Задача успешно создана");
                location.reload();
            } else {
                const data = await response.json();
                console.error("Error:", data.error);
                alert("Ошибка при создании задачи");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Произошла ошибка");
        }
    });
});
