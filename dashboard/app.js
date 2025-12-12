/**
 * Dashboard JavaScript
 * Handles WebSocket connection and real-time updates
 */

// Configuration
const API_BASE_URL = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000/ws';

// State
let websocket = null;
let chart = null;
let isConnected = false;

// DOM Elements
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const freshCount = document.getElementById('freshCount');
const spoiledCount = document.getElementById('spoiledCount');
const otherCount = document.getElementById('otherCount');
const totalCount = document.getElementById('totalCount');
const avgConfidence = document.getElementById('avgConfidence');
const avgProcessing = document.getElementById('avgProcessing');
const activityList = document.getElementById('activityList');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initChart();
    connectWebSocket();
    loadInitialData();
});

/**
 * Initialize Chart.js doughnut chart
 */
function initChart() {
    const ctx = document.getElementById('distributionChart').getContext('2d');

    chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Fresh Fruit', 'Spoiled Fruit', 'Other'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: [
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(245, 158, 11, 0.8)'
                ],
                borderColor: [
                    '#10b981',
                    '#ef4444',
                    '#f59e0b'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#f9fafb',
                        padding: 15,
                        font: {
                            size: 12,
                            family: 'Inter'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(26, 31, 53, 0.95)',
                    titleColor: '#f9fafb',
                    bodyColor: '#f9fafb',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                        label: function (context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Connect to WebSocket for real-time updates
 */
function connectWebSocket() {
    try {
        websocket = new WebSocket(WS_URL);

        websocket.onopen = () => {
            console.log('WebSocket connected');
            updateConnectionStatus(true);
            startHeartbeat();
        };

        websocket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            handleWebSocketMessage(message);
        };

        websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            updateConnectionStatus(false);
        };

        websocket.onclose = () => {
            console.log('WebSocket disconnected');
            updateConnectionStatus(false);

            // Attempt to reconnect after 5 seconds
            setTimeout(() => {
                console.log('Attempting to reconnect...');
                connectWebSocket();
            }, 5000);
        };

    } catch (error) {
        console.error('Failed to connect to WebSocket:', error);
        updateConnectionStatus(false);
    }
}

/**
 * Handle incoming WebSocket messages
 */
function handleWebSocketMessage(message) {
    if (message.type === 'stats') {
        updateStatistics(message.data);
    } else if (message.type === 'classification') {
        handleNewClassification(message.data);
    }
}

/**
 * Handle new classification result
 */
function handleNewClassification(data) {
    // Update quality metrics
    if (data.image_quality) {
        updateQualityMetrics(data.image_quality, data.quality_score);
    }

    // Update probability breakdown
    if (data.all_probabilities) {
        updateProbabilityBars(data.all_probabilities, data.classification);
    }

    // Update recommendations
    if (data.recommendation) {
        updateRecommendations(data.recommendation);
    }

    // Add to activity feed
    addClassificationToActivity(data);

    // Refresh statistics
    loadStatistics();
}

/**
 * Update quality metrics display
 */
function updateQualityMetrics(quality, overallScore) {
    // Update brightness
    updateQualityBar('brightnessBar', 'brightnessValue', quality.brightness);

    // Update sharpness
    updateQualityBar('sharpnessBar', 'sharpnessValue', quality.sharpness);

    // Update focus (blur)
    updateQualityBar('focusBar', 'focusValue', quality.blur);

    // Update contrast
    updateQualityBar('contrastBar', 'contrastValue', quality.contrast);

    // Update overall score
    const overallElement = document.getElementById('overallQuality');
    if (overallElement) {
        overallElement.textContent = Math.round(overallScore) + '%';

        // Change color based on score
        if (overallScore > 80) {
            overallElement.style.background = 'linear-gradient(135deg, var(--accent-fresh), var(--accent-primary))';
        } else if (overallScore > 60) {
            overallElement.style.background = 'linear-gradient(135deg, var(--accent-primary), var(--accent-fresh))';
        } else if (overallScore > 40) {
            overallElement.style.background = 'linear-gradient(135deg, var(--accent-other), var(--accent-primary))';
        } else {
            overallElement.style.background = 'linear-gradient(135deg, var(--accent-spoiled), var(--accent-other))';
        }
        overallElement.style.webkitBackgroundClip = 'text';
        overallElement.style.webkitTextFillColor = 'transparent';
        overallElement.style.backgroundClip = 'text';
    }
}

/**
 * Update individual quality bar
 */
function updateQualityBar(barId, valueId, score) {
    const bar = document.getElementById(barId);
    const value = document.getElementById(valueId);

    if (bar && value) {
        const percentage = Math.round(score * 100);
        bar.style.width = percentage + '%';
        value.textContent = percentage + '%';

        // Color based on score
        if (score > 0.8) {
            bar.style.background = 'var(--accent-fresh)';
        } else if (score > 0.6) {
            bar.style.background = 'var(--accent-primary)';
        } else if (score > 0.4) {
            bar.style.background = 'var(--accent-other)';
        } else {
            bar.style.background = 'var(--accent-spoiled)';
        }
    }
}

/**
 * Update probability bars
 */
function updateProbabilityBars(probabilities, topClass) {
    const container = document.getElementById('probabilityBars');
    if (!container) return;

    const iconMap = {
        'fresh_fruit': '🍏',
        'spoiled_fruit': '🍎',
        'other': '📦'
    };

    const labelMap = {
        'fresh_fruit': 'Fresh Fruit',
        'spoiled_fruit': 'Spoiled Fruit',
        'other': 'Other Object'
    };

    const classMap = {
        'fresh_fruit': 'fresh',
        'spoiled_fruit': 'spoiled',
        'other': 'other'
    };

    container.innerHTML = '';

    // Sort by probability
    const sorted = Object.entries(probabilities).sort((a, b) => b[1] - a[1]);

    sorted.forEach(([className, prob]) => {
        const percentage = (prob * 100).toFixed(1);
        const isTop = className === topClass;

        const item = document.createElement('div');
        item.className = 'prob-item';
        item.innerHTML = `
            <div class="prob-header">
                <span class="prob-label">
                    <span class="prob-label-icon">${iconMap[className] || '❓'}</span>
                    ${labelMap[className] || className}
                    ${isTop ? '<span style="color: var(--accent-primary);">★</span>' : ''}
                </span>
                <span class="prob-percentage">${percentage}%</span>
            </div>
            <div class="prob-bar-container">
                <div class="prob-bar ${classMap[className]}" style="width: ${percentage}%">
                    ${percentage}%
                </div>
            </div>
        `;

        container.appendChild(item);
    });
}

/**
 * Update recommendations display
 */
function updateRecommendations(recommendation) {
    const textElement = document.getElementById('recommendationText');
    if (!textElement) return;

    // Split by pipe and create formatted list
    const items = recommendation.split(' | ');

    let html = '<ul style="margin: 0; padding-left: 1.5rem; line-height: 1.8;">';
    items.forEach(item => {
        let className = '';
        if (item.includes('⚠️') || item.includes('Low') || item.includes('Poor')) {
            className = 'warning';
        } else if (item.includes('✅') || item.includes('Excellent') || item.includes('High')) {
            className = 'success';
        } else if (item.includes('❌')) {
            className = 'error';
        }

        html += `<li class="${className}">${item}</li>`;
    });
    html += '</ul>';

    textElement.innerHTML = html;
}

/**
 * Send periodic ping to keep connection alive
 */
function startHeartbeat() {
    setInterval(() => {
        if (websocket && websocket.readyState === WebSocket.OPEN) {
            websocket.send('ping');
        }
    }, 30000); // 30 seconds
}

/**
 * Update connection status indicator
 */
function updateConnectionStatus(connected) {
    isConnected = connected;

    if (connected) {
        statusDot.classList.add('connected');
        statusText.textContent = 'Connected';
    } else {
        statusDot.classList.remove('connected');
        statusText.textContent = 'Disconnected';
    }
}

/**
 * Load initial data from API
 */
async function loadInitialData() {
    await loadStatistics();
    await loadHistory();
}

/**
 * Load statistics from API
 */
async function loadStatistics() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/stats`);
        const stats = await response.json();
        updateStatistics(stats);
    } catch (error) {
        console.error('Failed to load statistics:', error);
    }
}

/**
 * Update statistics on dashboard
 */
function updateStatistics(stats) {
    // Update counts
    const fresh = stats.category_counts?.fresh_fruit || 0;
    const spoiled = stats.category_counts?.spoiled_fruit || 0;
    const other = stats.category_counts?.other || 0;
    const total = stats.total || 0;

    animateValue(freshCount, fresh);
    animateValue(spoiledCount, spoiled);
    animateValue(otherCount, other);
    animateValue(totalCount, total);

    // Update chart
    if (chart) {
        chart.data.datasets[0].data = [fresh, spoiled, other];
        chart.update('none');
    }

    // Update metrics
    const confidence = ((stats.avg_confidence || 0) * 100).toFixed(1);
    const processing = ((stats.avg_processing_time || 0) * 1000).toFixed(0);

    avgConfidence.textContent = `${confidence}%`;
    avgProcessing.textContent = `${processing}ms`;
}

/**
 * Animate number changes
 */
function animateValue(element, newValue) {
    const currentValue = parseInt(element.textContent) || 0;

    if (currentValue === newValue) return;

    const duration = 500;
    const steps = 20;
    const stepValue = (newValue - currentValue) / steps;
    const stepDuration = duration / steps;

    let current = currentValue;
    let step = 0;

    const timer = setInterval(() => {
        step++;
        current += stepValue;

        if (step >= steps) {
            element.textContent = newValue;
            clearInterval(timer);
        } else {
            element.textContent = Math.round(current);
        }
    }, stepDuration);
}

/**
 * Load classification history from API
 */
async function loadHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/history?limit=20`);
        const data = await response.json();

        displayHistory(data.history);
    } catch (error) {
        console.error('Failed to load history:', error);
    }
}

/**
 * Display classification history
 */
function displayHistory(history) {
    if (!history || history.length === 0) {
        return;
    }

    // Clear empty state
    activityList.innerHTML = '';

    // Add items
    history.forEach(item => {
        addActivityItem(item);
    });
}

/**
 * Add classification to activity feed
 */
function addClassificationToActivity(classification) {
    addActivityItem(classification, true);
}

/**
 * Add activity item to list
 */
function addActivityItem(item, prepend = false) {
    const { classification, confidence, timestamp, processing_time } = item;

    // Get icon and label
    const iconMap = {
        'fresh_fruit': '🍏',
        'spoiled_fruit': '🍎',
        'other': '📦'
    };

    const labelMap = {
        'fresh_fruit': 'Fresh Fruit',
        'spoiled_fruit': 'Spoiled Fruit',
        'other': 'Other Object'
    };

    const icon = iconMap[classification] || '❓';
    const label = labelMap[classification] || 'Unknown';

    // Format time
    const date = new Date(timestamp * 1000);
    const timeStr = date.toLocaleTimeString();

    // Confidence badge class
    let confidenceClass = 'confidence-high';
    if (confidence < 0.6) {
        confidenceClass = 'confidence-low';
    } else if (confidence < 0.8) {
        confidenceClass = 'confidence-medium';
    }

    // Create element
    const activityItem = document.createElement('div');
    activityItem.className = 'activity-item';
    activityItem.innerHTML = `
        <div class="activity-icon">${icon}</div>
        <div class="activity-content">
            <div class="activity-title">${label}</div>
            <div class="activity-meta">
                <span>${timeStr}</span>
                ${processing_time ? `<span>${(processing_time * 1000).toFixed(0)}ms</span>` : ''}
            </div>
        </div>
        <span class="confidence-badge ${confidenceClass}">
            ${(confidence * 100).toFixed(1)}%
        </span>
    `;

    // Add to list
    if (prepend) {
        activityList.insertBefore(activityItem, activityList.firstChild);

        // Limit items
        while (activityList.children.length > 20) {
            activityList.removeChild(activityList.lastChild);
        }
    } else {
        activityList.appendChild(activityItem);
    }
}

/**
 * Refresh data periodically
 */
setInterval(() => {
    if (!isConnected) {
        loadStatistics();
    }
}, 10000); // Every 10 seconds
