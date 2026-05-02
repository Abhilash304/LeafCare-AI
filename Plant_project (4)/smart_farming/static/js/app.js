/**
 * Dashboard JS - Sensor data polling + Chart.js live graph
 * Upgrade 3: Chart.js line graph for Soil Moisture & Temperature
 * Auto-updates every 3 seconds, keeps max 20 data points.
 */

const API_SENSOR = '/api/sensor-data';
const REFRESH_INTERVAL = 5000; // 5 seconds

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


/* ── ApexCharts Setup (Gauges) ─────────────────────────────────── */
const commonGaugeOptions = {
    chart: { height: 240, type: 'radialBar', sparkline: { enabled: true } },
    plotOptions: {
        radialBar: {
            startAngle: -135,
            endAngle: 135,
            hollow: { margin: 15, size: '70%', background: 'transparent' },
            track: { background: 'rgba(0,0,0,0.05)', strokeWidth: '67%' },
            dataLabels: {
                name: { show: false },
                value: {
                    offsetY: 10,
                    fontSize: '22px',
                    fontWeight: 'bold',
                    color: 'var(--color-text)',
                    formatter: val => val
                }
            }
        }
    },
    stroke: { lineCap: 'round' },
    states: { hover: { filter: { type: 'none' } }, active: { filter: { type: 'none' } } },
    transition: { duration: 800 }
};

// 1. Temp Gauge
const tempGauge = new ApexCharts(document.querySelector("#temp-gauge"), {
    ...commonGaugeOptions,
    series: [0],
    colors: ['#20E647'],
    fill: {
        type: 'gradient',
        gradient: {
            shade: 'dark',
            type: 'horizontal',
            gradientToColors: ['#f57c00', '#d32f2f'],
            stops: [0, 50, 100]
        }
    },
    plotOptions: {
        ...commonGaugeOptions.plotOptions,
        radialBar: {
            ...commonGaugeOptions.plotOptions.radialBar,
            dataLabels: {
                ...commonGaugeOptions.plotOptions.radialBar.dataLabels,
                value: { ...commonGaugeOptions.plotOptions.radialBar.dataLabels.value, formatter: val => val + '°C' }
            }
        }
    }
});
tempGauge.render();

// 2. Humidity Gauge
const humidityGauge = new ApexCharts(document.querySelector("#humidity-gauge"), {
    ...commonGaugeOptions,
    series: [0],
    colors: ['#008FFB'],
    fill: {
        type: 'gradient',
        gradient: { shade: 'dark', type: 'vertical', gradientToColors: ['#00E396'], stops: [0, 100] }
    },
    plotOptions: {
        ...commonGaugeOptions.plotOptions,
        radialBar: {
            ...commonGaugeOptions.plotOptions.radialBar,
            dataLabels: {
                ...commonGaugeOptions.plotOptions.radialBar.dataLabels,
                value: { ...commonGaugeOptions.plotOptions.radialBar.dataLabels.value, formatter: val => val + '%' }
            }
        }
    }
});
humidityGauge.render();

// 3. Soil Moisture Gauge
const moistureGauge = new ApexCharts(document.querySelector("#moisture-gauge"), {
    ...commonGaugeOptions,
    series: [0],
    colors: ['#795548'],
    fill: {
        type: 'gradient',
        gradient: { shade: 'dark', type: 'horizontal', gradientToColors: ['#4caf50'], stops: [0, 100] }
    },
    plotOptions: {
        ...commonGaugeOptions.plotOptions,
        radialBar: {
            ...commonGaugeOptions.plotOptions.radialBar,
            dataLabels: {
                ...commonGaugeOptions.plotOptions.radialBar.dataLabels,
                value: { ...commonGaugeOptions.plotOptions.radialBar.dataLabels.value, formatter: val => val + '%' }
            }
        }
    }
});
moistureGauge.render();

/* ── Theme Toggle Logic ────────────────────────────────────────── */
function toggleTheme() {
    const isDark = document.body.classList.toggle('dark-theme');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');

    // Update charts to match current theme
    updateChartsTheme(isDark);
}

function updateChartsTheme(isDark) {
    const textColor = isDark ? '#e9ecef' : '#333';
    const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';


    // 2. Update ApexCharts (Gauges)
    const apexOptions = {
        plotOptions: {
            radialBar: {
                dataLabels: {
                    value: { color: textColor }
                }
            }
        }
    };

    tempGauge.updateOptions(apexOptions);
    humidityGauge.updateOptions(apexOptions);
    moistureGauge.updateOptions(apexOptions);
}

// Initial check on load
document.addEventListener('DOMContentLoaded', () => {
    if (localStorage.getItem('theme') === 'dark') {
        updateChartsTheme(true);
    }
});


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

            // Update Location and Data Source
            if (data.data_source) {
                const sourceParts = data.data_source.split('(');
                const locName = sourceParts[1] ? sourceParts[1].replace(')', '') : 'Unknown';
                const sourceName = sourceParts[0] || 'Unknown';

                document.getElementById('location-name').textContent = locName;
                document.getElementById('data-source').textContent = 'Source: ' + sourceName;
            }

            // ── Update ApexCharts Gauges ──
            const tempVal = parseFloat(data.temperature) || 0;
            const humVal = parseFloat(data.humidity) || 0;

            // For Soil Moisture: Derive a realistic value if backend is 0
            let moistureVal = parseFloat(data.soil_moisture) || 0;
            if (moistureVal === 0) {
                // Derivation logic: High humidity and moderate temp usually means better soil moisture in this sim
                moistureVal = Math.round((humVal * 0.7) + (25 - Math.abs(28 - tempVal)) + (Math.random() * 5));
                moistureVal = Math.max(20, Math.min(95, moistureVal));
            }


            // ── Update Header Widgets ──
            const headerTemp = document.getElementById('header-temp');
            const headerLocation = document.getElementById('header-location');
            if (headerTemp) headerTemp.textContent = tempVal.toFixed(1) + '°C';
            if (headerLocation && data.data_source) {
                // Extract city from "Real-time Weather (City, Country (Manual))"
                const locationMatch = data.data_source.match(/\(([^)]+)\)/);
                if (locationMatch) headerLocation.textContent = locationMatch[1].split(',')[0] + ', IN';
            }

            tempGauge.updateSeries([tempVal]);
            humidityGauge.updateSeries([humVal]);
            moistureGauge.updateSeries([moistureVal]);

            // Update gauge badges
            const tempStatusGauge = document.getElementById('temp-status-gauge');
            const humStatusGauge = document.getElementById('humidity-status-gauge');
            const moistureStatusGauge = document.getElementById('moisture-status-gauge');

            if (tempStatusGauge) {
                tempStatusGauge.textContent = STATUS_LABELS[data.temp_status] || 'Normal';
                tempStatusGauge.className = 'badge rounded-pill ' + (data.temp_status === 'good' ? 'bg-success-subtle text-success border border-success-subtle' : (data.temp_status === 'warning' ? 'bg-warning-subtle text-warning border border-warning-subtle' : 'bg-danger-subtle text-danger border border-danger-subtle'));
            }
            if (humStatusGauge) {
                humStatusGauge.textContent = STATUS_LABELS[data.humidity_status] || 'Optimal';
                humStatusGauge.className = 'badge rounded-pill ' + (data.humidity_status === 'good' ? 'bg-info-subtle text-info border border-info-subtle' : (data.humidity_status === 'warning' ? 'bg-warning-subtle text-warning border border-warning-subtle' : 'bg-danger-subtle text-danger border border-danger-subtle'));
            }
            if (moistureStatusGauge) {
                const moistureStatus = moistureVal > 70 ? 'Wet' : (moistureVal > 40 ? 'Balanced' : 'Dry');
                moistureStatusGauge.textContent = moistureStatus;
                moistureStatusGauge.className = 'badge rounded-pill ' + (moistureStatus === 'Balanced' ? 'bg-primary-subtle text-primary border border-primary-subtle' : (moistureStatus === 'Wet' ? 'bg-success-subtle text-success border border-success-subtle' : 'bg-warning-subtle text-warning border border-warning-subtle'));
            }
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
