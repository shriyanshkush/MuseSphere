# 🎟️ MuseSphere – Intelligent Museum Ticketing & Visitor Assistant

MuseSphere is a full-stack AI-powered museum management platform that transforms traditional ticket booking into a seamless conversational experience. The system combines Generative AI, Retrieval-Augmented Generation (RAG), Machine Learning, QR-based ticketing, analytics, and multilingual support to enhance visitor engagement while streamlining museum operations.

---

## 🚀 Features

### 🤖 AI Museum Assistant

* Conversational ticket booking
* Exhibition and event recommendations
* Museum FAQs and visitor support
* Context-aware multi-turn conversations
* Multilingual interactions

### 🎫 Smart Ticketing System

* Exhibition ticket booking
* Event and show reservations
* Dynamic slot management
* QR-based digital tickets
* Booking history management

### 💳 Secure Payments

* Razorpay payment integration
* UPI, Credit Card, Debit Card, Net Banking
* Payment verification and tracking
* Automated ticket generation after successful payment

### 📚 RAG-Powered Knowledge Base

* Upload museum documents (PDF, DOCX, TXT)
* Semantic search using vector embeddings
* Context-aware AI responses
* Museum guides and exhibition information retrieval

### 🧠 Machine Learning Features

* Personalized exhibit recommendations
* Visitor preference analysis
* Sentiment analysis on feedback
* Visitor behavior insights

### 📊 Analytics Dashboard

* Visitor statistics
* Revenue analytics
* Popular exhibits
* Booking trends
* Language distribution
* AI usage metrics

### 🌍 Multilingual Support

* English
* Hindi
* Spanish
* French
* German

### 🔐 Security

* JWT Authentication
* Role-Based Access Control
* Password hashing
* Secure API endpoints
* Rate limiting and validation

---

## 🏗️ System Architecture

```text
                Android App
                     │
                     │
              FastAPI Backend
                     │
 ┌─────────────┬──────────────┬─────────────┐
 │             │              │             │
PostgreSQL    Redis       ChromaDB      Gemini AI
 │             │              │             │
 └─────────────┴──────────────┴─────────────┘
                     │
              LangGraph Agents
                     │
       ┌─────────────┼─────────────┐
       │             │             │
 Booking Agent   RAG Agent   Recommendation ML
       │
 Razorpay Payment Gateway
       │
 QR Ticket Generator
```

---

## 🛠 Tech Stack

### Frontend (Android)

* Kotlin
* Jetpack Compose
* Material 3
* MVVM Architecture
* Hilt Dependency Injection
* Retrofit
* Room Database
* Coroutines & Flow

### Backend

* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* Redis
* Celery

### AI & GenAI

* Gemini AI
* LangChain
* LangGraph
* ChromaDB
* Sentence Transformers

### Machine Learning

* Scikit-Learn
* Pandas
* NumPy
* Recommendation Systems
* Sentiment Analysis

### DevOps

* Docker
* Docker Compose
* Nginx
* GitHub Actions

---

## 📂 Project Structure

```text
MuseSphere/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── ai/
│   │   ├── ml/
│   │   ├── database/
│   │   ├── core/
│   │   └── utils/
│   │
│   ├── requirements.txt
│   └── Dockerfile
│
├── android/
│   ├── presentation/
│   ├── domain/
│   ├── data/
│   └── app/
│
├── docker-compose.yml
└── README.md
```

---

## 📱 Android Application Features

### Authentication

* Login
* Signup
* Google Sign-In
* Forgot Password

### Visitor Features

* Browse Exhibitions
* Search Events
* Book Tickets
* Digital QR Tickets
* AI Chat Assistant
* Booking History
* Museum Navigation
* Profile Management

### Admin Features

* Manage Exhibitions
* Manage Events
* Upload Knowledge Documents
* View Analytics Dashboard
* Monitor Bookings

---

## 🤖 AI Workflow

```text
User Query
      │
      ▼
Intent Detection
      │
      ▼
LangGraph Agent Router
      │
 ┌────┼────┬────-------┬────----------┐
 │    │    │           │              │
Booking  Knowledge  Recommendation  Payment
Agent    Agent      Agent           Agent
      │
      ▼
Response Generator
      │
      ▼
User Response
```

**Example:**

```text
User:
Book 2 tickets for tomorrow.

AI:
Available slots:
10:00 AM
12:00 PM
2:00 PM

Which slot would you like?
```

---

## 📚 RAG Pipeline

```text
Document Upload
       │
       ▼
Text Extraction
       │
       ▼
Chunking
       │
       ▼
Embeddings
       │
       ▼
ChromaDB
       │
       ▼
Retriever
       │
       ▼
Gemini AI
       │
       ▼
Context-Aware Answer
```

**Supported Documents:**

* PDF
* DOCX
* TXT

---

## 🧠 ML Modules

### Recommendation Engine

Provides personalized exhibit suggestions using:

* Visitor history
* Preferences
* Popular exhibits
* Booking behavior

### Sentiment Analysis

Classifies feedback as:

* Positive
* Neutral
* Negative

Used for:

* Visitor satisfaction monitoring
* Service improvement
* Analytics generation

---

## 🔗 API Modules

### Authentication

```http
POST /auth/register
POST /auth/login
POST /auth/refresh
GET  /auth/profile
```

### Exhibitions

```http
GET    /exhibitions
POST   /exhibitions
PUT    /exhibitions/{id}
DELETE /exhibitions/{id}
```

### Events

```http
GET    /events
POST   /events
PUT    /events/{id}
DELETE /events/{id}
```

### Bookings

```http
POST /bookings
GET  /bookings
GET  /bookings/{id}
```

### AI Assistant

```http
POST /chat/message
GET  /chat/history
```

### Knowledge Base

```http
POST /knowledge/upload
POST /knowledge/query
```

### Recommendations

```http
GET /recommendations
```

---

## 🚀 Local Setup

### Backend

```bash
cd backend

python -m venv .venv

source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

API Documentation available at:

```text
http://localhost:8000/docs
```

---

### Docker Setup

```bash
docker compose up --build
```

Services started:

* FastAPI
* PostgreSQL
* Redis
* ChromaDB

---

## 📊 Future Enhancements

* Voice-to-Voice AI Assistant
* Indoor Museum Navigation
* Facial Recognition Entry
* AR-Powered Exhibit Exploration
* Smart Crowd Prediction
* AI Tour Guide
* Real-Time Event Notifications
* Multi-Museum SaaS Platform

---

## 🎯 Key Highlights

✅ Full-Stack Development

✅ FastAPI Backend

✅ Kotlin Android Application

✅ Generative AI Integration

✅ Retrieval-Augmented Generation (RAG)

✅ LangGraph Agent Workflows

✅ Machine Learning Recommendations

✅ Sentiment Analysis

✅ QR Ticketing System

✅ Payment Gateway Integration

✅ Docker Deployment

✅ Analytics Dashboard

---

## 👨‍💻 Author

**Shriyansh Kushwaha**

Passionate about Backend Engineering, Artificial Intelligence, Machine Learning, and Mobile Application Development.

GitHub: https://github.com/shriyanshkush
