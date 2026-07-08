from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging

from . import algorithms
from .schemas import TSPRequest, TSPResponse

logger = logging.getLogger("tsp-api")

# Создаём экземпляр приложения FastAPI
# Это центральный объект, в котором регистрируются все эндпоинты
app = FastAPI(
    title="TSP Visualizer API",
    description="API для визуализации решения задачи коммивояжёра TSP",
    version="1.0.0"
)

# CORS-миддлварь: без неё фронтенд (порт 8080) не сможет вызвать
# бэкенд (порт 8000) — браузер заблокирует запрос как межсайтовый.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    """Проверочная ручка - убедиться, что сервер запущен и отвечает."""
    return {"status": "ok", "message": "Сервер запущен успешно!"}

@app.post("/solve", response_model=TSPResponse)
def solve_tsp(req: TSPRequest):
    """
    Принимает список городов {x, y} и название алгоритма, возвращает найденный маршрут + историю шагов (для истории/ статистики) + длину.

    Поддерживаемые алгоритмы (см. algorithms.py):
  - greedy            — жадный (быстро, приближённо)
  - ant               — муравьиный (эвристика с балансом скорость/качество)
  - bruteforce        — полный перебор (точно, но только до 10 городов)
  - branch_and_bound  — ветви и границы (точно, тоже до 10 городов —
                          его граница отсечения слабая, поэтому лимит
                          такой же, плюс есть аварийный таймер на 5 секунд
                          на случай неудачной раскладки городов)
    """

    # С 2 городами оптимизировать нечего - это просто "туда-обратно"
    if len(req.cities) < 3:
        raise HTTPException(422, "Нужно минимум 3 города")

    if req.algorithm in ("bruteforce", "branch_and_bound") and len(req.cities) > 10:
        raise HTTPException(
            422,
            f"Алгоритм «{req.algorithm}» работает только для ≤10 городов "
            f"(сейчас {len(req.cities)}) — иначе расчёт займёт слишком много времени",
        )

    cities = [(city.x, city.y) for city in req.cities]

    try:
        result = algorithms.solve(req.algorithm, cities)
    except ValueError as e:
        # предсказуемая ошибка (например, неизвестное имя алгоритма) —
        # текст безопасно показать пользователю напрямую
        raise HTTPException(422, str(e))
    except Exception:
        # непредвиденная ошибка — полный traceback в лог сервера,
        # пользователю наружу уходит только безопасный общий текст
        logger.exception("Неожиданная ошибка при решении TSP")
        raise HTTPException(500, "Внутренняя ошибка сервера при расчёте маршрута")

    if result.get("found") is False:
        # например, город больше лимита — это ловится и выше, но алгоритм
        # тоже умеет сам вернуть "error" (двойная защита, ничего страшного)
        raise HTTPException(422, result.get("error", "Не удалось найти маршрут"))

    return TSPResponse(
        order=result["order"],                       #  порядок обхода городов
        total_distance=result["total_distance"],     #  длина маршрута
        history=result.get("history", []),           #  история для анимации
        algorithm=result["algorithm"],               #  какой алгоритм использовался
        time_ms=result.get("time_ms", 0),            #  время выполнения
        found=result.get("found", True),             #  маршрут найден
        checked=result.get("checked"),               #  сколько маршрутов проверено (для статистики)
        truncated=result.get("truncated"),           #  прерван ли поиск по таймеру
        note_global=result.get("note_global"),       #  пояснение (если прерван)
    )