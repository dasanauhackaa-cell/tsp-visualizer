from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="TSP Visualizer API",
    description="API для визуализации решения задачи коммивояжёра TSP",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():

    return {"status": "ok", "message": "Сервер запущен успешно!"}