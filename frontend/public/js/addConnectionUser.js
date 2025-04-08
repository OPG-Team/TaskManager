import { attachDeleteHandlers } from './deleteConnectionUser.js';

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll('.add-participant').forEach(button => {
        button.addEventListener('click', (event) => {
            const taskItem = event.target.closest('.task-item');
            const participantForm = taskItem.querySelector('.participant-form');
            participantForm.style.display = 'block';
        });
    });

    document.querySelectorAll('.save-participant').forEach(button => {
        button.addEventListener('click', async (event) => {
            const taskItem = event.target.closest('.task-item');
            const taskId = taskItem.dataset.id;
            const emailInput = taskItem.querySelector('.participant-email');
            const email = emailInput.value;
            const typeSelect = taskItem.querySelector('.participant-type');
            const typeConnection = typeSelect.value;

            if (!email) {
                alert("Пожалуйста, введите email участника");
                return;
            }

            try {
                const response = await fetch(`/add-participant/${taskId}`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ email, typeConnection })
                });

                if (response.ok) {
                    // Обновите список участников на странице
                    const participantItem = document.createElement('li');
                    participantItem.innerHTML = `${email} (${typeConnection}) <button class="remove-participant" data-task-id="${taskId}" data-user-email="${email}">Удалить</button>`;
                    taskItem.querySelector('.task-participants ul').appendChild(participantItem);

                    // Скрываем форму после успешного добавления
                    taskItem.querySelector('.participant-form').style.display = 'none';
                    emailInput.value = '';
                    alert("Участник успешно добавлен");
                    
                    attachDeleteHandlers()
                } else if (response.status === 404) {
                    const data = await response.json();
                    alert(data.error);
                } else {
                    const data = await response.json();
                    console.error("Error:", data.error);
                    alert("Ошибка при добавлении участника");
                }
            } catch (error) {
                console.error("Error:", error);
                alert("Произошла ошибка");
            }
        });
    });

    document.querySelectorAll('.cancel-add-participant').forEach(button => {
        button.addEventListener('click', (event) => {
            const taskItem = event.target.closest('.task-item');
            const participantForm = taskItem.querySelector('.participant-form');
            participantForm.style.display = 'none';
        });
    });
});
