/**
 * Dashboard JS - Sensor data polling + Chart.js live graph
 * Upgrade 3: Chart.js line graph for Soil Moisture & Temperature
 * Auto-updates every 3 seconds, keeps max 20 data points.
 */

const API_SENSOR = '/api/sensor-data';
const REFRESH_INTERVAL = 3000; // 3 seconds

// Status badge classes
const STATUS_CLASSES = {
    good: 'badge-good',
    warning: 'badge-warning',
    critical: 'badge-critical'
};
const STATUS_LABELS = {
    good: 'Good',
    warning: 'Warning',
    critical: 'Critical'
};

/* ── Chart.js Setup ─────────────────────────────────────────────── */
const MAX_POINTS = 20;

const chartLabels = [];
const humidityData = [];
const temperatureData = [];

const ctx = document.getElementById('sensorChart').getContext('2d');
const sensorChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: chartLabels,
        datasets: [
            {
                label: 'Humidity %',
                data: humidityData,
                borderColor: '#4caf50',
                backgroundColor: 'rgba(76,175,80,.12)',
                borderWidth: 2.5,
                pointRadius: 3,
                tension: 0.4,
                fill: true,
                yAxisID: 'y'
            },
            {
                label: 'Temp °C',
                data: temperatureData,
                borderColor: '#f57c00',
                backgroundColor: 'transparent',
                borderWidth: 2.5,
                borderDash: [5, 5],
                pointRadius: 3,
                tension: 0.4,
                fill: false,
                yAxisID: 'y2'
            }
        ]
    },
    options: {
        responsive: true,
        interaction: { mode: 'index', intersect: false },
        plugins: {
            legend: {
                position: 'bottom',
                labels: { usePointStyle: true, boxWidth: 10 }
            },
            tooltip: {
                callbacks: {
                    label: ctx => ctx.dataset.label + ': ' + ctx.parsed.y.toFixed(1)
                }
            }
        },
        scales: {
            x: { grid: { color: 'rgba(0,0,0,.05)' } },
            y: {
                type: 'linear',
                position: 'left',
                title: { display: false },
                min: 0, max: 100,
                grid: { color: 'rgba(0,0,0,.05)' }
            },
            y2: {
                type: 'linear',
                position: 'right',
                title: { display: false },
                min: 0, max: 50,
                grid: { drawOnChartArea: false }
            }
        }
    }
});

function pushChartPoint(humidity, temperature) {
    const now = new Date();
    const label = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

    chartLabels.push(label);
    humidityData.push(humidity);
    temperatureData.push(temperature);

    if (chartLabels.length > MAX_POINTS) {
        chartLabels.shift();
        humidityData.shift();
        temperatureData.shift();
    }
    sensorChart.update('active');
}

/* ── Sensor Polling ─────────────────────────────────────────────── */
function updateSensorData() {
    fetch(API_SENSOR)
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                console.error('Sensor API error:', data.error);
                return;
            }

            // Update temperature
            document.getElementById('temp-value').textContent = data.temperature;
            const tempBadge = document.getElementById('temp-badge');
            tempBadge.textContent = STATUS_LABELS[data.temp_status] || 'Unknown';
            tempBadge.className = 'badge ' + (STATUS_CLASSES[data.temp_status] || 'bg-secondary');

            // Update humidity
            document.getElementById('humidity-value').textContent = data.humidity;
            const humidityBadge = document.getElementById('humidity-badge');
            humidityBadge.textContent = STATUS_LABELS[data.humidity_status] || 'Unknown';
            humidityBadge.className = 'badge ' + (STATUS_CLASSES[data.humidity_status] || 'bg-secondary');


            // Update irrigation status
            const statusEl = document.getElementById('irrigation-status');
            const visualEl = document.getElementById('irrigation-visual');
            const ruleEl = document.getElementById('irrigation-rule');

            if (data.irrigation_status === 'ON') {
                statusEl.innerHTML = '<span class="irrigation-indicator on"></span> ON';
                visualEl.className = 'irrigation-visual';
                visualEl.innerHTML = '<i class="bi bi-droplet-fill"></i>';
            } else {
                statusEl.innerHTML = '<span class="irrigation-indicator off"></span> OFF';
                visualEl.className = 'irrigation-visual off';
                visualEl.innerHTML = '<i class="bi bi-droplet"></i>';
            }

            // Handle manual mode UI
            if (data.manual_mode) {
                if (ruleEl) ruleEl.innerHTML = '<span class="badge bg-warning text-dark"><i class="bi bi-hand-index-thumb me-1"></i>Manual Override Active</span>';

                // Update toggle buttons if they exist
                const btnAuto = document.getElementById('btn-irrigation-auto');
                const btnOn = document.getElementById('btn-irrigation-on');
                const btnOff = document.getElementById('btn-irrigation-off');

                if (btnAuto && btnOn && btnOff) {
                    btnAuto.classList.remove('active');
                    if (data.irrigation_status === 'ON') {
                        btnOn.classList.add('active');
                        btnOff.classList.remove('active');
                    } else {
                        btnOn.classList.remove('active');
                        btnOff.classList.add('active');
                    }
                }
            } else {
                if (ruleEl) ruleEl.textContent = 'Rule: Soil moisture < 40% → Irrigation ON';

                // Update toggle buttons
                const btnAuto = document.getElementById('btn-irrigation-auto');
                const btnOn = document.getElementById('btn-irrigation-on');
                const btnOff = document.getElementById('btn-irrigation-off');

                if (btnAuto && btnOn && btnOff) {
                    btnAuto.classList.add('active');
                    btnOn.classList.remove('active');
                    btnOff.classList.remove('active');
                }
            }

            // Update ML Prediction
            const mlBadgeEl = document.getElementById('ml-prediction-badge');
            const mlConfidenceEl = document.getElementById('ml-confidence');
            const mlBarEl = document.getElementById('ml-confidence-bar');

            if (data.irrigation_prediction !== undefined) {
                const isNeeded = data.irrigation_prediction;
                mlBadgeEl.textContent = isNeeded ? 'IRRIGATION ON' : 'IRRIGATION OFF';
                mlBadgeEl.className = 'badge ' + (isNeeded ? 'bg-primary' : 'bg-success');
                const confidencePercent = Math.round(data.irrigation_confidence * 100);
                mlConfidenceEl.textContent = confidencePercent + '%';
                mlBarEl.style.width = confidencePercent + '%';
                mlBarEl.className = 'progress-bar ' + (confidencePercent > 80 ? 'bg-success' : 'bg-warning');
            }

            // Update timestamp
            document.getElementById('last-updated').textContent = data.timestamp || '--';

            // ── Upgrade 3: Push to chart ──
            pushChartPoint(
                parseFloat(data.humidity) || 0,
                parseFloat(data.temperature) || 0
            );
        })
        .catch(err => {
            console.error('Fetch error:', err);
            document.getElementById('temp-badge').textContent = 'Error';
            document.getElementById('humidity-badge').textContent = 'Error';
        });
}

// Initial load + interval
updateSensorData();
setInterval(updateSensorData, REFRESH_INTERVAL);

/* ── Manual Irrigation Toggle ── */
async function setIrrigationMode(mode, status) {
    try {
        const response = await fetch('/api/irrigation/toggle', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ mode: mode, status: status })
        });
        const result = await response.json();

        if (result.success) {
            // Update buttons optimistically
            const btnAuto = document.getElementById('btn-irrigation-auto');
            const btnOn = document.getElementById('btn-irrigation-on');
            const btnOff = document.getElementById('btn-irrigation-off');

            if (mode === 'auto') {
                btnAuto.classList.add('active');
                btnOn.classList.remove('active');
                btnOff.classList.remove('active');
            } else if (status === 'ON') {
                btnAuto.classList.remove('active');
                btnOn.classList.add('active');
                btnOff.classList.remove('active');
            } else {
                btnAuto.classList.remove('active');
                btnOn.classList.remove('active');
                btnOff.classList.add('active');
            }
            // Fetch dashboard to immediately reflect the change
            updateSensorData();
        } else {
            console.error('Failed to toggle irrigation:', result.error);
        }
    } catch (err) {
        console.error('Error toggling irrigation:', err);
    }
}
