# Curiosity Box API Documentation

This directory contains the OpenAPI 3.0 specification for the Curiosity Box API.

## Viewing the API Documentation

### Option 1: Swagger UI (Recommended)

The easiest way to view and interact with the API documentation:

1. **Online Swagger Editor**
   - Go to https://editor.swagger.io/
   - Click **File > Import File**
   - Select `openapi.yaml`
   - You can now browse the docs and even try API calls

2. **Local Swagger UI with Docker**
   ```bash
   docker run -p 8080:8080 \
     -e SWAGGER_JSON=/docs/openapi.yaml \
     -v $(pwd)/docs:/docs \
     swaggerapi/swagger-ui
   ```
   Then open http://localhost:8080

3. **Using npx (Node.js required)**
   ```bash
   npx @stoplight/prism-cli mock docs/openapi.yaml
   ```

### Option 2: Redoc

For a beautiful, read-only documentation view:

```bash
docker run -p 8081:80 \
  -e SPEC_URL=openapi.yaml \
  -v $(pwd)/docs:/usr/share/nginx/html \
  redocly/redoc
```

Then open http://localhost:8081

### Option 3: VS Code Extension

Install the **OpenAPI (Swagger) Editor** extension in VS Code:
1. Install extension: `42Crunch.vscode-openapi`
2. Open `openapi.yaml`
3. Click the preview icon or press `Ctrl+Shift+P` → "OpenAPI: Show Preview"

## API Overview

### Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://api.curiositybox.example.com` (configure as needed)

### Authentication

The API uses **Token Authentication**. Include the token in the `Authorization` header:

```bash
Authorization: Token abc123def456ghi789jkl012mno345pqr678stu901vwx234
```

**Getting a token:**
1. Register: `POST /api/auth/register/`
2. Login: `POST /api/auth/login/`

### Rate Limiting

**Current Status**: Not implemented

**Recommended for Production**:
- Anonymous users: 10 requests/minute
- Authenticated users: 100 requests/minute
- AI question generation: 20 requests/minute per child

**Implementation**: Add to `config/settings.py`:
```python
REST_FRAMEWORK = {
    # ... existing settings ...
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10/minute',
        'user': '100/minute',
    }
}
```

### Pagination

All list endpoints support pagination with these query parameters:

| Parameter | Type | Default | Max | Description |
|-----------|------|---------|-----|-------------|
| `page` | integer | 1 | - | Page number |
| `page_size` | integer | 20 | 20 | Items per page |

**Example:**
```bash
GET /api/questions/?page=2&page_size=10
```

**Response format:**
```json
{
  "count": 42,
  "next": "http://localhost:8000/api/questions/?page=3",
  "previous": "http://localhost:8000/api/questions/?page=1",
  "results": [...]
}
```

## Quick Examples

### 1. Register a Parent

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "parent@example.com",
    "password": "securepass123",
    "name": "Jane Doe",
    "family_name": "Doe Family"
  }'
```

**Response:**
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

### 2. List Topics (Public)

```bash
curl http://localhost:8000/api/topics/
```

### 3. Enable Topic for Child (Requires Auth)

```bash
curl -X POST http://localhost:8000/api/children/1/topics/enable/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"topic_slug": "animals"}'
```

### 4. Ask a Question (Public)

```bash
curl -X POST http://localhost:8000/api/questions/ask/ \
  -H "Content-Type: application/json" \
  -d '{
    "child_id": 1,
    "question": "Why do lions roar?"
  }'
```

**Response (Allowed Topic):**
```json
{
  "question": {
    "id": 1,
    "child_name": "Emma",
    "text": "Why do lions roar?",
    "topic_name": "Animals",
    "answer": "Lions roar to communicate with their pride...",
    "was_within_boundaries": true,
    "created_at": "2026-01-11T15:30:00Z"
  },
  "within_boundaries": true
}
```

**Response (Denied Topic):**
```json
{
  "question": {
    "id": 2,
    "text": "How big is the moon?",
    "topic_name": "Space",
    "answer": "That's a great question about Space! However, I can't help you with that right now.\n\nInstead, you can ask me about: 🦁 Animals",
    "was_within_boundaries": false
  },
  "within_boundaries": false
}
```

## API Endpoints Summary

### Authentication
- `POST /api/auth/register/` - Register new parent
- `POST /api/auth/login/` - Login and get token
- `POST /api/auth/logout/` - Logout (requires auth)

### Topics (Public)
- `GET /api/topics/` - List all topics
- `GET /api/topics/{slug}/` - Get topic details

### Children (Requires Auth)
- `GET /api/children/` - List all children
- `GET /api/children/{id}/` - Get child details
- `GET /api/children/{id}/questions/` - Get child's questions
- `POST /api/children/{id}/topics/enable/` - Enable topic for child
- `POST /api/children/{id}/topics/disable/` - Disable topic for child

### Questions (Public)
- `GET /api/questions/` - List all questions
- `GET /api/questions/{id}/` - Get question details
- `POST /api/questions/ask/` - Ask a question
- `POST /api/questions/{id}/mark_helpful/` - Mark answer as helpful

## Permission Model

The API has a permission boundary system:

1. **Public Endpoints**: Topics browsing, question asking, question viewing
2. **Protected Endpoints**: Child management, topic access control
3. **Topic-Based Permissions**: Children can only ask questions about unlocked topics

**When a child asks about a restricted topic:**
- ❌ Question is NOT answered by AI
- ✅ Response suggests allowed topics
- ✅ Question is logged with `was_within_boundaries: false`

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid input",
  "errors": {
    "email": ["This field is required."]
  }
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 429 Rate Limit Exceeded (when implemented)
```json
{
  "detail": "Request was throttled. Expected available in 60 seconds."
}
```

## Schema Validation

The OpenAPI spec includes full schema validation for:
- Request bodies
- Response bodies
- Query parameters
- Path parameters

You can use tools like:
- **Postman** - Import `openapi.yaml` for automatic request/response validation
- **Insomnia** - Supports OpenAPI spec import
- **OpenAPI Generator** - Generate client SDKs in multiple languages

## Generating Client SDKs

You can generate client libraries in various languages using OpenAPI Generator:

```bash
# JavaScript/TypeScript
npx @openapitools/openapi-generator-cli generate \
  -i docs/openapi.yaml \
  -g typescript-fetch \
  -o clients/typescript

# Python
npx @openapitools/openapi-generator-cli generate \
  -i docs/openapi.yaml \
  -g python \
  -o clients/python

# Java
npx @openapitools/openapi-generator-cli generate \
  -i docs/openapi.yaml \
  -g java \
  -o clients/java
```

## Maintaining the Documentation

When adding new endpoints or modifying existing ones:

1. **Update `openapi.yaml`** with the new/changed endpoint
2. **Include examples** in the spec
3. **Document all parameters** and response codes
4. **Test the spec** using Swagger Editor to ensure it's valid
5. **Update this README** if adding major new features

## Additional Resources

- [OpenAPI Specification](https://spec.openapis.org/oas/v3.0.3)
- [Swagger Tools](https://swagger.io/tools/)
- [Redoc](https://redocly.com/redoc)
- [OpenAPI Generator](https://openapi-generator.tech/)
