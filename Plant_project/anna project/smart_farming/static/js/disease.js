/**
 * disease.js - Live Camera Preview + Capture & Detect
 * Upgrade 1: Browser getUserMedia → base64 → backend
 * Upgrade 2: Shows crop + disease name separately
 * Upgrade 4: Warning banner on low-confidence result
 */

const API_CAPTURE = '/api/capture-and-detect';

// DOM refs
const videoEl = document.getElementById('cameraPreview');
const canvasEl = document.getElementById('captureCanvas');
const capturedImage = document.getElementById('captured-image');
const placeholderPreview = document.getElementById('placeholder-preview');
const btnCapture = document.getElementById('btn-capture');
const btnText = document.getElementById('btn-text');
const btnLoading = document.getElementById('btn-loading');
const resultPlaceholder = document.getElementById('result-placeholder');
const resultContent = document.getElementById('result-content');
const cropNameEl = document.getElementById('crop-name');
const diseaseNameEl = document.getElementById('disease-name');
const healthBadgeEl = document.getElementById('health-badge');
const confidenceEl = document.getElementById('confidence-value');
const lowConfBanner = document.getElementById('low-conf-banner');
const recommendationBox = document.getElementById('recommendation-box');
const recommendationContent = document.getElementById('recommendation-content');

let stream = null;

/* ── Step 1: Start live camera preview on page load ──────────────── */
async function startCamera() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        console.warn('getUserMedia not supported.');
        return;
    }
    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        videoEl.srcObject = stream;
        videoEl.classList.remove('d-none');
        placeholderPreview.classList.add('d-none');
        capturedImage.classList.add('d-none');
    } catch (err) {
        console.warn('Camera access denied or not available:', err);
        // Leave placeholder visible; fallback to server-side OpenCV
    }
}

startCamera();

/* ── Step 2: Capture button logic ────────────────────────────────── */
btnCapture.addEventListener('click', async () => {
    if (btnCapture.disabled) return;

    // Show loading state
    btnCapture.disabled = true;
    btnText.classList.add('d-none');
    btnLoading.classList.remove('d-none');
    hideLowConfBanner();

    // Read optional plant name
    const manualPlantNameInput = document.getElementById('manual-plant-name');
    const manualPlantName = manualPlantNameInput ? manualPlantNameInput.value.trim() : "";

    try {
        let body = {};
        if (manualPlantName) {
            body.plant_name = manualPlantName;
        }

        // If webcam stream is active → capture frame to canvas → base64
        if (stream && videoEl.readyState >= 2) {
            canvasEl.width = videoEl.videoWidth || 640;
            canvasEl.height = videoEl.videoHeight || 480;
            const ctx = canvasEl.getContext('2d');
            ctx.drawImage(videoEl, 0, 0, canvasEl.width, canvasEl.height);
            const dataUrl = canvasEl.toDataURL('image/jpeg', 0.9);

            // Show captured image, hide video
            videoEl.classList.add('d-none');
            capturedImage.src = dataUrl;
            capturedImage.classList.remove('d-none');

            body.image = dataUrl;
        }
        // else: no stream → server will use OpenCV fallback

        const res = await fetch(API_CAPTURE, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        const data = await res.json();

        if (data.success) {
            // If image came from server (OpenCV path)
            if (!body.image && data.image_path) {
                placeholderPreview.classList.add('d-none');
                videoEl.classList.add('d-none');
                capturedImage.src = data.image_path;
                capturedImage.classList.remove('d-none');
            }

            // Show result panel
            resultPlaceholder.classList.add('d-none');
            resultContent.classList.remove('d-none');

            // ── Upgrade 2: Crop + Disease ──
            if (cropNameEl) cropNameEl.textContent = data.crop || '—';
            diseaseNameEl.textContent = data.disease || data.disease_name || '—';
            confidenceEl.textContent = data.confidence;

            // ── Upgrade 4: Low-confidence warning ──
            if (data.status === 'Low Confidence - Retake Image') {
                showLowConfBanner();
            }

            // Health badge
            if (data.health_status === 'Healthy') {
                healthBadgeEl.textContent = 'Healthy';
                healthBadgeEl.className = 'badge bg-success fs-6';
                diseaseNameEl.className = 'fw-bold text-success fs-5';
            } else if (data.health_status === 'N/A') {
                // E.g. Human detected
                healthBadgeEl.textContent = 'N/A';
                healthBadgeEl.className = 'badge bg-secondary fs-6';
                diseaseNameEl.className = 'fw-bold text-secondary fs-5';
            } else {
                healthBadgeEl.textContent = 'Diseased';
                healthBadgeEl.className = 'badge bg-danger fs-6';
                diseaseNameEl.className = 'fw-bold text-danger fs-5';
            }

            renderRecommendation(data.recommendation, data);

        } else {
            alert(data.error || 'Capture failed. Please try again.');
            // Restore camera preview
            if (stream) {
                capturedImage.classList.add('d-none');
                videoEl.classList.remove('d-none');
            }
        }
    } catch (err) {
        console.error(err);
        alert('Network error. Please try again.');
    } finally {
        btnCapture.disabled = false;
        btnText.classList.remove('d-none');
        btnLoading.classList.add('d-none');
    }
});

/* ── Low Confidence banner helpers ──────────────────────────────── */
function showLowConfBanner() {
    if (lowConfBanner) lowConfBanner.classList.remove('d-none');
}
function hideLowConfBanner() {
    if (lowConfBanner) lowConfBanner.classList.add('d-none');
}

/* ── renderRecommendation ────────────────────────────────────────── */
function renderRecommendation(rec, fullData = null) {
    if (fullData && (fullData.health_status === 'N/A' || fullData.disease === 'Human Detected')) {
        recommendationBox.classList.add('d-none');
        return;
    }

    recommendationBox.classList.remove('d-none');

    if (!rec) {
        recommendationContent.innerHTML = '<p class="text-muted small">No specific recommendation available.</p>';
        return;
    }

    recommendationBox.classList.remove('diseased');
    if (rec.type === 'diseased') {
        recommendationBox.classList.add('diseased');
    }

    let html = '';
    if (rec.type === 'healthy') {
        html += `
            <p class="mb-2"><strong>Fertilizer:</strong> ${rec.fertilizer}</p>
            <p class="mb-2"><strong>Quantity:</strong> ${rec.quantity}</p>
            <p class="mb-3"><strong>When:</strong> ${rec.when_to_apply}</p>
            <p class="mb-2"><strong>Preventive Tips:</strong></p>
            <ul class="small mb-0">`;
        (rec.preventive_tips || []).forEach(tip => { html += `<li>${tip}</li>`; });
        html += '</ul>';
    } else {
        html += `
            <p class="mb-2"><strong>Cause:</strong> ${rec.cause || '--'}</p>
            <p class="mb-2"><strong>Pesticide:</strong> ${rec.pesticide || '--'}</p>
            <p class="mb-3"><strong>Usage:</strong> ${rec.usage || '--'}</p>
            <p class="mb-2"><strong>Preventive Tips:</strong></p>
            <ul class="small mb-0">`;
        (rec.preventive_tips || []).forEach(tip => { html += `<li>${tip}</li>`; });
        html += '</ul>';
    }
    recommendationContent.innerHTML = html;
}

/* ── Step 4: Handle File Upload ──────────────────────────────────── */
const fileUpload = document.getElementById('file-upload');
const uploadLabel = document.getElementById('btn-upload-label');
const uploadText = document.getElementById('btn-upload-text');
const uploadLoading = document.getElementById('btn-upload-loading');

if (fileUpload) {
    fileUpload.addEventListener('change', async (e) => {
        if (e.target.files.length === 0) return;
        const file = e.target.files[0];

        btnCapture.disabled = true;
        uploadLabel.classList.add('disabled');
        uploadText.classList.add('d-none');
        uploadLoading.classList.remove('d-none');
        hideLowConfBanner();

        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await fetch('/api/upload-and-detect', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();

            if (data.success) {
                placeholderPreview.classList.add('d-none');
                videoEl.classList.add('d-none');
                capturedImage.src = data.image_path;
                capturedImage.classList.remove('d-none');

                resultPlaceholder.classList.add('d-none');
                resultContent.classList.remove('d-none');

                if (cropNameEl) cropNameEl.textContent = data.crop || '—';
                diseaseNameEl.textContent = data.disease || data.disease_name || '—';
                confidenceEl.textContent = data.confidence;

                if (data.status === 'Low Confidence - Retake Image') {
                    showLowConfBanner();
                }

                if (data.health_status === 'Healthy') {
                    healthBadgeEl.textContent = 'Healthy';
                    healthBadgeEl.className = 'badge bg-success fs-6';
                    diseaseNameEl.className = 'fw-bold text-success fs-5';
                } else if (data.health_status === 'N/A') {
                    healthBadgeEl.textContent = 'N/A';
                    healthBadgeEl.className = 'badge bg-secondary fs-6';
                    diseaseNameEl.className = 'fw-bold text-secondary fs-5';
                } else {
                    healthBadgeEl.textContent = 'Diseased';
                    healthBadgeEl.className = 'badge bg-danger fs-6';
                    diseaseNameEl.className = 'fw-bold text-danger fs-5';
                }

                renderRecommendation(data.recommendation, data);
            } else {
                alert(data.error || 'Upload failed.');
                if (stream) {
                    capturedImage.classList.add('d-none');
                    videoEl.classList.remove('d-none');
                }
            }
        } catch (err) {
            console.error(err);
            alert('Upload error. Please try again.');
        } finally {
            e.target.value = ''; // Reset file input
            btnCapture.disabled = false;
            uploadLabel.classList.remove('disabled');
            uploadText.classList.remove('d-none');
            uploadLoading.classList.add('d-none');
        }
    });
}
