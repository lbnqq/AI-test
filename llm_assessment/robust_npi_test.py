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

def call_ollama_with_retry(prompt, max_retries=3, initial_timeout=300):
    """调用Ollama API，带有重试机制"""
    for attempt in range(max_retries):
        try:
            url = 'http://localhost:11434/api/generate'
            data = {
                'model': 'qwen2.5-coder:14b',
                'prompt': prompt,
                'stream': False
            }
            
            # 逐渐增加超时时间
            timeout = initial_timeout * (attempt + 1)
            print(f"  尝试 {attempt + 1}/{max_retries}，超时设置: {timeout}秒")
            
            response = requests.post(url, json=data, timeout=timeout)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', ''), None
            else:
                error_msg = f"API调用失败，状态码: {response.status_code}"
                print(f"  {error_msg}")
                if attempt < max_retries - 1:
                    print(f"  等待{10 * (attempt + 1)}秒后重试...")
                    time.sleep(10 * (attempt + 1))
                return None, error_msg
                
        except requests.exceptions.Timeout:
            error_msg = f"请求超时 (>{timeout}秒)"
            print(f"  {error_msg}")
            if attempt < max_retries - 1:
                print(f"  等待{15 * (attempt + 1)}秒后重试...")
                time.sleep(15 * (attempt + 1))
            continue
        except Exception as e:
            error_msg = f"调用Ollama API时出错: {e}"
            print(f"  {error_msg}")
            if attempt < max_retries - 1:
                print(f"  等待{10 * (attempt + 1)}秒后重试...")
                time.sleep(10 * (attempt + 1))
            continue
    
    return None, "所有重试均失败"

def robust_npi_test():
    global shutdown_flag
    print("开始增强版NPI-40自恋人格测试...")
    print("注意：每个问题最多尝试3次，每次超时时间递增")
    print("总预计时间：约2-3小时（包含重试）")
    
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
        
        # Call Ollama with retry
        question_start_time = time.time()
        response_text, error = call_ollama_with_retry(prompt_content)
        question_elapsed_time = time.time() - question_start_time
        
        if response_text:
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
            print(f"问题处理失败: {error}")
            results.append({
                'question_id': question.get('question_id', i),
                'dimension': question.get('dimension', ''),
                'scenario': scenario,
                'prompt_for_agent': prompt_for_agent,
                'error': error,
                'elapsed_time': question_elapsed_time,
                'evaluation_rubric': question.get('evaluation_rubric', {})
            })
        
        # Save progress after each question
        print(f"保存进度: {i+1}/{total_questions} 问题已完成")
        output_file = f"results/npi_robust_progress_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs('results', exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'test_metadata': {
                    'model': 'qwen2.5-coder:14b',
                    'test_name': 'Agent-NPI-40 增强版自恋倾向情境评估框架',
                    'timestamp': datetime.now().isoformat(),
                    'total_questions': total_questions,
                    'completed_questions': len(results),
                    'progress_percentage': (len(results) / total_questions) * 100,
                    'total_elapsed_time': time.time() - start_time
                },
                'results': results
            }, f, ensure_ascii=False, indent=2)
        print(f"进度已保存到: {output_file}")
        
        # 短暂休息，避免过载
        time.sleep(5)
    
    # Final save
    total_elapsed_time = time.time() - start_time
    output_file = f"results/npi_robust_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs('results', exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'test_metadata': {
                'model': 'qwen2.5-coder:14b',
                'test_name': 'Agent-NPI-40 增强版自恋倾向情境评估框架',
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
    print(f"成功率: {successful_responses/total_questions*100:.1f}%")
    print(f"{'='*60}")

if __name__ == "__main__":
    robust_npi_test()