# Asynchronous NLP Document Processing Pipeline

An asynchronous document processing API built with FastAPI, PostgreSQL, Redis, and Celery.

The system is designed to accept documents through a REST API, create asynchronous processing tasks, process documents in background workers, and return NLP-generated summaries.

> **Current Status:** Phase 1 — Project Foundation Complete

---

## Project Overview

The goal of this project is to build a production-oriented asynchronous NLP document processing pipeline.

Instead of performing expensive document processing directly inside an API request, the system will use a background task queue:

```text
Client
   │
   ▼
FastAPI
   │
   ▼
Create Task
   │
   ▼
Redis
   │
   ▼
Celery Worker
   │
   ▼
Document Processing
   │
   ▼
NLP Summarization
   │
   ▼
PostgreSQL
   │
   ▼
Task Result