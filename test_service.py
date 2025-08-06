#!/usr/bin/env python3
"""
Test specific Railway service patterns
"""

import requests

def test_service_patterns():
    """Test Railway service-specific patterns"""
    # Railway often uses random service IDs
    test_patterns = [
        "https://vocelio-backend-production.up.railway.app",
        "https://web-production-drams3a.up.railway.app",  # Based on the context ID from build
        "https://production-drams3a.up.railway.app",
        "https://drams3a.up.railway.app",
        "https://api-gateway-production.up.railway.app"
    ]
    
    print("🔍 Testing Railway service-specific patterns...")
    print("=" * 50)
    
    for url in test_patterns:
        try:
            print(f"\n📡 Testing: {url}")
            response = requests.get(url, timeout=5)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ JSON Response: {data}")
                    if "Vocelio" in str(data) or "Simple Server" in str(data):
                        return url
                except:
                    text = response.text[:100]
                    print(f"✅ Text Response: {text}...")
                    if "Vocelio" in text or "Simple HTTP server" in text:
                        return url
            elif response.status_code == 404:
                print("❌ 404 - Not found")
            else:
                print(f"⚠️  {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    found = test_service_patterns()
    if found:
        print(f"\n🎉 Found actual service at: {found}")
    else:
        print("\n❌ Could not find the actual service URL")
        print("The deployment exists but may need proper domain configuration")
