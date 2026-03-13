FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml .
# Install only dependencies (no editable install needed in container)
RUN uv pip install --system fastapi uvicorn[standard] pydantic pydantic-settings httpx redis celery sqlalchemy asyncpg alembic psycopg2-binary python-dotenv

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
