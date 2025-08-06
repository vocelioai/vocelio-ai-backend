#!/usr/bin/env python3
"""
Railway Deployment Tester
Tests common Railway URL patterns for your Vocelio deployment
"""

import requests
import sys
import time
from urllib.parse import urljoin

def test_endpoint(url, endpoint="/", timeout=10):
    """Test a specific endpoint on a URL"""
    try:
        full_url = urljoin(url, endpoint)
        print(f"Testing: {full_url}")
        
        response = requests.get(full_url, timeout=timeout)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response: {data}")
                return True, data
            except:
                text = response.text[:200]
                print(f"Response: {text}...")
                return True, text
        elif response.status_code == 404:
            print("❌ 404 - Service not found or not ready")
            return False, None
        elif response.status_code >= 500:
            print(f"❌ {response.status_code} - Server error, deployment may be starting")
            return False, None
        else:
            print(f"⚠️  {response.status_code} - {response.text[:100]}")
            return False, None
            
    except requests.exceptions.Timeout:
        print(f"⏱️  Timeout after {timeout}s - deployment may be starting")
        return False, None
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error - deployment not ready")
        return False, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

def monitor_deployment(url, max_attempts=20, delay=15):
    """Monitor deployment status with retries"""
    print(f"� Monitoring deployment at: {url}")
    print(f"Will check every {delay} seconds for up to {max_attempts} attempts")
    print("=" * 50)
    
    for attempt in range(1, max_attempts + 1):
        print(f"\n📡 Attempt {attempt}/{max_attempts}")
        print("-" * 30)
        
        # Test root endpoint
        success, data = test_endpoint(url, "/")
        if success:
            print("✅ Root endpoint accessible!")
            
            # Test health endpoint
            health_success, health_data = test_endpoint(url, "/health")
            if health_success:
                print("✅ Health endpoint accessible!")
                print(f"🎉 DEPLOYMENT SUCCESSFUL: {url}")
                return True
        
        if attempt < max_attempts:
            print(f"⏳ Waiting {delay} seconds before next attempt...")
            time.sleep(delay)
    
    print(f"\n❌ Deployment not accessible after {max_attempts} attempts")
    return False

def test_common_patterns():
    """Test common Railway URL patterns"""
    # Common Railway URL patterns
    possible_urls = [
        "https://vocelio-backend-production.up.railway.app",
        "https://vocelio-ai-backend-production.up.railway.app", 
        "https://vocelio-production.up.railway.app",
        "https://backend-production.up.railway.app",
        "https://vocelio-backend.up.railway.app",
        "https://vocelio-ai.up.railway.app"
    ]
    
    print("🔍 Testing common Railway URL patterns...")
    print("=" * 50)
    
    for url in possible_urls:
        print(f"\n📡 Testing: {url}")
        print("-" * 30)
        
        success, data = test_endpoint(url, "/", timeout=5)
        if success:
            return url
        
        print("❌ Not accessible")
    
    return None

if __name__ == "__main__":
    print("🚀 Vocelio Railway Deployment Tester")
    print("=" * 40)
    
    # If URL provided as argument, test it
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
        
        if "--monitor" in sys.argv:
            monitor_deployment(test_url)
        else:
            print(f"Testing provided URL: {test_url}")
            success, data = test_endpoint(test_url, "/")
            if success:
                test_endpoint(test_url, "/health")
    else:
        # Test common patterns
        found_url = test_common_patterns()
        
        if found_url:
            print(f"\n✅ Deployment accessible at: {found_url}")
        else:
            print("\n📋 To test a specific URL, run:")
            print("python test_deployment.py https://your-railway-url.railway.app")
            print("\n📋 To monitor a deployment, run:")
            print("python test_deployment.py https://your-railway-url.railway.app --monitor")
