Async NLP Document Processing Platform

An asynchronous, containerized document-processing platform built with FastAPI, Celery, Redis, PostgreSQL, Docker, and NLP tooling.

The system accepts PDF/TXT documents through an API, creates a persistent processing task, queues the NLP workload through Redis, executes it in a Celery worker, and stores the resulting NLP output in PostgreSQL.

Project status: Backend MVP completed.
Next development phase: Improving the NLP pipeline, summary quality, and evaluation.

Overview

The platform is designed to process documents without making the API request wait for the full NLP workload.

Processing architecture

Client
  |
  v
FastAPI
  |
  +--------------------+
  |                    |
  v                    v
PostgreSQL            Redis
(Task State)          (Queue)
                         |
                         v
                  Celery Worker
                         |
                         v
                    NLP Pipeline
                         |
                         v
                    PostgreSQL
                       (Result)

Task lifecycle

Upload Document
      |
      v
202 Accepted
      |
      v
Task Created
      |
      v
PENDING
      |
      v
PROCESSING
      |
      +------------------+
      |                  |
      v                  v
   SUCCESS             FAILED

The key architectural decision is to separate request handling from long-running NLP execution.

Key Features

Asynchronous processing

PDF/TXT document upload

Background processing with Celery

Redis-backed task queue

Non-blocking API workflow

PostgreSQL-backed task state

Persisted NLP results

Reliability

Retry handling for transient connection and timeout failures

Exponential retry backoff

Idempotent task execution

One persisted result per task

Centralized application error classification

Processing time limits

Transaction-safe result persistence

Infrastructure

Dockerized application stack

Docker Compose orchestration

Dedicated database migration service

PostgreSQL health checks

Redis health checks

API health endpoints

Alembic migrations

NLP Pipeline

The current NLP implementation is an extractive summarization pipeline using LexRank.

Document
   |
   v
Text Extraction
   |
   v
Text Cleaning
   |
   v
Chunking
   |
   v
LexRank Summarization
   |
   +--> Word Count
   +--> Sentence Count
   +--> Character Count
   +--> Chunk Count
   |
   v
Structured Result

The current result conceptually contains:

{
    "summary": str,
    "chunk_count": int,
    "word_count": int,
    "sentence_count": int,
    "character_count": int,
}

Why Asynchronous Processing?

A document-processing workload may involve extraction, cleaning, chunking, and summarization.

A synchronous design would keep the HTTP request open:

Client
  |
  v
API
  |
  v
NLP
  |
  v
Response

This project instead uses:

Client
  |
  v
FastAPI -------> 202 Accepted
  |
  v
Create Task
  |
  v
Redis
  |
  v
Celery Worker
  |
  v
NLP
  |
  v
PostgreSQL

This architecture provides a cleaner foundation for longer-running workloads, retries, and future worker scaling.

Reliability and Fault Tolerance

Retry model

Transient infrastructure failures can be retried:

Retryable exceptions:
- ConnectionError
- TimeoutError

Maximum retries:
- 3

Backoff:
- 2 ** retries

When retry attempts are exhausted:

FAILED
TRANSIENT_ERROR

Non-retryable exceptions are classified directly.

Idempotency

Before doing NLP work, the worker checks whether a result already exists for the task.

Task received
     |
     v
Existing result?
   /           \
 Yes            No
  |              |
  |              v
  |             NLP
  |              |
  +--------------+
         |
         v
      Result

This protects against accidentally running the same logical task multiple times.

Error Classification

The application uses a centralized error taxonomy rather than exposing raw Python exception names.

Current error codes:

DOCUMENT_NOT_FOUND
INVALID_DOCUMENT
PROCESSING_TIMEOUT
TRANSIENT_ERROR
NLP_PROCESSING_ERROR
UNKNOWN_ERROR

This keeps error handling consistent between the worker, persistence layer, and API.

Technology Stack

Backend

Python 3.12

FastAPI

Uvicorn

Pydantic

Pydantic Settings

Database

PostgreSQL 16

SQLAlchemy 2.x

Alembic

asyncpg

Asynchronous Processing

Celery 5.6.x

Redis 7

NLP

NLTK

Sumy

LexRank

PDF/text extraction dependencies

Containerization

Docker

Docker Compose

python:3.12-slim

Development

Git

GitHub

PowerShell

Docker Desktop

WSL2

Repository Structure

async-nlp-pipeline/
|
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── documents.py
│   │       ├── tasks.py
│   │       └── __init__.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   │
│   ├── models/
│   │   ├── base.py
│   │   ├── enums.py
│   │   ├── error_codes.py
│   │   ├── task.py
│   │   └── result.py
│   │
│   ├── schemas/
│   │   ├── document.py
│   │   └── __init__.py
│   │
│   ├── services/
│   │   ├── error_classifier.py
│   │   ├── file_storage.py
│   │   ├── file_validator.py
│   │   ├── task_service.py
│   │   ├── result_service.py
│   │   └── nlp/
│   │       ├── service.py
│   │       └── summarizer.py
│   │
│   ├── workers/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── task_service.py
│   │   └── tasks.py
│   │
│   └── main.py
│
├── alembic/
│   ├── versions/
│   └── env.py
│
├── tests/
├── uploads/
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── alembic.ini
├── requirements.txt
└── README.md

Docker Compose Stack

The complete local stack contains:

postgres
redis
migration
api
worker

Start the stack

docker compose up -d

Check services

docker compose ps

Expected services:

nlp-postgres
nlp-redis
nlp-migration
nlp-api
nlp-worker

API logs

docker compose logs api

Worker logs

docker compose logs worker

Database Migrations

The project uses Alembic for explicit, reproducible database schema changes.

Run migrations

docker exec nlp-api python -m alembic upgrade head

Check migration version

docker exec nlp-api python -m alembic current

Health Checks

API

GET /health

Example:

{
  "status": "healthy"
}

Database

GET /health/db

Example:

{
  "database": 1
}

Core API

Upload a document

POST /api/v1/documents

The endpoint:

Validates the uploaded document

Stores the file

Creates a processing task

Enqueues a Celery task

Returns 202 Accepted with a task ID

Example:

{
  "task_id": "..."
}

Retrieve task status

GET /api/v1/tasks/{task_id}

Returns the current status and, when processing is complete, the persisted NLP result.

Example End-to-End Workflow

                    Upload
                       |
                       v
               FastAPI validation
                       |
                       v
                 Create Task
                       |
                       v
                   202 OK
                       |
                       v
                    Redis
                       |
                       v
                Celery Worker
                       |
                       v
                NLP Processing
                       |
                       v
             Persist NLP Result
                       |
                       v
                    SUCCESS

Failure path:

Processing failure
       |
       v
Retry when applicable
       |
       v
Error classification
       |
       v
FAILED
+
error_code
+
error_message

Project Status

Completed — Backend MVP

✅ FastAPI API
✅ PDF/TXT upload
✅ File validation
✅ PostgreSQL persistence
✅ Redis queue
✅ Celery background worker
✅ Task lifecycle management
✅ Result persistence
✅ Alembic migrations
✅ Retry handling
✅ Exponential backoff
✅ Idempotent processing
✅ Centralized error classification
✅ Processing time limits
✅ API health checks
✅ Database health checks
✅ Dockerized multi-service stack

The current GitHub version is intentionally focused on the backend and NLP-processing architecture.

Next Development Phase — NLP Improvements

The infrastructure layer is stable enough to support a more capable NLP engine.

The next phase focuses on improving summary quality and making NLP behavior measurable rather than adding another UI layer.

1. Better preprocessing

Planned improvements:

whitespace normalization

duplicate-line removal

noisy-text filtering

improved sentence segmentation

document normalization

better extraction cleanup

2. Smarter chunking

Move toward:

sentence-aware chunking
+
document-size-aware chunk sizes
+
section-aware boundaries

The goal is to avoid cutting sentences or logical sections in the middle.

3. Semantic sentence representation

Introduce lightweight sentence embeddings so sentence importance can be evaluated using semantic similarity rather than only lexical structure.

4. Hybrid sentence ranking

Combine signals such as:

semantic relevance
+
LexRank centrality
+
position
+
keyword relevance
+
section importance
-
redundancy

5. Redundancy reduction

Add similarity-aware sentence selection so summaries do not repeatedly express the same idea.

6. Adaptive summary length

Adjust summarization behavior based on document size:

Short document
    -> extractive summary

Medium document
    -> adaptive extractive summary

Long document
    -> hierarchical summarization

7. Hierarchical summarization

For larger documents:

Document
   |
   +--> Chunk 1 -> summary
   +--> Chunk 2 -> summary
   +--> Chunk 3 -> summary
   +--> Chunk N -> summary
                    |
                    v
              Global summary

8. NLP evaluation

The improved pipeline will be compared against the current LexRank baseline using objective measures such as:

ROUGE-1

ROUGE-2

ROUGE-L

compression ratio

redundancy

summary length

processing latency

The goal is to measure whether changes actually improve the system.

Planned NLP Architecture

The target NLP architecture is:

                    DOCUMENT
                        |
                        v
                 Text Extraction
                        |
                        v
                Text Normalization
                        |
                        v
              Sentence Segmentation
                        |
                        v
                Document Analysis
                        |
              +---------+---------+
              |                   |
              v                   v
       Document Type          Statistics
         Detection
              |
              v
       Adaptive Chunking
              |
              v
      Sentence Representation
              |
              v
        Hybrid Ranking
              |
        +-----+-----+------+
        |           |      |
        v           v      v
     Semantic    Position  Keywords
        |           |      |
        +-----+-----+------+
              |
              v
       Redundancy Filter
              |
              v
        Final Summary
              |
              v
        Quality Checks
              |
              v
            Result

Future Extensions

Once the NLP core is stronger, the platform can be extended with:

Document classification
Information extraction
Keyword/entity extraction
Document embeddings
Semantic search
Question answering
RAG integration
Batch document processing
NLP quality monitoring

These are future extensions and are not claimed as completed functionality.

Why This Project?

The project is designed to demonstrate more than an NLP model.

It combines:

API engineering
+
asynchronous systems
+
message queues
+
background workers
+
database persistence
+
fault tolerance
+
NLP
+
containerization

The key engineering challenge is coordinating a long-running NLP workload while keeping task state, failures, retries, and results consistent.

Project Positioning

Async NLP Document Processing Platform is a backend / ML-engineering project demonstrating a production-style architecture for asynchronous document processing.

The core technologies and concepts are:

FastAPI
Celery
Redis
PostgreSQL
Docker
Alembic
Async processing
Fault tolerance
Retry strategy
Idempotency
NLP processing

The current implementation establishes the processing infrastructure first. The next major milestone is upgrading the NLP engine and benchmarking the improved pipeline against the current LexRank baseline.
