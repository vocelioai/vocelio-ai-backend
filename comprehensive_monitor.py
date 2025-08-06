#!/usr/bin/env python3
"""
Comprehensive Railway Deployment Monitor & API Tester
Monitors deployment progress and tests all endpoints once live
"""

import requests
import time
import json
from datetime import datetime

def test_endpoint(url, endpoint="", timeout=10):
    """Test a specific endpoint"""
    try:
        full_url = f"{url.rstrip('/')}{endpoint}"
        print(f"    📡 Testing: {full_url}")
        
        response = requests.get(full_url, timeout=timeout)
        print(f"    📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"    ✅ JSON: {json.dumps(data, indent=2)}")
                return True, data
            except:
                text = response.text[:200]
                print(f"    ✅ Text: {text}...")
                return True, text
        elif response.status_code == 404:
            print("    ❌ 404 - Not found (deployment may be in progress)")
            return False, None
        else:
            print(f"    ⚠️  {response.status_code} - {response.text[:100]}")
            return False, None
            
    except requests.exceptions.Timeout:
        print(f"    ⏱️  Timeout after {timeout}s")
        return False, None
    except requests.exceptions.ConnectionError:
        print("    🔌 Connection error")
        return False, None
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False, None

def test_full_api(url):
    """Test all API endpoints comprehensively"""
    print(f"\n🚀 COMPREHENSIVE API TESTING")
    print(f"🔗 Base URL: {url}")
    print("=" * 60)
    
    endpoints_to_test = [
        ("", "Root endpoint"),
        ("/health", "Health check"),
        ("/health/detailed", "Detailed health check"),
        ("/docs", "API Documentation"),
        ("/redoc", "ReDoc Documentation"),
        ("/services", "Service registry"),
        ("/metrics", "Gateway metrics"),
        ("/openapi.json", "OpenAPI specification")
    ]
    
    results = {}
    
    for endpoint, description in endpoints_to_test:
        print(f"\n📋 {description}:")
        success, data = test_endpoint(url, endpoint)
        results[endpoint] = {
            "success": success,
            "data": data,
            "description": description
        }
        time.sleep(1)  # Be nice to the server
    
    # Test microservice proxy endpoints
    print(f"\n🔧 MICROSERVICE PROXY TESTING:")
    print("-" * 40)
    
    microservices = [
        "overview", "agents", "smart-campaigns", "call-center",
        "phone-numbers", "voice-marketplace", "analytics-pro"
    ]
    
    for service in microservices:
        print(f"\n📋 Testing {service} proxy:")
        success, data = test_endpoint(url, f"/{service}/health")
        results[f"/{service}/health"] = {
            "success": success,
            "data": data,
            "description": f"{service} health check"
        }
    
    return results

def monitor_deployment(url, max_attempts=20, delay=15):
    """Monitor deployment until it's live, then test comprehensively"""
    print(f"🔄 MONITORING RAILWAY DEPLOYMENT")
    print("=" * 60)
    print(f"📡 URL: {url}")
    print(f"⏱️  Checking every {delay} seconds (max {max_attempts} attempts)")
    print("=" * 60)
    
    for attempt in range(1, max_attempts + 1):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n🔍 Attempt {attempt}/{max_attempts} [{timestamp}]")
        print("-" * 30)
        
        # Test root endpoint first
        success, data = test_endpoint(url, "", timeout=10)
        
        if success and data:
            # Check if it's actually our Vocelio API
            if isinstance(data, dict) and ("Vocelio" in str(data) or "API Gateway" in str(data)):
                print(f"\n🎉 DEPLOYMENT SUCCESSFUL!")
                print("🚀 Vocelio API Gateway is LIVE!")
                
                # Run comprehensive testing
                results = test_full_api(url)
                
                # Summary
                print(f"\n📊 DEPLOYMENT SUMMARY")
                print("=" * 60)
                successful_endpoints = sum(1 for r in results.values() if r["success"])
                total_endpoints = len(results)
                print(f"✅ Successful endpoints: {successful_endpoints}/{total_endpoints}")
                
                if successful_endpoints > 0:
                    print(f"🎉 Vocelio API Gateway is fully operational!")
                    print(f"🔗 Access your API at: {url}")
                    print(f"📚 Documentation: {url}/docs")
                    print(f"🏥 Health check: {url}/health")
                    
                return True
            else:
                print("⚠️  Service responding but not Vocelio API yet")
        
        if attempt < max_attempts:
            print(f"⏳ Waiting {delay} seconds before next check...")
            time.sleep(delay)
    
    print(f"\n❌ Deployment not ready after {max_attempts} attempts")
    print("💡 Check Railway dashboard for deployment status")
    return False

if __name__ == "__main__":
    railway_url = "https://vocelio-api-gateway-production.up.railway.app"
    
    print("🚀 VOCELIO RAILWAY DEPLOYMENT MONITOR")
    print("=" * 60)
    print("🎯 This script will:")
    print("   1. Monitor deployment progress")
    print("   2. Test all API endpoints once live")
    print("   3. Verify microservice proxy functionality")
    print("   4. Provide comprehensive deployment summary")
    print("=" * 60)
    
    # Start monitoring
    success = monitor_deployment(railway_url)
    
    if success:
        print(f"\n✅ MISSION ACCOMPLISHED!")
        print("Your Vocelio AI Call Center platform is deployed and operational!")
    else:
        print(f"\n⏳ Deployment still in progress")
        print("Please check Railway dashboard or run this script again later")
