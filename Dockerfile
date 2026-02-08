FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./

RUN uv sync

COPY src ./src
COPY static ./static

EXPOSE 5001

CMD ["uv", "run", "--no-sync", "python", "-m", "uvicorn", "main:app", "--app-dir", "/app/src", "--host", "0.0.0.0", "--port", "5001"]
