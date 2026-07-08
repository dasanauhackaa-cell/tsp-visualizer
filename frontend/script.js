// СОСТОЯНИЕ
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const statusEl = document.getElementById('status');

let cities = [];
let route = null;    //найденный маршрут
let solving = false; //блокировка во время расчёта

const API_BASE = 'http://localhost:8000';
const CELL_SIZE = 40;

// РАССТОЯНИЕ (в клетках)
function distance(city1, city2) {
    const dx = city1.x - city2.x;
    const dy = city1.y - city2.y;
    return Math.sqrt(dx * dx + dy * dy) / CELL_SIZE;
}

// ОТРИСОВКА КАРТЫ
function draw() {
    ctx.clearRect(0, 0, 800, 600);

    ctx.strokeStyle = 'rgba(255,255,255,0.03)';
    ctx.lineWidth = 0.5;
    for (let x = 0; x <= 800; x += CELL_SIZE) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, 600);
        ctx.stroke();
    }
    for (let y = 0; y <= 600; y += CELL_SIZE) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(800, y);
        ctx.stroke();
    }

    // НОВОЕ: РИСУЕМ МАРШРУТ
    if (route && route.length > 1) {
        ctx.beginPath();
        ctx.moveTo(cities[route[0]].x, cities[route[0]].y);
        for (let i = 1; i < route.length; i++) {
            ctx.lineTo(cities[route[i]].x, cities[route[i]].y);
        }
        ctx.closePath();
        ctx.strokeStyle = '#4ADE80';
        ctx.lineWidth = 2.5;
        ctx.shadowColor = 'rgba(74, 222, 128, 0.4)';
        ctx.shadowBlur = 12;
        ctx.stroke();
        ctx.shadowBlur = 0;
    }

    cities.forEach((city, i) => {
        ctx.shadowColor = 'rgba(76, 201, 240, 0.2)';
        ctx.shadowBlur = 20;

        ctx.beginPath();
        ctx.arc(city.x, city.y, 10, 0, Math.PI * 2);
        ctx.fillStyle = '#4CC9F0';
        ctx.fill();

        ctx.shadowBlur = 0;
        ctx.strokeStyle = 'rgba(255,255,255,0.15)';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        ctx.fillStyle = '#0A0E14';
        ctx.font = 'bold 12px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(i + 1, city.x, city.y);
    });

    document.getElementById('cityCount').textContent = cities.length;
    renderMatrix();
}

// МАТРИЦА РАССТОЯНИЙ
function renderMatrix() {
    const wrapper = document.getElementById('matrixWrapper');
    const badge = document.getElementById('matrixBadge');
    const totalEl = document.getElementById('totalDistance');

    badge.textContent = `${cities.length} городов`;

    if (cities.length < 2) {
        wrapper.innerHTML = `<div style="text-align:center;color:#2D3540;padding:20px;font-size:13px;">// Добавьте минимум 2 города</div>`;
        totalEl.textContent = '—';
        return;
    }

    const n = cities.length;
    let html = '<table class="matrix-table"><thead><tr><th>Города</th>';
    for (let i = 0; i < n; i++) html += `<th>${i + 1}</th>`;
    html += '</tr></thead><tbody>';

    for (let i = 0; i < n; i++) {
        html += `<tr><th>${i + 1}</th>`;
        for (let j = 0; j < n; j++) {
            let cellClass = '', value = '';
            if (i === j) {
                cellClass = 'diagonal';
                value = '—';
            } else {
                value = distance(cities[i], cities[j]).toFixed(1);
            }
            html += `<td class="${cellClass}">${value}</td>`;
        }
        html += '</tr>';
    }
    html += '</tbody></table>';
    wrapper.innerHTML = html;

    let total = 0;
    for (let i = 0; i < n; i++) {
        for (let j = i + 1; j < n; j++) {
            total += distance(cities[i], cities[j]);
        }
    }
    totalEl.textContent = total.toFixed(2);
}

// СКРЫТЬ СВОДКУ ПО МАРШРУТУ
function hideRouteSummary() {
    route = null;
    document.getElementById('routeSummary').style.display = 'none';
}

// СОБЫТИЯ
canvas.addEventListener('click', (e) => {
    if (solving) return;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    const x = (e.clientX - rect.left) * scaleX;
    const y = (e.clientY - rect.top) * scaleY;

    cities.push({ x, y });
    draw();

    statusEl.innerHTML = `<span class="info">📍</span> Добавлен город ${cities.length}`;
});

document.getElementById('clearBtn').onclick = () => {
    cities = [];
    hideRouteSummary();
    draw();
    statusEl.innerHTML = `<span>🗑</span> Все города удалены`;
};

document.getElementById('randomBtn').onclick = () => {
    cities = [];
    for (let i = 0; i < 5; i++) {
        cities.push({
            x: 60 + Math.random() * 680,
            y: 60 + Math.random() * 480
        });
    }
    hideRouteSummary();
    draw();
    statusEl.innerHTML = `<span class="info">🎲</span> Сгенерировано 5 случайных городов`;
};

// ФОН
function createBgCities() {
    const container = document.getElementById('bgContainer');
    const numCities = 30, numLines = 35;
    const bgCities = [];

    for (let i = 0; i < numCities; i++) {
        const x = Math.random() * 100;
        const y = Math.random() * 100;
        bgCities.push({ x, y });

        const el = document.createElement('div');
        el.className = 'bg-city';
        el.style.left = x + '%';
        el.style.top = y + '%';
        el.style.animationDelay = (Math.random() * 4) + 's';
        container.appendChild(el);
    }

    for (let i = 0; i < numLines; i++) {
        const from = bgCities[Math.floor(Math.random() * bgCities.length)];
        const to = bgCities[Math.floor(Math.random() * bgCities.length)];
        if (from === to) continue;

        const dx = to.x - from.x;
        const dy = to.y - from.y;
        const length = Math.sqrt(dx * dx + dy * dy);
        const angle = Math.atan2(dy, dx) * 180 / Math.PI;

        const el = document.createElement('div');
        el.className = 'bg-line';
        el.style.left = from.x + '%';
        el.style.top = from.y + '%';
        el.style.width = length + '%';
        el.style.transform = `rotate(${angle}deg)`;
        el.style.transformOrigin = 'left center';
        el.style.animationDelay = (Math.random() * 6) + 's';
        container.appendChild(el);
    }
}

document.getElementById('solveBtn').onclick = async () => {
    if (solving) return;

    if (cities.length < 3) {
        statusEl.innerHTML = `<span class="error">❌</span> Нужно минимум 3 города!`;
        return;
    }

    const algorithm = document.getElementById('algoSelect').value;
    const HEAVY_ALGO_LIMIT = 10;

    if ((algorithm === 'bruteforce' || algorithm === 'branch_and_bound') && cities.length > HEAVY_ALGO_LIMIT) {
        statusEl.innerHTML = `<span class="error">❌</span> Для этого алгоритма максимум ${HEAVY_ALGO_LIMIT} городов (сейчас ${cities.length})`;
        return;
    }

    solving = true;
    const btn = document.getElementById('solveBtn');
    btn.textContent = '⏳ Считаю...';
    btn.disabled = true;
    statusEl.innerHTML = `<span>⏳</span> Отправка запроса на бэкенд...`;

    try {
        const res = await fetch(`${API_BASE}/solve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cities, algorithm })
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `Ошибка сервера: ${res.status}`);
        }

        const data = await res.json();
        route = data.order;
        draw();

        statusEl.innerHTML = `<span class="ok">✅</span> Маршрут найден!`;

        const algoNames = {
            greedy: 'Жадный алгоритм',
            ant: 'Муравьиный алгоритм',
            bruteforce: 'Полный перебор',
            branch_and_bound: 'Ветви и границы'
        };
        document.getElementById('routeAlgo').textContent = algoNames[data.algorithm] || data.algorithm;
        const totalDistanceInCells = data.total_distance / CELL_SIZE;
        document.getElementById('routeDistance').textContent = totalDistanceInCells.toFixed(2);
        document.getElementById('routeTime').textContent =
            `${data.time_ms.toFixed(1)} мс` + (data.checked != null ? ` · проверено ${data.checked}` : '');
        document.getElementById('routeSummary').style.display = 'flex';

        if (data.truncated) {
            statusEl.innerHTML = `<span class="error">⚠️</span> ${data.note_global || 'Поиск прерван по таймеру — маршрут может быть не оптимальным'}`;
        }

    } catch (err) {
        statusEl.innerHTML = `<span class="error">❌</span> Ошибка: ${err.message}`;
    }

    solving = false;
    btn.textContent = '🚀 Найти маршрут';
    btn.disabled = false;
};

createBgCities();

const glow = document.getElementById('mouseGlow');
const glowWarm = document.getElementById('mouseGlowWarm');
document.addEventListener('mousemove', (e) => {
    const x = e.clientX;
    const y = e.clientY;
    glow.style.left = x + 'px';
    glow.style.top = y + 'px';
    glowWarm.style.left = x + 'px';
    glowWarm.style.top = y + 'px';
});

const bgContainer = document.getElementById('bgContainer');
document.addEventListener('mousemove', (e) => {
    const x = (e.clientX / window.innerWidth - 0.5) * 10;
    const y = (e.clientY / window.innerHeight - 0.5) * 10;
    bgContainer.style.transform = `translate(${x}px, ${y}px)`;
    bgContainer.style.transition = 'transform 0.5s ease-out';
});

// СТАРТ
draw();
statusEl.innerHTML = `<span>💡</span> Кликни на карту, чтобы поставить первый город`;