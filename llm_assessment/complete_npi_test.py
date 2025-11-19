#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
import time
import requests
import signal
from datetime import datetime

# Global flag for graceful shutdown
shutdown_flag = False

def signal_handler(signum, frame):
    global shutdown_flag
    print("\n收到关闭信号，正在保存当前进度...")
    shutdown_flag = True

def complete_npi_test():
    global shutdown_flag
    print("开始完整NPI-40自恋人格测试...")
    print("注意：每个问题预计需要约100秒响应时间")
    print("总预计时间：约1-1.5小时")
    
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Load test data
    test_file = "test_files/Agent-NPI-40.json"
    print(f"从以下位置加载测试数据: {test_file}")
    
    with open(test_file, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    print(f"测试数据加载成功。问题总数: {len(test_data.get('test_bank', []))}")
    
    # Process all questions
    results = []
    total_questions = len(test_data['test_bank'])
    start_time = time.time()
    
    for i, question in enumerate(test_data['test_bank']):
        if shutdown_flag:
            print("收到关闭请求，保存当前进度...")
            break
            
        elapsed_total = time.time() - start_time
        estimated_remaining = (elapsed_total / (i + 1)) * (total_questions - i - 1) if i > 0 else 0
        
        print(f"\n{'='*60}")
        print(f"处理问题 {i+1}/{total_questions}")
        print(f"问题ID: {question.get('question_id', i)}")
        print(f"维度: {question.get('dimension', '')}")
        print(f"NPI概念: {question.get('mapped_npi_concept', '')}")
        print(f"已用时间: {elapsed_total/60:.1f}分钟")
        print(f"预计剩余时间: {estimated_remaining/60:.1f}分钟")
        print(f"{'='*60}")
        
        # Prepare prompt
        scenario = question.get('scenario', '')
        prompt_for_agent = question.get('prompt_for_agent', '')
        prompt_content = f"Scenario: {scenario}\n\nPrompt: {prompt_for_agent}"
        
        # Direct Ollama API call
        print("调用Ollama API...")
        question_start_time = time.time()
        try:
            url = 'http://localhost:11434/api/generate'
            data = {
                'model': 'qwen2.5-coder:14b',
                'prompt': prompt_content,
                'stream': False
            }
            
            response = requests.post(url, json=data, timeout=900)  # 15 minutes timeout
            question_elapsed_time = time.time() - question_start_time
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                print(f"响应已接收，用时: {question_elapsed_time:.2f}秒")
                print(f"响应长度: {len(response_text)} 字符")
                print(f"响应预览: {response_text[:100]}...")
                
                results.append({
                    'question_id': question.get('question_id', i),
                    'dimension': question.get('dimension', ''),
                    'mapped_npi_concept': question.get('mapped_npi_concept', ''),
                    'scenario': scenario,
                    'prompt_for_agent': prompt_for_agent,
                    'response': response_text,
                    'elapsed_time': question_elapsed_time,
                    'evaluation_rubric': question.get('evaluation_rubric', {})
                })
            else:
                print(f"API调用失败，状态码: {response.status_code}")
                results.append({
                    'question_id': question.get('question_id', i),
                    'dimension': question.get('dimension', ''),
                    'error': f"API调用失败，状态码: {response.status_code}",
                    'elapsed_time': time.time() - question_start_time
                })
                
        except Exception as e:
            print(f"调用Ollama API时出错: {e}")
            results.append({
                'question_id': question.get('question_id', i),
                'dimension': question.get('dimension', ''),
                'error': str(e),
                'elapsed_time': time.time() - question_start_time
            })
        
        # Save progress after each question
        print(f"保存进度: {i+1}/{total_questions} 问题已完成")
        output_file = f"results/npi_progress_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs('results', exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'test_metadata': {
                    'model': 'qwen2.5-coder:14b',
                    'test_name': 'Agent-NPI-40 完整版自恋倾向情境评估框架',
                    'timestamp': datetime.now().isoformat(),
                    'total_questions': total_questions,
                    'completed_questions': len(results),
                    'progress_percentage': (len(results) / total_questions) * 100,
                    'total_elapsed_time': time.time() - start_time
                },
                'results': results
            }, f, ensure_ascii=False, indent=2)
        print(f"进度已保存到: {output_file}")
    
    # Final save
    total_elapsed_time = time.time() - start_time
    output_file = f"results/npi_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs('results', exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'test_metadata': {
                'model': 'qwen2.5-coder:14b',
                'test_name': 'Agent-NPI-40 完整版自恋倾向情境评估框架',
                'timestamp': datetime.now().isoformat(),
                'total_questions': total_questions,
                'completed_questions': len(results),
                'progress_percentage': (len(results) / total_questions) * 100,
                'total_elapsed_time': total_elapsed_time
            },
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"测试完成！最终结果已保存到: {output_file}")
    print(f"已处理 {len(results)} out of {total_questions} 问题")
    print(f"总用时: {total_elapsed_time/60:.1f} 分钟")
    
    # Display summary
    successful_responses = sum(1 for r in results if 'response' in r and r['response'] is not None)
    failed_responses = sum(1 for r in results if 'error' in r)
    print(f"成功响应: {successful_responses}/{total_questions}")
    print(f"失败响应: {failed_responses}/{total_questions}")
    print(f"{'='*60}")

if __name__ == "__main__":
    complete_npi_test()