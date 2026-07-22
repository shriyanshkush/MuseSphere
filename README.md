# 🎟️ MuseSphere – Intelligent Museum Ticketing, RAG Assistant & Full-Stack Platform

<p align="center">
  <img src="https://img.shields.io/badge/Kotlin-Jetpack%20Compose-7F52FF.svg?style=for-the-badge&logo=kotlin&logoColor=white" alt="Kotlin Jetpack Compose" />
  <img src="https://img.shields.io/badge/Material%203-Android%20MVVM-3DDC84.svg?style=for-the-badge&logo=android&logoColor=white" alt="Android MVVM" />
  <img src="https://img.shields.io/badge/FastAPI-0.115.6-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0%20Async-red.svg?style=for-the-badge&logo=python&logoColor=white" alt="SQLAlchemy Async" />
  <img src="https://img.shields.io/badge/PostgreSQL-16-316192.svg?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Redis-7.0-DC382D.svg?style=for-the-badge&logo=redis&logoColor=white" alt="Redis" />
  <img src="https://img.shields.io/badge/LangGraph-Agentic%20AI-blueviolet.svg?style=for-the-badge" alt="LangGraph" />
  <img src="https://img.shields.io/badge/ChromaDB-Vector%20Store-FF6F00.svg?style=for-the-badge" alt="ChromaDB" />
  <img src="https://img.shields.io/badge/Docker-Multi--Stage-2496ED.svg?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
</p>

**MuseSphere** is a next-generation, full-stack AI-powered museum management and visitor engagement ecosystem. It combines a state-of-the-art **Android Application (Kotlin / Jetpack Compose MVVM)** with an enterprise **FastAPI Backend engineered with Clean Architecture**. The platform transforms traditional museum ticketing into a dynamic conversational experience using **Generative AI (Google Gemini)**, **Stateful LangGraph Agent Routing**, **Retrieval-Augmented Generation (RAG)** over **ChromaDB vector embeddings**, **Machine Learning recommendation engines**, **cryptographic QR digital ticketing**, and **enterprise rate limiting / token blacklisting**.

---

## 🚀 Key Features

### 🤖 AI Museum Assistant (`LangGraph` + `Gemini AI`)
* Conversational ticket booking with automated time slot and pricing recommendations.
* Exhibition and event discovery with real-time capacity checking.
* Museum FAQs, operational hours, and context-aware multi-turn visitor support.
* Seamless multilingual interactions (`English`, `Hindi`, `Spanish`, `French`, `German`).

### 🎫 Smart Ticketing & Dynamic Slot Management
* Digital reservation system across categories (`adult`, `child`, `student`, `senior`).
* Dynamic slot capacity control (`maximum 100 visitors per window`) to prevent overcrowding.
* Cryptographically secure, base64-encoded PNG **QR-based digital entry passes**.
* Real-time booking history tracking and cancellation workflows.

### 💳 Secure Payments Gateway (`Razorpay Mock Integration`)
* Checkout initiation with automated order creation and tracking.
* Payment signature verification and instant order status settlement (`pending_payment` → `paid`).
* Automated digital QR ticket pass generation upon transaction confirmation.

### 📚 RAG-Powered Knowledge Base (`ChromaDB`)
* Semantic vector indexing across uploaded museum documents (`PDF`, `DOCX`, `TXT`).
* Overlapping text chunking (`size=800`, `overlap=100`) preserving contextual continuity.
* High-precision cosine similarity retrieval ensuring fact-based, grounded AI responses.

### 🧠 Machine Learning & Visitor Analytics
* Personalized exhibit recommendations derived from visitor category preferences and historical popularity.
* Natural language **Sentiment Analysis** (`Positive`, `Neutral`, `Negative`) classifying visitor reviews.
* Real-time telemetric dashboard tracking daily footfall, revenue, popular exhibits, and peak booking windows.

### 🔐 Enterprise Security & Rate Limiting (`SlowAPI`)
* Role-Based Access Control (`UserRole.visitor` vs `UserRole.admin`) locking administrative catalogs and RAG uploads.
* JWT Access & Refresh token rotation with unique `JTI` (JSON Token Identifier) tracking.
* Instant token revocation via asynchronous **Redis blacklisting** upon user logout.
* Resource rate limiting (`@limiter.limit("20/minute")`) protecting conversational AI endpoints against DDoS attacks.

---

## 🏗️ End-to-End System Architecture

MuseSphere decouples presentation across native mobile clients (`Android`) and web portals from the backend services, using structured REST/JSON communication over asynchronous connection pools:

```text
       ┌─────────────────────────────────────────────────────────┐
       │     Android Mobile Application (Kotlin / MVVM / Hilt)   │
       │     • Jetpack Compose UI • Retrofit REST • Room Cache   │
       └────────────────────────────┬────────────────────────────┘
                                    │ HTTP / REST / JSON
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │     API & Presentation Layer (app/api/routes/)          │
       │  • Route Handlers, Dependency Injection, SlowAPI Limits │
       │  • OpenAPI / Swagger Documentation & Status Code Rules  │
       └────────────────────────────┬────────────────────────────┘
                                    │ Validated Pydantic v2 DTOs (app/schemas/dtos.py)
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │        Business Service Layer (app/services/)           │
       │  • AuthService (JWT issuance, refresh rotation, logout) │
       │  • BookingService (Slot capacity check, QR generation)  │
       │  • ChatService (LangGraph orchestration, chat history)  │
       └────────────────────────────┬────────────────────────────┘
                                    │ Domain Calls
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │      Async Repository Layer (app/repositories/)         │
       │  • Generic & Specialized CRUD over AsyncSession         │
       │  • Decouples SQL queries from business logic            │
       └────────────────────────────┬────────────────────────────┘
                                    │ SQLAlchemy 2.0 Async ORM Models (app/models/entities.py)
                                    ▼
┌───────────────────────────────────┼──────────────────────────────────┐
│                                   │                                  │
▼                                   ▼                                  ▼
┌──────────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐
│  PostgreSQL / SQLite │  │  Redis Caching   │  │ ChromaDB + Google Gemini │
│  (Alembic Migrated)  │  │ (Token Blacklist)│  │ (Vector RAG + LangGraph) │
└──────────────────────┘  └──────────────────┘  └──────────────────────────┘
```

---

## 🛠 Tech Stack

### Frontend (Android Application)
* **Kotlin**: Modern, type-safe programming language.
* **Jetpack Compose**: Declarative UI toolkit featuring dynamic Material Design 3 components.
* **MVVM Architecture**: Strict Separation of Presentation (`UI`), Domain (`Use Cases`), and Data (`Repositories`) layers.
* **Hilt Dependency Injection**: Compile-time dependency injection across ViewModels and Repositories.
* **Retrofit & OkHttp**: Type-safe HTTP client with JSON serialization and authentication headers.
* **Room Database & Coroutines/Flow**: Asynchronous local data caching and reactive state streams.

### Backend & Database Layer
* **FastAPI**: High-performance asynchronous web framework (`Python 3.12+`).
* **SQLAlchemy 2.0 (`AsyncSession`)**: Asynchronous Object-Relational Mapper with connection pooling.
* **PostgreSQL 16 & SQLite (`aiosqlite`)**: Relational database storage across production and testing environments.
* **Alembic**: Versioned database schema migration engine (`upgrade head`).
* **Redis 7 (`redis.asyncio`)**: High-speed caching and real-time JWT revocation blacklist.

### AI, RAG & Machine Learning
* **Google Gemini (`gemini-1.5-flash`)**: Core generative LLM powering conversational interactions.
* **LangGraph (`StateGraph`)**: Stateful agentic orchestration routing user intents across specialized nodes.
* **ChromaDB (`chromadb-client`)**: High-speed vector embedding database for document knowledge retrieval.
* **Scikit-Learn / NumPy / Pandas**: Statistical calculations for preference matching and sentiment scoring.

### DevOps & Cloud Deployment
* **Docker & Docker Compose**: Multi-stage containerized builds (`builder` + `runtime` with non-root `appuser`).
* **AWS Free Tier Ready**: Optimized memory footprint (`1 workers/2 workers`) supporting `EC2 t2.micro` and `RDS db.t3.micro`.

---

## 📱 Android Application (`android/`)

The Android client (`android/app/src/main/java/com/museai`) implements strict **Clean MVVM Architecture**:

```text
android/app/src/main/java/com/museai/
├── presentation/   # Jetpack Compose UI Screens, ViewModels, and ScreenCatalog
├── domain/         # Domain use cases and business validation
└── data/           # MuseAiRepository, Retrofit API client, and local Room cache
```

### Authentication & User Flows
* **Login & Registration**: Secure authentication storing JWT access and refresh tokens locally.
* **Profile Management**: Displays visitor details and language preferences.

### Visitor Experience
* **Exhibitions Catalog**: Browse active museum galleries, check locations, and review popularity indices.
* **Events Explorer**: Discover scheduled workshops, lectures, and guided museum tours.
* **Ticket Booking & Digital Pass**: Reserve entry tickets, select time slots, view dynamic pricing, and render **digital QR code entry passes** (`base64 PNG`) directly inside the app.
* **AI Chat Assistant**: Interactive multi-turn chat interface communicating with the backend's LangGraph agent for instant guidance and ticket booking assistance.

### Admin Experience
* **Catalog Administration**: Create, update, and delete exhibitions and events directly from the mobile interface (`require_admin`).
* **Analytics Monitoring**: View real-time visitor footfall, revenue metrics, and booking capacity trends.

---

## 🏛️ Backend Clean Architecture & Engineering (`backend/`)

The backend (`backend/app`) enforces rigorous separation across layered abstractions:

1. **Presentation Layer (`app/api/routes/`)**: Handlers for `/auth`, `/bookings`, `/exhibitions`, `/events`, `/payments`, and `/misc`. Enforces Pydantic v2 validation and injects authentication/database dependencies.
2. **Data Transfer Objects (`app/schemas/dtos.py`)**: Pydantic v2 schemas utilizing `Field(...)` validation constraints, date formats, bounds checking, and rich OpenAPI examples.
3. **Business Service Layer (`app/services/`)**:
   * **`AuthService`**: Hashing (`bcrypt==4.0.1`), token generation, rotation, and Redis logout blacklisting.
   * **`BookingService`**: Slot checking, pricing calculation (`adult $15`, `child $8`, `student $10`, `senior $12`), Razorpay checkout, and QR pass generation.
   * **`ChatService`**: Orchestrates LangGraph state transitions and stores historical chat messages.
4. **Repository Layer (`app/repositories/domain.py`)**: Generic & specialized asynchronous CRUD methods (`await db.execute`, `await db.get`) decoupling business logic from ORM queries.
5. **Database Layer (`app/database/session.py` & `alembic/`)**:
   * **Asynchronous Engine & Pooling**: Configured with `pool_size=5`, `max_overflow=10`, `pool_recycle=1800` ensuring zero connection leaks under high traffic.
   * **Alembic Schema Migrations**: All table modifications (`users`, `exhibitions`, `events`, `bookings`, `payments`, `tickets`, `chat_history`, `knowledge_documents`, `feedback`, `recommendations`, `analytics`) are version-controlled (`alembic upgrade head`).

---

## 🤖 AI Workflow: LangGraph + Gemini AI + ChromaDB RAG

The AI engine (`app/ai/workflow.py` and `app/ai/rag.py`) operates as a stateful, multi-turn LangGraph pipeline:

```text
Visitor Query ("Book 2 adult tickets for tomorrow at 10 AM")
   │
   ▼
┌───────────────────────────────────────────────────────────────┐
│               Node 1: Intent Detection (LangGraph)            │
│  Classifies query into exact category using Gemini 1.5 Flash: │
│  [booking | recommendation | payment | knowledge | support]   │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│          Node 2: Semantic Vector Search (ChromaDB RAG)        │
│  Computes cosine similarity across overlapping text chunks    │
│  retrieved from uploaded museum guides & brochures            │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│         Node 3: Context-Aware Response Generation             │
│  Synthesizes visitor prompt, classified intent, vector RAG    │
│  context, and target language code into an accurate reply     │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
           Structured Response returned to Visitor & Saved in DB
```

### RAG Vector Pipeline (`KnowledgeBase`)
* **Document Processing (`/knowledge/upload`)**: Uploads text guides/brochures, chunking them into `size=800` segments with `overlap=100`.
* **ChromaDB Indexing (`chromadb-client`)**: Indexes vector embeddings (`doc_{id}_chunk_{i}`). Uses `chromadb-client` to ensure zero compilation headaches across local machines and cloud containers.
* **Deterministic Offline Fallback**: If the `GEMINI_API_KEY` is omitted or vector storage is offline during local testing, the workflow automatically transitions to a rule-based intent classifier and keyword retrieval engine so demonstrations always run smoothly.

---

## 🧠 Machine Learning & Telemetric Analytics (`app/ml/`)

### 1. Recommendation Engine (`recommendation.py`)
Calculates personalized exhibit scores based on visitor preferences and historical popularity indices:
$$\text{Score} = (\text{Category Match Bonus} \times 10.0) + \text{Popularity Score}$$

### 2. Sentiment Classification (`sentiment.py`)
Analyzes visitor feedback submissions (`/feedback/analyze`), classifying text sentiment into **Positive**, **Neutral**, or **Negative** with normalized confidence scores (`0.0 to 1.0`).

### 3. Telemetric Dashboard (`/analytics/dashboard`)
Provides administrators with real-time operational metrics across daily/monthly visitor footfall, verified Razorpay revenue, most popular exhibits, and peak booking slots.

---

## 🔗 Complete API Endpoints Catalog (`/docs`)

Full interactive Swagger/OpenAPI documentation with request schemas and response examples is available at **`http://localhost:8000/docs`**.

### 🔐 Authentication & Profile (`/auth`)
| Method | Endpoint | Description | Status | Responses |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/auth/register` | Register new visitor/admin account with bcrypt hashing | `201 Created` | `409` Email registered, `422` Validation |
| `POST` | `/auth/login` | Authenticate credentials and issue JWT access/refresh pair | `200 OK` | `401` Invalid credentials, `403` Inactive |
| `POST` | `/auth/refresh` | Rotate access token using valid refresh JWT | `200 OK` | `401` Expired or revoked refresh token |
| `POST` | `/auth/logout` | Revoke active access token via Redis/in-memory blacklist | `200 OK` | `401` Unauthorized |
| `GET` | `/auth/profile` | Retrieve authenticated profile and language settings | `200 OK` | `401` Unauthorized |

### 🎫 Bookings & QR Tickets (`/bookings`, `/tickets`)
| Method | Endpoint | Description | Status | Responses |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/bookings` | Reserve time slot tickets with capacity verification | `201 Created` | `409` Slot full, `422` Invalid parameters |
| `GET` | `/bookings` | List all ticket reservations belonging to active user | `200 OK` | `401` Unauthorized |
| `GET` | `/bookings/{id}` | Retrieve pricing and details for specific reservation | `200 OK` | `404` Booking not found |
| `DELETE` | `/bookings/{id}` | Cancel reservation and release slot capacity | `204 No Content` | `404` Booking not found |
| `GET` | `/tickets/{booking_id}` | Fetch digital pass with base64 PNG QR code image | `200 OK` | `404` Unpaid or missing ticket |

### 💳 Payments Gateway (`/payments`)
| Method | Endpoint | Description | Status | Responses |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/payments/create-order` | Initiate Razorpay checkout order for pending booking | `200 OK` | `404` Booking not found |
| `POST` | `/payments/verify` | Verify transaction signature and generate QR pass | `200 OK` | `404` Payment record not found |

### 🏛️ Exhibitions & Events (`/exhibitions`, `/events`)
| Method | Endpoint | Description | Status | Access Level |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/exhibitions` | Get paginated catalog of active museum exhibitions | `200 OK` | Public / Visitor |
| `POST` | `/exhibitions` | Add new exhibition entry to museum catalog | `201 Created` | **Admin Only (`require_admin`)** |
| `PUT` | `/exhibitions/{id}` | Update exhibition timings, location, or popularity | `200 OK` | **Admin Only (`require_admin`)** |
| `DELETE` | `/exhibitions/{id}` | Permanently delete exhibition from catalog | `204 No Content` | **Admin Only (`require_admin`)** |
| `GET` | `/events` | List upcoming live workshops, lectures, and tours | `200 OK` | Public / Visitor |
| `POST` | `/events` | Schedule a new live event or guided tour | `201 Created` | **Admin Only (`require_admin`)** |

### 🤖 AI Chatbot, RAG & Analytics (`/chat`, `/knowledge`, `/recommendations`, `/analytics`)
| Method | Endpoint | Description | Status | Access Level |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/chat/message` | Send multilingual prompt to LangGraph/Gemini AI | `200 OK` | Authenticated (Rate limit: `20/min`) |
| `GET` | `/chat/history` | Retrieve chronological multi-turn dialogue logs | `200 OK` | Authenticated Visitor |
| `POST` | `/knowledge/upload` | Upload and chunk text document for vector indexing | `201 Created` | **Admin Only (`require_admin`)** |
| `POST` | `/knowledge/query` | Test semantic vector retrieval over ChromaDB | `200 OK` | Authenticated Visitor |
| `GET` | `/recommendations` | Get ML personalized exhibit suggestions | `200 OK` | Authenticated Visitor |
| `POST` | `/feedback/analyze` | Submit review and compute sentiment classification | `200 OK` | Authenticated Visitor |
| `GET` | `/analytics/dashboard` | Get telemetric KPI metrics (visitors, revenue, peaks) | `200 OK` | **Admin Only (`require_admin`)** |

---

## 💻 Local Development Setup

### 1. Prerequisites
* Python 3.12+
* Android Studio (for running the Android application)
* Docker & Docker Compose (Optional for full containerized run)

### 2. Full Stack Orchestration (Docker Compose)
Launch all required backend services (`FastAPI`, `PostgreSQL 16`, `Redis 7`, `ChromaDB`) with a single command from the root directory:
```bash
docker compose up --build
```
* **FastAPI Backend**: `http://localhost:8000`
* **Swagger Documentation**: `http://localhost:8000/docs`
* **PostgreSQL Database**: `localhost:5432`
* **Redis Caching**: `localhost:6379`
* **ChromaDB Server**: `http://localhost:8001`

### 3. Standalone Backend Setup (`Local Virtual Environment`)
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .\.venv\Scripts\activate

# Install required dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Execute versioned schema migrations to build database tables
alembic upgrade head

# Launch asynchronous server with auto-reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Running the Automated Test Suite (`pytest`)
The project includes a comprehensive, automated test suite (`pytest tests/ -v`) validating full end-to-end user flows across registration, login, profile verification, ticket bookings, and AI chatbot orchestration:
```bash
cd backend
pytest tests/ -v
```

### 5. Running the Android Application
1. Open Android Studio and select **Open an Existing Project**.
2. Navigate to the `MuseSphere/android` folder.
3. Allow Gradle to sync and download dependencies.
4. In `RetrofitClient.kt` or `app/build.gradle.kts`, configure the base URL to point to your backend server (`http://10.0.2.2:8000/` for Android Emulator or your local IP for physical devices).
5. Click **Run** (`Shift + F10`) to launch the app on an emulator or Android device.

---

## 🐳 Docker & AWS Free Tier Deployment ($0/Month Cost)

The `backend/` directory features a multi-stage `Dockerfile` (`builder` stage + `runtime` stage running as unprivileged `appuser`) and `docker-compose.prod.yml` optimized specifically for **AWS Free Tier (`EC2 t2.micro` / `t3.micro`)** at zero operational cost.

```bash
cd backend

# Build and launch optimized production containers in detached mode
docker compose -f docker-compose.prod.yml up -d --build

# Run Alembic schema migrations inside the running API container
docker compose -f docker-compose.prod.yml exec api alembic upgrade head
```

> [!TIP]
> For complete instructions covering **Option A (`EC2 + Managed RDS PostgreSQL db.t3.micro`)** and **Option B (`All-in-One EC2 with mandatory 2GB Linux Swap Space`)**, reference our deployment guide: [aws_free_tier_deployment_guide.md](file:///C:/Users/shriy/.gemini/antigravity-ide/brain/48200bfb-b90a-43da-b98e-171ce8740d51/aws_free_tier_deployment_guide.md).

---

## 📂 Complete Project Structure

```text
MuseSphere/
│
├── backend/                    # FastAPI Clean Architecture Backend
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/         # Presentation layer: Route handlers & Swagger metadata
│   │   ├── services/           # Business logic layer: Auth, Bookings, Chat, Rate limits
│   │   ├── repositories/       # Data access layer: Async ORM repository patterns
│   │   ├── models/             # Domain ORM entities: Declarative SQLAlchemy AsyncAttrs
│   │   ├── schemas/            # Validation DTOs: Pydantic v2 schemas with examples
│   │   ├── ai/                 # AI & GenAI: LangGraph workflow & ChromaDB RAG engine
│   │   ├── ml/                 # Machine learning: Recommendations & sentiment analysis
│   │   ├── database/           # Database setup: create_async_engine & AsyncSessionLocal
│   │   ├── core/               # Core configuration: Settings, Security, SlowAPI Limiter
│   │   └── main.py             # Application entry point, CORS & exception handlers
│   │
│   ├── alembic/                # Versioned schema migration environment & revisions
│   ├── tests/                  # Automated integration & unit test suites (pytest)
│   ├── requirements.txt        # Production dependencies (pinned & MSVC-optimized)
│   ├── Dockerfile              # Multi-stage container definition for AWS t2.micro
│   └── docker-compose.prod.yml # Production orchestration (API + Postgres + Redis)
│
├── android/                    # Kotlin Jetpack Compose MVVM Android Application
│   ├── app/src/main/java/com/museai/
│   │   ├── presentation/       # Jetpack Compose UI Screens, ViewModels, and Catalog
│   │   ├── domain/             # Domain use cases and business validation rules
│   │   └── data/               # MuseAiRepository, Retrofit API client, and Room cache
│   └── build.gradle.kts        # Android build configuration & Hilt dependencies
│
├── docker-compose.yml          # Root multi-container orchestration (Backend + DBs + AI)
└── README.md                   # Full-Stack ecosystem documentation
```

---

## 📊 Future Enhancements

* Voice-to-Voice AI Assistant with real-time speech synthesis.
* Indoor Museum Navigation using Bluetooth beacons and AR-powered exhibit exploration.
* Facial Recognition fast-track VIP entry at security turnstiles.
* Smart Crowd Prediction and automated dynamic ticket pricing.
* Multi-Museum SaaS tenancy platform managing regional networks.

---

## 👨‍💻 Author

**Shriyansh Kushwaha**
* **Expertise**: Backend Engineering, Artificial Intelligence, Machine Learning, and Mobile Application Development.
* **GitHub**: [https://github.com/shriyanshkush](https://github.com/shriyanshkush)
