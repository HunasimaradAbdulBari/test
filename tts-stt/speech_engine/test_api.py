import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    print("\n" + "="*60)
    print("Testing Health Endpoint")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_tts():
    print("\n" + "="*60)
    print("Testing TTS Endpoint")
    print("="*60)
    try:
        data = {
            "text": "Hello world, this is a test",
            "language": "en"
        }
        
        print(f"Sending request to: {BASE_URL}/api/v1/tts")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/api/v1/tts",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            audio_url = response.json().get("audio_url")
            print(f"\n✅ Success! Audio URL: {audio_url}")
            
            # Try to download the audio file
            audio_response = requests.get(audio_url)
            if audio_response.status_code == 200:
                print(f"✅ Audio file accessible! Size: {len(audio_response.content)} bytes")
            else:
                print(f"⚠️ Could not access audio file")
                
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_root():
    print("\n" + "="*60)
    print("Testing Root Endpoint")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("\n🧪 Starting API Tests...")
    print("="*60)
    
    # Test 1: Root
    root_ok = test_root()
    
    # Test 2: Health
    health_ok = test_health()
    
    # Test 3: TTS
    tts_ok = test_tts()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"Root Endpoint:   {'✅ PASS' if root_ok else '❌ FAIL'}")
    print(f"Health Endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"TTS Endpoint:    {'✅ PASS' if tts_ok else '❌ FAIL'}")
    print("="*60)
    
    if all([root_ok, health_ok, tts_ok]):
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Some tests failed. Check the output above.")