# Curiosity Box

A safe learning platform where kids ask questions within parent-approved topics, powered by Claude AI.

## Features

### Core Functionality
- **Safe Learning Environment**: Parents control which topics children can explore
- **AI-Powered Answers**: Claude provides age-appropriate, educational responses
- **Topic Categories**: Pre-defined safe learning categories (Animals, Space, Science, etc.)
- **Question History**: Track all questions and answers
- **Family Management**: Support for multiple children per family
- **Authentication**: Token-based API authentication for parents

### Production-Ready Features
- **Performance Optimized**: Query optimization with strategic database indexes
- **Rate Limiting**: Prevents abuse and controls API costs
- **Health Checks**: Kubernetes-ready health/readiness/liveness endpoints
- **Structured Logging**: JSON logging for production observability
- **API Versioning**: Future-proof API design with v1 namespace
- **Error Handling**: Standardized error responses across all endpoints
- **CI/CD Pipeline**: Automated testing, linting, and security scanning

## Tech Stack

- **Backend**: Django 6.0 + Django REST Framework
- **Database**: PostgreSQL 15
- **AI**: Anthropic Claude API
- **Authentication**: Token-based (DRF)

## 📚 API Documentation

Complete OpenAPI 3.0 specification available in the [`docs/`](./docs) directory.

**Quick links:**
- [OpenAPI Spec (YAML)](./docs/openapi.yaml)
- [API Documentation Guide](./docs/README.md)
- View interactively: https://editor.swagger.io/ (import `openapi.yaml`)

The API documentation includes:
- ✅ All endpoint specifications with examples
- ✅ Authentication flow details
- ✅ Pagination structure
- ✅ Rate limiting recommendations
- ✅ Request/response schemas
- ✅ Error response formats

## Quick Start with Docker (Recommended)

### Prerequisites

- Docker and Docker Compose installed
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd curiosity-box
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your Anthropic API key:
   ```env
   ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
   ```

3. **Start the application**
   ```bash
   docker-compose up --build
   ```

   This will:
   - Start PostgreSQL database
   - Run database migrations
   - Seed topic categories
   - Start Django development server at http://localhost:8000

4. **Create a superuser** (in a new terminal)
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

### Access the Application

- **API**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/

### Stop the Application

```bash
docker-compose down
```

To remove all data (database volumes):
```bash
docker-compose down -v
```

## Local Development Setup (Alternative)

If you prefer running without Docker:

### Prerequisites

- Python 3.14
- PostgreSQL 15
- pip and virtualenv

### Installation

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL database**
   ```bash
   # Using Docker
   docker run --name curiositybox-db \
     -e POSTGRES_DB=curiositybox \
     -e POSTGRES_USER=postgres \
     -e POSTGRES_PASSWORD=postgres \
     -p 5432:5432 \
     -d postgres:15

   # Or create manually with psql
   psql -U postgres
   CREATE DATABASE curiositybox;
   \q
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   python manage.py seed_topics
   python manage.py createsuperuser
   ```

6. **Start development server**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

**Base URL**: `/api/v1/` (versioned for future compatibility)

### Authentication

- `POST /api/v1/auth/register/` - Register a new parent account
- `POST /api/v1/auth/login/` - Login and get auth token
- `POST /api/v1/auth/logout/` - Logout (delete token)

### Topics

- `GET /api/v1/topics/` - List all active topics (public)
- `GET /api/v1/topics/{slug}/` - Get topic details (public)

### Children

- `GET /api/v1/children/` - List children (requires auth)
- `GET /api/v1/children/{id}/` - Get child details (requires auth)
- `GET /api/v1/children/{id}/questions/` - Get child's questions (requires auth)
- `POST /api/v1/children/{id}/topics/enable/` - Enable topic for child (requires auth)
- `POST /api/v1/children/{id}/topics/disable/` - Disable topic for child (requires auth)

### Questions

- `POST /api/v1/questions/ask/` - Ask a question (public, rate limited: 20/min per child)
- `GET /api/v1/questions/` - List questions (public, paginated)
- `GET /api/v1/questions/?child_id={id}` - Filter by child (public)
- `POST /api/v1/questions/{id}/mark_helpful/` - Mark answer as helpful (public)

### Health Checks

- `GET /api/v1/health/` - Overall health status (for monitoring)
- `GET /api/v1/health/ready/` - Readiness probe (for Kubernetes)
- `GET /api/v1/health/live/` - Liveness probe (for Kubernetes)

**Note**: Legacy `/api/` endpoints (without `/v1/`) still work for backward compatibility but will be deprecated in future releases.

## Example API Usage

### 1. Register a parent account

```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "parent@example.com",
    "password": "securepass123",
    "name": "Jane Doe",
    "family_name": "Doe Family"
  }'
```

Response:
```json
{
  "token": "abc123...",
  "parent": {
    "id": 1,
    "name": "Jane Doe",
    "email": "parent@example.com",
    "family": 1
  },
  "message": "Registration successful"
}
```

### 2. Create a child (via Django admin)

Visit http://localhost:8000/admin/ and create:
- A Child profile with name, age, and reading level

### 3. Enable a topic for the child

```bash
curl -X POST http://localhost:8000/api/v1/children/1/topics/enable/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"topic_slug": "animals"}'
```

### 4. Ask a question

```bash
curl -X POST http://localhost:8000/api/v1/questions/ask/ \
  -H "Content-Type: application/json" \
  -d '{
    "child_id": 1,
    "question": "Why do lions roar?"
  }'
```

Response:
```json
{
  "question": {
    "id": 1,
    "child_name": "Emma",
    "text": "Why do lions roar?",
    "topic_name": "Animals",
    "answer": "Lions roar to communicate with their pride...",
    "created_at": "2026-01-11T22:30:00Z"
  },
  "within_boundaries": true
}
```

## Project Structure

```
curiosity-box/
├── config/                 # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                   # Main application
│   ├── models/            # Database models
│   │   ├── family.py      # Family, Parent models
│   │   ├── child.py       # Child model
│   │   ├── topic.py       # TopicCategory, ChildTopicAccess
│   │   └── question.py    # Question model
│   ├── views/             # API views
│   │   ├── auth.py        # Authentication endpoints
│   │   ├── children.py    # Child management
│   │   ├── topics.py      # Topic browsing
│   │   └── questions.py   # Question asking
│   ├── serializers/       # DRF serializers
│   │   ├── auth.py
│   │   ├── child.py
│   │   ├── topic.py
│   │   └── question.py
│   ├── services/          # Business logic
│   │   └── question_service.py  # Question processing & Claude integration
│   ├── tests/             # Unit tests
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   ├── test_auth.py
│   │   └── test_views.py
│   ├── management/        # Django commands
│   │   └── commands/
│   │       └── seed_topics.py
│   ├── admin.py           # Django admin configuration
│   └── urls.py            # API URL routing
├── Dockerfile             # Docker image definition
├── docker-compose.yml     # Docker orchestration
├── entrypoint.sh          # Container startup script
├── requirements.txt       # Python dependencies
└── .env.example           # Environment variable template
```

## Running Tests

### With Docker

```bash
docker-compose exec web python manage.py test core
```

### Without Docker

```bash
python manage.py test core
```

Run specific test files:
```bash
python manage.py test core.tests.test_models
python manage.py test core.tests.test_services
python manage.py test core.tests.test_auth
python manage.py test core.tests.test_views
python manage.py test core.tests.test_performance
```

### Test Coverage

```bash
coverage run --source='core' manage.py test core
coverage report
coverage html  # Generate HTML report
```

## Performance & Scalability

This application is designed with production-grade performance in mind:

### Query Optimization
- **N+1 Prevention**: All list endpoints use `select_related()` and `prefetch_related()` to minimize database queries
- **Strategic Indexes**: Database indexes on frequently-queried fields:
  - `question_child_created_idx`: Questions filtered by child with ordering
  - `topic_slug_active_idx`: Topic lookups by slug
  - `child_topic_access_idx`: Permission boundary checks
  - `parent_email_idx`: Authentication lookups
- **Performance Tests**: Automated tests (`test_performance.py`) verify query counts don't regress

### Rate Limiting (Implemented)

| User Type | Limit | Purpose |
|-----------|-------|---------|
| Anonymous | 10/min | Prevent abuse |
| Authenticated | 100/min | Fair usage |
| AI Questions | 20/min per child | Control API costs |

Rate limiting is implemented using DRF throttles with custom per-child limiting for AI questions.

### Monitoring & Observability

**Structured Logging**
- JSON-formatted logs for easy parsing by log aggregation tools (ELK, Splunk, CloudWatch)
- Contextual information included: user_id, child_id, request path, error details
- Log levels: INFO for operations, WARNING for boundary violations, ERROR for failures

**Health Check Endpoints**
```bash
GET /api/v1/health/        # Overall health status
GET /api/v1/health/ready/  # Readiness probe (for K8s)
GET /api/v1/health/live/   # Liveness probe (for K8s)
```

These endpoints check:
- Database connectivity
- Anthropic API configuration
- Cache availability

**Error Tracking**
- Standardized error responses with error codes
- Detailed logging with stack traces for 5xx errors
- Client-friendly error messages

### Scalability Considerations

- **Stateless Design**: No session storage, scales horizontally
- **Database Connection Pooling**: Configured for high concurrency
- **Caching Ready**: Django cache framework configured (can add Redis)
- **Container-Ready**: Docker setup with health probes for orchestration

## CI/CD Pipeline

Automated quality checks run on every push:

### GitHub Actions Workflow

**Testing**
- Full test suite execution (40+ tests)
- Code coverage enforcement (>80% required)
- PostgreSQL integration testing

**Code Quality**
- Black: Code formatting validation
- isort: Import sorting validation
- flake8: Linting and complexity checks

**Security**
- Safety: Dependency vulnerability scanning
- OpenAPI spec validation

**Documentation**
- OpenAPI specification validation

See `.github/workflows/ci.yml` for complete pipeline configuration.

### Running Quality Checks Locally

```bash
# Run tests with coverage
coverage run --source='core' manage.py test core
coverage report --fail-under=80

# Format code
black .
isort .

# Lint
flake8 .

# Security scan
safety check --file=requirements.txt
```

## Available Topics

The application comes pre-seeded with these topic categories:

- 🦁 **Animals** - Wildlife, pets, and creatures
- 🚀 **Space** - Planets, stars, and the universe
- ⚙️ **How Things Work** - Everyday objects and machines
- 🌦️ **Weather** - Rain, snow, storms, and seasons
- 🔬 **Science Experiments** - Chemistry, physics, and fun experiments
- 📜 **History** - Past civilizations and historical events
- 🐠 **Ocean Life** - Marine biology and underwater ecosystems
- 🫀 **Human Body** - How our bodies work and stay healthy

## Development

### Adding a New Topic Category

Use the Django admin or create via management command:

```python
from core.models import TopicCategory

TopicCategory.objects.create(
    name="Dinosaurs",
    slug="dinosaurs",
    icon="🦕",
    description="Learn about prehistoric creatures",
    recommended_min_age=5,
    context_guidelines="Focus on fascinating facts about different dinosaur species..."
)
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_NAME` | PostgreSQL database name | `curiositybox` |
| `DB_USER` | PostgreSQL username | `postgres` |
| `DB_PASSWORD` | PostgreSQL password | `postgres` |
| `DB_HOST` | PostgreSQL host | `localhost` (`db` in Docker) |
| `DB_PORT` | PostgreSQL port | `5432` |
| `ANTHROPIC_API_KEY` | Claude API key | Required |

## Troubleshooting

### Database connection errors

If you see "database does not exist":
```bash
docker-compose exec db createdb -U postgres curiositybox
```

### Port already in use

If port 8000 or 5432 is already in use, edit `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change host port
```

### Migrations not running

Force migrations:
```bash
docker-compose exec web python manage.py migrate --run-syncdb
```

## License

[Your License Here]

## Contributing

[Contributing guidelines here]
