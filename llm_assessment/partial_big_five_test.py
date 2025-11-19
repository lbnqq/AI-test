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

def run_partial_big_five_test():
    print("Starting Partial Big Five Test (5 questions)...")
    
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
    
    # Process only first 5 questions
    results = []
    total_questions = 5
    
    for i, question in enumerate(test_data['test_bank'][:total_questions]):
        print(f"\nProcessing question {i+1}/{total_questions}")
        print(f"Question ID: {question.get('question_id', i)}")
        print(f"Dimension: {question.get('dimension', '')}")
        
        # Prepare prompt
        prompt_content = f"Scenario: {question.get('scenario', '')}\n\nQuestion: {question.get('prompt_for_agent', '')}"
        prompt = [{"role": "user", "content": prompt_content}]
        
        # Generate response with extended timeout
        print("Generating response...")
        start_time = time.time()
        try:
            response = client.generate_response(prompt, "qwen2.5-coder:14b", timeout=600)  # 10 minutes timeout
            elapsed_time = time.time() - start_time
            print(f"Response received in {elapsed_time:.2f}s")
            
            if response:
                print(f"Response length: {len(response)} characters")
                print(f"Response preview: {response[:100]}...")
            else:
                print("No response received")
            
            results.append({
                'question_id': question.get('question_id', i),
                'dimension': question.get('dimension', ''),
                'scenario': question.get('scenario', ''),
                'prompt_for_agent': question.get('prompt_for_agent', ''),
                'response': response,
                'elapsed_time': elapsed_time,
                'evaluation_rubric': question.get('evaluation_rubric', {})
            })
            
        except Exception as e:
            print(f"Error generating response: {e}")
            results.append({
                'question_id': question.get('question_id', i),
                'dimension': question.get('dimension', ''),
                'error': str(e),
                'elapsed_time': time.time() - start_time
            })
    
    # Save results
    output_file = f"results/partial_big_five_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs('results', exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'test_metadata': {
                'model': 'qwen2.5-coder:14b',
                'test_name': 'Agent-IPIP-FFM-50 完整版大五人格情境评估框架 (Partial)',
                'timestamp': datetime.now().isoformat(),
                'total_questions': total_questions,
                'completed_questions': len(results)
            },
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\nTest completed! Results saved to: {output_file}")
    print(f"Processed {len(results)} out of {total_questions} questions")
    
    # Display summary
    successful_responses = sum(1 for r in results if 'response' in r and r['response'] is not None)
    print(f"Successful responses: {successful_responses}/{total_questions}")

if __name__ == "__main__":
    run_partial_big_five_test()