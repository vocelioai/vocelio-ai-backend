#!/usr/bin/env python3
"""
Quick test for Railway deployment URL
"""

import requests
import time

def test_railway_url():
    """Test the Railway deployment URL"""
    url = "https://vocelio-api-gateway-production.up.railway.app"
    
    print(f"🔍 Testing: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ JSON Response: {data}")
            except:
                text = response.text[:200]
                print(f"✅ Text Response: {text}...")
        
        # Test health endpoint
        health_url = f"{url}/health"
        print(f"\n🏥 Testing health endpoint: {health_url}")
        health_response = requests.get(health_url, timeout=10)
        print(f"📊 Health Status: {health_response.status_code}")
        
        if health_response.status_code == 200:
            try:
                health_data = health_response.json()
                print(f"✅ Health Response: {health_data}")
            except:
                print(f"✅ Health Text: {health_response.text[:100]}...")
        
        # Test docs endpoint
        docs_url = f"{url}/docs"
        print(f"\n📚 Testing docs endpoint: {docs_url}")
        docs_response = requests.get(docs_url, timeout=10)
        print(f"📊 Docs Status: {docs_response.status_code}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Railway Deployment Test")
    print("=" * 40)
    test_railway_url()
    print("\n💡 Waiting for deployment to complete...")
    print("Railway should rebuild and redeploy in 1-2 minutes")
