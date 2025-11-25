#!/bin/bash

# HoloTutor - AI Avatar Tutoring System
# Starts all services: Avatar Service, DASH API, Media Mixer, and Frontend

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Clean up old logs and create a fresh logs directory
rm -rf "$SCRIPT_DIR/logs"
mkdir -p "$SCRIPT_DIR/logs"

# Array to hold the PIDs of background processes
pids=()

# Function to clean up background processes
cleanup() {
    echo -e "\n${YELLOW}Shutting down HoloTutor...${NC}"
    for pid in "${pids[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "  Stopping process $pid"
            kill "$pid" 2>/dev/null
        fi
    done
    # Give processes time to terminate gracefully
    sleep 1
    # Force kill any remaining
    for pid in "${pids[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill -9 "$pid" 2>/dev/null
        fi
    done
    echo -e "${GREEN}All processes terminated.${NC}"
    exit 0
}

# Trap signals for cleanup
trap cleanup INT TERM

# Detect Python executable
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}Error: Python not found. Please install Python 3.${NC}"
    exit 1
fi

# Check if virtual environment exists and activate it
if [ -d "$SCRIPT_DIR/.venv" ]; then
    echo -e "${BLUE}Activating virtual environment...${NC}"
    source "$SCRIPT_DIR/.venv/bin/activate"
elif [ -d "$SCRIPT_DIR/venv" ]; then
    echo -e "${BLUE}Activating virtual environment...${NC}"
    source "$SCRIPT_DIR/venv/bin/activate"
fi

echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║             🎓 HoloTutor - AI Avatar System               ║"
echo "║       Learn from History's Greatest Minds                 ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Start the Avatar Service
echo -e "${BLUE}[1/4]${NC} Starting Avatar Service... (port 8001)"
(cd "$SCRIPT_DIR" && $PYTHON_CMD -m uvicorn AvatarService.avatar_service:app --host 0.0.0.0 --port 8001 --reload) > "$SCRIPT_DIR/logs/avatar.log" 2>&1 &
pids+=($!)
echo -e "       ${GREEN}✓${NC} Avatar Service started (PID: ${pids[-1]})"

# Start the DASH API server
echo -e "${BLUE}[2/4]${NC} Starting DASH Learning API... (port 8000)"
(cd "$SCRIPT_DIR" && $PYTHON_CMD DashSystem/dash_api.py) > "$SCRIPT_DIR/logs/api.log" 2>&1 &
pids+=($!)
echo -e "       ${GREEN}✓${NC} DASH API started (PID: ${pids[-1]})"

# Start the Media Mixer
echo -e "${BLUE}[3/4]${NC} Starting Media Mixer... (port 8765)"
(cd "$SCRIPT_DIR" && $PYTHON_CMD MediaMixer/media_mixer.py) > "$SCRIPT_DIR/logs/mediamixer.log" 2>&1 &
pids+=($!)
echo -e "       ${GREEN}✓${NC} Media Mixer started (PID: ${pids[-1]})"

# Give the backend servers a moment to start
echo -e "\n${YELLOW}Waiting for backend services to initialize...${NC}"
sleep 3

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: npm not found. Please install Node.js and npm.${NC}"
    cleanup
fi

# Install frontend dependencies if needed
if [ ! -d "$SCRIPT_DIR/frontend/node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    (cd "$SCRIPT_DIR/frontend" && npm install) > "$SCRIPT_DIR/logs/npm-install.log" 2>&1
fi

# Start the Node.js frontend
echo -e "${BLUE}[4/4]${NC} Starting React Frontend... (port 3000)"
(cd "$SCRIPT_DIR/frontend" && npm start) > "$SCRIPT_DIR/logs/frontend.log" 2>&1 &
pids+=($!)
echo -e "       ${GREEN}✓${NC} Frontend started (PID: ${pids[-1]})"

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ HoloTutor is running!${NC}"
echo ""
echo -e "  Services:"
echo -e "    • Frontend:       ${BLUE}http://localhost:3000${NC}"
echo -e "    • Avatar API:     ${BLUE}http://localhost:8001${NC}"
echo -e "    • DASH API:       ${BLUE}http://localhost:8000${NC}"
echo -e "    • Media Mixer:    ${BLUE}ws://localhost:8765${NC}"
echo ""
echo -e "  PIDs: ${pids[*]}"
echo -e "  Logs: ${SCRIPT_DIR}/logs/"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services.${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"

# Wait indefinitely until the script is interrupted
wait
