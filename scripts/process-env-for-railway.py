#!/usr/bin/env python3
"""
Railway Environment Variable Processor
Automatically processes .env file for Railway deployment
"""

import os
import re
from pathlib import Path

def process_env_for_railway(input_file=".env", output_file=".env.railway.deploy"):
    """
    Process .env file for Railway deployment:
    1. Remove sensitive production keys
    2. Keep placeholder values for Railway environment variables
    3. Generate Railway-ready environment file
    """
    
    # Sensitive keys that should be replaced with Railway environment variables
    sensitive_keys = {
        'OPENAI_API_KEY': 'your_openai_api_key_here',
        'ELEVENLABS_API_KEY': 'your_elevenlabs_api_key_here',
        'RAMBLE_API_KEY': 'your_ramble_api_key_here',
        'TWILIO_ACCOUNT_SID': 'your_twilio_account_sid_here',
        'TWILIO_AUTH_TOKEN': 'your_twilio_auth_token_here',
        'STRIPE_SECRET_KEY': 'your_stripe_secret_key_here',
        'STRIPE_WEBHOOK_SECRET': 'your_stripe_webhook_secret_here',
        'STRIPE_PUBLISHABLE_KEY': 'your_stripe_publishable_key_here',
        'SUPABASE_KEY': 'your_supabase_anon_key_here',
        'JWT_SECRET_KEY': 'your_jwt_secret_key_here'
    }
    
    # Railway-specific replacements
    railway_replacements = {
        'DATABASE_URL': 'postgresql://${{PGUSER}}:${{PGPASSWORD}}@${{PGHOST}}:${{PGPORT}}/${{PGDATABASE}}',
        'REDIS_URL': '${{REDIS_URL}}',
        'ENVIRONMENT': 'production',
        'DEBUG': 'false',
        'CORS_ORIGINS': 'https://your-frontend-domain.com',
        'NODE_ENV': 'production'
    }
    
    print(f"🔄 Processing {input_file} for Railway deployment...")
    
    if not Path(input_file).exists():
        print(f"❌ {input_file} not found!")
        return False
    
    processed_lines = []
    
    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                processed_lines.append(line)
                continue
            
            # Parse key=value
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                
                # Replace sensitive keys with placeholders
                if key in sensitive_keys:
                    processed_lines.append(f"{key}={sensitive_keys[key]}")
                # Apply Railway-specific replacements
                elif key in railway_replacements:
                    processed_lines.append(f"{key}={railway_replacements[key]}")
                else:
                    processed_lines.append(line)
            else:
                processed_lines.append(line)
    
    # Write processed file
    with open(output_file, 'w') as f:
        f.write('\n'.join(processed_lines))
    
    print(f"✅ Railway environment file created: {output_file}")
    print(f"📋 You can now upload this file to Railway using:")
    print(f"   railway variables set --from-env-file {output_file}")
    
    return True

def create_railway_upload_instructions():
    """Create instructions for uploading to Railway"""
    instructions = """
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
"""
    
    with open("RAILWAY_ENV_UPLOAD.md", "w") as f:
        f.write(instructions)
    
    print("📖 Created RAILWAY_ENV_UPLOAD.md with detailed instructions")

if __name__ == "__main__":
    success = process_env_for_railway()
    if success:
        create_railway_upload_instructions()
        print("\n🎯 Next steps:")
        print("1. Review .env.railway.deploy file")
        print("2. Run: railway variables set --from-env-file .env.railway.deploy")
        print("3. Add your real API keys in Railway dashboard")
        print("4. Deploy your services!")
