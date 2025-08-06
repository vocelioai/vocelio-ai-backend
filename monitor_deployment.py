#!/usr/bin/env python3
"""
Railway Deployment Monitor
Monitors Railway deployment until service is exposed
"""

import requests
import time
import sys

def monitor_railway_deployment(max_attempts=30, delay=20):
    """Monitor Railway deployment with comprehensive URL testing"""
    
    # Potential Railway URLs to test
    test_urls = [
        "https://vocelio-backend-production.up.railway.app",
        "https://vocelio-api-gateway-production.up.railway.app",
        "https://web-production-drams3a.up.railway.app",
        "https://api-gateway-production.up.railway.app"
    ]
    
    print("🚀 Railway Deployment Monitor")
    print("=" * 50)
    print(f"⏱️  Will check every {delay} seconds for up to {max_attempts} attempts")
    print(f"📡 Testing {len(test_urls)} potential URLs")
    print("=" * 50)
    
    for attempt in range(1, max_attempts + 1):
        print(f"\n🔄 Attempt {attempt}/{max_attempts}")
        print("-" * 30)
        
        for url in test_urls:
            try:
                print(f"📡 Testing: {url}")
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if "Vocelio" in str(data) and "running" in str(data):
                            print(f"✅ Status: {response.status_code}")
                            print(f"✅ Response: {data}")
                            print(f"\n🎉 SUCCESS! Vocelio deployed at: {url}")
                            
                            # Test health endpoint
                            health_url = f"{url}/health"
                            try:
                                health_response = requests.get(health_url, timeout=5)
                                if health_response.status_code == 200:
                                    health_data = health_response.json()
                                    print(f"✅ Health check: {health_data}")
                                else:
                                    print(f"⚠️  Health check returned: {health_response.status_code}")
                            except:
                                print("⚠️  Health check failed")
                            
                            return url
                        else:
                            print(f"⚠️  Status: {response.status_code} - Not Vocelio service")
                    except:
                        text = response.text[:100]
                        if "Railway API" in text:
                            print("⚠️  Status: 200 - Railway API (not deployed service)")
                        else:
                            print(f"⚠️  Status: 200 - Unknown service: {text}...")
                            
                elif response.status_code == 404:
                    print("❌ Status: 404 - Service not found")
                elif response.status_code >= 500:
                    print(f"⚠️  Status: {response.status_code} - Server error (may be starting)")
                else:
                    print(f"⚠️  Status: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                print("⏱️  Timeout - Service may be starting")
            except requests.exceptions.ConnectionError:
                print("🔌 Connection error - Service not ready")
            except Exception as e:
                print(f"❌ Error: {str(e)[:50]}...")
        
        if attempt < max_attempts:
            print(f"\n⏳ Waiting {delay} seconds before next check...")
            time.sleep(delay)
    
    print(f"\n❌ Service not accessible after {max_attempts} attempts")
    print("💡 Check Railway dashboard for deployment status and logs")
    return None

if __name__ == "__main__":
    print("Starting Railway deployment monitoring...")
    found_url = monitor_railway_deployment()
    
    if found_url:
        print(f"\n🎉 Deployment successful!")
        print(f"🔗 Your Vocelio API is live at: {found_url}")
        print(f"🏥 Health check: {found_url}/health")
    else:
        print(f"\n❌ Deployment monitoring completed without finding active service")
        print("📋 Next steps:")
        print("1. Check Railway dashboard for logs")
        print("2. Verify health check endpoints are working")
        print("3. Check if domain generation is in progress")
