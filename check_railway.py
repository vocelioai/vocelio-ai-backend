import requests
import time
import sys

def check_deployment():
    """Check Railway deployment status and logs"""
    url = "https://vocelio-api-gateway-production.up.railway.app"
    
    print("🔍 Checking Railway deployment...")
    print(f"URL: {url}")
    
    # Test root endpoint
    try:
        response = requests.get(url, timeout=10)
        print(f"Root endpoint status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.text[:200]}...")
        else:
            print(f"Error response: {response.text[:200]}...")
    except Exception as e:
        print(f"Root endpoint error: {e}")
    
    # Test health endpoint
    try:
        health_response = requests.get(f"{url}/health", timeout=10)
        print(f"Health endpoint status: {health_response.status_code}")
        if health_response.status_code == 200:
            print(f"Health response: {health_response.json()}")
        else:
            print(f"Health error: {health_response.text[:200]}...")
    except Exception as e:
        print(f"Health endpoint error: {e}")
    
    # Test docs
    try:
        docs_response = requests.get(f"{url}/docs", timeout=10)
        print(f"Docs endpoint status: {docs_response.status_code}")
    except Exception as e:
        print(f"Docs endpoint error: {e}")

if __name__ == "__main__":
    check_deployment()
