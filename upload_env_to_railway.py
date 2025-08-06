#!/usr/bin/env python3
"""
Railway Environment Variables Uploader
Reads .env file and provides Railway CLI commands to set all variables
"""

import os
import re

def parse_env_file(file_path=".env"):
    """Parse .env file and extract environment variables"""
    env_vars = {}
    
    if not os.path.exists(file_path):
        print(f"❌ {file_path} not found!")
        return env_vars
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Parse KEY=VALUE format
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                env_vars[key] = value
    
    return env_vars

def generate_railway_commands(env_vars):
    """Generate Railway CLI commands to set environment variables"""
    print("🚀 Railway Environment Variables Setup")
    print("=" * 60)
    print(f"📊 Found {len(env_vars)} environment variables")
    print("=" * 60)
    
    # Critical production variables (need attention)
    critical_vars = [
        'DATABASE_URL', 'SUPABASE_URL', 'SUPABASE_KEY', 'REDIS_URL',
        'JWT_SECRET_KEY', 'OPENAI_API_KEY', 'ELEVENLABS_API_KEY',
        'TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 
        'STRIPE_SECRET_KEY', 'STRIPE_WEBHOOK_SECRET'
    ]
    
    print("\n🔴 CRITICAL VARIABLES (Review carefully for production):")
    print("-" * 50)
    
    for var in critical_vars:
        if var in env_vars:
            value = env_vars[var]
            # Mask sensitive values for display
            if len(value) > 10:
                masked_value = value[:4] + "..." + value[-4:]
            else:
                masked_value = "***"
            print(f"railway variables set {var}=\"{masked_value}\"")
    
    print("\n🟡 CONFIGURATION VARIABLES:")
    print("-" * 50)
    
    config_vars = [var for var in env_vars if var not in critical_vars]
    for var in sorted(config_vars):
        value = env_vars[var]
        print(f"railway variables set {var}=\"{value}\"")
    
    print("\n" + "=" * 60)
    print("📋 COPY AND PASTE COMMANDS:")
    print("=" * 60)
    print("Run these commands in your terminal (one by one):\n")
    
    # Generate actual commands
    for var, value in env_vars.items():
        # Escape special characters for shell
        escaped_value = value.replace('"', '\\"').replace('$', '\\$')
        print(f'railway variables set {var}="{escaped_value}"')
    
    print("\n" + "=" * 60)
    print("📋 BATCH UPLOAD SCRIPT:")
    print("=" * 60)
    print("Or save this as 'upload_env.py' and run it:\n")
    
    batch_script = '''#!/usr/bin/env python3
import subprocess
import sys

env_vars = {
'''
    
    for var, value in env_vars.items():
        # Escape Python string
        escaped_value = value.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")
        batch_script += f'    "{var}": "{escaped_value}",\n'
    
    batch_script += '''}

def upload_variables():
    """Upload all environment variables to Railway"""
    for var, value in env_vars.items():
        try:
            cmd = ["railway", "variables", "set", f"{var}={value}"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {var}: Set successfully")
            else:
                print(f"❌ {var}: {result.stderr.strip()}")
                
        except Exception as e:
            print(f"❌ {var}: Error - {e}")

if __name__ == "__main__":
    print("🚀 Uploading environment variables to Railway...")
    upload_variables()
    print("✅ Upload complete!")
'''
    
    print(batch_script)

def main():
    env_vars = parse_env_file()
    
    if not env_vars:
        print("❌ No environment variables found!")
        return
    
    generate_railway_commands(env_vars)
    
    print("\n💡 NEXT STEPS:")
    print("1. Review all variables, especially sensitive ones")
    print("2. Run the Railway CLI commands above")
    print("3. Verify with: railway variables")
    print("4. Deploy your application: git push")

if __name__ == "__main__":
    main()
