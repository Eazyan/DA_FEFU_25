let temperatureChart;
const updateInterval = 5000;

const weatherIcons = {
    'sunny': '☀️',
    'partly_cloudy': '⛅',
    'cloudy': '☁️',
    'rainy': '🌧️',
    'snowy': '❄️',
    'foggy': '🌫️'
};

const weatherConditions = {
    'sunny': 'Солнечно',
    'partly_cloudy': 'Переменная облачность',
    'cloudy': 'Облачно',
    'rainy': 'Дождь',
    'snowy': 'Снег',
    'foggy': 'Туман'
};

const windDirections = {
    'N': 'С', 'NE': 'С-В', 'E': 'В', 'SE': 'Ю-В',
    'S': 'Ю', 'SW': 'Ю-З', 'W': 'З', 'NW': 'С-З'
};

function getWindDirection(degrees) {
    const directions = ['С', 'С-В', 'В', 'Ю-В', 'Ю', 'Ю-З', 'З', 'С-З'];
    const index = Math.round(((degrees % 360) / 45)) % 8;
    return directions[index];
}

function initChart() {
    const ctx = document.getElementById('temperatureChart').getContext('2d');

    temperatureChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Температура (°C)',
                data: [],
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                pointRadius: 0,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: '#e0e5ec',
                    titleColor: '#333',
                    bodyColor: '#666',
                    borderColor: '#6366f1',
                    borderWidth: 2,
                    padding: 12,
                    boxPadding: 6
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        callback: function(value) {
                            return value + '°C';
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
}

async function fetchLatestData() {
    try {
        const response = await fetch('/api/latest');
        if (!response.ok) throw new Error('Failed to fetch data');

        const data = await response.json();
        updateMetrics(data);
        updateConnectionStatus(true);
    } catch (error) {
        console.error('Error fetching latest data:', error);
        updateConnectionStatus(false);
    }
}

async function fetchHistoricalData() {
    try {
        const response = await fetch('/api/history?hours=24');
        if (!response.ok) throw new Error('Failed to fetch history');

        const data = await response.json();
        updateChart(data);
    } catch (error) {
        console.error('Error fetching historical data:', error);
    }
}

async function fetchStats() {
    try {
        const response = await fetch('/api/stats');
        if (!response.ok) throw new Error('Failed to fetch stats');

        const data = await response.json();
        updateStats(data);
    } catch (error) {
        console.error('Error fetching stats:', error);
    }
}

function updateMetrics(data) {
    document.getElementById('temperature').textContent = data.temperature.toFixed(1);
    document.getElementById('humidity').textContent = data.humidity.toFixed(1);
    document.getElementById('pressure').textContent = data.pressure.toFixed(1);
    document.getElementById('windSpeed').textContent = data.wind_speed.toFixed(1);

    const weatherIcon = weatherIcons[data.weather_condition] || '☀️';
    const weatherText = weatherConditions[data.weather_condition] || data.weather_condition;
    const windDir = getWindDirection(data.wind_direction);

    document.getElementById('weatherIcon').textContent = weatherIcon;
    document.getElementById('weatherCondition').textContent = weatherText;
    document.getElementById('windDirection').textContent = `Ветер: ${windDir}`;

    const loadingEl = document.getElementById('loading');
    if (loadingEl) {
        loadingEl.style.display = 'none';
    }
}

function updateChart(data) {
    if (!temperatureChart) return;

    const maxPoints = 50;
    const step = Math.max(1, Math.floor(data.length / maxPoints));

    const labels = [];
    const temperatures = [];

    for (let i = 0; i < data.length; i += step) {
        const item = data[i];
        const date = new Date(item.timestamp);
        labels.push(date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }));
        temperatures.push(item.temperature);
    }

    temperatureChart.data.labels = labels;
    temperatureChart.data.datasets[0].data = temperatures;
    temperatureChart.update('none');
}

function updateStats(data) {
    if (data.temperature) {
        document.getElementById('minTemp').textContent = `${data.temperature.min.toFixed(1)} °C`;
        document.getElementById('maxTemp').textContent = `${data.temperature.max.toFixed(1)} °C`;
        document.getElementById('avgTemp').textContent = `${data.temperature.avg.toFixed(1)} °C`;
    }
}

function updateConnectionStatus(connected) {
    const statusEl = document.getElementById('connectionStatus');
    if (connected) {
        statusEl.className = 'connection-status status-connected';
        statusEl.innerHTML = '<span class="status-dot"></span><span>Подключено</span>';
    } else {
        statusEl.className = 'connection-status status-disconnected';
        statusEl.innerHTML = '<span class="status-dot"></span><span>Нет подключения</span>';
    }
}

async function updateAll() {
    await fetchLatestData();
    await fetchHistoricalData();
    await fetchStats();
}

document.addEventListener('DOMContentLoaded', () => {
    initChart();
    updateAll();

    setInterval(updateAll, updateInterval);
});
