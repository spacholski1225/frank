# Frank the Assistant - API Documentation

Base URL: `http://localhost:8000`

## Endpoints

### 1. Chat with Frank

**Endpoint:** `POST /v1/chat`

**Description:** Main conversational endpoint. Send messages to Frank and receive responses.

**Request Body:**
```json
{
  "message": "Zjadłem owsiankę i banana",
  "session_id": "optional-session-id-for-context"
}
```

**Response:**
```json
{
  "response": "Zalogowałem do dziennika:\n- Owsianka: 450 kcal (20g B, 60g W, 15g T) - z bazy\n- Banan: 105 kcal (1g B, 27g W, 0g T) - z bazy\n\nRazem: 555 kcal",
  "session_id": "generated-session-id"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Zjadłem jajecznicę",
    "session_id": null
  }'
```

---

### 2. Get Nutrition Status

**Endpoint:** `GET /v1/status/nutrition`

**Description:** Get today's nutrition summary from daily log.

**Response:**
```json
{
  "date": "2026-02-13",
  "total_kcal": 1250,
  "total_protein": 65.0,
  "total_carbs": 120.0,
  "total_fat": 45.0,
  "meal_count": 3
}
```

**Example:**
```bash
curl http://localhost:8000/v1/status/nutrition
```

---

### 3. Refresh Food Database

**Endpoint:** `POST /v1/system/refresh-db`

**Description:** Reload food_database.md after making changes.

**Response:**
```json
{
  "status": "reloaded",
  "item_count": 15
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/v1/system/refresh-db
```

---

### 4. Health Check

**Endpoint:** `GET /health`

**Description:** Service health check.

**Response:**
```json
{
  "status": "healthy",
  "service": "Frank the Assistant",
  "version": "0.1.0"
}
```

---

## Session Management

Frank maintains conversation context using session IDs:

1. **First message**: Omit `session_id` or set to `null`
2. **Follow-up messages**: Use the `session_id` from previous responses

**Example Session:**
```bash
# First message
curl -X POST http://localhost:8000/v1/chat \
  -d '{"message": "Co jadłem dzisiaj?"}' | jq
# Response includes: "session_id": "abc123"

# Follow-up (remembers context)
curl -X POST http://localhost:8000/v1/chat \
  -d '{"message": "Dodaj jeszcze jabłko", "session_id": "abc123"}'
```

---

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK`: Success
- `400 Bad Request`: Invalid request body
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Components not initialized

**Error Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Rate Limiting

No built-in rate limiting currently. For production deployment, consider adding:
- Nginx reverse proxy with rate limiting
- API gateway (Kong, Tyk)
- Application-level rate limiting middleware

---

## Authentication

Currently no authentication. For production:
- Add API key authentication
- Implement JWT tokens
- Use OAuth2 for multi-user scenarios

See [docs/SECURITY.md](docs/SECURITY.md) for securing Frank.
