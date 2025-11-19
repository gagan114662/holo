#!/usr/bin/env python3
"""
Simple test to check if configuration is working
"""

import os
from dotenv import load_dotenv
from config_manager import ConfigManager

def main():
    print("🔧 Testing Configuration")
    print("=" * 40)
    
    # Load environment
    load_dotenv()
    
    # Check if API key is loaded
    api_key = os.getenv("OPENROUTER_API_KEY")
    print(f"API Key loaded: {'✅ Yes' if api_key else '❌ No'}")
    if api_key:
        print(f"API Key starts with: {api_key[:15]}...")
    
    # Test config manager
    try:
        config_manager = ConfigManager()
        api_key_from_config = config_manager.get_api_key("openrouter")
        print(f"Config Manager API Key: {'✅ Yes' if api_key_from_config else '❌ No'}")
        
        llm_config = config_manager.get_llm_config("question_generator")
        print(f"LLM Config: {llm_config}")
        
        endpoint = config_manager.get_api_endpoint("openrouter")
        print(f"API Endpoint: {endpoint}")
        
    except Exception as e:
        print(f"❌ Config Manager Error: {e}")

if __name__ == "__main__":
    main()