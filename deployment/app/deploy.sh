#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/opt/chatbot-project"
GIT_REPO="https://github.com/yourusername/chatbot-project.git"  # Update this!
OLLAMA_MODEL="mistral:7b"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "This script should NOT be run as root (except for install_dependencies)"
        log_info "Use: sudo ./deploy.sh install_dependencies"
        log_info "Then: ./deploy.sh deploy"
        exit 1
    fi
}

install_dependencies() {
    log_info "Installing system dependencies..."
    
    # Update package list
    sudo apt update
    
    # Install required packages
    sudo apt install -y \
        curl \
        wget \
        git \
        ca-certificates \
        gnupg \
        lsb-release \
        python3 \
        python3-pip \
        python3-venv
    
    # Install Docker
    if ! command -v docker &> /dev/null; then
        log_info "Installing Docker..."
        
        # Add Docker's official GPG key
        sudo install -m 0755 -d /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        sudo chmod a+r /etc/apt/keyrings/docker.gpg
        
        # Set up the repository
        echo \
          "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
          $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # Install Docker Engine
        sudo apt update
        sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        
        # Add current user to docker group
        sudo usermod -aG docker $USER
        log_warning "Docker installed. You may need to log out and back in for group changes to take effect."
    else
        log_success "Docker is already installed"
    fi
    
    # Verify Docker Compose
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose plugin not found"
        exit 1
    fi
    
    log_success "All dependencies installed successfully"
}

check_dependencies() {
    log_info "Checking system dependencies..."
    
    local missing_deps=()
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        missing_deps+=("docker")
    fi
    
    # Check Docker Compose
    if ! docker compose version &> /dev/null; then
        missing_deps+=("docker-compose")
    fi
    
    # Check Git
    if ! command -v git &> /dev/null; then
        missing_deps+=("git")
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        log_info "Run: sudo ./deploy.sh install_dependencies"
        exit 1
    fi
    
    log_success "All dependencies are installed"
}

setup_project() {
    log_info "Setting up project directory..."
    
    # Create project directory if it doesn't exist
    if [ ! -d "$PROJECT_DIR" ]; then
        sudo mkdir -p "$PROJECT_DIR"
        sudo chown $USER:$USER "$PROJECT_DIR"
    fi
    
    cd "$PROJECT_DIR"
    
    # Clone or update repository
    if [ ! -d ".git" ]; then
        log_info "Cloning repository..."
        git clone "$GIT_REPO" "$PROJECT_DIR"
    else
        log_info "Updating repository..."
        git pull origin main
    fi
    
    # Copy .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_warning "Created .env file from .env.example. Please review and update it."
        fi
    fi
    
    log_success "Project directory set up successfully"
}

create_docker_network() {
    log_info "Creating Docker network..."
    
    if docker network inspect ai_network &> /dev/null; then
        log_success "Network 'ai_network' already exists"
    else
        docker network create ai_network
        log_success "Network 'ai_network' created"
    fi
}

start_infrastructure() {
    log_info "Starting infrastructure services (Qdrant, Ollama, Node-RED)..."
    
    cd "$PROJECT_DIR"
    
    # Start core services
    docker compose up -d qdrant ollama node-red
    
    log_info "Waiting for services to be healthy..."
    sleep 10
    
    # Check Qdrant
    local retry=0
    while [ $retry -lt 30 ]; do
        if curl -f http://localhost:6333/health &> /dev/null; then
            log_success "Qdrant is healthy"
            break
        fi
        sleep 2
        ((retry++))
    done
    
    # Check Ollama
    retry=0
    while [ $retry -lt 30 ]; do
        if curl -f http://localhost:11434/api/tags &> /dev/null; then
            log_success "Ollama is healthy"
            break
        fi
        sleep 2
        ((retry++))
    done
    
    log_success "Infrastructure services started"
}

download_ollama_model() {
    log_info "Downloading Ollama model: $OLLAMA_MODEL..."
    
    # Check if model already exists
    if docker exec ollama ollama list | grep -q "$OLLAMA_MODEL"; then
        log_success "Model $OLLAMA_MODEL already exists"
        return
    fi
    
    # Pull the model
    docker exec ollama ollama pull "$OLLAMA_MODEL"
    
    log_success "Model $OLLAMA_MODEL downloaded successfully"
}

initialize_knowledge_base() {
    log_info "Initializing knowledge base..."
    
    cd "$PROJECT_DIR/agents/agent1_student"
    
    # Check if Python virtualenv exists
    if [ ! -d "venv" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtualenv and install dependencies
    source venv/bin/activate
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    
    # Run knowledge base initialization
    log_info "Loading knowledge base into Qdrant..."
    python3 helpers/load_knowledge_base.py
    
    deactivate
    
    log_success "Knowledge base initialized"
}

import_nodered_flow() {
    log_info "Importing Node-RED flow..."
    
    # Copy flow file to Node-RED container
    docker cp "$PROJECT_DIR/agents/agent1_student/agent1_flow.json" node-red:/data/flows.json
    
    # Restart Node-RED to load the flow
    docker restart node-red
    
    log_info "Waiting for Node-RED to restart..."
    sleep 10
    
    log_success "Node-RED flow imported"
}

start_agents() {
    log_info "Starting agent services..."
    
    cd "$PROJECT_DIR"
    
    # Start all agent services
    docker compose up -d agent1_student agent2_ticket agent3_analytics agent4_bos agent5_security
    
    log_info "Waiting for agents to start..."
    sleep 10
    
    # Check agent1_student health
    if curl -f http://localhost:8001/health &> /dev/null; then
        log_success "Agent1 (Student Support) is healthy"
    else
        log_warning "Agent1 may not be fully ready yet"
    fi
    
    log_success "Agent services started"
}

start_optional_services() {
    log_info "Starting optional services (Open WebUI)..."
    
    cd "$PROJECT_DIR"
    
    docker compose up -d open-webui
    
    log_success "Optional services started"
}

show_status() {
    log_info "System Status:"
    echo ""
    docker compose ps
    echo ""
    
    log_info "Service URLs:"
    echo -e "  ${BLUE}Agent1 Student:${NC} http://localhost:8001"
    echo -e "  ${BLUE}Qdrant:${NC}        http://localhost:6333"
    echo -e "  ${BLUE}Ollama:${NC}        http://localhost:11434"
    echo -e "  ${BLUE}Node-RED:${NC}      http://localhost:1880"
    echo -e "  ${BLUE}Open WebUI:${NC}    http://localhost:3000"
    echo ""
    
    log_info "Health checks:"
    curl -s http://localhost:8001/health && echo "Agent1: OK" || echo "Agent1: NOT READY"
    curl -s http://localhost:6333/health && echo "Qdrant: OK" || echo "Qdrant: NOT READY"
    curl -s http://localhost:11434/api/tags > /dev/null && echo "Ollama: OK" || echo "Ollama: NOT READY"
    curl -s http://localhost:1880/ > /dev/null && echo "Node-RED: OK" || echo "Node-RED: NOT READY"
}

full_deployment() {
    log_info "Starting full deployment..."
    echo ""
    
    check_dependencies
    setup_project
    create_docker_network
    start_infrastructure
    download_ollama_model
    initialize_knowledge_base
    import_nodered_flow
    start_agents
    start_optional_services
    
    echo ""
    log_success "=== DEPLOYMENT COMPLETED SUCCESSFULLY ==="
    echo ""
    show_status
}

stop_all() {
    log_info "Stopping all services..."
    cd "$PROJECT_DIR"
    docker compose down
    log_success "All services stopped"
}

cleanup() {
    log_warning "This will remove all containers, volumes, and data!"
    read -p "Are you sure? (yes/no): " confirm
    
    if [ "$confirm" == "yes" ]; then
        cd "$PROJECT_DIR"
        docker compose down -v
        docker network rm ai_network 2>/dev/null || true
        log_success "Cleanup completed"
    else
        log_info "Cleanup cancelled"
    fi
}

show_help() {
    echo "ChatBot Project - Automated Deployment Script"
    echo ""
    echo "Usage: ./deploy.sh [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  install_dependencies  Install Docker, Docker Compose, and other dependencies (requires sudo)"
    echo "  deploy               Full deployment (check deps, setup, start all services)"
    echo "  start                Start all services"
    echo "  stop                 Stop all services"
    echo "  restart              Restart all services"
    echo "  status               Show status of all services"
    echo "  logs [service]       Show logs for a service (or all if not specified)"
    echo "  init-kb              Initialize knowledge base"
    echo "  cleanup              Remove all containers and volumes"
    echo "  help                 Show this help message"
    echo ""
    echo "Examples:"
    echo "  sudo ./deploy.sh install_dependencies"
    echo "  ./deploy.sh deploy"
    echo "  ./deploy.sh status"
    echo "  ./deploy.sh logs agent1_student"
}

# Main script logic
case "${1:-}" in
    install_dependencies)
        # This command needs root
        if [[ $EUID -ne 0 ]]; then
            log_error "This command must be run as root"
            log_info "Use: sudo ./deploy.sh install_dependencies"
            exit 1
        fi
        install_dependencies
        ;;
    deploy)
        check_root
        full_deployment
        ;;
    start)
        check_root
        cd "$PROJECT_DIR"
        docker compose up -d
        show_status
        ;;
    stop)
        check_root
        stop_all
        ;;
    restart)
        check_root
        stop_all
        sleep 5
        cd "$PROJECT_DIR"
        docker compose up -d
        show_status
        ;;
    status)
        cd "$PROJECT_DIR" 2>/dev/null || { log_error "Project not deployed yet"; exit 1; }
        show_status
        ;;
    logs)
        cd "$PROJECT_DIR" 2>/dev/null || { log_error "Project not deployed yet"; exit 1; }
        if [ -n "${2:-}" ]; then
            docker compose logs -f "$2"
        else
            docker compose logs -f
        fi
        ;;
    init-kb)
        check_root
        initialize_knowledge_base
        ;;
    cleanup)
        check_root
        cleanup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: ${1:-}"
        echo ""
        show_help
        exit 1
        ;;
esac
