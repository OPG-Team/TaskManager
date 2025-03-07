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
        const text = await response.text(); // Отладка текста ответа
        console.log("Текстовый ответ от /refresh:", text);

        if (!response.ok) {
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
                    body: JSON.stringify({ email, password: password })
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
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        const tasks = await response.json();
        console.log("Задачи загружены:", tasks);

        // Отображаем задачи в списке
        const taskList = document.getElementById("tasks");
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
            taskList.appendChild(li);
        });
    } catch (error) {
        console.error("Ошибка загрузки задач:", error);
        alert("Failed to load tasks: " + error.message);
    }
}