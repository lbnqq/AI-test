#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
import time
import requests
from datetime import datetime

def minimal_test():
    print("Starting Minimal Big Five Test (1 question)...")
    
    # Load test data
    test_file = "test_files/agent-big-five-50-complete2.json"
    print(f"Loading test data from: {test_file}")
    
    with open(test_file, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    print(f"Test data loaded successfully. Number of questions: {len(test_data.get('test_bank', []))}")
    
    # Process only first question
    question = test_data['test_bank'][0]
    print(f"\nProcessing first question")
    print(f"Question ID: {question.get('question_id', '0')}")
    print(f"Dimension: {question.get('dimension', '')}")
    
    # Prepare prompt
    prompt_content = f"Scenario: {question.get('scenario', '')}\n\nQuestion: {question.get('prompt_for_agent', '')}"
    print(f"Prompt length: {len(prompt_content)} characters")
    
    # Direct Ollama API call
    print("Calling Ollama API directly...")
    start_time = time.time()
    try:
        url = 'http://localhost:11434/api/generate'
        data = {
            'model': 'qwen2.5-coder:14b',
            'prompt': prompt_content,
            'stream': False
        }
        
        print(f"Sending request to {url}")
        print(f"Model: {data['model']}")
        print(f"Timeout: 900 seconds")
        
        response = requests.post(url, json=data, timeout=900)  # 15 minutes timeout
        elapsed_time = time.time() - start_time
        
        print(f"Response status: {response.status_code}")
        print(f"Response received in {elapsed_time:.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get('response', '')
            print(f"Response length: {len(response_text)} characters")
            print(f"Response preview: {response_text[:200]}...")
            
            # Save result
            output_file = f"results/minimal_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs('results', exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'test_metadata': {
                        'model': 'qwen2.5-coder:14b',
                        'test_name': 'Agent-IPIP-FFM-50 最小化测试',
                        'timestamp': datetime.now().isoformat(),
                        'total_questions': 1,
                        'completed_questions': 1
                    },
                    'result': {
                        'question_id': question.get('question_id', '0'),
                        'dimension': question.get('dimension', ''),
                        'scenario': question.get('scenario', ''),
                        'prompt_for_agent': question.get('prompt_for_agent', ''),
                        'response': response_text,
                        'elapsed_time': elapsed_time,
                        'evaluation_rubric': question.get('evaluation_rubric', {})
                    }
                }, f, ensure_ascii=False, indent=2)
            
            print(f"Result saved to: {output_file}")
            print("Test completed successfully!")
            
        else:
            print(f"API call failed with status {response.status_code}")
            print(f"Response content: {response.text}")
            
    except Exception as e:
        print(f"Error calling Ollama API: {e}")
        print(f"Elapsed time before error: {time.time() - start_time:.2f}s")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    minimal_test()