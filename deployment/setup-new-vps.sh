#!/bin/bash
# Complete Deployment and Security Setup for New VPS
# Usage: ./setup-new-vps.sh
# This script automates the entire process:
# 1. Security hardening
# 2. Geo-blocking
# 3. Monitoring setup
# 4. Deploy application

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    ChatBot VPS - Complete Setup & Deployment Wizard      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    log_error "This script should NOT be run as root initially"
    echo "First step (install dependencies) will ask for sudo"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Step 1: Security Hardening
log_info "Starting ChatBot VPS Setup"
echo ""
echo -e "${YELLOW}=== STEP 1: Security Hardening ===${NC}"
echo "This will:"
echo "  - Install and configure fail2ban"
echo "  - Configure UFW firewall"
echo "  - Harden SSH"
echo "  - Enable automatic security updates"
echo ""
read -p "Continue? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    log_warning "Setup cancelled"
    exit 0
fi

echo ""
sudo "$SCRIPT_DIR/secure.sh"

# Step 2: Geo-blocking
echo ""
echo -e "${YELLOW}=== STEP 2: Geo-Blocking (EU Only) ===${NC}"
echo "This will:"
echo "  - Install ipset for geo-blocking"
echo "  - Load EU IP ranges"
echo "  - Enable weekly updates"
echo ""
read -p "Continue? (yes/no): " confirm
if [ "$confirm" = "yes" ]; then
    sudo "$SCRIPT_DIR/geo-blocking.sh"
else
    log_warning "Geo-blocking skipped"
fi

# Step 3: Monitoring & Alerts
echo ""
echo -e "${YELLOW}=== STEP 3: Monitoring & Alerting ===${NC}"
echo "This will:"
echo "  - Configure email alerts to adam.siehen@gmail.com"
echo "  - Setup health checks (every 4 hours)"
echo "  - Setup security audits (daily)"
echo ""
read -p "Continue? (yes/no): " confirm
if [ "$confirm" = "yes" ]; then
    sudo "$SCRIPT_DIR/monitoring-alerts.sh"
else
    log_warning "Monitoring setup skipped"
fi

# Step 4: Deploy Application
echo ""
echo -e "${YELLOW}=== STEP 4: Deploy ChatBot Application ===${NC}"
echo "This will:"
echo "  - Install Docker and dependencies"
echo "  - Start Qdrant, Ollama, Node-RED"
echo "  - Download models"
echo "  - Start all agents"
echo ""
read -p "Continue? (yes/no): " confirm
if [ "$confirm" = "yes" ]; then
    cd "$SCRIPT_DIR/.."
    sudo ./deploy.sh install_dependencies
    
    # Copy .env if needed
    if [ ! -f ".env" ]; then
        cp .env.example .env
        log_warning "Created .env from .env.example - please review!"
    fi
    
    ./deploy.sh deploy
else
    log_warning "Application deployment skipped"
fi

# Final summary
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Complete Setup Finished!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${BLUE}What's Next:${NC}"
echo "  1. Add SSH Key:"
echo "     ssh-copy-id -i ~/.ssh/id_rsa -p 2222 asiehen@<vps-ip>"
echo ""
echo "  2. Connect to VPS:"
echo "     ssh -p 2222 asiehen@<vps-ip>"
echo ""
echo "  3. Check status:"
echo "     cd /opt/chatbot-project"
echo "     ./deploy.sh status"
echo ""
echo "  4. Monitor health:"
echo "     chatbot-status"
echo ""
echo "  5. View logs:"
echo "     ./deploy.sh logs"
echo ""

log_success "Thank you for using ChatBot VPS Setup!"
