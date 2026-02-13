# Frank the Assistant

Local AI assistant for food tracking, note search, and calendar management.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

3. Run server:
   ```bash
   uvicorn src.main:app --reload
   ```

## API Endpoints

- `POST /v1/chat` - Main conversational endpoint
- `POST /v1/system/refresh-db` - Reload food database
- `GET /v1/status/nutrition` - Today's nutrition summary

## Project Structure

```
frank/
├── src/              # Application code
├── tests/            # Test suite
├── frank_system/     # Data & configuration
│   ├── configs/      # System prompts, food DB
│   └── obsidian_vault/  # User data (markdown)
└── docs/             # Documentation
```
