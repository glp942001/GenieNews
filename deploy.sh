#!/bin/bash

# GenieNews Fly.io Deployment Helper Script
# This script helps with common deployment tasks

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if flyctl is installed
check_flyctl() {
    if ! command -v flyctl &> /dev/null; then
        print_error "flyctl is not installed. Please install it from https://fly.io/docs/hands-on/install-flyctl/"
        exit 1
    fi
    print_success "flyctl is installed"
}

# Check if logged in to Fly.io
check_fly_auth() {
    if ! flyctl auth whoami &> /dev/null; then
        print_error "Not logged in to Fly.io. Please run: flyctl auth login"
        exit 1
    fi
    print_success "Logged in to Fly.io"
}

# Deploy backend
deploy_backend() {
    print_info "Deploying backend..."
    cd backend
    flyctl deploy --app genienews-backend
    cd ..
    print_success "Backend deployed"
}

# Deploy frontend
deploy_frontend() {
    print_info "Deploying frontend..."
    cd frontend
    flyctl deploy --app genienews-frontend
    cd ..
    print_success "Frontend deployed"
}

# Check backend status
check_backend() {
    print_info "Checking backend status..."
    flyctl status --app genienews-backend
}

# Check frontend status
check_frontend() {
    print_info "Checking frontend status..."
    flyctl status --app genienews-frontend
}

# View backend logs
logs_backend() {
    print_info "Viewing backend logs (Ctrl+C to exit)..."
    flyctl logs --app genienews-backend
}

# View frontend logs
logs_frontend() {
    print_info "Viewing frontend logs (Ctrl+C to exit)..."
    flyctl logs --app genienews-frontend
}

# SSH into backend
ssh_backend() {
    print_info "Opening SSH console to backend..."
    flyctl ssh console --app genienews-backend
}

# Open backend in browser
open_backend() {
    print_info "Opening backend in browser..."
    open "https://genienews-backend.fly.dev/admin/"
}

# Open frontend in browser
open_frontend() {
    print_info "Opening frontend in browser..."
    flyctl open --app genienews-frontend
}

# Show help
show_help() {
    echo "GenieNews Fly.io Deployment Helper"
    echo ""
    echo "Usage: ./deploy.sh [command]"
    echo ""
    echo "Commands:"
    echo "  deploy-backend    Deploy backend to Fly.io"
    echo "  deploy-frontend   Deploy frontend to Fly.io"
    echo "  deploy-all        Deploy both backend and frontend"
    echo "  status-backend    Check backend app status"
    echo "  status-frontend   Check frontend app status"
    echo "  status-all        Check status of both apps"
    echo "  logs-backend      View backend logs"
    echo "  logs-frontend     View frontend logs"
    echo "  ssh-backend       SSH into backend container"
    echo "  open-backend      Open backend admin in browser"
    echo "  open-frontend     Open frontend in browser"
    echo "  open-all          Open both in browser"
    echo "  check             Verify flyctl installation and auth"
    echo "  help              Show this help message"
    echo ""
}

# Main script
main() {
    case "$1" in
        check)
            check_flyctl
            check_fly_auth
            ;;
        deploy-backend)
            check_flyctl
            check_fly_auth
            deploy_backend
            ;;
        deploy-frontend)
            check_flyctl
            check_fly_auth
            deploy_frontend
            ;;
        deploy-all)
            check_flyctl
            check_fly_auth
            deploy_backend
            deploy_frontend
            ;;
        status-backend)
            check_flyctl
            check_fly_auth
            check_backend
            ;;
        status-frontend)
            check_flyctl
            check_fly_auth
            check_frontend
            ;;
        status-all)
            check_flyctl
            check_fly_auth
            check_backend
            check_frontend
            ;;
        logs-backend)
            check_flyctl
            check_fly_auth
            logs_backend
            ;;
        logs-frontend)
            check_flyctl
            check_fly_auth
            logs_frontend
            ;;
        ssh-backend)
            check_flyctl
            check_fly_auth
            ssh_backend
            ;;
        open-backend)
            open_backend
            ;;
        open-frontend)
            open_frontend
            ;;
        open-all)
            open_backend
            open_frontend
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"

