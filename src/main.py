"""myapp: a minimal web API used to demonstrate a Kubernetes CI/CD pipeline."""
import os

from fastapi import FastAPI
from prometheus_client import Counter, make_asgi_app

app = FastAPI(title="myapp")
REQUESTS = Counter("myapp_requests_total", "Requests served by the root endpoint")

# Prometheus scrape endpoint
app.mount("/metrics", make_asgi_app())


@app.get("/")
def hello():
    REQUESTS.inc()
    return {
        "message": os.getenv("GREETING", "hello"),
        "version": os.getenv("APP_VERSION", "dev"),
    }


@app.get("/healthz")
def healthz():
    """Liveness: the process is up."""
    return {"status": "alive"}


@app.get("/readyz")
def readyz():
    """Readiness: dependencies are reachable. Add DB checks here in a real app."""
    return {"status": "ready"}
