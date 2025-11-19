#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
import time
import requests
from datetime import datetime

def direct_ollama_test():
    print("Starting Direct Ollama Big Five Test...")
    
    # Load test data
    test_file = "test_files/agent-big-five-50-complete2.json"
    print(f"Loading test data from: {test_file}")
    
    with open(test_file, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    print(f"Test data loaded successfully. Number of questions: {len(test_data.get('test_bank', []))}")
    
    # Process all questions
    results = []
    total_questions = len(test_data['test_bank'])
    
    for i, question in enumerate(test_data['test_bank']):
        print(f"\n{'='*60}")
        print(f"Processing question {i+1}/{total_questions}")
        print(f"Question ID: {question.get('question_id', i)}")
        print(f"Dimension: {question.get('dimension', '')}")
        print(f"{'='*60}")
        
        # Prepare prompt
        prompt_content = f"Scenario: {question.get('scenario', '')}\n\nQuestion: {question.get('prompt_for_agent', '')}"
        
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
            
            response = requests.post(url, json=data, timeout=900)  # 15 minutes timeout
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                print(f"Response received in {elapsed_time:.2f}s")
                print(f"Response length: {len(response_text)} characters")
                print(f"Response preview: {response_text[:100]}...")
                
                results.append({
                    'question_id': question.get('question_id', i),
                    'dimension': question.get('dimension', ''),
                    'scenario': question.get('scenario', ''),
                    'prompt_for_agent': question.get('prompt_for_agent', ''),
                    'response': response_text,
                    'elapsed_time': elapsed_time,
                    'evaluation_rubric': question.get('evaluation_rubric', {})
                })
            else:
                print(f"API call failed with status {response.status_code}")
                results.append({
                    'question_id': question.get('question_id', i),
                    'dimension': question.get('dimension', ''),
                    'error': f"API call failed with status {response.status_code}",
                    'elapsed_time': time.time() - start_time
                })
                
        except Exception as e:
            print(f"Error calling Ollama API: {e}")
            results.append({
                'question_id': question.get('question_id', i),
                'dimension': question.get('dimension', ''),
                'error': str(e),
                'elapsed_time': time.time() - start_time
            })
        
        # Save progress after each question
        if (i + 1) % 5 == 0 or i == total_questions - 1:
            print(f"\nSaving progress after {i+1} questions...")
            output_file = f"results/direct_big_five_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs('results', exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'test_metadata': {
                        'model': 'qwen2.5-coder:14b',
                        'test_name': 'Agent-IPIP-FFM-50 完整版大五人格情境评估框架 (Direct API)',
                        'timestamp': datetime.now().isoformat(),
                        'total_questions': total_questions,
                        'completed_questions': len(results),
                        'progress_percentage': (len(results) / total_questions) * 100
                    },
                    'results': results
                }, f, ensure_ascii=False, indent=2)
            print(f"Progress saved to: {output_file}")
    
    # Final save
    output_file = f"results/direct_big_five_test_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs('results', exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'test_metadata': {
                'model': 'qwen2.5-coder:14b',
                'test_name': 'Agent-IPIP-FFM-50 完整版大五人格情境评估框架 (Direct API)',
                'timestamp': datetime.now().isoformat(),
                'total_questions': total_questions,
                'completed_questions': len(results),
                'progress_percentage': (len(results) / total_questions) * 100
            },
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Test completed! Final results saved to: {output_file}")
    print(f"Processed {len(results)} out of {total_questions} questions")
    
    # Display summary
    successful_responses = sum(1 for r in results if 'response' in r and r['response'] is not None)
    failed_responses = sum(1 for r in results if 'error' in r)
    print(f"Successful responses: {successful_responses}/{total_questions}")
    print(f"Failed responses: {failed_responses}/{total_questions}")
    print(f"{'='*60}")

if __name__ == "__main__":
    direct_ollama_test()