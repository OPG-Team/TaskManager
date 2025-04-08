document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll('.edit-task').forEach(button => {
        button.addEventListener('click', (event) => {
            const taskItem = event.target.closest('.task-item');
            const viewSection = taskItem.querySelector('.task-view');
            const editSection = taskItem.querySelector('.task-edit');
            viewSection.style.display = 'none';
            editSection.style.display = 'block';
        });
    });

    document.querySelectorAll('.save-task').forEach(button => {
        button.addEventListener('click', async (event) => {
            const taskItem = event.target.closest('.task-item');
            const taskId = taskItem.dataset.id;
            const title = taskItem.querySelector('.edit-title').value;
            const status = taskItem.querySelector('.edit-status').value;
            const description = taskItem.querySelector('.edit-description').value;

            const updatedTask = {
                title,
                status,
                description
            };

            try {
                const response = await fetch(`/update-task/${taskId}`, {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(updatedTask)
                });

                if (response.ok) {
                    // Обновите отображение задачи на странице
                    taskItem.querySelector('.task-title').textContent = title;
                    taskItem.querySelector('.task-status span').textContent = status;
                    taskItem.querySelector('.task-description span').textContent = description;
                    taskItem.querySelector('.task-view').style.display = 'block';
                    taskItem.querySelector('.task-edit').style.display = 'none';
                    alert("Задача успешно обновлена");
                } else {
                    const data = await response.json();
                    console.error("Error:", data.error);
                    alert("Ошибка при обновлении задачи");
                }
            } catch (error) {
                console.error("Error:", error);
                alert("Произошла ошибка");
            }
        });
    });

    document.querySelectorAll('.cancel-edit').forEach(button => {
        button.addEventListener('click', (event) => {
            const taskItem = event.target.closest('.task-item');
            const viewSection = taskItem.querySelector('.task-view');
            const editSection = taskItem.querySelector('.task-edit');
            viewSection.style.display = 'block';
            editSection.style.display = 'none';
        });
    });
});
