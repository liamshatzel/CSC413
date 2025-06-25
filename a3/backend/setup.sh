#!/bin/bash

# Backend Setup Script for Smart Studio

echo "🔧 Setting up Smart Studio Backend..."
echo "======================================"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js version: $(node --version)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi

echo "✅ npm version: $(npm --version)"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp env.example .env
    echo "✅ Created .env file from template"
    echo ""
    echo "📝 Please edit .env file with your configuration:"
    echo "   - Add your OpenAI API key"
    echo "   - Update Arduino serial port"
    echo ""
    echo "Example .env content:"
    echo "OPENAI_API_KEY=sk-your-api-key-here"
    echo "PORT=3001"
    echo "SERIAL_PORT=/dev/tty.usbmodem1101"
    echo "BAUD_RATE=9600"
else
    echo "✅ .env file already exists"
fi

# Check for required environment variables
echo "🔍 Checking environment configuration..."

if [ -f ".env" ]; then
    source .env
    
    if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
        echo "⚠️  OpenAI API key not configured"
    else
        echo "✅ OpenAI API key configured"
    fi
    
    if [ -z "$SERIAL_PORT" ] || [ "$SERIAL_PORT" = "/dev/tty.usbmodem1101" ]; then
        echo "⚠️  Serial port not configured (using default)"
    else
        echo "✅ Serial port configured: $SERIAL_PORT"
    fi
fi

echo ""
echo "🎉 Backend setup complete!"
echo "=========================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your OpenAI API key"
echo "2. Update SERIAL_PORT to match your Arduino port"
echo "3. Upload Arduino code to your board"
echo "4. Run: npm start"
echo ""
echo "To find your Arduino port:"
echo "- macOS: ls /dev/tty.usbmodem*"
echo "- Windows: Check Device Manager for COM ports"
echo "- Linux: ls /dev/ttyUSB* or ls /dev/ttyACM*" 