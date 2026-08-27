# Async NLP Pipeline

An asynchronous document processing pipeline built with FastAPI, PostgreSQL, Redis, Celery, and lightweight NLP techniques.

The system accepts documents through an API, stores them locally, creates a processing task, places the task on a Redis-backed Celery queue, and asynchronously processes the document using an NLP pipeline.

---

## Project Status

### Completed

- [x] Project foundation
- [x] Environment configuration
- [x] FastAPI application
- [x] PostgreSQL integration
- [x] Redis integration
- [x] Docker-based PostgreSQL and Redis
- [x] SQLAlchemy models
- [x] Alembic migrations
- [x] Task and result database schema
- [x] Task status management
- [x] Document upload API
- [x] File validation
- [x] Local file storage
- [x] Celery worker
- [x] Redis task queue
- [x] Asynchronous document processing
- [x] Failure handling
- [x] TXT text extraction
- [x] PDF text extraction
- [x] Text cleaning
- [x] Text chunking
- [x] Extractive summarization
- [x] NLP statistics
- [x] Long-document processing

### Current Phase

**Phase 5 — NLP Processing: COMPLETE**

### Next Phase

**Phase 6 — Result Persistence and Idempotency**

---

# Architecture

```text
                         Client
                           |
                           | HTTP
                           v
                    +--------------+
                    |   FastAPI    |
                    +------+-------+
                           |
                           | Upload
                           v
                    +--------------+
                    | File Storage |
                    +------+-------+
                           |
                           v
                    +--------------+
                    | PostgreSQL   |
                    |    PENDING   |
                    +------+-------+
                           |
                           | Celery task
                           v
                    +--------------+
                    |    Redis     |
                    |    Queue     |
                    +------+-------+
                           |
                           v
                    +--------------+
                    |    Celery    |
                    |    Worker    |
                    +------+-------+
                           |
                           | PROCESSING
                           v
                    +--------------+
                    |  NLPService  |
                    +------+-------+
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
        Extraction      Cleaning      Chunking
             |             |             |
             +-------------+-------------+
                           |
                           v
                    +--------------+
                    |   LexRank    |
                    | Summarization|
                    +------+-------+
                           |
                           v
                    +--------------+
                    | NLP Results  |
                    +------+-------+
                           |
                           v
                    +--------------+
                    | PostgreSQL   |
                    |   SUCCESS    |
                    +--------------+