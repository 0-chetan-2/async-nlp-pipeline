# Async NLP Pipeline

An asynchronous Natural Language Processing (NLP) pipeline built with **FastAPI**, **Celery**, **Redis**, **SQLAlchemy (Async)**, and **PostgreSQL**.

## Directory Structure

```
async-nlp-pipeline/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── documents.py
│   │       └── tasks.py
│   │
│   ├── models/
│   │   └── __init__.py
│   │
│   ├── schemas/
│   │   └── __init__.py
│   │
│   ├── services/
│   │   └── __init__.py
│   │
│   └── workers/
│       └── __init__.py
│
├── tests/
│   └── __init__.py
│
├── uploads/
│   └── .gitkeep
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Features

- **FastAPI Web Framework**: Asynchronous REST API endpoints for document management and task tracking.
- **Background Worker Queue**: Celery workers powered by Redis broker for non-blocking NLP text extraction & processing.
- **Async Database Layer**: SQLAlchemy 2.0 with PostgreSQL (`asyncpg`).
- **Containerized Setup**: Docker and Docker Compose definitions for easy local development and deployment.

## Getting Started

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (Optional for containerized run)
- Redis and PostgreSQL (if running locally without Docker)

### Quickstart with Docker Compose

1. Clone the repository and navigate into the project directory:
   ```bash
   cd async-nlp-pipeline
   ```

2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

3. Start all services using Docker Compose:
   ```bash
   docker-compose up --build
   ```

4. Access the API documentation:
   - Interactive Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Running Locally without Docker

1. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the FastAPI web application:
   ```bash
   uvicorn app.main:app --reload
   ```

4. Start the Celery worker (in a separate terminal):
   ```bash
   celery -A app.workers celery_app worker --loglevel=info
   ```

## License

MIT
