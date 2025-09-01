# Claude Development Guide

## Project Overview
This is a Course Materials RAG (Retrieval-Augmented Generation) System that enables intelligent Q&A about course content using semantic search and AI-powered responses.

## Tech Stack
- **Backend**: Python 3.13+, FastAPI, uvicorn
- **AI**: Anthropic Claude API
- **Vector DB**: ChromaDB with Sentence Transformers
- **Package Manager**: uv

## Key Commands

### Running the Application
```bash
# Quick start
./run.sh

# Manual start
cd backend
uv run uvicorn app:app --reload --port 8000
```

### Development Commands
```bash
# Install dependencies
uv sync

# Install development dependencies (includes code quality tools)
uv sync --extra dev

# Run tests (if available)
uv run pytest

# Code Quality Tools
# Format code with black and isort
./scripts/format.sh

# Run linting with ruff
./scripts/lint.sh

# Run complete code quality pipeline
./scripts/check-all.sh

# Pre-commit checks (run before committing)
./scripts/pre-commit.sh

# Manual commands (if needed)
uv run black .          # Format code
uv run isort .          # Sort imports
uv run ruff check .     # Check code quality
uv run ruff format .    # Format with ruff
```

## Project Structure
```
/
├── backend/
│   ├── app.py              # FastAPI application and endpoints
│   ├── rag_system.py       # Core RAG orchestration
│   ├── vector_store.py     # ChromaDB operations
│   ├── ai_generator.py     # Claude AI integration
│   ├── document_processor.py # Document parsing and chunking
│   ├── search_tools.py     # Semantic search capabilities
│   ├── session_manager.py  # Conversation history tracking
│   ├── config.py          # Configuration management
│   └── models.py          # Pydantic data models
├── scripts/               # Development and quality scripts
│   ├── format.sh          # Code formatting script
│   ├── lint.sh           # Linting script
│   ├── check-all.sh      # Complete quality pipeline
│   └── pre-commit.sh     # Pre-commit hook script
├── frontend/              # Web interface files
├── docs/                  # Course materials to be indexed
└── pyproject.toml        # Project dependencies & tool config

```

## API Endpoints
- `GET /` - Web interface
- `POST /query` - Submit question and get AI response
- `GET /docs` - API documentation (Swagger UI)

## Environment Variables
Required in `.env` file:
```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## Data Flow
1. User submits question via web UI
2. FastAPI endpoint receives query
3. Session manager tracks conversation
4. RAG system orchestrates retrieval:
   - Generates embeddings via Sentence Transformers
   - Searches ChromaDB for relevant documents
   - Retrieves document chunks
5. AI Generator sends context to Claude API
6. Response with sources returned to user

## Code Quality & Standards

This project uses a comprehensive code quality pipeline with the following tools:

### Formatting Tools
- **Black**: Python code formatter (line-length: 88)
- **isort**: Import sorter (black-compatible profile)

### Linting Tools  
- **Ruff**: Fast Python linter and formatter
  - Replaces flake8, pycodestyle, pyflakes
  - Includes import sorting and code modernization
  - Configured for Python 3.13+

### Development Scripts
- `./scripts/format.sh` - Format code with black and isort
- `./scripts/lint.sh` - Run ruff linting with auto-fixes
- `./scripts/check-all.sh` - Complete quality pipeline + tests
- `./scripts/pre-commit.sh` - Pre-commit hook for staged files

### Configuration
All tool configurations are in `pyproject.toml`:
- Black: 88 character line length, Python 3.13 target
- isort: Black-compatible profile
- Ruff: Modern Python linting rules with sensible defaults

## Development Notes
- The system uses ChromaDB for persistent vector storage
- Session management allows for conversational context
- Document processor handles multiple file formats
- Search tools provide both semantic and keyword search
- Code is automatically formatted and linted via development scripts

## Common Tasks

### Adding New Documents
Place documents in the `docs/` directory. The system will automatically process and index them.

### Debugging
- API logs appear in terminal when running with `--reload`
- Check `/docs` endpoint for API testing
- Session data persists between requests

### Performance Considerations
- ChromaDB stores embeddings locally for fast retrieval
- Sentence Transformers model cached after first load
- API responses cached in session for conversation continuity