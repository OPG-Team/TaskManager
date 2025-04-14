const express = require("express");
const session = require("express-session");
const bodyParser = require("body-parser");
const axios = require("axios");
const path = require("path");
const cookieParser = require("cookie-parser");
require('dotenv').config();

const app = express();
const BACKEND_URL = process.env.BACKEND_URL || "http://127.0.0.1:8005";

// Настройка EJS
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));

// Middleware
app.use(express.static("public"));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(cookieParser());
app.use(
    session({
        secret: process.env.SESSION_SECRET || "your-secret-key",
        resave: false,
        saveUninitialized: true,
        cookie: {
            secure: false,
            httpOnly: true,
            sameSite: 'lax',
            maxAge: 24 * 60 * 60 * 1000 // 1 день
        }
    })
);


// Кастомный middleware для добавления Access Token к запросам
app.use(async (req, res, next) => {
    // Пропускаем запросы на аутентификацию
    if (req.path === '/login' || req.path === '/register') {
        return next();
    }
    
    // Если есть Access Token в сессии - добавляем его к запросам
    if (req.session.access_token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${req.session.access_token}`;
    }
    
    next();
});


// Роуты
app.get("/", async (req, res) => {
    if (req.session.access_token) {
        try {
            const response = await axios.get(`${BACKEND_URL}/tasks`, {}, {
                headers: {
                    Authorization: `Bearer ${req.session.access_token}`,
                    "Content-Type": "application/json",
                },
            });
    
            const response2 = await axios.get(`${BACKEND_URL}/me`, {}, {
                headers: {
                    Authorization: `Bearer ${req.session.access_token}`,
                    "Content-Type": "application/json",
                },
            });
    
            res.render("index", { emailCurrentUser: response2.data.email, tasks: response.data });
        } catch (error) {
            console.log("Ошибка сервера:", error.response?.data)
        }
    } else {
        res.redirect("/login");
    }
});


app.get("/login", (req, res) => {
    res.render("login", { error: null });
});


app.get("/register", (req, res) => {
    res.render("register", { error: null });
});


app.post("/login", async (req, res) => {
    const { email, password } = req.body;
    try {
        const response = await axios.post(`${BACKEND_URL}/login`, { 
            email, 
            password 
        }, {
            withCredentials: true,
            headers: {
                "Content-Type": "application/json"
            }
        });
        
        req.session.access_token = response.data.access_token;
        
        // Явный return с redirect
        return req.session.save((err) => {
            if (err) {
                console.error("Session save error:", err);
                return res.render("login", { error: "Ошибка сервера" });
            }
            return res.redirect("/");
        });
        
    } catch (error) {
        console.error("Login error:", error.response?.data);
        return res.render("login", { error: "Неверный email или пароль" });
    }
});


app.post("/register", async (req, res) => {
    const { email, password_1 } = req.body;
    const password = password_1;

    try {
        const response = await axios.post(`${BACKEND_URL}/register`, { 
            email, 
            password
        }, {
            withCredentials: true,
            headers: {
                "Content-Type": "application/json"
            }
        });
        
        return req.session.save((err) => {
            if (err) {
                console.error("Session save error:", err);
                return res.render("register", { error: "Ошибка сервера" });
            }
            return res.redirect("/login");
        });
    } catch (error) {
        console.error("Registration error:", error.response?.data);
        return res.render("register", { 
            error: error.response?.data?.message || "Ошибка регистрации" 
        });
    }
});


app.post("/logout", async (req, res) => {
    try {
        await axios.post(`${BACKEND_URL}/logout`, {}, {
            withCredentials: true
        });
    } catch (error) {
        console.error("Logout error:", error);
    } finally {
        req.session.destroy();
        return res.redirect("/login");
    }
});


app.delete("/delete-connection/:taskId", async (req, res) => {
    const { taskId } = req.params;
    const { email_user } = req.query;

    try {
        const response = await axios.delete(`${BACKEND_URL}/tasks/delete_connection/${taskId}`, {
            params: { email_user },
            headers: {
                Authorization: `Bearer ${req.session.access_token}`,
                "Content-Type": "application/json",
            },
        });

        res.json(response.data);
    } catch (error) {
        console.error("Error deleting connection:", error.response?.data);
        res.status(500).json({ error: "Ошибка при удалении участника" });
    }
});


app.post("/create-task", async (req, res) => {
    const { title, status, description } = req.body;
    try {
        const response = await axios.post(`${BACKEND_URL}/tasks`, {
            title,
            status,
            description
        }, {
            headers: {
                Authorization: `Bearer ${req.session.access_token}`,
                "Content-Type": "application/json",
            },
        });

        res.json(response.data);
    } catch (error) {
        console.error("Error creating task:", error.response?.data);
        res.status(500).json({ error: "Ошибка при создании задачи" });
    }
});


app.put('/update-task/:taskId', async (req, res) => {
    const taskId = req.params.taskId;
    const { title, status, description } = req.body;

    try {
        const response = await axios.put(
            `${BACKEND_URL}/tasks/${taskId}`,
            { title, status, description },
            {
                headers: {
                    Authorization: `Bearer ${req.session.access_token}`,
                    "Content-Type": "application/json",
                },
            }
        );

        res.json(response.data);
    } catch (error) {
        console.error("Error updating task:", error.response?.data || error.message);
        res.status(500).json({ error: "Ошибка при обновлении задачи" });
    }
});


app.delete("/delete-task/:taskId", async (req, res) => {
    const { taskId } = req.params;

    try {
        const response = await axios.delete(`${BACKEND_URL}/tasks/${taskId}`, {
            headers: {
                Authorization: `Bearer ${req.session.access_token}`,
                "Content-Type": "application/json",
            },
        });

        res.json(response.data);
    } catch (error) {
        console.error("Error deleting connection:", error.response?.data);
        res.status(500).json({ error: "Ошибка при удалении участника" });
    }
});


app.post("/add-participant/:taskId", async (req, res) => {
    const { taskId } = req.params;
    const { email, typeConnection } = req.body;

    try {
        const response = await axios.post(`${BACKEND_URL}/tasks/add_user/${taskId}`, {}, {
            params: {
                new_user: email,
                type_connection: typeConnection
            },
            headers: {
                Authorization: `Bearer ${req.session.access_token}`,
                "Content-Type": "application/json", 
            },
        });

        res.json(response.data);
    } catch (error) {
        if (error.response && error.response.data && error.response.data.detail) {
            const { code, reason } = error.response.data.detail;
            if (code === "USER_NOT_FOUND") {
                return res.status(404).json({ error: "Пользователь с таким email не найден" });
            }
        }

        console.error("Error adding participant:", error.response?.data);
        res.status(500).json({ error: "Ошибка при добавлении участника" });
    }
});


// Обработчик для обновления Access Token
const refreshAccessToken = async (req) => {
    try {
        const response = await axios.post(`${BACKEND_URL}/refresh_token`, {}, {
            withCredentials: true // Отправляем HTTP-Only куки с Refresh Token
        });
        
        req.session.access_token = response.data.access_token;
        axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`;
        return true;
    } catch (error) {
        console.error("Token refresh failed:", error);
        return false;
    }
};

// Перехватчик ошибок для Axios
axios.interceptors.response.use(
    response => response,
    async error => {
        const originalRequest = error.config;
        
        // Если ошибка 401 и это не запрос на обновление токена
        if (error.response.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            
            // Пробуем обновить Access Token
            const refreshed = await refreshAccessToken(originalRequest.req);
            if (refreshed) {
                // Повторяем оригинальный запрос с новым токеном
                originalRequest.headers['Authorization'] = `Bearer ${originalRequest.req.session.access_token}`;
                return axios(originalRequest);
            }
        }
        
        return Promise.reject(error);
    }
);


// Запуск сервера
const PORT = 8085;
app.listen(PORT, () => {
    console.log(`Сервер запущен на порту: ${PORT}`);
});