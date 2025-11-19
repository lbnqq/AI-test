#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
import time
import threading
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

# Add the services directory to the Python path
services_dir = os.path.join(os.path.dirname(__file__), 'services')
sys.path.insert(0, services_dir)

def timeout_handler():
    print("TIMEOUT: Test is taking too long!")
    import traceback
    traceback.print_stack()

def debug_test():
    print("Starting debug test...")
    
    # Set timeout alarm
    timer = threading.Timer(120.0, timeout_handler)
    timer.start()
    
    try:
        # Load test data
        test_file = "test_files/agent-big-five-50-complete2.json"
        print(f"Loading test data from: {test_file}")
        
        with open(test_file, 'r', encoding='utf-8') as f:
            test_data = json.load(f)
        
        print(f"Test data loaded successfully. Number of questions: {len(test_data.get('test_bank', []))}")
        
        # Initialize LLM client
        print("Initializing LLM client...")
        from services.llm_client import LLMClient
        client = LLMClient()
        print("LLM client initialized successfully.")
        
        # Test first question only
        question = test_data['test_bank'][0]
        print(f"\nProcessing first question")
        print(f"Question ID: {question.get('question_id', '0')}")
        
        # Prepare prompt
        prompt_content = f"Scenario: {question.get('scenario', '')}\n\nQuestion: {question.get('prompt_for_agent', '')}"
        print(f"Prompt length: {len(prompt_content)} characters")
        prompt = [{"role": "user", "content": prompt_content}]
        
        # Generate response with short timeout
        print("Generating response with 30s timeout...")
        start_time = time.time()
        try:
            response = client.generate_response(prompt, "qwen2.5-coder:14b", timeout=30)
            elapsed_time = time.time() - start_time
            print(f"Response received in {elapsed_time:.2f}s")
            print(f"Response length: {len(response) if response else 0} characters")
            print(f"Response preview: {response[:100] if response else 'No response'}...")
            
            # Save simple result
            output_file = f"results/debug_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs('results', exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'test_metadata': {
                        'model': 'qwen2.5-coder:14b',
                        'timestamp': datetime.now().isoformat(),
                        'question_id': question.get('question_id', '0'),
                        'elapsed_time': elapsed_time
                    },
                    'response': response
                }, f, ensure_ascii=False, indent=2)
            
            print(f"Test result saved to: {output_file}")
            
        except Exception as e:
            print(f"Error generating response: {e}")
            import traceback
            traceback.print_exc()
    finally:
        timer.cancel()

if __name__ == "__main__":
    debug_test()