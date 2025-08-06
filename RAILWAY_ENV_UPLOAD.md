
# Railway Environment Variable Upload Instructions

## Option 1: Using Railway CLI (Recommended)
1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Link your project: `railway link`
4. Upload variables: `railway variables set --from-env-file .env.railway.deploy`

## Option 2: Manual Upload
1. Go to https://railway.app/dashboard
2. Select your project
3. Go to Variables tab
4. Copy variables from .env.railway.deploy

## Option 3: Programmatic Upload
Use the generated PowerShell script: ./scripts/deploy-env-railway.ps1

## Important Notes:
- Replace placeholder values with your actual API keys in Railway dashboard
- Database URL will be automatically provided by Railway's PostgreSQL service
- Redis URL will be automatically provided by Railway's Redis service
