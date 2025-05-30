# Project Management API

A comprehensive REST API for managing projects and tasks with multiple permission levels, built with Django REST Framework.

## Features

- JWT Authentication
- Project Management with multiple permission levels
- Task Management with status tracking
- Comments on tasks
- Notification system
- Activity logging
- Dynamic filtering and search
- Swagger documentation

## Requirements

- Python 3.8+
- Pipenv

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd project-management
```

2. Install dependencies:
```bash
pipenv install
```

3. Activate the virtual environment:
```bash
pipenv shell
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## API Documentation

Once the server is running, you can access the API documentation at:

- Swagger UI: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`

## API Endpoints

### Authentication
- `POST /api/v1/auth/register/`: Register a new user
- `POST /api/v1/auth/login/`: Obtain JWT token
- `POST /api/v1/auth/refresh/`: Refresh JWT token

### Users
- `GET /api/v1/users/`: List all users
- `GET /api/v1/users/profile/`: Get current user profile
- `PUT /api/v1/users/profile/`: Update current user profile

### Projects
- `GET /api/v1/projects/`: List all projects for current user
- `POST /api/v1/projects/`: Create a new project
- `GET /api/v1/projects/{id}/`: Get project details
- `PUT /api/v1/projects/{id}/`: Update project
- `DELETE /api/v1/projects/{id}/`: Delete project

### Tasks
- `GET /api/v1/tasks/`: List all tasks
- `POST /api/v1/tasks/`: Create a new task
- `GET /api/v1/tasks/{id}/`: Get task details
- `PUT /api/v1/tasks/{id}/`: Update task
- `DELETE /api/v1/tasks/{id}/`: Delete task
- `GET /api/v1/tasks/{id}/comments/`: List task comments
- `POST /api/v1/tasks/{id}/comments/`: Add comment to task
- `PUT /api/v1/tasks/{id}/comments/{comment_id}/`: Update comment
- `DELETE /api/v1/tasks/{id}/comments/{comment_id}/`: Delete comment

### Notifications
- `GET /api/v1/notifications/`: List all notifications
- `PUT /api/v1/notifications/{id}/`: Mark notification as read
- `POST /api/v1/notifications/mark-all-read/`: Mark all notifications as read

## Filtering and Search

### Projects
- Search by title and description
- Order by creation date, start date, or end date

### Tasks
- Filter by status, project, assigned user, and pinned status
- Filter by due date range
- Search by title and description
- Order by creation date, due date, or pinned status

## Authentication

The API uses JWT (JSON Web Token) authentication. To authenticate requests, include the JWT token in the Authorization header:

```
Authorization: Bearer <your-token>
```

## Permissions

- Project Manager:
  - Can create, update, and delete their projects
  - Can create and assign tasks
  - Can view all project details and tasks

- Project Member:
  - Can view project details
  - Can view and update assigned tasks
  - Can comment on tasks
  - Can view project activity

## Development

To run tests:
```bash
python manage.py test
```

## License

 