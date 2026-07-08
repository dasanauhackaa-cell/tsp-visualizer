"""
Алгоритмы для задачи коммивояжёра (TSP).

Каждая функция возвращает:
    {
        "order": [0, 3, 1, 2],       # порядок обхода городов
        "total_distance": 41.7,      # длина маршрута
        "history": [                 # история шагов для анимации
            {
                "order": [0, 3],         # маршрут на этом шаге
                "complete": False,       # True = полный маршрут, False = строится
                "distance": 12.4,        # длина на этом шаге
                "note": "Город 3 добавлен, ребро +12.4",
            },
        ],
        "time_ms": 3.2,              # время выполнения
    }
"""

import math
import time
import random
from typing import List, Tuple, Dict
from itertools import permutations

# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
def distance(city1: Tuple[float, float], city2: Tuple[float, float]) -> float:
    """Расстояние между двумя городами по теореме Пифагора."""
    return math.sqrt((city1[0] - city2[0]) ** 2 + (city1[1] - city2[1]) ** 2)


def total_distance(order: List[int], cities: List[Tuple[float, float]]) -> float:
    """Длина замкнутого маршрута (с возвратом в стартовый город)."""
    if len(order) < 2:
        return 0.0
    dist = 0.0
    for i in range(len(order) - 1):
        dist += distance(cities[order[i]], cities[order[i + 1]])
    dist += distance(cities[order[-1]], cities[order[0]])
    return dist


def partial_distance(order: List[int], cities: List[Tuple[float, float]]) -> float:
    """Длина маршрута без замыкания (для незавершённых шагов)."""
    if len(order) < 2:
        return 0.0
    dist = 0.0
    for i in range(len(order) - 1):
        dist += distance(cities[order[i]], cities[order[i + 1]])
    return dist

# 1. ЖАДНЫЙ АЛГОРИТМ
def greedy(cities: List[Tuple[float, float]]) -> Dict:
    """На каждом шаге идёт в ближайший непосещённый город. Быстро, но не оптимально."""
    start_time = time.time()
    n = len(cities)

    if n == 0:
        return {"order": [], "total_distance": 0, "history": [], "time_ms": 0}

    visited = [False] * n
    order = [0]
    visited[0] = True

    history = [
        {
            "order": order.copy(),
            "complete": (n == 1),
            "distance": 0.0,
            "note": "Старт: город 0",
        }
    ]

    for _ in range(n - 1):
        last = order[-1]
        best_idx = -1
        best_dist = float("inf")

        for i in range(n):
            if not visited[i]:
                d = distance(cities[last], cities[i])
                if d < best_dist:
                    best_dist = d
                    best_idx = i

        order.append(best_idx)
        visited[best_idx] = True

        is_complete = len(order) == n
        history.append(
            {
                "order": order.copy(),
                "complete": is_complete,
                "distance": total_distance(order, cities) if is_complete else partial_distance(order, cities),
                "note": f"Город {last} → {best_idx}, ребро +{best_dist:.1f}",
            }
        )

    return {
        "order": order,
        "total_distance": total_distance(order, cities),
        "history": history,
        "time_ms": (time.time() - start_time) * 1000,
    }

# 2. ПОЛНЫЙ ПЕРЕБОР
def bruteforce(cities: List[Tuple[float, float]]) -> Dict:
    """Перебирает все маршруты и выбирает лучший. Точно, но только для ≤10 городов."""
    start_time = time.time()
    n = len(cities)

    if n > 10:
        return {
            "order": list(range(n)),
            "total_distance": total_distance(list(range(n)), cities),
            "history": [],
            "time_ms": (time.time() - start_time) * 1000,
            "error": "Слишком много городов для полного перебора (макс. 10)",
        }

    best_order = None
    best_dist = float("inf")
    history = []
    checked = 0

    for perm in permutations(range(1, n)):
        checked += 1
        order = [0] + list(perm)
        dist = total_distance(order, cities)

        if dist < best_dist:
            best_dist = dist
            best_order = order.copy()
            history.append(
                {
                    "order": order.copy(),
                    "complete": True,
                    "distance": dist,
                    "note": f"Новый лучший маршрут, длина {dist:.1f} (проверено {checked})",
                }
            )

    return {
        "order": best_order,
        "total_distance": best_dist,
        "history": history,
        "time_ms": (time.time() - start_time) * 1000,
        "checked": checked,
    }

# 3. МУРАВЬИНЫЙ АЛГОРИТМ
def ant_colony(
    cities: List[Tuple[float, float]],
    n_ants: int = 20,
    n_iterations: int = 100,
    evaporation: float = 0.5,
    alpha: float = 1.0,
    beta: float = 2.0,
) -> Dict:
    """
    Имитирует муравьёв: они оставляют феромон на коротких путях,
    со временем все муравьи идут по лучшему маршруту.
    """
    start_time = time.time()
    n = len(cities)

    if n < 2:
        return {"order": list(range(n)), "total_distance": 0, "history": [], "time_ms": 0}

    dist_matrix = [[distance(cities[i], cities[j]) for j in range(n)] for i in range(n)]
    pheromone = [[1.0 for _ in range(n)] for _ in range(n)]

    best_order = None
    best_dist = float("inf")
    history = []

    for iteration in range(n_iterations):
        ant_orders = []
        ant_distances = []

        for ant in range(n_ants):
            start_city = random.randint(0, n - 1)
            order = [start_city]
            visited = [False] * n
            visited[start_city] = True

            for _ in range(n - 1):
                current = order[-1]
                probabilities = []
                total_prob = 0.0

                for next_city in range(n):
                    if not visited[next_city]:
                        tau = pheromone[current][next_city] ** alpha
                        eta = (1.0 / dist_matrix[current][next_city]) ** beta
                        prob = tau * eta
                        probabilities.append((next_city, prob))
                        total_prob += prob

                if total_prob == 0:
                    remaining = [i for i in range(n) if not visited[i]]
                    next_city = random.choice(remaining)
                else:
                    r = random.random() * total_prob
                    cum_prob = 0.0
                    next_city = probabilities[-1][0]
                    for city, prob in probabilities:
                        cum_prob += prob
                        if r <= cum_prob:
                            next_city = city
                            break

                order.append(next_city)
                visited[next_city] = True

            ant_orders.append(order)
            ant_distances.append(total_distance(order, cities))

        # Испарение феромона
        for i in range(n):
            for j in range(n):
                pheromone[i][j] *= 1 - evaporation

        # Откладывание феромона
        for order, dist in zip(ant_orders, ant_distances):
            deposit = 1.0 / dist if dist > 0 else 0
            for i in range(len(order) - 1):
                a, b = order[i], order[i + 1]
                pheromone[a][b] += deposit
                pheromone[b][a] += deposit
            a, b = order[-1], order[0]
            pheromone[a][b] += deposit
            pheromone[b][a] += deposit

        best_ant_idx = min(range(len(ant_distances)), key=lambda i: ant_distances[i])
        current_best = ant_orders[best_ant_idx]
        current_dist = ant_distances[best_ant_idx]

        if current_dist < best_dist:
            best_dist = current_dist
            best_order = current_best.copy()

        if iteration % 10 == 0 or iteration == n_iterations - 1:
            history.append(
                {
                    "order": best_order.copy(),
                    "complete": True,
                    "distance": best_dist,
                    "note": f"Итерация {iteration + 1}/{n_iterations}: лучшая длина {best_dist:.1f}",
                }
            )

    return {
        "order": best_order,
        "total_distance": best_dist,
        "history": history,
        "time_ms": (time.time() - start_time) * 1000,
    }

# 4. ВЕТВИ И ГРАНИЦЫ
MAX_BNB_CITIES = 10


def branch_and_bound(cities: List[Tuple[float, float]], time_limit: float = 5.0) -> Dict:
    """
    Умный перебор: отсекает ветки, которые заведомо хуже найденного решения.
    Точно, но только для ≤10 городов. При превышении таймера (5с) возвращает
    лучшее найденное решение (не гарантирует оптимальность).
    """
    start_time = time.time()
    n = len(cities)

    if n < 2:
        return {"order": list(range(n)), "total_distance": 0, "history": [], "time_ms": 0}

    if n > MAX_BNB_CITIES:
        return {
            "order": list(range(n)),
            "total_distance": total_distance(list(range(n)), cities),
            "history": [],
            "time_ms": (time.time() - start_time) * 1000,
            "error": f"Слишком много городов для ветвей и границ (макс. {MAX_BNB_CITIES})",
        }

    greedy_result = greedy(cities)
    best_order = greedy_result["order"]
    best_distance = greedy_result["total_distance"]
    history = []
    checked = 0

    visited = [False] * n
    visited[0] = True

    deadline = start_time + time_limit
    truncated = [False]
    calls = [0]

    def bound(order: List[int], current_distance: float) -> float:
        """Нижняя граница: текущая длина + минимум до любого непосещённого города."""
        last = order[-1]
        min_to_unvisited = float("inf")
        for i in range(n):
            if not visited[i]:
                d = distance(cities[last], cities[i])
                if d < min_to_unvisited:
                    min_to_unvisited = d
        if min_to_unvisited == float("inf"):
            return current_distance + distance(cities[last], cities[0])
        return current_distance + min_to_unvisited

    def dfs(order: List[int], current_distance: float):
        nonlocal best_order, best_distance, checked

        if truncated[0]:
            return

        calls[0] += 1
        if calls[0] % 2000 == 0 and time.time() > deadline:
            truncated[0] = True
            return

        if len(order) == n:
            checked += 1
            total = current_distance + distance(cities[order[-1]], cities[order[0]])
            if total < best_distance:
                best_distance = total
                best_order = order.copy()
                history.append(
                    {
                        "order": order.copy(),
                        "complete": True,
                        "distance": total,
                        "note": f"Новый лучший маршрут, длина {total:.1f}",
                    }
                )
            return

        for next_city in range(n):
            if truncated[0]:
                return
            if not visited[next_city]:
                new_distance = current_distance + distance(cities[order[-1]], cities[next_city])
                new_order = order + [next_city]
                lower_bound = bound(new_order, new_distance)

                if lower_bound < best_distance:
                    visited[next_city] = True
                    dfs(new_order, new_distance)
                    visited[next_city] = False

    dfs([0], 0)

    result = {
        "order": best_order,
        "total_distance": best_distance,
        "history": history,
        "time_ms": (time.time() - start_time) * 1000,
        "checked": checked,
        "truncated": truncated[0],
    }

    if truncated[0]:
        result["note_global"] = (
            f"Поиск прерван по таймеру ({time_limit:.0f}с) — показан лучший "
            f"из найденных маршрутов, оптимальность не гарантирована"
        )

    return result

# СЛОВАРЬ АЛГОРИТМОВ
ALGORITHMS = {
    "greedy": greedy,
    "bruteforce": bruteforce,
    "ant": ant_colony,
    "branch_and_bound": branch_and_bound,
}


def solve(algorithm: str, cities: List[Tuple[float, float]]) -> Dict:
    """Единая точка входа для всех алгоритмов."""
    if algorithm not in ALGORITHMS:
        raise ValueError(f"Неизвестный алгоритм: {algorithm}")

    result = ALGORITHMS[algorithm](cities)
    result["algorithm"] = algorithm
    result["found"] = "error" not in result

    return result