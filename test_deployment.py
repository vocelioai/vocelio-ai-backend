#!/usr/bin/env python3
"""
Railway Deployment Tester
Tests common Railway URL patterns for your Vocelio deployment
"""

import requests
import sys
from urllib.parse import urljoin

def test_endpoint(url, endpoint="/"):
    """Test a specific endpoint on a URL"""
    try:
        full_url = urljoin(url, endpoint)
        print(f"Testing: {full_url}")
        
        response = requests.get(full_url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response: {data}")
                return True
            except:
                print(f"Response: {response.text[:200]}...")
                return True
        else:
            print(f"Error: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_common_patterns():
    """Test common Railway URL patterns"""
    # You'll need to replace these with your actual Railway project info
    possible_urls = [
        "https://vocelio-backend-production.up.railway.app",
        "https://vocelio-ai-backend-production.up.railway.app", 
        "https://vocelio-production.up.railway.app",
        "https://backend-production.up.railway.app"
    ]
    
    print("🔍 Testing common Railway URL patterns...")
    print("=" * 50)
    
    for url in possible_urls:
        print(f"\n📡 Testing: {url}")
        print("-" * 30)
        
        # Test root endpoint
        if test_endpoint(url, "/"):
            print("✅ Root endpoint accessible")
            
            # Test health endpoint
            if test_endpoint(url, "/health"):
                print("✅ Health endpoint accessible")
                print(f"🎉 DEPLOYMENT FOUND: {url}")
                return url
        
        print("❌ Not accessible")
    
    print("\n⚠️  Could not find deployment at common URLs")
    print("Please check your Railway dashboard for the correct URL")
    return None

if __name__ == "__main__":
    print("🚀 Vocelio Railway Deployment Tester")
    print("=" * 40)
    
    # If URL provided as argument, test it
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
        print(f"Testing provided URL: {test_url}")
        
        if test_endpoint(test_url, "/"):
            test_endpoint(test_url, "/health")
    else:
        # Test common patterns
        found_url = test_common_patterns()
        
        if found_url:
            print(f"\n✅ Deployment accessible at: {found_url}")
        else:
            print("\n📋 To test a specific URL, run:")
            print("python test_deployment.py https://your-railway-url.railway.app")
