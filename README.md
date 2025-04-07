# Assingment of MediaAMP
I am Kushal Singh, Student at Poornima University. Want to work with MediaAMP to show off my skills .

# Task Manager API

A Flask-based API for task management, including user creation, task creation, logging, CSV upload, task retrieval, and soft deletion, with JWT authentication and Redis caching.

---

## Features

- User registration and login with JWT authentication
- Create, log, and manage tasks
- CSV upload support
- Task retrieval with pagination and filtering
- Redis caching for efficient data access
- Soft delete functionality for tasks
- Rate limiting to prevent abuse

---

## Tech Stack

- **Backend**: Flask, SQLAlchemy, Alembic
- **Database**: PostgreSQL
- **Authentication**: JWT
- **Cache**: Redis
- **Task Queue**: Celery (optional)
- **Testing**: Pytest, Postman
- **Rate Limiting**: Flask-Limiter

---

## Installation
## Use Python 3.11.7 

```bash
git clone https://github.com/kushalraj125/MediaAMP.git
cd flaskapp
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Setup

### PostgreSQL
Ensure PostgreSQL is running and a database named `task_manager` is created.

### Alembic Migration
```bash
flask db migrate -m "Initial migrate"
flask db upgrade

```

### Redis
Make sure Redis is running on `localhost:6379` (cheak at app/routes.py )

---

## Run the Server

```bash
flask run
```

---

## Plase Cheak imagesOfTestingAPIs Folder 

## API Endpoints

### Auth
- `POST /create-user` — Create a new user
- `POST /login` — Login and get JWT token

### Task
- `POST /create-task` — Create a task (JWT required)
- `POST /upload-csv` — Upload tasks via CSV
- `GET /tasks` — List paginated logs (with optional date filter)
- `GET /task/<task_logger_id>` — Get specific task log details
- `DELETE /task/<task_id>` — Soft delete a task

### Logs
- `POST /create-log` — Create a log for a task

---

## Testing with Postman or cURL

### Create User
```bash
curl -X POST http://127.0.0.1:5000/create-user \
-H "Content-Type: application/json" \
-d '{"username": "john_doe", "password": "secret123"}'

```

### Login
```bash
curl -X POST http://127.0.0.1:5000/login \
-H "Content-Type: application/json" \
-d '{"username": "john_doe", "password": "secret123"}'

```
### ✅ 3. Create Task (Requires JWT)

```bash
curl -X POST http://127.0.0.1:5000/create-task \
-H "Content-Type: application/json" \
-H "Authorization: Bearer <TOKEN>" \
-d '{
  "task_name": "Write Report",
  "description": "Finish the sustainability report",
  "status": true,
  "priority": "High",
  "created_at": "2025-04-03"
}'

```

### ✅ 4. Create Log Entry
``` bash
curl -X POST http://127.0.0.1:5000/create-log \
-H "Content-Type: application/json" \
-d '{"task_id": 1, "log_message": "Initial draft completed"}'

```

### ✅ 5. Upload CSV
```bash
curl -X POST http://127.0.0.1:5000/upload-csv \
-F "file=@/full/path/to/your/tasks.csv"
```

### ✅ 6. Get All Task Logs (Paginated)
``` bash
curl "http://127.0.0.1:5000/tasks?page=1&per_page=10"

```

### ✅ 7. Get Task Logs by Date (Cached with Redis)
``` bash
curl "http://127.0.0.1:5000/tasks?date=2025-04-03"

```

### ✅ 8. Get Task Log by Log ID
``` bash
curl http://127.0.0.1:5000/task/1

```

### ✅ 9. Soft Delete Task by Task ID
``` bash
curl -X DELETE http://127.0.0.1:5000/task/1

```

## Rate Limiting

Configured to allow:
- **100 requests per hour per IP**

Implemented using Flask-Limiter.

---

## Environment

Set environment variables using `.env`:
```
FLASK_ENV=development
SECRET_KEY=your_secret_key
```

---


