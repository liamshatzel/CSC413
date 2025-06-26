// Configuration
const API_BASE_URL = 'http://localhost:3001';

// DOM Elements
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const chatMessages = document.getElementById('chatMessages');
const connectionStatus = document.getElementById('connectionStatus');
const connectionText = document.getElementById('connectionText');
const sensorData = document.getElementById('sensorData');

// RGB Controls
const redSlider = document.getElementById('redSlider');
const greenSlider = document.getElementById('greenSlider');
const blueSlider = document.getElementById('blueSlider');
const redValue = document.getElementById('redValue');
const greenValue = document.getElementById('greenValue');
const blueValue = document.getElementById('blueValue');

// Fan Controls
const fanSlider = document.getElementById('fanSlider');
const fanValue = document.getElementById('fanValue');

// State
let isConnected = false;
let currentTemp = 0;
let currentHumidity = 0;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkConnection();
    setupEventListeners();
    updateColorValues();
    updateFanValue();
    startSensorPolling();
});

// Event Listeners
function setupEventListeners() {
    chatForm.addEventListener('submit', handleChatSubmit);

    // RGB sliders
    redSlider.addEventListener('input', updateColorValues);
    greenSlider.addEventListener('input', updateColorValues);
    blueSlider.addEventListener('input', updateColorValues);

    // Fan slider
    fanSlider.addEventListener('input', updateFanValue);

    // Auto-resize text input
    messageInput.addEventListener('input', () => {
        messageInput.style.height = 'auto';
        messageInput.style.height = messageInput.scrollHeight + 'px';
    });
}

// Connection Management
async function checkConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        const data = await response.json();

        isConnected = data.status === 'ok';
        updateConnectionStatus(isConnected);
    } catch (error) {
        console.error('Connection check failed:', error);
        isConnected = false;
        updateConnectionStatus(false);
    }
}

function updateConnectionStatus(connected) {
    if (connected) {
        connectionStatus.classList.add('connected');
        connectionText.textContent = 'Connected';
    } else {
        connectionStatus.classList.remove('connected');
        connectionText.textContent = 'Disconnected';
    }
}

// Sensor Data
async function fetchSensorData() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/sensor`);
        const data = await response.json();
        currentTemp = data.temperature;
        currentHumidity = data.humidity;
        updateSensorDisplay();
    } catch (error) {
        console.error('Failed to fetch sensor data:', error);
    }
}

function updateSensorDisplay() {
    sensorData.textContent = `${currentTemp}°C, ${currentHumidity}% humidity`;
}

function startSensorPolling() {
    fetchSensorData();
    setInterval(fetchSensorData, 5000); // Poll every 5 seconds
}

// Chat Functionality
async function handleChatSubmit(e) {
    e.preventDefault();

    const message = messageInput.value.trim();
    if (!message) return;

    // Add user message to chat
    addMessage(message, 'user');
    messageInput.value = '';
    messageInput.style.height = 'auto';

    // Disable send button and show loading
    sendButton.disabled = true;
    sendButton.innerHTML = '<div class="loading"></div>';

    try {
        if (!isConnected) {
            throw new Error('Not connected to server');
        }

        // Send message with current sensor data
        const requestBody = {
            msg: message,
            temp: currentTemp.toString(),
            humidity: currentHumidity.toString()
        };

        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Add assistant response to chat
        addMessage(data.response, 'assistant');

    } catch (error) {
        console.error('Chat error:', error);
        addMessage('Sorry, I encountered an error. Please check your connection and try again.', 'assistant');
    } finally {
        // Re-enable send button
        sendButton.disabled = false;
        sendButton.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22,2 15,22 11,13 2,9"></polygon>
            </svg>
        `;
    }
}

function addMessage(content, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    // Parse content for reasoning section
    if (type === 'assistant' && content.includes('---')) {
        const parts = content.split('---');
        const artistResponse = parts[0].trim();
        const reasoning = parts[1] ? parts[1].trim() : '';

        // Create the main response
        const responseText = document.createElement('div');
        responseText.innerHTML = artistResponse;
        contentDiv.appendChild(responseText);

        // Add reasoning section if it exists
        if (reasoning) {
            const reasoningDiv = document.createElement('div');
            reasoningDiv.className = 'reasoning';

            //TODO: FIX!!

            // Extract the reasoning title and content
            if (reasoning.includes('**Why this environment?**')) {
                const reasoningParts = reasoning.split('**Why this environment?**');
                const reasoningTitle = document.createElement('div');
                reasoningTitle.className = 'reasoning-title';
                reasoningTitle.textContent = 'Why this environment?';
                reasoningDiv.appendChild(reasoningTitle);

                const reasoningContent = document.createElement('div');
                reasoningContent.innerHTML = reasoningParts[1] ? reasoningParts[1].trim() : reasoning;
                reasoningDiv.appendChild(reasoningContent);
            } else {
                // If no specific title, create a generic one
                const reasoningTitle = document.createElement('div');
                reasoningTitle.className = 'reasoning-title';
                reasoningTitle.textContent = 'Environment Notes';
                reasoningDiv.appendChild(reasoningTitle);

                const reasoningContent = document.createElement('div');
                reasoningContent.innerHTML = reasoning;
                reasoningDiv.appendChild(reasoningContent);
            }

            contentDiv.appendChild(reasoningDiv);
        }
    } else {
        contentDiv.innerHTML = content;
    }

    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// RGB Controls
function updateColorValues() {
    redValue.textContent = redSlider.value;
    greenValue.textContent = greenSlider.value;
    blueValue.textContent = blueSlider.value;
}

// Fan Controls
function updateFanValue() {
    fanValue.textContent = fanSlider.value;
}

// Combined RGB and Fan Control
async function sendControlCommand() {
    const r = parseInt(redSlider.value);
    const g = parseInt(greenSlider.value);
    const b = parseInt(blueSlider.value);
    const fan = parseInt(fanSlider.value);

    try {
        const response = await fetch(`${API_BASE_URL}/api/control`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ r, g, b, fan }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
    } catch (error) {
        console.error('Control command error:', error);
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Enter to send message
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }

    // Escape to clear input
    if (e.key === 'Escape') {
        messageInput.value = '';
        messageInput.style.height = 'auto';
        messageInput.blur();
    }
});

// Auto-focus input on page load
window.addEventListener('load', () => {
    messageInput.focus();
}); 