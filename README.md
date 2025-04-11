# TaskManager
Была проделана работа над созданием TaskManager, создан backend и frontend в разных модулях, работают физически независимо друг от друга.

## Что было использовано для создания
- **FastAPI (Python)** - для создания API;
- **PostgreSQL** - база данных для хранения данных о пользователях и заданий;
- **Redis** - для временного хранения заблокированных refresh_token's;
- **HTML/CSS** - верстка сайта;
- **NodeJS** - логика frontend, взаимодействие с API;
- **Prometheus/Grafana** - мониторинг ресурсов;
- **Alertmanager** - увеомления в Telegram на основе метрик Prometheus;
- **Экспортеры**:
    - Postgres-exporter - сбор метрик из PostgreSQL;
    - Redis-exporter - сбор метрик из Redis;
    - cAdvisor - сбор метрик из Docker;
    - prometheus_fastapi_instrumentator - сбор метрик из FastAPI;
- **Docker** - для контейнеризации сервисов;
- **Git** - для управлений версиями;
- **GitHub** - для облачного хранения проекта.

## Как запустить проект
Для начала, вам нужно клонировать проект вам на устройство, можно это сделать с помощью **git**:
```
git clone https://github.com/OPG-Team/TaskManager.git
```

После этого переходим в папку с проектом:
```
cd <your path>/TaskManager
```

Также нужно настроить `.env`, а если быть точнее создать `.env` и скопировать данные из `example.env` и поменять на нужные вам настройки.

### Опционально:

- **На Windows не будет работать cAdvisor, а так же уведомления в Telegram на основе его метрик по контейнерам** 

Дальше нужно установить настройки для **alertmanager**, переходим в директорию:
```
cd alertmanager
```

В `alertmanager.yml` устанавливаем свои значения для **bot_token** (бот который будет отправлять уведомления) и **chat_id** (чат в который будет отправлять уведомления)

<img width="640" src="https://github.com/user-attachments/assets/ace19f66-1ca4-4246-b29a-dca207243bb5" />

Далее возвращаемся в корень проекта и запускаем сборку проекта с помощью **docker-compose**:
```
cd ..
docker-compose up
```

После чего, вам будут доступны интерфейсы:

- Frontend - http://127.0.0.1:8085
- FastAPI (SwaggerUI) - http://127.0.0.1:8005/docs
- Grafana - http://127.0.0.1:2222
- Prometheus - http://127.0.0.1:7090
- cAdvisor - http://127.0.0.1:8080

А так же метрики:

- Postgres-exporter - http://127.0.0.1:9187/metrics
- Redis-exporter - http://127.0.0.1:9121/metrics
- cAdvisor - http://127.0.0.1:8080/metrics
- FastAPI - http://127.0.0.1:8005/metrics


## Использование
### Frontend

<img width="640" src="https://github.com/user-attachments/assets/917c83f3-3065-45a6-8762-237b84449b5d" />

После авторизации в приложении:

<img width="640" src="https://github.com/user-attachments/assets/e084528e-dc25-4b89-a1c3-85cf23a89767" />

**Возможности пользователя**
- Регистрация, авторизация и аутентификация;
- Создавать, редактировать и удалять свои задания;
- Добавлять пользователей в задание (по email);
- При добавлении пользователей можно указать "тип связи", то есть роли (**Владелец**, **Соавтор**, **Обычный**):
    - **Владелец**: редактировать задание, удалять задание, добавлять пользователей, удалять пользователей, просматривать задание;
    - **Соавтор**: редактировать задание, просматривать задание;
    - **Обычный**: просматривать задание.
- Фильтровать задания по дате создания и статусу;
- Выход из аккаунта.


### Swggaer UI
На главной странице отображаются два сервиса:
- Users - ендпоинты для работы с аккаунтом;
- Tasks - ендпоинты для работы с задачами.

<img width="640" alt="Screenshot 2025-04-11 at 14 37 00" src="https://github.com/user-attachments/assets/e863d6a0-fe58-4915-a991-96ecdf8aef98" />

Для авторизации в Swagger:
1. Регистрируем аккаунт;
2. Авторизируемся и получаем JWT токен, копируем;
3. Нажимаем на кнопку Authorize в верхней части страници;
4. Вставляем токен в поле `value` и нажимаем Authorize;
5. Готово! Теперь нам доступны все эндпоинты.

### Grafana
Данные для авторизации:
- Логин: `admin`
- Пароль: `admin`

Слева на панеле нажимте Dashboards

<img width="640" src="https://github.com/user-attachments/assets/ea7d8aea-a055-47fa-998a-c110ad5321d7" />

Откроется список доступных дашбордов:

<img width="640" src="https://github.com/user-attachments/assets/e1d677d4-413a-43eb-9e66-c58814dbd310" />

Пример dashboard для cAdvisor (на Windows не будет работать cAdvisor, все поля будут N/A)

<img width="640" src="https://github.com/user-attachments/assets/37eb4c84-d62c-4fb4-ae1d-01dd82735409" />

### Prometheus
На главной странице есть поле для ввода **promQL** запроса. С помощью данных запросов можно получить данные на конкретную (актуальную) метрику.

<img width="640" src="https://github.com/user-attachments/assets/039cc043-5442-40b5-97e3-b218f8a8135b" />

Вы можете перейти к статусам экспортеров, нужно перейти Status -> Targets

<img width="640" alt="Screenshot 2025-04-11 at 14 55 26" src="https://github.com/user-attachments/assets/3f225d32-7bcd-4218-95af-9758bb9ff695" />

Также есть страница проверки статуса триггеров для срабатывания уведомлений в Telegram, доступна по вкладке Alerts в верхней части страницы

<img width="640" alt="Screenshot 2025-04-11 at 15 00 11" src="https://github.com/user-attachments/assets/3425e558-0b37-4ac0-bae5-642cf405a04d" />

### cAdvisor
С главной страницы мы можем перейти к конкретному контейнеру и посмотреть его метрики

<img width="561" alt="Screenshot 2025-04-11 at 15 04 34" src="https://github.com/user-attachments/assets/49242bfe-2521-4e30-bc1f-afb35bbac5f6" />


## Описание работы
### Backend
Для backend был использован **FastAPI** и язык программирования **python**. Для работы с базой данных используется **SQLAlchemy** (ORM система) и миграции с помощью **Alembic**, как и говорилось выше **Redis** использовался для хранение _black_ листа _refresh_ токенов. По умолчанию работает на http://127.0.0.1:8005.

Чувствительные данные хранятся в `.env` и не выгружались в общий доступ на **GitHub**, а приводился пример файла для удобной последующей настройки.

```
backend
├── alembic.ini
├── auth        # Модуль для работы с аккаунтами
│   ├── database.py         # Классы ORM для алхимии для базы данных
│   ├── dependencies.py     # Зависимости для ендпоинтов
│   ├── models.py           # Pydantic модели для валидации данных
│   ├── responses           # Модуль с responses и error
│   │   ├── http_errors.py
│   │   ├── responses.py
│   │   └── utils.py
│   ├── router.py           # Роутер с ендпоинтами
│   ├── service.py          # Логика связи с БД (все функции с запросами)
│   └── utils.py            # Дополнительные утилиты
├── config.py        # Инициализация конфига         
├── database.py      # Базовые объекты для работы с БД
├── dockerfile
├── errors.py        # Общий класс для всех ошибок
├── logger.py        # Собственный объект для логирования
├── main.py          # Точка входа
├── migrations       # Миграции alembic
│   ├── env.py
│   ├── script.py.mako
│   └── versions
├── redis_tool.py    # Класс для работы с Redis
├── requirements.txt # Необходимые библиотеки
├── tasks            # Модуль для работы с задачами
│   ├── database.py
│   ├── models.py
│   ├── responses
│   │   ├── http_errors.py
│   │   └── responses.py
│   ├── router.py
│   └── service.py
└── utils.py         # Общие утилиты
```

#### Описание API
Для модуля `Users`:
- **POST** `/register` - регистрация нового аккаунта, принимает **json**:
    - email: string;
    - password: string.
- **POST** `/login` - авторизация и аутентификация пользователя, возврат JWT, принимает **json**:
    - email: string;
    - password: string.
- **POST** `/refresh_token` - обновления *access_token* с помощью *refresh_token*;
- **POST** `/logout` - выход из аккаунта, записывание *refresh_token* в *black list*;
- **GET** `/me` - данные о пользователя по JWT.

Для модуля `Tasks`:
- **GET** `/tasks/` - получение всех заданий;
- **POST** `/tasks/` - создание нового задания, принимает **json**: 
    - title: string;
    - status: enum (Новая, В работе, Завершена);
    - description: string.
- **PUT** `/tasks/{id}` - обновление определенного задания по **id**, принимает **json**:
    - title: string;
    - status: enum (Новая, В работе, Завершена);
    - description: string.
- **DELETE** `/tasks/{id}` - удаление задания по **id**;
- **POST** `/tasks/add_user/{id}` - добавление пользователя (**email**) в задание (**id**);
- **PUT** `/tasks/update_connection_type/{id}` - обновление типа связи пользователя с заданием;
- **DELETE** `/tasks/delete_connection/{id}` - удаление связи пользователя с заданием.

### Frontend
Базовый **frontend**, не замысловатая верстка и логика отрабатывает благодаря **NodeJS**. По умолчанию работает на http://127.0.0.1:8085.

```
frontend
├── app.js          # Вся логика с отправкой на FastAPI
├── dockerfile
├── package-lock.json
├── package.json
├── public          # Все статические данные
│   ├── css
│   │   ├── components
│   │   │   ├── filters.css
│   │   │   ├── form-add-connection-user.css
│   │   │   ├── login-form.css
│   │   │   ├── register-form.css
│   │   │   ├── task-form.css
│   │   │   ├── task-list-settings.css
│   │   │   └── task-list.css
│   │   ├── global.css
│   │   └── reset.css
│   └── js
│       ├── addConnectionUser.js
│       ├── createTask.js
│       ├── deleteConnectionUser.js
│       ├── deleteTask.js
│       ├── filter.js
│       ├── logout.js
│       └── settingTask.js
└── views          # Шаблоны страниц
    ├── index.ejs
    ├── login.ejs
    └── register.ejs
```

В файле `app.js` есть эндпоинты для запросов с браузера, а именно:
- **GET** `/` - главная страница с задачами;
- **GET** `/register` - страница для регистрации;
- **POST** `/register` - запрос на создание аккаунта;
- **GET** `/login` - страница для авторизации;
- **POST** `/login` - запрос на авторизацию;
- **POST** `/logout` - запрос на выход из аккаунта;
- **POST** `/create-task` - запрос на создание задачи, принимает **json**: 
    - title: string;
    - status: enum (Новая, В работе, Завершена);
    - description: string.
- **PUT** `/update-task/:taskId` - запрос на изменение задачи по _taskId_, принимает **json**: 
    - title: string;
    - status: enum (Новая, В работе, Завершена);
    - description: string.
- **DELETE** `/delete-task/:taskId` - запрос на удаление задачи по _taskId_;
- **POST** `/add-participant/:taskId` - запрос на создание участника в задачу по _taskID_ и _user_email_;
- **DELETE** `/delete-connection/:taskId` - запрос на удаление участника из задачи по _taskID_ и _user_email_.

Далее с эндпоинтов фронта запрос отправляется на **FastAPI**.

### Grafana
По умолчанию работает на http://127.0.0.1:2222.
```
grafana
├── dashboards        # Конфигурации для dashboard
│   ├── Cadvisor exporter-1744223552634.json        # для метрик от cAdvisor
│   ├── FastAPI Observability-1744117533744.json    # для метрик от FastAPI
│   ├── PostgreSQL Exporter-1744117548034.json      # для метрик от PostgreSQL
│   └── Redis Dashboard for Prometheus...           # для метрик от Reids
└── provisioning      # Инструкции для деплоя
    ├── dashboards
    │   └── dashboards.yaml
    └── datasources
        └── datasources.yml
```

### Prometheus
По умолчанию работает на http://127.0.0.1:7090.
```
prometheus
├── App.yml           # Инструкция для срабатывания уведомлений от FastAPI
├── Frontend.yml      # ... от Frontend
├── Redis.yml         # ... от Redis
├── postgres.yml      # ... от PostgreSQL
└── prometheus.yml    # Конфиг prometheus
```

### Alertmanager
```
alertmanager
├── alertmanager.yml    # Конфиг для alertmanager
└── template.tmpl       # Шаблон для текста уведмления
```

### База данных
ER-диаграмма базы данных PostgreSQL:
<img width="640" src="https://github.com/user-attachments/assets/0917d92f-ac6e-4904-a0d8-89f41eb35af2" />
