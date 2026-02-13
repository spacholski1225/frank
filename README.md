# Frank the Assistant

Local AI assistant for food tracking, note search, and calendar management using Claude Agent SDK.

## Features

### Phase 1 (MVP) - ✅ Complete
- 🍽️ **Food Tracking**: Log meals with automatic database lookup or LLM estimation
- 📊 **Nutrition Summary**: Daily calorie and macro tracking in markdown
- 💬 **Conversational Interface**: Natural language interaction via REST API

### Phase 2 (Coming Soon)
- 🔍 **Note Search**: RAG-powered search across Obsidian vault using ChromaDB

### Phase 3 (Planned)
- 📅 **Calendar Integration**: Google Calendar management via natural language

## Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Installation

1. **Clone repository**
   ```bash
   git clone <repo-url>
   cd frank
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

3. **Run with Docker**
   ```bash
   docker-compose up -d
   ```

   Or run locally:
   ```bash
   pip install -r requirements.txt
   uvicorn src.main:app --reload
   ```

4. **Test the API**
   ```bash
   curl -X POST http://localhost:8000/v1/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Zjadłem owsiankę i banana"}'
   ```

## API Documentation

See [docs/API.md](docs/API.md) for detailed API documentation.

### Quick Reference

#### Chat Endpoint
```bash
POST /v1/chat
{
  "message": "Zjadłem jajecznicę",
  "session_id": "optional-session-id"
}
```

#### Nutrition Status
```bash
GET /v1/status/nutrition
```

#### Refresh Food Database
```bash
POST /v1/system/refresh-db
```

## Project Structure

```
frank/
├── src/
│   ├── main.py              # FastAPI application
│   ├── agent.py             # FrankAgent (Agent SDK wrapper)
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   ├── tools/
│   │   ├── food_tool.py     # Food tracking tool
│   │   ├── notes_tool.py    # Note search (Phase 2)
│   │   └── calendar_tool.py # Calendar (Phase 3)
│   └── utils/
│       ├── markdown_parser.py
│       └── file_utils.py
├── frank_system/
│   ├── configs/
│   │   ├── system_prompt.md
│   │   └── food_database.md
│   └── obsidian_vault/
│       ├── Daily_Logs/
│       ├── Knowledge_Base/
│       └── Inbox/
├── tests/
├── docs/
└── docker-compose.yml
```

## Configuration

### Food Database

Edit `frank_system/configs/food_database.md` to add your custom meals:

```markdown
| Nazwa (Alias) | Kcal | Białko (g) | Węgle (g) | Tłuszcz (g) | Jednostka |
|---------------|------|------------|-----------|-------------|-----------|
| Owsianka      | 450  | 20         | 60        | 15          | porcja    |
```

After editing, reload: `POST /v1/system/refresh-db`

### System Prompt

Customize Frank's personality in `frank_system/configs/system_prompt.md`

## Development

### Running Tests
```bash
# Unit tests
pytest tests/ -v

# Integration tests (requires API key)
ANTHROPIC_API_KEY=your_key pytest tests/ -v -m integration

# Specific test file
pytest tests/test_food_tool.py -v
```

### Adding New Tools

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for guide on adding custom tools.

## Deployment

### Raspberry Pi 5

1. Install Docker on Raspberry Pi
2. Copy project files
3. Configure environment variables
4. Run: `docker-compose up -d`

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment guide.

## License

MIT License - see LICENSE file for details.

## Acknowledgments

Built with [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk)
