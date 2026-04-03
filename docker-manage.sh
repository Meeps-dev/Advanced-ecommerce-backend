#!/bin/bash

# 🚀 E-Commerce Docker Quick Start Script
# This script provides easy access to common Docker commands

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "\n${BLUE}════════════════════════════════════════${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Show menu
show_menu() {
    print_header "E-Commerce Docker Management"
    echo "Choose an option:"
    echo ""
    echo "  1) Start all services (build & up)"
    echo "  2) Start in background (-d)"
    echo "  3) Stop all services"
    echo "  4) View logs (all services)"
    echo "  5) View API logs only"
    echo "  6) View worker logs only"
    echo "  7) Access database shell"
    echo "  8) Access Redis CLI"
    echo "  9) Run migrations manually"
    echo "  10) Seed data manually"
    echo "  11) Health check status"
    echo "  12) Restart services"
    echo "  13) Clean up (remove volumes)"
    echo "  14) Open API Docs (browser)"
    echo "  15) Open Flower Dashboard (browser)"
    echo ""
    read -p "Enter choice [1-15]: " choice
    echo ""
}

# Option functions
start_services() {
    print_header "Starting all services with build"
    docker-compose up --build
}

start_background() {
    print_header "Starting services in background"
    docker-compose up -d
    sleep 3
    print_success "Services starting in background"
    health_check
}

stop_services() {
    print_header "Stopping all services"
    docker-compose down
    print_success "Services stopped"
}

view_logs() {
    print_header "Viewing all service logs (press Ctrl+C to exit)"
    docker-compose logs -f
}

view_api_logs() {
    print_header "Viewing API logs (press Ctrl+C to exit)"
    docker-compose logs -f api
}

view_worker_logs() {
    print_header "Viewing Worker logs (press Ctrl+C to exit)"
    docker-compose logs -f worker
}

database_shell() {
    print_header "Connecting to PostgreSQL database"
    print_info "Commands: \\dt (list tables), \\du (users), \\q (quit)"
    docker-compose exec db psql -U postgres -d ecommerce_db
}

redis_cli() {
    print_header "Connecting to Redis CLI"
    docker-compose exec redis redis-cli
}

run_migrations() {
    print_header "Running database migrations"
    docker-compose exec api alembic upgrade head
    print_success "Migrations completed"
}

seed_data() {
    print_header "Seeding test data"
    docker-compose exec api python seed_database.py
}

health_check() {
    print_header "Health Check Status"
    docker-compose ps
    echo ""
    print_info "Understanding status:"
    echo "  - (healthy) = Service is healthy and ready"
    echo "  - (starting) = Service is initializing"
    echo "  - (unhealthy) = Service has issues"
    echo "  - Up X seconds = No health check implemented"
}

restart_services() {
    print_header "Restarting services"
    docker-compose restart
    sleep 2
    print_success "Services restarted"
}

cleanup() {
    print_header "🔥 WARNING: This will delete all containers and volumes!"
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
        docker-compose down -v
        print_success "Cleanup completed"
    else
        print_info "Cleanup cancelled"
    fi
}

open_api_docs() {
    print_info "Opening API Docs in browser..."
    # macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open "http://localhost:8000/docs"
    # Linux
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open "http://localhost:8000/docs" 2>/dev/null || echo "Please open http://localhost:8000/docs manually"
    # Windows (Git Bash)
    else
        start "http://localhost:8000/docs" 2>/dev/null || echo "Please open http://localhost:8000/docs manually"
    fi
}

open_flower() {
    print_info "Opening Flower Dashboard in browser..."
    # macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open "http://localhost:5555"
    # Linux
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open "http://localhost:5555" 2>/dev/null || echo "Please open http://localhost:5555 manually"
    # Windows (Git Bash)
    else
        start "http://localhost:5555" 2>/dev/null || echo "Please open http://localhost:5555 manually"
    fi
}

# Main menu loop
while true; do
    show_menu
    
    case $choice in
        1) start_services ;;
        2) start_background ;;
        3) stop_services ;;
        4) view_logs ;;
        5) view_api_logs ;;
        6) view_worker_logs ;;
        7) database_shell ;;
        8) redis_cli ;;
        9) run_migrations ;;
        10) seed_data ;;
        11) health_check ;;
        12) restart_services ;;
        13) cleanup ;;
        14) open_api_docs ;;
        15) open_flower ;;
        *)
            print_error "Invalid option. Please enter 1-15."
            ;;
    esac
    
    if [ "$choice" != "4" ] && [ "$choice" != "5" ] && [ "$choice" != "6" ] && [ "$choice" != "7" ]; then
        read -p "Press Enter to continue..."
    fi
done
