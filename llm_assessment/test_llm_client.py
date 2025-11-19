#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import time

# Add the project root to the Python path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

# Add the services directory to the Python path
services_dir = os.path.join(os.path.dirname(__file__), 'services')
sys.path.insert(0, services_dir)

def test_llm_client():
    print("Testing LLM Client...")
    
    try:
        from services.llm_client import LLMClient
        print("Imported LLMClient successfully")
    except Exception as e:
        print(f"Failed to import LLMClient: {e}")
        return
    
    # Initialize LLM client
    print("Initializing LLM client...")
    try:
        client = LLMClient()
        print("LLM client initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize LLMClient: {e}")
        return
    
    # Test simple prompt
    print("Testing simple prompt...")
    prompt = [{"role": "user", "content": "Hello, please respond with 'I am working'"}]
    
    start_time = time.time()
    try:
        response = client.generate_response(prompt, "qwen2.5-coder:14b", timeout=30)
        elapsed_time = time.time() - start_time
        print(f"Response received in {elapsed_time:.2f}s")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error generating response: {e}")
        print(f"Elapsed time before error: {time.time() - start_time:.2f}s")

if __name__ == "__main__":
    test_llm_client()