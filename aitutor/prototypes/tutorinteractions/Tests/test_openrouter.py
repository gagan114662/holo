"""
Test script to verify OpenRouter API connection
"""

import sys
import os

# Add parent directory to path and change to parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
os.chdir(parent_dir)  # Change to parent directory so .env is found

from config_manager import ConfigManager
from LLMBase.llm_client import OpenRouterClient

def test_config():
    """Test configuration loading"""
    print("🔧 Testing Configuration...")
    
    # Debug: Check current directory and .env file
    print(f"🔍 Current directory: {os.getcwd()}")
    env_path = os.path.join(os.getcwd(), '.env')
    print(f"🔍 Looking for .env at: {env_path}")
    print(f"🔍 .env file exists: {os.path.exists(env_path)}")
    
    try:
        config_manager = ConfigManager()
        api_key = config_manager.get_api_key("openrouter")
        
        # Debug: Show what we actually got
        print(f"🔍 Debug - API key value: '{api_key}'")
        print(f"🔍 Debug - API key length: {len(api_key) if api_key else 0}")
        
        if not api_key:
            print("❌ No OpenRouter API key found in .env file")
            return False
        
        if api_key == "your_openrouter_api_key_here":
            print("❌ OpenRouter API key is still placeholder value")
            return False
        
        if not api_key.startswith("sk-or-v1-"):
            print("❌ OpenRouter API key format seems incorrect (should start with 'sk-or-v1-')")
            return False
        
        print(f"✅ API key found: {api_key[:15]}...")
        
        # Test config loading
        llm_config = config_manager.get_llm_config("question_generator")
        print(f"✅ LLM Config: {llm_config['model']}")
        
        endpoint = config_manager.get_api_endpoint("openrouter")
        print(f"✅ Endpoint: {endpoint}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_api_connection():
    """Test actual API connection"""
    print("\n🌐 Testing OpenRouter API Connection...")
    
    try:
        client = OpenRouterClient()
        
        # Simple test prompt
        test_prompt = "Say 'Hello, this is a test!' and nothing else."
        
        print("📡 Sending test request...")
        response = client.generate(test_prompt, "question_generator")
        
        print(f"✅ API Response: {response[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ API Connection failed: {e}")
        return False

def main():
    print("🧪 Testing OpenRouter API Setup")
    print("=" * 50)
    
    # Test configuration
    config_ok = test_config()
    
    if not config_ok:
        print("\n💡 To fix configuration issues:")
        print("   1. Check that .env file exists")
        print("   2. Get API key from https://openrouter.ai/keys")
        print("   3. Set OPENROUTER_API_KEY=sk-or-v1-... in .env file")
        return False
    
    # Test API connection
    api_ok = test_api_connection()
    
    if not api_ok:
        print("\n💡 API connection failed. This could be:")
        print("   1. Invalid API key")
        print("   2. Network connectivity issues")
        print("   3. OpenRouter service issues")
        return False
    
    print("\n🎉 All tests passed! OpenRouter API is working correctly.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)