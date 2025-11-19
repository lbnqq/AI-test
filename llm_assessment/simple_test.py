#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
import time
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

# Add the services directory to the Python path
services_dir = os.path.join(os.path.dirname(__file__), 'services')
sys.path.insert(0, services_dir)

from services.llm_client import LLMClient

def simple_test():
    print("Starting simple big five test...")
    
    # Load test data
    test_file = "test_files/agent-big-five-50-complete2.json"
    print(f"Loading test data from: {test_file}")
    
    with open(test_file, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    print(f"Test data loaded successfully. Number of questions: {len(test_data.get('test_bank', []))}")
    
    # Initialize LLM client
    print("Initializing LLM client...")
    client = LLMClient()
    print("LLM client initialized successfully.")
    
    # Process first 3 questions only for testing
    results = []
    for i, question in enumerate(test_data['test_bank'][:3]):
        print(f"\nProcessing question {i+1}/3")
        print(f"Question ID: {question.get('question_id', i)}")
        print(f"Scenario: {question.get('scenario', '')[:100]}...")
        print(f"Prompt: {question.get('prompt_for_agent', '')[:100]}...")
        
        # Prepare prompt
        prompt = [{"role": "user", "content": f"Scenario: {question.get('scenario', '')}\n\nQuestion: {question.get('prompt_for_agent', '')}"}]
        
        # Generate response
        print("Generating response...")
        start_time = time.time()
        try:
            response = client.generate_response(prompt, "qwen2.5-coder:14b", timeout=120)
            elapsed_time = time.time() - start_time
            print(f"Response received in {elapsed_time:.2f}s")
            print(f"Response: {response[:200]}...")
            
            results.append({
                'question_id': question.get('question_id', i),
                'response': response,
                'elapsed_time': elapsed_time
            })
        except Exception as e:
            print(f"Error generating response: {e}")
            results.append({
                'question_id': question.get('question_id', i),
                'error': str(e),
                'elapsed_time': time.time() - start_time
            })
    
    # Save results
    output_file = f"results/simple_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs('results', exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'test_metadata': {
                'model': 'qwen2.5-coder:14b',
                'timestamp': datetime.now().isoformat(),
                'total_questions': len(results)
            },
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\nTest completed! Results saved to: {output_file}")
    print(f"Processed {len(results)} questions")

if __name__ == "__main__":
    simple_test()