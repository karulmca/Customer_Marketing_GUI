# Copilot Instructions for Customer Marketing GUI

## Architecture Overview
- **Monorepo** with Python backend (FastAPI), React frontend, and PostgreSQL database, orchestrated via Docker Compose.
- **Backend** (`backend_api/`): FastAPI app exposing REST APIs for data scraping, file upload, and database operations. Uses APScheduler for background jobs. Key entry: `backend_api/main.py`.
- **Frontend** (`frontend/`): React app (see `frontend/package.json` for scripts). Communicates with backend via REST.
- **Database**: PostgreSQL, initialized via Docker Compose and `database_config/` scripts. Redis is optionally used for caching.
- **Configuration**: Environment variables and JSON/INI config files (`config.json`, `config.production.json`, `auth/config.ini`).

## Developer Workflows
- **Local Setup**: Run `setup_react_app.sh` to install backend (Python) and frontend (Node) dependencies.
- **Manual Start (Dev)**:
  - Backend: `python backend_api/main.py` (port 8000)
  - Frontend: `cd frontend && npm start` (port 3000)
- **Production Deployment**: Use `deploy.sh` (Linux/macOS) or `docker-compose.prod.yml` for all-in-one Docker deployment. See health checks in `docker-compose.yml`.
- **Database Setup**: Use `setup_fresh_production.py` or `setup_production_database.py` for initial schema. For local dev, see `database_config/setup_database.py`.
- **Logs**: Backend logs to `/app/logs` (Docker volume `backend_logs`).

## Project Conventions & Patterns
- **Backend**:
  - All API endpoints defined in `backend_api/main.py` and submodules.
  - Uses Pydantic models for request/response validation.
  - Background jobs via APScheduler (optional, auto-detects availability).
  - Database access via SQLAlchemy and psycopg2.
- **Frontend**:
  - Uses Material UI and React Router.
  - API calls via Axios to backend endpoints.
- **Config**:
  - Sensitive values (DB credentials, secrets) are loaded from `.env` files and not committed.
  - `config.json` and `config.production.json` are mounted read-only in Docker.
- **Docker**:
  - Each service has its own Dockerfile. Compose files define volumes, health checks, and dependencies.
  - Use `docker-compose.yml` for dev, `docker-compose.prod.yml` for production.

## Integration Points
- **Backend <-> Database**: Via SQLAlchemy/psycopg2, connection string from env/config.
- **Frontend <-> Backend**: REST API calls, CORS enabled in FastAPI.
- **Redis**: Optional, for caching (see `docker-compose.yml`).

## Examples
- To add a new API: Create endpoint in `backend_api/main.py` or a controller, update Pydantic models, and document in OpenAPI (auto-generated).
- To add a frontend feature: Add React component in `frontend/src/`, use Axios for API calls.

---

For more details, see key files:
- `backend_api/main.py`, `frontend/package.json`, `docker-compose.yml`, `setup_react_app.sh`, `deploy.sh`, `database_config/`

If any section is unclear or missing, please provide feedback for improvement.
