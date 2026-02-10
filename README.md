# DA Videoflix

A Django REST Framework-based video streaming platform with JWT authentication, HLS video streaming, and asynchronous task processing.

## Project Overview

DA Videoflix is a backend API for a video streaming service, similar to popular platforms like Netflix. It provides secure user authentication, video content management, and adaptive HLS (HTTP Live Streaming) for optimal video playback across different network conditions and devices.

## Features

- **User Authentication**
  - User registration with email verification
  - JWT-based authentication with access and refresh tokens
  - Secure cookie-based token storage
  - Password reset functionality
  - Token blacklisting for secure logout

- **Video Streaming**
  - HLS (HTTP Live Streaming) support
  - Multiple resolution variants for adaptive streaming
  - Secure video access with authentication
  - Video metadata management (title, description, category, thumbnails)

- **Asynchronous Processing**
  - Background task processing with RQ (Redis Queue)
  - Email notifications (welcome emails, password resets)
  - Scalable video processing pipeline

- **Infrastructure**
  - Docker and Docker Compose support
  - PostgreSQL database
  - Redis for caching and task queues
  - Static file serving with WhiteNoise

## Getting Started

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 13 or higher
- Redis 6 or higher
- Docker and Docker Compose (optional)

### Local Setup

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd da-videoflix
```
#### 2. Environment Configuration

Create a `.env` file in the project root or copy the `.env.template`:

```env
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=adminpassword
DJANGO_SUPERUSER_EMAIL=admin@example.com

SECRET_KEY="your_secret_key_here"
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500

DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=db
DB_PORT=5432

REDIS_HOST=redis
REDIS_LOCATION=redis://redis:6379/1
REDIS_PORT=6379
REDIS_DB=0

EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email_user
EMAIL_HOST_PASSWORD=your_email_user_password
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=default_from_email

```

### Docker Setup

```bash
# Build and start all services
docker-compose up --build
```

## API Reference

### Authentication Endpoints

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/api/register/` | POST | Register a new user | No |
| `/api/activate/<uidb64>/<token>/` | GET | Activate user account | No |
| `/api/login/` | POST | Login and receive JWT tokens | No |
| `/api/logout/` | POST | Logout and blacklist tokens | No |
| `/api/token/refresh/` | POST | Refresh access token | No |
| `/api/password_reset/` | POST | Request password reset | No |
| `/api/password_confirm/<uidb64>/<token>/` | POST | Confirm password reset | No |

### Video Endpoints

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/api/video/` | GET | List all videos | Required |
| `/api/video/<movie_id>/<resolution>/index.m3u8` | GET | Get HLS playlist | Required |
| `/api/video/<movie_id>/<resolution>/<segment>/` | GET | Get HLS video segment | Required |

## Project Structure

```
da-videoflix/
├── auth_app/              # Authentication application
│   ├── api/               # API views, serializers, services
│   ├── migrations/        # Database migrations
│   └── templates/         # Email templates
├── video_app/             # Video management application
│   ├── api/               # API views, serializers, services
│   └── migrations/        # Database migrations
├── core/                  # Project settings and configuration
├── media/                 # User-uploaded files
├── static/                # Static files (CSS, JS, images)
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Docker Compose configuration
└── backend.Dockerfile     # Docker image definition
```

## Support

For questions, issues, or feature requests, please open an issue in the repository's issue tracker.

## Contributing

Contributions are welcome! Please refer to the project's contribution guidelines before submitting pull requests.

## License

This project is licensed under the terms specified in the LICENSE file.