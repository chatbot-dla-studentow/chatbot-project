# ChatBot Project - Automated Deployment Script for Windows
# PowerShell version

param(
    [Parameter(Position=0)]
    [ValidateSet('deploy', 'start', 'stop', 'restart', 'status', 'logs', 'init-kb', 'cleanup', 'help')]
    [string]$Command = 'help',
    
    [Parameter(Position=1)]
    [string]$Service = ''
)

# Configuration
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$OllamaModel = "mistral:7b"

# Colors
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Test-Prerequisites {
    Write-Info "Checking prerequisites..."
    
    $missing = @()
    
    # Check Docker
    if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
        $missing += "Docker Desktop"
    }
    
    # Check Docker Compose
    try {
        docker compose version | Out-Null
    } catch {
        $missing += "Docker Compose"
    }
    
    # Check Git
    if (!(Get-Command git -ErrorAction SilentlyContinue)) {
        $missing += "Git"
    }
    
    # Check Python
    if (!(Get-Command python -ErrorAction SilentlyContinue) -and !(Get-Command python3 -ErrorAction SilentlyContinue)) {
        $missing += "Python 3"
    }
    
    if ($missing.Count -gt 0) {
        Write-Error "Missing prerequisites: $($missing -join ', ')"
        Write-Info "Please install:"
        foreach ($item in $missing) {
            Write-Host "  - $item" -ForegroundColor Yellow
        }
        Write-Info ""
        Write-Info "Installation links:"
        Write-Info "  Docker Desktop: https://www.docker.com/products/docker-desktop"
        Write-Info "  Git: https://git-scm.com/download/win"
        Write-Info "  Python: https://www.python.org/downloads/"
        exit 1
    }
    
    Write-Success "All prerequisites are installed"
}

function Initialize-Environment {
    Write-Info "Setting up environment..."
    
    # Copy .env.example if .env doesn't exist
    if (!(Test-Path "$ProjectDir\.env") -and (Test-Path "$ProjectDir\.env.example")) {
        Copy-Item "$ProjectDir\.env.example" "$ProjectDir\.env"
        Write-Warning "Created .env file from .env.example. Please review and update it."
    }
    
    Write-Success "Environment setup complete"
}

function Start-Infrastructure {
    Write-Info "Starting infrastructure services (Qdrant, Ollama, Node-RED)..."
    
    Set-Location $ProjectDir
    
    # Start core services
    docker compose up -d qdrant ollama node-red
    
    Write-Info "Waiting for services to be healthy..."
    Start-Sleep -Seconds 10
    
    # Check Qdrant
    $retry = 0
    while ($retry -lt 30) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:6333/health" -UseBasicParsing -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Success "Qdrant is healthy"
                break
            }
        } catch {
            Start-Sleep -Seconds 2
            $retry++
        }
    }
    
    # Check Ollama
    $retry = 0
    while ($retry -lt 30) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Success "Ollama is healthy"
                break
            }
        } catch {
            Start-Sleep -Seconds 2
            $retry++
        }
    }
    
    Write-Success "Infrastructure services started"
}

function Get-OllamaModel {
    Write-Info "Downloading Ollama model: $OllamaModel..."
    
    # Check if model already exists
    $modelList = docker exec ollama ollama list
    if ($modelList -match $OllamaModel) {
        Write-Success "Model $OllamaModel already exists"
        return
    }
    
    # Pull the model
    docker exec ollama ollama pull $OllamaModel
    
    Write-Success "Model $OllamaModel downloaded successfully"
}

function Initialize-KnowledgeBase {
    Write-Info "Initializing knowledge base..."
    
    $agent1Dir = Join-Path $ProjectDir "agents\agent1_student"
    Set-Location $agent1Dir
    
    # Check if virtualenv exists
    $venvPath = Join-Path $agent1Dir "venv"
    if (!(Test-Path $venvPath)) {
        Write-Info "Creating Python virtual environment..."
        python -m venv venv
    }
    
    # Activate virtualenv and install dependencies
    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
    & $activateScript
    
    Write-Info "Installing Python dependencies..."
    python -m pip install -q --upgrade pip
    pip install -q -r requirements.txt
    
    # Run knowledge base initialization
    Write-Info "Loading knowledge base into Qdrant..."
    python helpers\load_knowledge_base.py
    
    deactivate
    
    Write-Success "Knowledge base initialized"
}

function Import-NodeRedFlow {
    Write-Info "Importing Node-RED flow..."
    
    # Copy flow file to Node-RED container
    $flowPath = Join-Path $ProjectDir "agents\agent1_student\agent1_flow.json"
    docker cp $flowPath node-red:/data/flows.json
    
    # Restart Node-RED to load the flow
    docker restart node-red
    
    Write-Info "Waiting for Node-RED to restart..."
    Start-Sleep -Seconds 10
    
    Write-Success "Node-RED flow imported"
}

function Start-Agents {
    Write-Info "Starting agent services..."
    
    Set-Location $ProjectDir
    
    # Start all agent services
    docker compose up -d agent1_student agent2_ticket agent3_analytics agent4_bos agent5_security
    
    Write-Info "Waiting for agents to start..."
    Start-Sleep -Seconds 10
    
    # Check agent1_student health
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8001/health" -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Success "Agent1 (Student Support) is healthy"
        }
    } catch {
        Write-Warning "Agent1 may not be fully ready yet"
    }
    
    Write-Success "Agent services started"
}

function Start-OptionalServices {
    Write-Info "Starting optional services (Open WebUI)..."
    
    Set-Location $ProjectDir
    
    docker compose up -d open-webui
    
    Write-Success "Optional services started"
}

function Show-Status {
    Write-Info "System Status:"
    Write-Host ""
    
    Set-Location $ProjectDir
    docker compose ps
    
    Write-Host ""
    Write-Info "Service URLs:"
    Write-Host "  Agent1 Student: http://localhost:8001" -ForegroundColor Cyan
    Write-Host "  Qdrant:         http://localhost:6333" -ForegroundColor Cyan
    Write-Host "  Ollama:         http://localhost:11434" -ForegroundColor Cyan
    Write-Host "  Node-RED:       http://localhost:1880" -ForegroundColor Cyan
    Write-Host "  Open WebUI:     http://localhost:3000" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Info "Health checks:"
    
    # Agent1
    try {
        Invoke-WebRequest -Uri "http://localhost:8001/health" -UseBasicParsing -ErrorAction Stop | Out-Null
        Write-Host "  Agent1:   OK" -ForegroundColor Green
    } catch {
        Write-Host "  Agent1:   NOT READY" -ForegroundColor Red
    }
    
    # Qdrant
    try {
        Invoke-WebRequest -Uri "http://localhost:6333/health" -UseBasicParsing -ErrorAction Stop | Out-Null
        Write-Host "  Qdrant:   OK" -ForegroundColor Green
    } catch {
        Write-Host "  Qdrant:   NOT READY" -ForegroundColor Red
    }
    
    # Ollama
    try {
        Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -ErrorAction Stop | Out-Null
        Write-Host "  Ollama:   OK" -ForegroundColor Green
    } catch {
        Write-Host "  Ollama:   NOT READY" -ForegroundColor Red
    }
    
    # Node-RED
    try {
        Invoke-WebRequest -Uri "http://localhost:1880/" -UseBasicParsing -ErrorAction Stop | Out-Null
        Write-Host "  Node-RED: OK" -ForegroundColor Green
    } catch {
        Write-Host "  Node-RED: NOT READY" -ForegroundColor Red
    }
}

function Start-FullDeployment {
    Write-Info "Starting full deployment..."
    Write-Host ""
    
    Test-Prerequisites
    Initialize-Environment
    Start-Infrastructure
    Get-OllamaModel
    Initialize-KnowledgeBase
    Import-NodeRedFlow
    Start-Agents
    Start-OptionalServices
    
    Write-Host ""
    Write-Success "=== DEPLOYMENT COMPLETED SUCCESSFULLY ==="
    Write-Host ""
    Show-Status
}

function Stop-AllServices {
    Write-Info "Stopping all services..."
    Set-Location $ProjectDir
    docker compose down
    Write-Success "All services stopped"
}

function Invoke-Cleanup {
    Write-Warning "This will remove all containers, volumes, and data!"
    $confirm = Read-Host "Are you sure? (yes/no)"
    
    if ($confirm -eq "yes") {
        Set-Location $ProjectDir
        docker compose down -v
        Write-Success "Cleanup completed"
    } else {
        Write-Info "Cleanup cancelled"
    }
}

function Show-Logs {
    param([string]$ServiceName)
    
    Set-Location $ProjectDir
    
    if ($ServiceName) {
        docker compose logs -f $ServiceName
    } else {
        docker compose logs -f
    }
}

function Show-Help {
    Write-Host "ChatBot Project - Automated Deployment Script (Windows)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\deploy.ps1 [COMMAND] [SERVICE]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Green
    Write-Host "  deploy      Full deployment (check deps, setup, start all services)"
    Write-Host "  start       Start all services"
    Write-Host "  stop        Stop all services"
    Write-Host "  restart     Restart all services"
    Write-Host "  status      Show status of all services"
    Write-Host "  logs        Show logs for a service (or all if not specified)"
    Write-Host "  init-kb     Initialize knowledge base"
    Write-Host "  cleanup     Remove all containers and volumes"
    Write-Host "  help        Show this help message"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\deploy.ps1 deploy"
    Write-Host "  .\deploy.ps1 status"
    Write-Host "  .\deploy.ps1 logs agent1_student"
    Write-Host ""
}

# Main script logic
switch ($Command) {
    'deploy' {
        Start-FullDeployment
    }
    'start' {
        Set-Location $ProjectDir
        docker compose up -d
        Show-Status
    }
    'stop' {
        Stop-AllServices
    }
    'restart' {
        Stop-AllServices
        Start-Sleep -Seconds 5
        Set-Location $ProjectDir
        docker compose up -d
        Show-Status
    }
    'status' {
        Show-Status
    }
    'logs' {
        Show-Logs -ServiceName $Service
    }
    'init-kb' {
        Initialize-KnowledgeBase
    }
    'cleanup' {
        Invoke-Cleanup
    }
    'help' {
        Show-Help
    }
    default {
        Write-Error "Unknown command: $Command"
        Write-Host ""
        Show-Help
        exit 1
    }
}
