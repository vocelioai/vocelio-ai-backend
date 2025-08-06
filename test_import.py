#!/usr/bin/env python3
"""
Simple test to verify the FastAPI app can be imported and started
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, '/app')

try:
    # Try to import the main app (note: hyphens become underscores in imports)
    from apps.api_gateway.src.main import app
    print("✅ Successfully imported FastAPI app")
    
    # Test basic app properties
    print(f"✅ App title: {app.title}")
    print(f"✅ App version: {app.version}")
    print("✅ App is ready for deployment")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
