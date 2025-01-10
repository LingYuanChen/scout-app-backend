# Scout App Backend

A modern full-stack web application using FastAPI and React, with comprehensive user management, event planning, and meal management features.

## Quick Start Guide

### Prerequisites

- Docker and Docker Compose (for Docker setup)
- Python 3.9+ (for local setup)
- Node.js 16+ (for local setup)
- PostgreSQL (for local setup)

### Setting Up Development Environment

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd <project-directory>
```

2. **Configure Environment Variables**

Create and update the following variables in your `.env` file:

```bash
# Basic Configuration
PROJECT_NAME="Scout App"                    # Name shown to API users
STACK_NAME=scout-app                      # Docker Compose project name (no spaces/periods)

# Security
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY="your-generated-secret-key"      # JWT secret key
FIRST_SUPERUSER="admin@scoutapp.com"       # Admin email
FIRST_SUPERUSER_PASSWORD="secure-password"  # Admin password

# Database
POSTGRES_PASSWORD="your-db-password"        # PostgreSQL password

# Email Configuration (Optional - can be set up later)
SMTP_HOST=""                               # SMTP server host
SMTP_USER=""                               # SMTP username
SMTP_PASSWORD=""                           # SMTP password
EMAILS_FROM_EMAIL="noreply@scoutapp.com"   # Sender email address

# Monitoring (Optional)
SENTRY_DSN=""                             # Sentry DSN for error tracking
```

### Running with Docker

1. **Start all services**
```bash
docker compose watch
```

2. **View logs**
```bash
# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f backend
docker compose logs -f frontend
```

3. **Stop services**
```bash
docker compose down
```

The application will be available at:
- Frontend: http://localhost:5173
- API Documentation: http://localhost:8000/docs
- Automatic Alternative Docs (ReDoc): http://localhost:8000/redoc
- Database Web Administration: http://localhost:8080

## Documentation

- [API Documentation](./API.md) - Detailed API endpoints and usage
- [Interactive API Docs](http://localhost:8000/docs) - Swagger UI documentation (requires running server)

## Development Workflow

1. **Create a new branch**
```bash
git checkout -b feature/your-feature-name
```

2. **Modify or Add APIs**
```bash
# 1. Add/modify models in app/models.py

# 2. Create database migration
alembic revision --autogenerate -m "Add new model"
alembic upgrade head

# 3. Create/modify API endpoints in app/api/routes/
# 4. Register new router in app/api/main.py
```

3. **Write API Tests**
```bash
# Create test file for your new API
cd tests/api/routes/
touch test_new_model.py  # For Unix/Linux/mac
```

4. **Run tests before committing**
```bash
# Backend tests
cd backend
bash ./scripts/test.sh

# Test specific file
pytest ./app/tests/api/routes/test_file.py

# Run linting
bash ./scripts/lint.sh

# Frontend tests
cd frontend
npm run test
```

5. **Commit and push changes**
```bash
git add .
git commit -m "feat: description of your changes"
git push origin feature/your-feature-name
```

## License

This project is licensed under the MIT License.
