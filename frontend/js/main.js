const urlApi = "http://127.0.0.1:8000"


document.addEventListener("DOMContentLoaded", async () => {
    console.log("Страница загрузилась!");
    
    let token = localStorage.getItem('access_token');

    console.log("Текущий access_token:", token);

    const isLoginPage = window.location.pathname.endsWith('login.html');
    const isRegisterPage = window.location.pathname.endsWith('register.html');
    const isIndexPage = window.location.pathname.endsWith('index.html');

    // Если нет access_token, пытаемся обновить
    if (!token) {
        console.log("Access токена нет, пытаемся обновить с refresh_token из куки...");
        try {
            await refreshAccessToken();
            token = localStorage.getItem('access_token'); // Обновляем значение токена
        } catch (error) {
            console.error("Ошибка обновления токена или отсутствует refresh_token:", error);
            // Если обновление не удалось, продолжаем с текущим состоянием
        }
    }

    // После попытки обновления проверяем токены и маршруты
    if (!token && !isLoginPage && !isRegisterPage) {
        console.log("Токена нет, перенаправляем на login...");
        window.location.href = '/pages/login.html';
    } else if (!token && isLoginPage) {
        console.log("Настраиваем форму логина...");
        setupLoginForm();
    } else if (!token && isRegisterPage) {
        console.log("Настраиваем форму регистрации...");
        setupRegisterForm();
    } else if (token && !isIndexPage && !isLoginPage && !isRegisterPage) {
        console.log("Токен есть, перенаправляем на index...");
        window.location.href = '/index.html';
    } else if (token && isIndexPage) {
        console.log("Токен есть и мы на index, подгружаем таски...");
        loadTasks();
        setupForIndex();
    }
});


async function refreshAccessToken() {
    try {
        const response = await fetch(`${urlApi}/refresh_token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include' // Добавляем, чтобы отправлять куки
        });

        console.log("Статус ответа от /refresh:", response.status); // Отладка

        if (!response.ok) {
            if (response.status === 401) {
                localStorage.removeItem("access_token")
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.access_token) {
            console.log("Новый access_token получен:", data.access_token);
            localStorage.setItem('access_token', data.access_token);
            window.location.reload(); // Перезагружаем страницу для повторной проверки
        } else {
            throw new Error('No access_token in response');
        }
    } catch (error) {
        console.error("Ошибка обновления токена:", error);
        throw error; // Перебрасываем ошибку вверх
    }
}


function setupLoginForm() {
    const form = document.getElementById("loginForm");
    const message = document.getElementById("loginMessage");

    if (form) {
        console.log("Форма логина найдена, добавляем обработчик...");
        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            console.log("Форма отправлена!");
            const email = form.email.value;
            const password = form.password.value;
            console.log("Email:", email, "Password:", password);

            try {
                const response = await fetch(`${urlApi}/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email, password: password }),
                    credentials: 'include'
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                console.log("Ответ от сервера:", data);

                if (data.access_token) {
                    // Сохраняем access_token в localStorage
                    localStorage.setItem('access_token', data.access_token);
                    message.textContent = "Login successful! Redirecting...";
                    message.style.color = "#28a745"; // Зелёный цвет для успеха
                    setTimeout(() => window.location.href = '/index.html', 1000);
                } else {
                    throw new Error('No tokens in response');
                }
            } catch (error) {
                console.error("Ошибка авторизации:", error);
                message.textContent = "Login failed: " + error.message;
            }
        });
    } else {
        console.log("Форма логина не найдена");
    }
}


function setupRegisterForm() {
    const form = document.getElementById("registerForm");
    const message = document.getElementById("registerMessage");

    if (form) {
        console.log("Форма регистрации найдена, добавляем обработчик...");
        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            console.log("Форма регистрации отправлена!");

            const email = form.email.value;
            const password1 = form.password_1.value;
            const password2 = form.password_2.value;

            console.log("Email:", email, "Password 1:", password1, "Password 2:", password2);

            if (password1 !== password2) {
                console.log("Пароли не совпадают!");
                message.textContent = "Passwords do not match!";
                return;
            }

            try {
                const response = await fetch(`${urlApi}/register`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email, password: password1 })
                });

                if (response.ok) {
                    // Проверяем успешный ответ
                    message.textContent = "Registration successful! Redirecting to login...";
                    message.style.color = "#28a745";
                    setTimeout(() => window.location.href = '/pages/login.html', 1000);
                } else {
                    // Обрабатываем ошибки от сервера
                    throw new Error(data.detail || data.message || `HTTP error! status: ${response.status}`);
                }
            } catch (error) {
                console.error("Ошибка регистрации:", error);
                message.textContent = "Registration failed: " + error.message;
            }
        });
    } else {
        console.log("Форма регистрации не найдена");
    }
}


async function loadTasks() {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${urlApi}/tasks/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.log("Ошибка от сервера:", errorData);

            if (response.status === 403 && errorData.detail && errorData.detail.code === "BAD_CREDENTIALS" && errorData.detail.reason === "Access token expires but refresh exists") {
                console.log("Токен истёк, пытаемся обновить с refresh_token...");
                try {
                    await refreshAccessToken();
                    const newToken = localStorage.getItem('access_token');
                    if (newToken) {
                        console.log("Токен обновлён, повторяем запрос...");
                        return loadTasks();
                    } else {
                        throw new Error("Не удалось получить новый access_token");
                    }
                } catch (refreshError) {
                    console.error("Ошибка обновления токена:", refreshError);
                    throw new Error("Не удалось обновить токен: " + refreshError.message);
                }
            } else {
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }
        }

        const tasksData = await response.json();
        console.log("Задачи загружены:", tasksData);

        // Преобразуем объект задач в массив
        const tasks = tasksData ? Object.values(tasksData) : [];

        // Отображаем задачи в списке
        const taskList = document.getElementById("tasks");

        // Получаем email и роль пользователя
        const userEmail = await getUserEmailFromToken(token);
        const userRole = await getUserRoleFromToken(token);

        taskList.innerHTML = ""; // Очищаем список перед добавлением

        tasks.forEach(task => {
            const li = document.createElement("li");
            li.innerHTML = `
                <h3>${task.title}</h3>
                <p><strong>Status:</strong> ${task.status}</p>
                <p><strong>Description:</strong> ${task.description}</p>
                <p><strong>Created at:</strong> ${new Date(task.time).toLocaleString()}</p>
                <p><strong>Users:</strong> ${task.connections.map(conn => {
                    return `${conn.user.email} (${conn.type})`;
                }).join(", ")}</p>
            `;

            // Проверяем права для редактирования, удаления и управления связями
            const isOwner = task.connections.some(conn => conn.user.email === userEmail && conn.type === "Владелец");
            const isCoauthor = task.connections.some(conn => conn.user.email === userEmail && conn.type === "Соавтор");
            const isAdmin = userRole === "admin";

            // Кнопка редактирования
            if (isOwner || isCoauthor || isAdmin) {
                const editButton = document.createElement("button");
                editButton.textContent = "Редактировать";
                editButton.className = "btn-edit-task";
                editButton.addEventListener("click", () => {
                    const editForm = document.createElement("form");
                    editForm.className = "task-form";
                    editForm.innerHTML = `
                        <h3>Редактировать задачу</h3>
                        <label>Название:</label>
                        <input type="text" id="editTitle" value="${task.title}" required><br>
                        <label>Описание:</label>
                        <textarea id="editDescription">${task.description}</textarea><br>
                        <label>Статус:</label>
                        <select id="editStatus">
                            <option value="Новая" ${task.status === "Новая" ? "selected" : ""}>Новая</option>
                            <option value="В работе" ${task.status === "В работе" ? "selected" : ""}>В работе</option>
                            <option value="Завершена" ${task.status === "Завершена" ? "selected" : ""}>Завершена</option>
                        </select><br>
                        <button type="submit">Сохранить</button>
                        <button type="button" id="cancelEdit">Отмена</button>
                    `;

                    const existingForm = li.querySelector("form");
                    if (existingForm) {
                        existingForm.remove();
                    }

                    li.appendChild(editForm);

                    const cancelButton = editForm.querySelector("#cancelEdit");
                    cancelButton.addEventListener("click", () => {
                        editForm.remove();
                    });

                    editForm.addEventListener("submit", async (event) => {
                        event.preventDefault();
                        const newTitle = editForm.querySelector("#editTitle").value;
                        const newDescription = editForm.querySelector("#editDescription").value;
                        const newStatus = editForm.querySelector("#editStatus").value;
                        await editTask(task.id, newTitle, newDescription, newStatus);
                        editForm.remove();
                    });
                });
                li.appendChild(editButton);
            }

            // Кнопка удаления
            if (isOwner || isAdmin) {
                const deleteButton = document.createElement("button");
                deleteButton.textContent = "Удалить";
                deleteButton.className = "btn-delete";
                deleteButton.addEventListener("click", () => deleteTask(task.id));
                li.appendChild(deleteButton);
            }

            // Кнопки удаления связей
            if (isOwner || isAdmin) {
                task.connections.forEach(conn => {
                    if (conn.user.email !== userEmail) {
                        const removeConnectionButton = document.createElement("button");
                        removeConnectionButton.textContent = `Удалить ${conn.user.email}`;
                        removeConnectionButton.className = "btn-delete";
                        removeConnectionButton.addEventListener("click", () => removeConnection(task.id, conn.user.email));
                        li.appendChild(removeConnectionButton);
                    }
                });
            }

            // Кнопка для добавления новой связи
            if (isOwner || isAdmin) {
                const addConnectionButton = document.createElement("button");
                addConnectionButton.textContent = "Добавить связь";
                addConnectionButton.className = "btn-add-conection";
                addConnectionButton.addEventListener("click", () => {
                    const addConnectionForm = document.createElement("form");
                    addConnectionForm.className = "task-form";
                    addConnectionForm.innerHTML = `
                        <h3>Добавить связь</h3>
                        <label>Email пользователя:</label>
                        <input type="email" id="addEmail" placeholder="Введите email" required><br>
                        <label>Тип связи:</label>
                        <select id="addConnectionType">
                            <option value="Владелец">Владелец</option>
                            <option value="Соавтор">Соавтор</option>
                            <option value="Обычный" selected>Обычный</option>
                        </select><br>
                        <button type="submit">Сохранить</button>
                        <button type="button" id="cancelAddConnection">Отмена</button>
                    `;

                    const existingForm = li.querySelector("form");
                    if (existingForm) {
                        existingForm.remove();
                    }

                    li.appendChild(addConnectionForm);

                    const cancelButton = addConnectionForm.querySelector("#cancelAddConnection");
                    cancelButton.addEventListener("click", () => {
                        addConnectionForm.remove();
                    });

                    addConnectionForm.addEventListener("submit", async (event) => {
                        event.preventDefault();
                        const emailToAdd = addConnectionForm.querySelector("#addEmail").value;
                        const connectionType = addConnectionForm.querySelector("#addConnectionType").value;
                        if (emailToAdd && ["Владелец", "Соавтор", "Обычный"].includes(connectionType)) {
                            await addConnection(task.id, emailToAdd, connectionType);
                            addConnectionForm.remove();
                        } else {
                            alert("Неверный email или тип связи! Используйте Владелец, Соавтор или Обычный.");
                        }
                    });
                });
                li.appendChild(addConnectionButton);
            }

            taskList.appendChild(li);
        });

        // Добавление фильтрации поверх загруженных задач
        const filterStatus = document.getElementById("filterStatus");
        const filterTimeAfter = document.getElementById("filterTimeAfter");
        const applyFiltersButton = document.getElementById("applyFilters");
        const clearFiltersButton = document.getElementById("clearFilters");

        // Функция применения фильтров
        function applyFilters() {
            const filteredTasks = tasks.filter(task => {
                const taskDate = new Date(task.time).toISOString().split('T')[0]; // Извлекаем дату
                const matchesStatus = !filterStatus.value || task.status === filterStatus.value;
                const matchesTime = !filterTimeAfter.value || taskDate >= filterTimeAfter.value;
                return matchesStatus && matchesTime;
            });

            taskList.innerHTML = ""; // Очищаем текущий список
            filteredTasks.forEach(task => {
                const li = document.createElement("li");
                li.innerHTML = `
                    <h3>${task.title}</h3>
                    <p><strong>Status:</strong> ${task.status}</p>
                    <p><strong>Description:</strong> ${task.description}</p>
                    <p><strong>Created at:</strong> ${new Date(task.time).toLocaleString()}</p>
                    <p><strong>Users:</strong> ${task.connections.map(conn => {
                        return `${conn.user.email} (${conn.type})`;
                    }).join(", ")}</p>
                `;

                const isOwner = task.connections.some(conn => conn.user.email === userEmail && conn.type === "Владелец");
                const isCoauthor = task.connections.some(conn => conn.user.email === userEmail && conn.type === "Соавтор");
                const isAdmin = userRole === "admin";

                if (isOwner || isCoauthor || isAdmin) {
                    const editButton = document.createElement("button");
                    editButton.textContent = "Редактировать";
                    editButton.className = "btn-edit-task";
                    editButton.addEventListener("click", () => {
                        const editForm = document.createElement("form");
                        editForm.className = "task-form";
                        editForm.innerHTML = `
                            <h3>Редактировать задачу</h3>
                            <label>Название:</label>
                            <input type="text" id="editTitle" value="${task.title}" required><br>
                            <label>Описание:</label>
                            <textarea id="editDescription">${task.description}</textarea><br>
                            <label>Статус:</label>
                            <select id="editStatus">
                                <option value="Новая" ${task.status === "Новая" ? "selected" : ""}>Новая</option>
                                <option value="В работе" ${task.status === "В работе" ? "selected" : ""}>В работе</option>
                                <option value="Завершена" ${task.status === "Завершена" ? "selected" : ""}>Завершена</option>
                            </select><br>
                            <button type="submit">Сохранить</button>
                            <button type="button" id="cancelEdit">Отмена</button>
                        `;

                        const existingForm = li.querySelector("form");
                        if (existingForm) {
                            existingForm.remove();
                        }

                        li.appendChild(editForm);

                        const cancelButton = editForm.querySelector("#cancelEdit");
                        cancelButton.addEventListener("click", () => {
                            editForm.remove();
                        });

                        editForm.addEventListener("submit", async (event) => {
                            event.preventDefault();
                            const newTitle = editForm.querySelector("#editTitle").value;
                            const newDescription = editForm.querySelector("#editDescription").value;
                            const newStatus = editForm.querySelector("#editStatus").value;
                            await editTask(task.id, newTitle, newDescription, newStatus);
                            editForm.remove();
                        });
                    });
                    li.appendChild(editButton);
                }

                if (isOwner || isAdmin) {
                    const deleteButton = document.createElement("button");
                    deleteButton.textContent = "Удалить";
                    deleteButton.className = "btn-delete";
                    deleteButton.addEventListener("click", () => deleteTask(task.id));
                    li.appendChild(deleteButton);
                }

                if (isOwner || isAdmin) {
                    task.connections.forEach(conn => {
                        if (conn.user.email !== userEmail) {
                            const removeConnectionButton = document.createElement("button");
                            removeConnectionButton.textContent = `Удалить ${conn.user.email}`;
                            removeConnectionButton.className = "btn-delete";
                            removeConnectionButton.addEventListener("click", () => removeConnection(task.id, conn.user.email));
                            li.appendChild(removeConnectionButton);
                        }
                    });
                }

                if (isOwner || isAdmin) {
                    const addConnectionButton = document.createElement("button");
                    addConnectionButton.textContent = "Добавить связь";
                    addConnectionButton.className = "btn-add-conection";
                    addConnectionButton.addEventListener("click", () => {
                        const addConnectionForm = document.createElement("form");
                        addConnectionForm.className = "task-form";
                        addConnectionForm.innerHTML = `
                            <h3>Добавить связь</h3>
                            <label>Email пользователя:</label>
                            <input type="email" id="addEmail" placeholder="Введите email" required><br>
                            <label>Тип связи:</label>
                            <select id="addConnectionType">
                                <option value="Владелец">Владелец</option>
                                <option value="Соавтор">Соавтор</option>
                                <option value="Обычный" selected>Обычный</option>
                            </select><br>
                            <button type="submit">Сохранить</button>
                            <button type="button" id="cancelAddConnection">Отмена</button>
                        `;

                        const existingForm = li.querySelector("form");
                        if (existingForm) {
                            existingForm.remove();
                        }

                        li.appendChild(addConnectionForm);

                        const cancelButton = addConnectionForm.querySelector("#cancelAddConnection");
                        cancelButton.addEventListener("click", () => {
                            addConnectionForm.remove();
                        });

                        addConnectionForm.addEventListener("submit", async (event) => {
                            event.preventDefault();
                            const emailToAdd = addConnectionForm.querySelector("#addEmail").value;
                            const connectionType = addConnectionForm.querySelector("#addConnectionType").value;
                            if (emailToAdd && ["Владелец", "Соавтор", "Обычный"].includes(connectionType)) {
                                await addConnection(task.id, emailToAdd, connectionType);
                                addConnectionForm.remove();
                            } else {
                                alert("Неверный email или тип связи! Используйте Владелец, Соавтор или Обычный.");
                            }
                        });
                    });
                    li.appendChild(addConnectionButton);
                }

                taskList.appendChild(li);
            });

            if (filteredTasks.length === 0) {
                taskList.innerHTML = "<li>Нет задач для отображения</li>";
            }
        }

        // Обработчик кнопки "Применить фильтры"
        applyFiltersButton.addEventListener("click", () => {
            applyFilters();
        });

        // Обработчик кнопки "Сбросить фильтры"
        clearFiltersButton.addEventListener("click", () => {
            filterStatus.value = "";
            filterTimeAfter.value = "2025-03-01";
            applyFilters();
        });

        // Изначально рендерим все задачи
        applyFilters();
    } catch (error) {
        console.error("Ошибка загрузки задач:", error);
        alert("Failed to load tasks: " + error.message);
    }
}


// Новая функция для получения email из токена
async function getUserEmailFromToken(token) {
    try {
        const payload = JSON.parse(atob(token.split('.')[1])); // Декодируем payload JWT
        return payload.sub; // Предполагаем, что email хранится в поле sub
    } catch (error) {
        console.error("Ошибка декодирования токена:", error);
        return null;
    }
}

// Новая функция для получения роли из токена
async function getUserRoleFromToken(token) {
    try {
        const payload = JSON.parse(atob(token.split('.')[1])); // Декодируем payload JWT
        return payload.role || "default"; // Предполагаем, что роль хранится в поле role, по умолчанию "user"
    } catch (error) {
        console.error("Ошибка декодирования токена:", error);
        return "default";
    }
}


async function editTask(taskId, newTitle, newDescription, newStatus) {
    const token = localStorage.getItem('access_token');
    try {
        const response = await fetch(`${urlApi}/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                title: newTitle,
                description: newDescription,
                status: newStatus
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.log("Ошибка от сервера:", errorData);

            if (response.status === 403 && errorData.detail && errorData.detail.code === "BAD_CREDENTIALS" && errorData.detail.reason === "Access token expires but refresh exists") {
                console.log("Токен истёк, пытаемся обновить с refresh_token...");
                try {
                    await refreshAccessToken();
                    const newToken = localStorage.getItem('access_token');
                    if (newToken) {
                        console.log("Токен обновлён, повторяем запрос...");
                        const retryResponse = await fetch(`${urlApi}/tasks/${taskId}`, {
                            method: 'PUT',
                            headers: {
                                'Content-Type': 'application/json',
                                'Authorization': `Bearer ${newToken}`
                            },
                            body: JSON.stringify({
                                title: newTitle,
                                description: newDescription,
                                status: newStatus
                            })
                        });
                        if (!retryResponse.ok) {
                            throw new Error(await retryResponse.json() || `HTTP error! status: ${retryResponse.status}`);
                        }
                    } else {
                        throw new Error("Не удалось получить новый access_token");
                    }
                } catch (refreshError) {
                    console.error("Ошибка обновления токена:", refreshError);
                    throw new Error("Не удалось обновить токен: " + refreshError.message);
                }
            } else {
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }
        }

        loadTasks(); // Обновляем список задач
        alert("Задача успешно отредактирована!");
    } catch (error) {
        console.error("Ошибка редактирования задачи:", error);
        alert("Ошибка при редактировании задачи: " + error.message);
    }
}

// Функция для удаления задачи
async function deleteTask(taskId) {
    const token = localStorage.getItem('access_token');
    if (confirm("Вы уверены, что хотите удалить эту задачу?")) {
        try {
            const response = await fetch(`${urlApi}/tasks/${taskId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                if (response.status === 403 && errorData.detail && errorData.detail.code === "BAD_CREDENTIALS" && errorData.detail.reason === "Access token expires but refresh exists") {
                    console.log("Токен истёк, пытаемся обновить с refresh_token...");
                    try {
                        await refreshAccessToken(); // Обновляем токен
                        const newToken = localStorage.getItem('access_token'); // Получаем новый токен
                        if (newToken) {
                            console.log("Токен обновлён, повторяем запрос...");
                            return loadTasks(); // Рекурсивно повторяем запрос
                        } else {
                            throw new Error("Не удалось получить новый access_token");
                        }
                    } catch (refreshError) {
                        console.error("Ошибка обновления токена:", refreshError);
                        throw new Error("Не удалось обновить токен: " + refreshError.message);
                    }
                } else {
                    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
                }
            }

            loadTasks(); // Обновляем список задач
            alert("Задача успешно удалена!");
        } catch (error) {
            console.error("Ошибка удаления задачи:", error);
            alert("Ошибка при удалении задачи: " + error.message);
        }
    }
}

// Функция для удаления связи
async function removeConnection(taskId, emailToRemove) {
    const token = localStorage.getItem('access_token');
    if (confirm(`Вы уверены, что хотите удалить связь с ${emailToRemove}?`)) {
        try {
            const response = await fetch(`${urlApi}/tasks/delete_connection/${taskId}?email_user=${encodeURIComponent(emailToRemove)}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                    'accept': 'application/json' // Добавляем заголовок accept, как в примере curl
                }
            });

            if (!response.ok) {
                const errorData = await response.json(); // Декодируем тело ответа для получения деталей ошибки
                console.log("Ошибка от сервера:", errorData);

                if (response.status === 403 && errorData.detail && errorData.detail.code === "BAD_CREDENTIALS" && errorData.detail.reason === "Access token expires but refresh exists") {
                    console.log("Токен истёк, пытаемся обновить с refresh_token...");
                    try {
                        await refreshAccessToken(); // Обновляем токен
                        const newToken = localStorage.getItem('access_token'); // Получаем новый токен
                        if (newToken) {
                            console.log("Токен обновлён, повторяем запрос...");
                            // Повторяем запрос с новым токеном
                            const retryResponse = await fetch(`${urlApi}/tasks/delete_connection/${taskId}?email_user=${encodeURIComponent(emailToRemove)}`, {
                                method: 'DELETE',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'Authorization': `Bearer ${newToken}`,
                                    'accept': 'application/json'
                                }
                            });
                            if (!retryResponse.ok) {
                                throw new Error(await retryResponse.json() || `HTTP error! status: ${retryResponse.status}`);
                            }
                        } else {
                            throw new Error("Не удалось получить новый access_token");
                        }
                    } catch (refreshError) {
                        console.error("Ошибка обновления токена:", refreshError);
                        throw new Error("Не удалось обновить токен: " + refreshError.message);
                    }
                } else {
                    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
                }
            }

            loadTasks(); // Обновляем список задач
            alert("Связь успешно удалена!");
        } catch (error) {
            console.error("Ошибка удаления связи:", error);
            alert("Ошибка при удалении связи: " + error.message);
        }
    }
}


async function addConnection(taskId, emailToAdd, connectionType) {
    const token = localStorage.getItem('access_token');
    try {
        const response = await fetch(`${urlApi}/tasks/add_user/${taskId}?new_user=${encodeURIComponent(emailToAdd)}&type_connection=${encodeURIComponent(connectionType)}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'accept': 'application/json'
            },
            body: '' // Пустое тело, как в примере curl
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.log("Ошибка от сервера:", errorData);

            if (response.status === 403 && errorData.detail && errorData.detail.code === "BAD_CREDENTIALS" && errorData.detail.reason === "Access token expires but refresh exists") {
                console.log("Токен истёк, пытаемся обновить с refresh_token...");
                try {
                    await refreshAccessToken();
                    const newToken = localStorage.getItem('access_token');
                    if (newToken) {
                        console.log("Токен обновлён, повторяем запрос...");
                        const retryResponse = await fetch(`${urlApi}/tasks/add_user/${taskId}?new_user=${encodeURIComponent(emailToAdd)}&type_connection=${encodeURIComponent(connectionType)}`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'Authorization': `Bearer ${newToken}`,
                                'accept': 'application/json'
                            },
                            body: ''
                        });
                        if (!retryResponse.ok) {
                            throw new Error(await retryResponse.json() || `HTTP error! status: ${retryResponse.status}`);
                        }
                    } else {
                        throw new Error("Не удалось получить новый access_token");
                    }
                } catch (refreshError) {
                    console.error("Ошибка обновления токена:", refreshError);
                    throw new Error("Не удалось обновить токен: " + refreshError.message);
                }
            } else {
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }
        }

        loadTasks(); // Обновляем список задач
        alert("Связь успешно добавлена!");
    } catch (error) {
        console.error("Ошибка добавления связи:", error);
        alert("Ошибка при добавлении связи: " + error.message);
    }
}

async function setupForIndex() {
    const logoutButton = document.getElementById("logoutButton");
    const taskForm = document.getElementById("taskForm");

    if (logoutButton && taskForm) {
        // Обработчик для кнопки выхода
        logoutButton.addEventListener("click", async () => {
            console.log("Нажата кнопка выхода...");
        
            // Получаем текущий access_token из localStorage
            const accessToken = localStorage.getItem('access_token');
        
            if (accessToken) {
                try {
                    // Отправляем POST-запрос на сервер для выполнения logout
                    const response = await fetch(`${urlApi}/logout`, {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${accessToken}`,
                            'Content-Type': 'application/json'
                        },
                        credentials: 'include'
                    });
        
                    if (response.ok) {
                        console.log("Успешный выход из системы");
                    } else {
                        console.error("Ошибка при выходе из системы:", response.statusText);
                    }
                } catch (error) {
                    console.error("Ошибка при отправке запроса на logout:", error);
                }
            }
        
            // Очищаем access_token из localStorage
            localStorage.removeItem('access_token');
            console.log("Токен удалён из localStorage");
        
            // Перенаправляем на страницу логина
            window.location.href = '/pages/login.html';
        });

        // Обработчик для отправки формы задачи
        taskForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            console.log("Форма задачи отправлена!");

            // Получаем данные из формы
            const title = taskForm.querySelector("#title").value;
            const description = taskForm.querySelector("#description").value;
            const status = taskForm.querySelector("#status").value || "Новая";

            console.log("Данные формы:", { title, description, status });

            try {
                var token = localStorage.getItem('access_token');
                if (!token) {
                    try {
                        await refreshAccessToken(); // Обновляем токен
                        token = localStorage.getItem('access_token'); // Получаем новый токен
                        if (token) {
                            console.log("Токен обновлён");
                        } else {
                            throw new Error("Не удалось получить новый access_token");
                        }
                    } catch (refreshError) {
                        console.error("Ошибка обновления токена:", refreshError);
                        throw new Error("Не удалось обновить токен: " + refreshError.message);
                    }
                }

                const response = await fetch(`${urlApi}/tasks/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        title,
                        status,
                        description,
                    })
                });

                if (!response.ok) {
                    if (response.status == 403) {
                        try {
                            await refreshAccessToken(); // Обновляем токен
                            token = localStorage.getItem('access_token'); // Получаем новый токен
                            if (!token) {
                                throw new Error("Не удалось получить новый access_token");
                            }
                            console.log("Токен обновлён, повторяем запрос с новыми данными...");
                            // Повторяем POST-запрос с сохранёнными данными
                            const retryResponse = await fetch(`${urlApi}/tasks/`, {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'Authorization': `Bearer ${token}`
                                },
                                body: JSON.stringify({
                                    title,
                                    status,
                                    description,
                                })
                            });
                            if (!retryResponse.ok) {
                                throw new Error(await retryResponse.json() || `HTTP error! status: ${retryResponse.status}`);
                            }
                            // Если повторный запрос успешен, продолжаем
                        } catch (refreshError) {
                            console.error("Ошибка обновления токена:", refreshError);
                            throw new Error("Не удалось обновить токен: " + refreshError.message);
                        }
                    }
                    const errorData = await response.json();
                    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
                }

                // Очищаем форму после успешного создания
                taskForm.reset();
                alert("Задача успешно добавлена!");
                loadTasks(); // Обновляем список задач
            } catch (error) {
                console.error("Ошибка создания задачи:", error);
                alert("Ошибка при создании задачи: " + error.message);
            }
        });
    } else {
        console.log("Кнопка выхода или форма задачи не найдены");
    }
}