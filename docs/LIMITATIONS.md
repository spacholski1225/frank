# Known Limitations - MVP (v0.1.0)

## Current Limitations

### Food Tracking
- Manual food database management (no web UI)
- No portion size tracking (assumes standard portions)
- Estimation quality depends on LLM knowledge
- No food history or analytics

### Data Storage
- Daily logs not searchable yet (Phase 2 feature)
- No backup/sync mechanism
- Manual Obsidian vault management

### API
- No authentication
- No rate limiting
- Single user only
- No WebSocket/real-time updates

### Deployment
- Local deployment only (no cloud)
- No HTTPS support out of box
- Requires manual Raspberry Pi setup

## Coming in Phase 2

- ChromaDB integration for note search
- RAG-powered knowledge base queries
- Better food portion tracking
- Analytics dashboard

## Coming in Phase 3

- Google Calendar integration
- Multi-user support
- Authentication & authorization
- Newsletter summarization
