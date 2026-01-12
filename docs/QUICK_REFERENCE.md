# Curiosity Box API - Quick Reference Card

## Base URL
```
http://localhost:8000/api
```

## Authentication

**Header Format:**
```
Authorization: Token <your-token>
```

**Get Token:**
```bash
# Register
POST /api/auth/register/
{
  "email": "parent@example.com",
  "password": "securepass123",
  "name": "Jane Doe",
  "family_name": "Doe Family"
}

# Login
POST /api/auth/login/
{
  "email": "parent@example.com",
  "password": "securepass123"
}
```

## Pagination

**Query Parameters:**
- `?page=1` - Page number (default: 1)
- `?page_size=20` - Items per page (max: 20, default: 20)

**Response:**
```json
{
  "count": 42,
  "next": "http://localhost:8000/api/topics/?page=2",
  "previous": null,
  "results": [...]
}
```

## Rate Limiting (Recommended)

| User Type | Limit |
|-----------|-------|
| Anonymous | 10/min |
| Authenticated | 100/min |
| AI Questions | 20/min per child |

⚠️ **Status**: Not currently implemented. See `docs/README.md` for setup.

## Common Endpoints

### 🔐 Authentication (Public)
```bash
POST   /api/auth/register/    # Register new parent
POST   /api/auth/login/       # Login
POST   /api/auth/logout/      # Logout (requires auth)
```

### 📚 Topics (Public)
```bash
GET    /api/topics/           # List all topics
GET    /api/topics/{slug}/    # Get topic details
```

### 👶 Children (Auth Required)
```bash
GET    /api/children/                      # List children
GET    /api/children/{id}/                 # Get child details
GET    /api/children/{id}/questions/       # Get child's questions
POST   /api/children/{id}/topics/enable/   # Enable topic
POST   /api/children/{id}/topics/disable/  # Disable topic
```

### ❓ Questions (Public)
```bash
GET    /api/questions/                 # List questions
POST   /api/questions/ask/             # Ask a question
GET    /api/questions/{id}/            # Get question details
POST   /api/questions/{id}/mark_helpful/  # Mark helpful
```

## Quick Examples

### Register & Get Token
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

### Enable Topic (Auth Required)
```bash
curl -X POST http://localhost:8000/api/children/1/topics/enable/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"topic_slug": "animals"}'
```

### Ask Question
```bash
curl -X POST http://localhost:8000/api/questions/ask/ \
  -H "Content-Type: application/json" \
  -d '{
    "child_id": 1,
    "question": "Why do lions roar?"
  }'
```

### Get Questions with Pagination
```bash
curl "http://localhost:8000/api/questions/?page=2&page_size=10"
```

## Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |
| 429 | Rate Limit Exceeded (when implemented) |

## Permission Boundaries

**What happens when a child asks about a locked topic?**

✅ **Allowed Topic:**
```json
{
  "question": {
    "answer": "Lions roar to communicate...",
    "was_within_boundaries": true
  },
  "within_boundaries": true
}
```

❌ **Denied Topic:**
```json
{
  "question": {
    "answer": "That's a great question about Space! However, I can't help you with that right now.\n\nInstead, you can ask me about: 🦁 Animals",
    "was_within_boundaries": false
  },
  "within_boundaries": false
}
```

## Available Topics

| Icon | Topic | Slug | Min Age |
|------|-------|------|---------|
| 🦁 | Animals | animals | 3 |
| 🚀 | Space | space | 5 |
| ⚙️ | How Things Work | how-things-work | 6 |
| 🌦️ | Weather | weather | 4 |
| 🔬 | Science Experiments | science | 7 |
| 📜 | History | history | 8 |
| 🐠 | Ocean Life | ocean | 5 |
| 🫀 | Human Body | human-body | 6 |

## Reading Levels

- `early` - Early Reader (5-7)
- `intermediate` - Intermediate (8-10)
- `advanced` - Advanced (11+)

## Tools

**View Documentation:**
- https://editor.swagger.io/ - Import `openapi.yaml`
- Swagger UI: `docker run -p 8080:8080 -e SWAGGER_JSON=/docs/openapi.yaml -v $(pwd)/docs:/docs swaggerapi/swagger-ui`

**Validate Spec:**
```bash
cd docs && ./validate-spec.sh
```

**Test API:**
- Postman: Import `openapi.yaml`
- Insomnia: Import `openapi.yaml`
- curl: Use examples above

---

For complete documentation, see:
- **OpenAPI Spec**: `docs/openapi.yaml`
- **Full Guide**: `docs/README.md`
- **Main README**: `README.md`
