# CloudRec Backend

Python FastAPI backend featuring hybrid recommendation algorithms, PostgreSQL database models, JWT authentication, and Redis caching.

## Quick Start
```bash
pip install -r requirements.txt
python -m seed
uvicorn app.main:app --reload --port 8000
```

## Running Tests
```bash
python -m pytest tests
```

## API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
