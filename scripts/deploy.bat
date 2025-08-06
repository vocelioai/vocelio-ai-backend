@echo off
REM Vocelio AI Call Center - Production Deployment Script (Windows)
REM This script helps you deploy your Vocelio platform to GitHub and Railway

echo 🚀 Vocelio AI Call Center - Production Deployment
echo ==================================================

REM Check if required tools are installed
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed. Please install Git first.
    pause
    exit /b 1
)

where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed. Please install Node.js first.
    pause
    exit /b 1
)

where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] npm is not installed. Please install npm first.
    pause
    exit /b 1
)

echo [SUCCESS] All dependencies are installed!
echo.

REM Check if we're in the right directory
if not exist "package.json" (
    echo [ERROR] package.json not found. Please run this script from the project root.
    pause
    exit /b 1
)

REM Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo [INFO] Installing dependencies...
    npm install
)

REM Run pre-deployment checks
echo [INFO] Running pre-deployment checks...

echo [INFO] Running TypeScript check...
npm run type-check
if %errorlevel% neq 0 (
    echo [ERROR] TypeScript check failed. Please fix the errors before deploying.
    pause
    exit /b 1
)

echo [INFO] Running ESLint...
npm run lint
if %errorlevel% neq 0 (
    echo [WARNING] ESLint found issues. Consider fixing them before deploying.
)

echo [INFO] Running tests...
npm run test
if %errorlevel% neq 0 (
    echo [ERROR] Tests failed. Please fix the failing tests before deploying.
    pause
    exit /b 1
)

echo [INFO] Building the project...
npm run build
if %errorlevel% neq 0 (
    echo [ERROR] Build failed. Please fix the build errors before deploying.
    pause
    exit /b 1
)

echo [SUCCESS] All pre-deployment checks passed!
echo.

REM Setup Git repository
echo [INFO] Setting up Git repository...

if not exist ".git" (
    git init
    echo [SUCCESS] Git repository initialized!
)

REM Add all files
git add .

REM Commit changes
git status --porcelain >nul 2>nul
if %errorlevel% equ 0 (
    echo [WARNING] No changes to commit.
) else (
    set /p commit_message="Please enter a commit message (or press Enter for default): "
    if "%commit_message%"=="" (
        set commit_message=feat: complete Vocelio AI Call Center implementation - production ready
    )
    git commit -m "%commit_message%"
    echo [SUCCESS] Changes committed!
)

REM Push to GitHub
echo [INFO] Pushing to GitHub...

git remote get-url origin >nul 2>nul
if %errorlevel% neq 0 (
    set /p repo_url="Please enter your GitHub repository URL: "
    git remote add origin "!repo_url!"
)

git push -u origin main
if %errorlevel% equ 0 (
    echo [SUCCESS] Successfully pushed to GitHub!
) else (
    echo [ERROR] Failed to push to GitHub. Please check your repository URL and permissions.
    pause
    exit /b 1
)

echo.

REM Deploy to Railway
echo [INFO] Deploying to Railway...

where railway >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] Railway CLI not found. Please install it first:
    echo npm install -g @railway/cli
    set /p continue_without_railway="Do you want to continue without Railway deployment? (y/n): "
    if /i not "!continue_without_railway!"=="y" (
        exit /b 1
    )
    goto skip_railway
)

REM Check if logged in to Railway
railway whoami >nul 2>nul
if %errorlevel% neq 0 (
    echo [INFO] Please login to Railway...
    railway login
)

REM Link to Railway project or create new one
if not exist ".railway\project.json" (
    set /p project_choice="Do you want to (1) link to existing project or (2) create new project? Enter 1 or 2: "
    if "!project_choice!"=="1" (
        railway link
    ) else (
        railway create vocelio-ai-call-center
    )
)

REM Deploy to Railway
echo [INFO] Deploying to Railway...
railway up
if %errorlevel% equ 0 (
    echo [SUCCESS] Successfully deployed to Railway!
    railway status
) else (
    echo [ERROR] Railway deployment failed.
    pause
    exit /b 1
)

:skip_railway

echo.
echo [SUCCESS] 🎉 Deployment completed successfully!
echo.
echo 📋 Post-deployment checklist:
echo 1. Configure environment variables in Railway dashboard
echo 2. Run database migrations in Supabase:
echo    - Execute SUPABASE_COMPLETE_SCHEMA.sql
echo    - Execute SUPABASE_LOGIC_FUNCTIONS.sql
echo 3. Test your deployment endpoints
echo 4. Configure custom domain (optional)
echo 5. Set up monitoring and alerts
echo.
echo 📚 Documentation:
echo - Deployment Guide: deployment\railway\DEPLOYMENT_GUIDE.md
echo - Environment Variables: deployment\railway\.env.production.template
echo - Deployment Checklist: deployment\railway\DEPLOYMENT_CHECKLIST.md
echo.
echo [SUCCESS] Your Vocelio AI Call Center is now live! 🚀

pause
