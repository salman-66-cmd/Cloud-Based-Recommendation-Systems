# Cloud-Based Recommendation Systems

A production-style, fully functional full-stack web platform demonstrating how **Cloud Computing** and **Artificial Intelligence** power personalized recommendations at scale.

Built with **FastAPI**, **React 19**, **Tailwind CSS v4**, **PostgreSQL**, **Redis**, and **Scikit-Learn**.

---

## Key System Highlights

- **Real Working Recommendation Engine**:
  - **Content-Based Filtering**: TF-IDF vectorization and cosine similarity on cloud service specifications, categories, and tags.
  - **Collaborative Filtering**: User-Item interaction matrix factorization using $K$-nearest neighbor cosine similarity.
  - **Hybrid Engine**: Dynamic weighted combination: $\text{Score} = 0.6 \cdot \text{Content} + 0.4 \cdot \text{Collaborative}$.
  - **Cold-Start Protocol**: Interactive onboarding preference selection + real-time interaction velocity tracking.
  - **Dynamic Explainability**: Every recommendation includes an algorithmic reason (e.g., *"Matches your preferred domain 'AI & Machine Learning'"*, *"Trending in Cloud Infrastructure"*).
- **Production Full-Stack Architecture**:
  - **Frontend**: React 19, Vite, Tailwind CSS v4, React Router, Recharts, Lucide React icons, and Context API.
  - **Backend**: Python FastAPI, Pydantic v2, SQLAlchemy ORM, Uvicorn, and JWT Authentication.
  - **Database**: PostgreSQL (with automatic zero-config SQLite fallback for local developer testing).
  - **Caching**: Redis caching tier with automatic graceful degradation to an in-memory TTL cache if Redis is offline.
  - **Containerization**: Complete Docker & Docker Compose setup (`postgres`, `redis`, `backend`, `frontend`).
- **Comprehensive Administration & Analytics**:
  - Live Recharts visualizations for user growth, interaction velocity, rating distributions, and algorithm mix.
  - Full CRUD operations for cloud products and categories.
  - Real-time interaction event logs and recommendation audit trails.
- **Realistic Seed Dataset**:
  - **30 Users** across 6 technical engineering personas.
  - **100 Cloud & AI Products** across 10 distinct architectural categories.
  - **1,300+ Interactions** (views, clicks, likes, add-to-cart).
  - **300+ Ratings & Reviews** (1–5 stars).

---

## Default Test Credentials

| Role | Email | Password | Persona Profile |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@cloudrec.io` | `Admin@123` | Full access to Admin Dashboard, Analytics & Catalog CRUD |
| **AI Architect** | `elena.ai@cloudrec.io` | `Password@123` | Heavy interest in LLMs, Vector DBs & MLOps |
| **DevOps Lead** | `marcus.k8s@cloudrec.io` | `Password@123` | Focus on Kubernetes, CI/CD Pipelines & Microservices |

*Note: Quick 1-click login buttons for these accounts are provided directly on the Sign-In page.*

---

## Quick Start (Local Development)

### 1. Prerequisites
- **Python 3.10+**
- **Node.js 18+** & **npm**

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# (Optional) Create virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Seed the database with 100 products, 30 users, and 1,300+ interactions
python -m seed

# Start the FastAPI server
uvicorn app.main:app --reload --port 8000
```
Backend will be live at:
- **API Server**: `http://localhost:8000`
- **Swagger OpenAPI Docs**: `http://localhost:8000/docs`
- **ReDoc Docs**: `http://localhost:8000/redoc`
- **Health Check Probe**: `http://localhost:8000/health`

### 3. Frontend Setup
```bash
# In a new terminal window, navigate to frontend
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```
Open your browser at `http://localhost:5173`.

---

## Running with Docker Compose

To launch all four microservices (**PostgreSQL**, **Redis**, **FastAPI Backend**, and **React Nginx Frontend**) simultaneously:

```bash
# Start all containers in the background
docker-compose up --build -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

Access points:
- **Web Application**: `http://localhost:3000`
- **FastAPI API & Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

---

## Running Automated Tests

A comprehensive `pytest` test suite validates authentication, items CRUD, interactions, ratings, recommendations, and admin authorization:

```bash
cd backend
python -m pytest tests
```

---

## Recommendation Algorithm Details

### 1. Content-Based Model
- Constructs an item feature vector $\mathbf{v}_i$ by compiling title, category, tags, description, provider, and features.
- Vectorized into a high-dimensional feature space using Scikit-Learn's `TfidfVectorizer`.
- Aggregates user profile vector $\mathbf{u}$ using weighted interactions:
  - View ($1.0$), Click ($1.5$), Like ($3.0$), Rating ($r / 5 \times 4.0$), Add to Cart ($4.0$), Purchase ($5.0$), Onboarding Preferences ($3.0$).
- Scores items via Cosine Similarity: $\cos(\mathbf{u}, \mathbf{v}_i)$.

### 2. Collaborative Filtering Model
- Constructs an explicit User-Item interaction and rating matrix $R \in \mathbb{R}^{U \times I}$.
- Calculates User-User Cosine Similarity across all active architects.
- Identifies Top-$K$ ($K=7$) nearest architectural neighbors and computes normalized predicted scores for unobserved items:
  $$\hat{R}_{u, j} = \frac{\sum_{v \in N_k(u)} \text{sim}(u, v) \cdot R_{v, j}}{\sum_{v \in N_k(u)} |\text{sim}(u, v)|}$$

### 3. Hybrid Model
$$\text{Score}_{\text{hybrid}} = \alpha \cdot \text{Score}_{\text{content}} + (1 - \alpha) \cdot \text{Score}_{\text{collab}}$$
- Defaults to $\alpha = 0.60, (1 - \alpha) = 0.40$.
- Can be tuned interactively in the **Recommendation Lab** slider UI.

### 4. Cold-Start Protocol
- When a user has minimal historical interactions, the engine falls back to their onboarding interest selections (`UserPreference`) blended with real-time interaction velocity metrics.

---

## Cloud Deployment Guide

### Deploying the Frontend (Vercel / Netlify)
1. Push the code to GitHub.
2. In Vercel or Netlify, select the `frontend` subdirectory as the root directory.
3. Build Command: `npm run build`
4. Output Directory: `dist`
5. Configure environment variable: `VITE_API_BASE_URL=https://your-backend-api.onrender.com`

### Deploying the Backend (Render / Railway / AWS ECS)
1. In Render or Railway, create a new Web Service pointing to `backend/Dockerfile` or standard Python environment.
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `sh -c "python -m seed && uvicorn app.main:app --host 0.0.0.0 --port $PORT"`
4. Configure environment variables:
   - `DATABASE_URL`: Your managed PostgreSQL connection URI (e.g., from Neon, Supabase, or AWS RDS).
   - `REDIS_URL`: Your Redis cloud URI (e.g., from Upstash or Redis Cloud).
   - `JWT_SECRET`: Random 256-bit secret key.
   - `CORS_ORIGINS`: `["https://your-frontend.vercel.app"]`

---

## Project Structure

```
cloud-recommendation-system/
├── backend/
│   ├── app/
│   │   ├── auth/              # JWT token generation, bcrypt hashing, dependencies
│   │   ├── models/            # SQLAlchemy ORM database models
│   │   ├── recommendation/    # Recommendation engine (TF-IDF, CF, Hybrid)
│   │   ├── routers/           # FastAPI REST API endpoints
│   │   ├── schemas/           # Pydantic v2 validation models
│   │   ├── utils/             # Redis cache manager & resilient in-memory fallback
│   │   ├── config.py          # Settings and environment variables
│   │   ├── database.py        # SQLAlchemy engine and session dependency
│   │   └── main.py            # FastAPI application entrypoint
│   ├── tests/                 # Automated pytest test suite
│   ├── seed.py                # Database population script (100 items, 30 users)
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile             # Backend container configuration
├── frontend/
│   ├── src/
│   │   ├── components/        # Reusable UI components (Navbar, ItemCard, etc.)
│   │   ├── context/           # Auth and Toast context providers
│   │   ├── layouts/           # RootLayout with sidebar and diagnostics
│   │   ├── pages/             # 15 React application views
│   │   ├── services/          # Axios API client with JWT interceptor
│   │   ├── App.jsx            # React Router routing configuration
│   │   ├── index.css          # Tailwind CSS v4 styling
│   │   └── main.jsx           # Vite application entrypoint
│   ├── nginx.conf             # Production Nginx reverse proxy configuration
│   ├── package.json           # Frontend dependencies
│   ├── vite.config.js         # Vite configuration with Tailwind CSS plugin
│   └── Dockerfile             # Multi-stage production container build
├── docs/
│   └── architecture.md        # Technical architecture & mathematical specifications
├── docker-compose.yml         # Full multi-container composition
├── .env.example               # Environment variable templates
└── README.md                  # Complete system documentation
```
