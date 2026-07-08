"""
Модели данных (Pydantic) для запроса и ответа API.

Pydantic проверяет данные до того, как они попадут в algorithms.py.
Если фронтенд пришлёт неверные данные (например, строку вместо числа),
FastAPI сам вернёт ошибку 422, не заходя в логику алгоритмов.
"""

from pydantic import BaseModel
from typing import List, Literal, Optional

# Допустимые названия алгоритмов
Algorithm = Literal["bruteforce", "greedy", "ant", "branch_and_bound"]


class City(BaseModel):
    """Город на карте с координатами x и y."""
    x: float
    y: float


class TSPRequest(BaseModel):
    """Запрос от фронтенда: список городов и название алгоритма."""
    cities: List[City]
    algorithm: Algorithm = "greedy"


class HistoryStep(BaseModel):
    """
    Один шаг истории для анимации на фронтенде.

    - order: маршрут на этом шаге (индексы городов)
    - complete: True = маршрут завершён (замкнутая петля),
                False = маршрут ещё строится (открытая линия)
    - distance: длина маршрута на этом шаге
    - note: текстовое описание для журнала
    """
    order: List[int]
    complete: bool
    distance: float
    note: str


class TSPResponse(BaseModel):
    """Ответ от бэкенда: маршрут, длина, история и статистика."""
    order: List[int]                 # финальный порядок городов
    total_distance: float            # длина маршрута
    history: List[HistoryStep]       # история для анимации
    algorithm: str                   # название алгоритма
    time_ms: float                   # время выполнения в миллисекундах
    found: bool = True               # маршрут найден

    checked: Optional[int] = None    # сколько маршрутов проверено (для статистики)
    truncated: Optional[bool] = None # True, если поиск прерван по таймеру
    note_global: Optional[str] = None # пояснение (если truncated=True)