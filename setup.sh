#!/bin/bash

# RunPod Document Reader API Setup Script
# Automates installation and testing for dedicated RunPod instances

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Progress indicator
progress() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Banner
echo "=========================================="
echo "   RunPod Document Reader API Setup"
echo "=========================================="
echo

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    progress "Running as root - perfect for RunPod setup"
else
    warning "Not running as root. You may need to add 'sudo' to some commands."
fi

# Step 1: System updates and dependencies
progress "Updating system packages..."
apt update > /dev/null 2>&1 || error "Failed to update packages"

progress "Installing system dependencies..."
apt install -y python3 python3-pip curl wget > /dev/null 2>&1 || error "Failed to install system dependencies"

# Step 2: Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' || echo "0.0")
progress "Python version: $PYTHON_VERSION"

if [ "$(echo "$PYTHON_VERSION >= 3.8" | bc -l 2>/dev/null || echo 0)" -eq 1 ]; then
    success "Python version is compatible"
else
    warning "Python version might be too old, but continuing..."
fi

# Step 3: Install Python requirements
progress "Installing Python dependencies (this may take a few minutes)..."
pip3 install -r requirements.txt || error "Failed to install Python requirements"

success "All dependencies installed successfully"

# Step 4: Environment variable setup
echo
progress "Setting up environment variables..."

# Check if environment variables are already set
if [ -z "$BTW_DOC_READER_API_KEY" ]; then
    echo -e "${YELLOW}BTW_DOC_READER_API_KEY not set.${NC}"
    read -p "Enter your API key (or press Enter for default 'doc-reader-api'): " user_api_key
    export BTW_DOC_READER_API_KEY="${user_api_key:-doc-reader-api}"
fi

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${YELLOW}ANTHROPIC_API_KEY not set.${NC}"
    read -p "Enter your Anthropic API key: " anthropic_key
    if [ -z "$anthropic_key" ]; then
        warning "No Anthropic API key provided. AI extraction features will not work."
        export ANTHROPIC_API_KEY="test-key"
    else
        export ANTHROPIC_API_KEY="$anthropic_key"
    fi
fi

success "Environment variables configured"

# Step 5: Start the server in background
progress "Starting Document Reader API server..."
python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
SERVER_PID=$!

# Give server time to start
sleep 5

# Step 6: Test the server
progress "Testing server health..."

# Test health endpoint
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    success "Health check passed"
    HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
    echo "  Response: $HEALTH_RESPONSE"
else
    error "Health check failed. Check server.log for details."
fi

# Test authentication
progress "Testing API authentication..."
AUTH_TEST=$(curl -s -w "%{http_code}" -X POST "http://localhost:8000/ocr" \
    -H "Authorization: Bearer $BTW_DOC_READER_API_KEY" \
    -F "file=" 2>/dev/null | tail -c 3)

if [ "$AUTH_TEST" = "400" ]; then
    success "Authentication working (expected 400 for empty file)"
elif [ "$AUTH_TEST" = "401" ]; then
    warning "Authentication might be failing. Check your API key."
else
    warning "Unexpected authentication response: $AUTH_TEST"
fi

# Step 7: Get public IP for external access
progress "Detecting public access information..."
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "Unable to detect")

echo
echo "=========================================="
success "Setup completed successfully!"
echo "=========================================="
echo
echo "🚀 Server Status:"
echo "  - Process ID: $SERVER_PID"
echo "  - Local URL: http://localhost:8000"
echo "  - Health: http://localhost:8000/health"
echo "  - API Docs: http://localhost:8000/docs"
echo

if [ "$PUBLIC_IP" != "Unable to detect" ]; then
    echo "🌐 External Access:"
    echo "  - Public URL: http://$PUBLIC_IP:8000"
    echo "  - Make sure port 8000 is open in RunPod settings"
    echo
fi

echo "🔧 Server Management:"
echo "  - View logs: tail -f server.log"
echo "  - Stop server: kill $SERVER_PID"
echo "  - Restart: python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 &"
echo

echo "📝 Test Commands:"
echo "  # Health check"
echo "  curl http://localhost:8000/health"
echo
echo "  # OCR test (upload a PDF)"
echo "  curl -X POST \"http://localhost:8000/ocr\" \\"
echo "    -H \"Authorization: Bearer $BTW_DOC_READER_API_KEY\" \\"
echo "    -F \"file=@your-document.pdf\""
echo
echo "  # Extract test"
echo "  curl -X POST \"http://localhost:8000/extract\" \\"
echo "    -H \"Authorization: Bearer $BTW_DOC_READER_API_KEY\" \\"
echo "    -F \"file=@your-document.pdf\" \\"
echo "    -F \"prompt=Extract key information\""
echo

echo "🔑 Environment Variables:"
echo "  - BTW_DOC_READER_API_KEY=$BTW_DOC_READER_API_KEY"
echo "  - ANTHROPIC_API_KEY=$(echo $ANTHROPIC_API_KEY | sed 's/./*/g')"
echo

success "Document Reader API is ready to use!"

# Keep track of server PID for user
echo $SERVER_PID > server.pid
echo "Server PID saved to server.pid"