#!/usr/bin/env python3
"""
Extended Railway URL Pattern Tester
Tests more comprehensive Railway URL patterns
"""

import requests
import sys
import time
from urllib.parse import urljoin

def test_endpoint(url, endpoint="/", timeout=5):
    """Test a specific endpoint on a URL"""
    try:
        full_url = urljoin(url, endpoint)
        print(f"Testing: {full_url}")
        
        response = requests.get(full_url, timeout=timeout)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Response: {data}")
                return True, data
            except:
                text = response.text[:200]
                print(f"✅ Response: {text}...")
                return True, text
        elif response.status_code == 404:
            print("❌ 404 - Service not found")
            return False, None
        else:
            print(f"⚠️  {response.status_code}")
            return False, None
            
    except requests.exceptions.Timeout:
        print(f"⏱️  Timeout")
        return False, None
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error")
        return False, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

def test_comprehensive_patterns():
    """Test comprehensive Railway URL patterns"""
    base_names = [
        "vocelio-backend",
        "vocelio-ai-backend", 
        "vocelio",
        "backend",
        "vocelio-ai",
        "vocelio-app",
        "vocelio-api"
    ]
    
    environments = [
        "production",
        "main", 
        "master",
        ""  # No environment suffix
    ]
    
    domains = [
        "up.railway.app",
        "railway.app"
    ]
    
    all_urls = []
    
    # Generate all combinations
    for base in base_names:
        for env in environments:
            for domain in domains:
                if env:
                    url = f"https://{base}-{env}.{domain}"
                else:
                    url = f"https://{base}.{domain}"
                all_urls.append(url)
    
    print(f"🔍 Testing {len(all_urls)} Railway URL patterns...")
    print("=" * 60)
    
    for i, url in enumerate(all_urls, 1):
        print(f"\n📡 {i}/{len(all_urls)}: {url}")
        print("-" * 40)
        
        success, data = test_endpoint(url, "/", timeout=3)
        if success:
            print(f"🎉 FOUND DEPLOYMENT: {url}")
            # Test health endpoint
            test_endpoint(url, "/health", timeout=3)
            return url
    
    return None

if __name__ == "__main__":
    print("🚀 Extended Railway URL Pattern Tester")
    print("=" * 50)
    
    found_url = test_comprehensive_patterns()
    
    if found_url:
        print(f"\n✅ Deployment found at: {found_url}")
    else:
        print("\n❌ No deployment found in comprehensive patterns")
        print("\n💡 Next steps:")
        print("1. Check your Railway dashboard for the exact URL")
        print("2. Look for any custom domains you may have set")
        print("3. Verify the deployment is actually running")
