const express = require('express');
const cors = require('cors');
const { SerialPort } = require('serialport');
const OpenAI = require('openai');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Initialize OpenAI
const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
});

// Initialize Serial Port
let serialPort;
try {
    serialPort = new SerialPort({
        path: process.env.SERIAL_PORT || '/dev/tty.usbmodem1101',
        baudRate: parseInt(process.env.BAUD_RATE) || 9600,
    });

    serialPort.on('open', () => {
        console.log('Serial port opened successfully');
    });

    serialPort.on('error', (err) => {
        console.error('Serial port error:', err);
    });

    serialPort.on('data', (data) => {
        console.log('Received from Arduino:', data.toString());
    });
} catch (error) {
    console.error('Failed to initialize serial port:', error);
}

// Function to send command to Arduino
function sendToArduino(command) {
    if (serialPort && serialPort.isOpen) {
        serialPort.write(command + '\n');
        console.log('Sent to Arduino:', command);
    } else {
        console.log('Serial port not available, command would be:', command);
    }
}

// Function to parse ChatGPT response and convert to Arduino commands
function parseResponseToArduinoCommands(response) {
    const commands = [];

    // Simple parsing logic - you can enhance this based on your needs
    const lowerResponse = response.toLowerCase();

    if (lowerResponse.includes('led') || lowerResponse.includes('light')) {
        if (lowerResponse.includes('on') || lowerResponse.includes('turn on')) {
            commands.push('LED_ON');
        } else if (lowerResponse.includes('off') || lowerResponse.includes('turn off')) {
            commands.push('LED_OFF');
        }
    }

    if (lowerResponse.includes('servo') || lowerResponse.includes('motor')) {
        const servoMatch = response.match(/(\d+)/);
        if (servoMatch) {
            const angle = parseInt(servoMatch[1]);
            if (angle >= 0 && angle <= 180) {
                commands.push(`SERVO_${angle}`);
            }
        }
    }

    if (lowerResponse.includes('buzzer') || lowerResponse.includes('beep')) {
        if (lowerResponse.includes('on') || lowerResponse.includes('play')) {
            commands.push('BUZZER_ON');
        } else if (lowerResponse.includes('off') || lowerResponse.includes('stop')) {
            commands.push('BUZZER_OFF');
        }
    }

    // If no specific commands found, send a generic response
    if (commands.length === 0) {
        commands.push('RESPONSE_RECEIVED');
    }

    return commands;
}

// API Routes
app.post('/api/chat', async (req, res) => {
    try {
        const { message } = req.body;

        if (!message) {
            return res.status(400).json({ error: 'Message is required' });
        }

        // Call ChatGPT API
        const completion = await openai.chat.completions.create({
            model: "gpt-3.5-turbo",
            messages: [
                {
                    role: "system",
                    content: "You are a helpful assistant that can control Arduino components. When asked about controlling hardware, respond with clear instructions that can be parsed into Arduino commands. You can control LEDs, servos, buzzers, and other components."
                },
                {
                    role: "user",
                    content: message
                }
            ],
            max_tokens: 150
        });

        const response = completion.choices[0].message.content;

        // Parse response and send to Arduino
        const arduinoCommands = parseResponseToArduinoCommands(response);

        // Send commands to Arduino
        arduinoCommands.forEach(command => {
            sendToArduino(command);
        });

        res.json({
            response: response,
            commands: arduinoCommands
        });

    } catch (error) {
        console.error('Error:', error);
        res.status(500).json({ error: 'Failed to process request' });
    }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({
        status: 'ok',
        serialConnected: serialPort ? serialPort.isOpen : false
    });
});

// Manual Arduino control endpoint
app.post('/api/arduino', (req, res) => {
    const { command } = req.body;

    if (!command) {
        return res.status(400).json({ error: 'Command is required' });
    }

    sendToArduino(command);
    res.json({ message: 'Command sent to Arduino', command });
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
    console.log(`Serial port: ${process.env.SERIAL_PORT || '/dev/tty.usbmodem1101'}`);
}); 