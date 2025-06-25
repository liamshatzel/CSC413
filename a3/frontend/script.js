// Configuration
const API_BASE_URL = 'http://localhost:3001';

// DOM Elements
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const chatMessages = document.getElementById('chatMessages');
const connectionStatus = document.getElementById('connectionStatus');
const connectionText = document.getElementById('connectionText');
const commandLog = document.getElementById('commandLog');
const servoSlider = document.getElementById('servoSlider');
const servoValue = document.getElementById('servoValue');

// State
let isConnected = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkConnection();
    setupEventListeners();
    updateServoValue();
});

// Event Listeners
function setupEventListeners() {
    chatForm.addEventListener('submit', handleChatSubmit);
    servoSlider.addEventListener('input', updateServoValue);

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

        if (isConnected) {
            addLogEntry('Connected to backend server');
        }
    } catch (error) {
        console.error('Connection check failed:', error);
        isConnected = false;
        updateConnectionStatus(false);
        addLogEntry('Failed to connect to backend server', 'error');
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

        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Add assistant response to chat
        addMessage(data.response, 'assistant');

        // Log commands sent to Arduino
        if (data.commands && data.commands.length > 0) {
            data.commands.forEach(command => {
                addLogEntry(`Sent: ${command}`);
            });
        }

    } catch (error) {
        console.error('Chat error:', error);
        addMessage('Sorry, I encountered an error. Please check your connection and try again.', 'assistant');
        addLogEntry(`Error: ${error.message}`, 'error');
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
    contentDiv.innerHTML = content;

    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Arduino Control Functions
async function sendCommand(command) {
    try {
        if (!isConnected) {
            throw new Error('Not connected to server');
        }

        const response = await fetch(`${API_BASE_URL}/api/arduino`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ command }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        addLogEntry(`Sent: ${command}`);

    } catch (error) {
        console.error('Command error:', error);
        addLogEntry(`Error sending command: ${error.message}`, 'error');
    }
}

function sendServoCommand() {
    const angle = servoSlider.value;
    sendCommand(`SERVO_${angle}`);
}

function updateServoValue() {
    servoValue.textContent = `${servoSlider.value}°`;
}

// Logging
function addLogEntry(message, type = 'info') {
    const logEntry = document.createElement('div');
    logEntry.className = 'log-entry';

    const timestamp = new Date().toLocaleTimeString();
    logEntry.textContent = `[${timestamp}] ${message}`;

    if (type === 'error') {
        logEntry.style.borderLeftColor = '#ff6b6b';
        logEntry.style.color = '#d63031';
    }

    commandLog.appendChild(logEntry);

    // Keep only last 10 entries
    while (commandLog.children.length > 10) {
        commandLog.removeChild(commandLog.firstChild);
    }

    // Scroll to bottom
    commandLog.scrollTop = commandLog.scrollHeight;
}

// Periodic connection check
setInterval(checkConnection, 10000); // Check every 10 seconds

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