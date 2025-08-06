#!/bin/bash

# Vocelio AI Call Center - Production Deployment Script
# This script helps you deploy your Vocelio platform to GitHub and Railway

set -e

echo "🚀 Vocelio AI Call Center - Production Deployment"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
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

# Check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js first."
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm first."
        exit 1
    fi
    
    print_success "All dependencies are installed!"
}

# Run pre-deployment checks
run_checks() {
    print_status "Running pre-deployment checks..."
    
    # Check if we're in the right directory
    if [ ! -f "package.json" ]; then
        print_error "package.json not found. Please run this script from the project root."
        exit 1
    fi
    
    # Install dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
        print_status "Installing dependencies..."
        npm install
    fi
    
    # Run TypeScript check
    print_status "Running TypeScript check..."
    if ! npm run type-check; then
        print_error "TypeScript check failed. Please fix the errors before deploying."
        exit 1
    fi
    
    # Run linting
    print_status "Running ESLint..."
    if ! npm run lint; then
        print_warning "ESLint found issues. Consider fixing them before deploying."
    fi
    
    # Run tests
    print_status "Running tests..."
    if ! npm run test; then
        print_error "Tests failed. Please fix the failing tests before deploying."
        exit 1
    fi
    
    # Build the project
    print_status "Building the project..."
    if ! npm run build; then
        print_error "Build failed. Please fix the build errors before deploying."
        exit 1
    fi
    
    print_success "All pre-deployment checks passed!"
}

# Setup Git repository
setup_git() {
    print_status "Setting up Git repository..."
    
    # Initialize git if not already initialized
    if [ ! -d ".git" ]; then
        git init
        print_success "Git repository initialized!"
    fi
    
    # Add all files
    git add .
    
    # Commit changes
    if [ -z "$(git status --porcelain)" ]; then
        print_warning "No changes to commit."
    else
        echo "Please enter a commit message (or press Enter for default):"
        read -r commit_message
        if [ -z "$commit_message" ]; then
            commit_message="feat: complete Vocelio AI Call Center implementation - production ready"
        fi
        
        git commit -m "$commit_message"
        print_success "Changes committed!"
    fi
}

# Push to GitHub
push_to_github() {
    print_status "Pushing to GitHub..."
    
    # Check if remote origin exists
    if ! git remote get-url origin &> /dev/null; then
        echo "Please enter your GitHub repository URL:"
        read -r repo_url
        git remote add origin "$repo_url"
    fi
    
    # Push to GitHub
    if git push -u origin main; then
        print_success "Successfully pushed to GitHub!"
    else
        print_error "Failed to push to GitHub. Please check your repository URL and permissions."
        exit 1
    fi
}

# Deploy to Railway
deploy_to_railway() {
    print_status "Deploying to Railway..."
    
    # Check if Railway CLI is installed
    if ! command -v railway &> /dev/null; then
        print_warning "Railway CLI not found. Please install it first:"
        print_status "npm install -g @railway/cli"
        echo "Do you want to continue without Railway deployment? (y/n)"
        read -r continue_without_railway
        if [ "$continue_without_railway" != "y" ]; then
            exit 1
        fi
        return
    fi
    
    # Login to Railway if not already logged in
    if ! railway whoami &> /dev/null; then
        print_status "Please login to Railway..."
        railway login
    fi
    
    # Link to Railway project or create new one
    if [ ! -f ".railway/project.json" ]; then
        echo "Do you want to (1) link to existing project or (2) create new project?"
        read -r project_choice
        
        if [ "$project_choice" = "1" ]; then
            railway link
        else
            railway create vocelio-ai-call-center
        fi
    fi
    
    # Deploy to Railway
    print_status "Deploying to Railway..."
    if railway up; then
        print_success "Successfully deployed to Railway!"
    else
        print_error "Railway deployment failed."
        exit 1
    fi
    
    # Get the deployment URL
    deployment_url=$(railway status --json | grep -o '"url":"[^"]*"' | cut -d'"' -f4)
    if [ -n "$deployment_url" ]; then
        print_success "Deployment URL: $deployment_url"
    fi
}

# Display post-deployment steps
show_post_deployment() {
    print_success "🎉 Deployment completed successfully!"
    echo ""
    echo "📋 Post-deployment checklist:"
    echo "1. Configure environment variables in Railway dashboard"
    echo "2. Run database migrations in Supabase:"
    echo "   - Execute SUPABASE_COMPLETE_SCHEMA.sql"
    echo "   - Execute SUPABASE_LOGIC_FUNCTIONS.sql"
    echo "3. Test your deployment endpoints"
    echo "4. Configure custom domain (optional)"
    echo "5. Set up monitoring and alerts"
    echo ""
    echo "📚 Documentation:"
    echo "- Deployment Guide: deployment/railway/DEPLOYMENT_GUIDE.md"
    echo "- Environment Variables: deployment/railway/.env.production.template"
    echo "- Deployment Checklist: deployment/railway/DEPLOYMENT_CHECKLIST.md"
    echo ""
    print_success "Your Vocelio AI Call Center is now live! 🚀"
}

# Main deployment flow
main() {
    echo "Starting deployment process..."
    echo ""
    
    check_dependencies
    echo ""
    
    run_checks
    echo ""
    
    setup_git
    echo ""
    
    push_to_github
    echo ""
    
    deploy_to_railway
    echo ""
    
    show_post_deployment
}

# Handle script interruption
trap 'print_error "Deployment interrupted!"; exit 1' INT

# Run the main function
main
