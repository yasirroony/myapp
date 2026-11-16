# ---- Stage 1: install dependencies ----
FROM python:3.12-slim AS build
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Stage 2: small runtime image ----
FROM python:3.12-slim
WORKDIR /app
COPY --from=build /install /usr/local
COPY src/ ./src/

# Run as a non-root user with a numeric UID (required by runAsNonRoot checks)
RUN useradd --uid 10001 --no-create-home appuser
USER 10001

ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION} PYTHONUNBUFFERED=1
EXPOSE 8080
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
