import requests
import json

def test_correct_domain():
    """Test the correct Railway domain"""
    correct_url = "https://vocelio-ai-backend-production.up.railway.app"
    
    print(f"🔍 Testing CORRECT Railway domain:")
    print(f"URL: {correct_url}")
    print("=" * 60)
    
    endpoints = [
        ("Root", ""),
        ("Health", "/health"),
        ("Ping", "/ping"),
        ("Test", "/test"),
        ("Docs", "/docs")
    ]
    
    for name, endpoint in endpoints:
        full_url = f"{correct_url}{endpoint}"
        try:
            print(f"🔍 Testing {name}: {full_url}")
            response = requests.get(full_url, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ Status: {response.status_code} - SUCCESS!")
                try:
                    data = response.json()
                    print(f"   📄 Response: {json.dumps(data, indent=2)}")
                except:
                    print(f"   📄 Response: {response.text[:200]}...")
            else:
                print(f"   ❌ Status: {response.status_code} - FAILED")
                print(f"   📄 Error: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()

if __name__ == "__main__":
    test_correct_domain()
