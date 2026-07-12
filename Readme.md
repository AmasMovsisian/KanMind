# KanMind Backend

KanMind Backend is a REST API backend for a Kanban-style project management application built with Django and Django REST Framework.

---

## Frontend

The Kanmind frontend application provides the user interface for managing boards, tasks, users, and project workflows.

The frontend repository can be found here:

**Frontend Repository:**  
https://github.com/AmasMovsisian/Kanmind_Frontend

---

## Features

- **User Authentication**: Registration, login, and token-based authentication.
- **Email Check**: Endpoint to verify if an email is already registered.
- **Board Management**: Create, view, update, delete boards, and manage members.
- **Task Management**: Assign tasks, track status, set priority, and define due dates.
- **Comment System**: Add, view, and delete comments on a per-task basis.
- **Role-Based Permissions**: Granular access control for owners, members, assignees, and reviewers.
- **Standardized REST API**: Clean endpoints utilizing correct HTTP status codes.

---

## Tech Stack

- **Language**: Python 3.10+
- **Framework**: Django 6.x
- **Extension**: Django REST Framework
- **Database**: SQLite (Development)
- **Authentication**: Token Authentication

---

## Setup

### 1. Clone the Project

```bash
git clone <repository-url>
cd Kanmind_Backend
```

---

### 2. Create a Virtual Environment

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**Mac/Linux:**

```bash
python -m venv .venv
source .venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Environment Setup

```bash
cp .env.template .env
```

Generate a secure secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Open the newly created `.env` file and add the required variables:

```env
SECRET_KEY=your-generated-secret-key
DEBUG=True
```

---

### 5. Run Migrations

```bash
python manage.py migrate
```

---

### 6. Start the Development Server

```bash
python manage.py runserver
```

- **API Base URL**: `http://127.0.0.1:8000`
- **Django Admin**: `http://127.0.0.1:8000/admin`

---

## Authentication

All protected endpoints require an explicit authorization header using your generated token:

```http
Authorization: Token <your_token>
```

---

## API Endpoints

### 🔐 Authentication Module

Endpoints for user identity, registration, and onboarding.

* 📥 **`POST`** `/api/registration/`
  > Register a new user account.

* 🔑 **`POST`** `/api/login/`
  > Authenticate user credentials and return a session token.

* 🔍 **`GET`** `/api/email-check/?email=<address>`
  > Verify if an email address is already registered in the system.

---

### 📋 Boards Module

Endpoints for workspace and kanban board administration.

* ➕ **`POST`** `/api/boards/`
  > Create a brand new project board.

* 📂 **`GET`** `/api/boards/`
  > Retrieve a list of all boards available to you.

* 📄 **`GET`** `/api/boards/<id>/`
  > Fetch detailed information about a specific board.

* ✏️ **`PATCH`** `/api/boards/<id>/`
  > Update specific fields of an existing board.

* ❌ **`DELETE`** `/api/boards/<id>/`
  > Permanently remove a board.

---

### 🛠️ Tasks Module

Endpoints for managing individual cards, assignments, and statuses.

* ➕ **`POST`** `/api/tasks/`
  > Create a new task within a board.

* 👤 **`GET`** `/api/tasks/assigned-to-me/`
  > Fetch all active tasks assigned to the logged-in user.

* 👁️ **`GET`** `/api/tasks/reviewing/`
  > List all tasks currently awaiting your review.

* ✏️ **`PATCH`** `/api/tasks/<id>/`
  > Modify details or shift the status of a specific task.

* ❌ **`DELETE`** `/api/tasks/<id>/`
  > Delete a specific task from the system.

---

### 💬 Comments Module

Endpoints for team communication within individual tasks.

* 💬 **`GET`** `/api/tasks/<id>/comments/`
  > Fetch the complete comment history for a specific task.

* 📝 **`POST`** `/api/tasks/<id>/comments/`
  > Publish a new comment on a specific task.

* 🗑️ **`DELETE`** `/api/tasks/<task_id>/comments/<comment_id>/`
  > Remove a specific comment from a task.

---

## Status Codes

The API actively uses standard HTTP status codes to communicate response results:

* **200 OK**: Request succeeded.
* **201 CREATED**: Resource successfully created.
* **204 NO CONTENT**: Request succeeded, no content returned (e.g., after deletion).
* **400 BAD REQUEST**: Invalid data or missing parameters.
* **401 UNAUTHORIZED**: Missing or invalid authentication token.
* **403 FORBIDDEN**: Authenticated but lacks permission for this resource.
* **404 NOT FOUND**: Resource could not be found.

---

## Author

**Kanmind_Backend Project**  
Developed by Amas Movsisian
