# MuseAI – Intelligent Museum Ticketing & Visitor Assistant

MuseAI is a production-oriented full-stack project scaffold with a FastAPI backend, PostgreSQL/Redis/ChromaDB Docker deployment, AI assistant workflow, RAG knowledge endpoints, ML recommendations, sentiment analysis, Razorpay-style payment order flow, and QR ticket generation.

## Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Swagger docs are available at `http://localhost:8000/docs`.

## Docker

```bash
docker compose up --build
```

## Android

The `android/` directory contains a Jetpack Compose clean-architecture skeleton documenting the requested screens, MVVM layers, Retrofit repository abstractions, and navigation destinations.
