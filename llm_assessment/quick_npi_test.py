#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import glob
import requests
from datetime import datetime

def quick_npi_test():
    print("开始快速NPI-40自恋人格测试...")
    
    # Load test data
    test_file = "test_files/Agent-NPI-40.json"
    print(f"从以下位置加载测试数据: {test_file}")
    
    with open(test_file, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    total_questions = len(test_data['test_bank'])
    print(f"测试数据加载成功。问题总数: {total_questions}")
    
    # Find latest progress file to resume from
    progress_files = glob.glob('results/npi_progress_*.json')
    results = []
    start_idx = 0
    
    if progress_files:
        latest_file = max(progress_files, key=os.path.getmtime)
        print(f"找到最新进度文件: {latest_file}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            progress_data = json.load(f)
        
        results = progress_data.get('results', [])
        start_idx = len(results)
        print(f"从问题 {start_idx + 1} 开始继续测试")
    
    # Process remaining questions
    for i in range(start_idx, total_questions):
        question = test_data['test_bank'][i]
        print(f"\n处理问题 {i+1}/{total_questions}: {question.get('question_id', i)}")
        print(f"NPI概念: {question.get('mapped_npi_concept', '')}")
        
        # Prepare prompt
        scenario = question.get('scenario', '')
        prompt_for_agent = question.get('prompt_for_agent', '')
        prompt_content = f"Scenario: {scenario}\n\nPrompt: {prompt_for_agent}"
        
        # Direct Ollama API call with shorter timeout
        try:
            print("调用Ollama API...")
            url = 'http://localhost:11434/api/generate'
            data = {
                'model': 'qwen2.5-coder:14b',
                'prompt': prompt_content,
                'stream': False,
                'options': {
                    'temperature': 0.1,
                    'num_predict': 500  # 限制响应长度
                }
            }
            
            response = requests.post(url, json=data, timeout=120)  # 2 minutes timeout
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                print(f"响应已接收，长度: {len(response_text)} 字符")
                
                results.append({
                    'question_id': question.get('question_id', i),
                    'dimension': question.get('dimension', ''),
                    'mapped_npi_concept': question.get('mapped_npi_concept', ''),
                    'scenario': scenario,
                    'prompt_for_agent': prompt_for_agent,
                    'response': response_text,
                    'evaluation_rubric': question.get('evaluation_rubric', {})
                })
            else:
                print(f"API调用失败，状态码: {response.status_code}")
                results.append({
                    'question_id': question.get('question_id', i),
                    'dimension': question.get('dimension', ''),
                    'error': f"API调用失败，状态码: {response.status_code}"
                })
                
        except Exception as e:
            print(f"调用Ollama API时出错: {e}")
            results.append({
                'question_id': question.get('question_id', i),
                'dimension': question.get('dimension', ''),
                'error': str(e)
            })
        
        # Save progress every 5 questions
        if (i + 1) % 5 == 0 or i == total_questions - 1:
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
                        'progress_percentage': (len(results) / total_questions) * 100
                    },
                    'results': results
                }, f, ensure_ascii=False, indent=2)
            print(f"进度已保存: {len(results)}/{total_questions} 问题完成")
    
    # Final save
    output_file = f"results/npi_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'test_metadata': {
                'model': 'qwen2.5-coder:14b',
                'test_name': 'Agent-NPI-40 完整版自恋倾向情境评估框架',
                'timestamp': datetime.now().isoformat(),
                'total_questions': total_questions,
                'completed_questions': len(results),
                'progress_percentage': (len(results) / total_questions) * 100
            },
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n测试完成！结果已保存到: {output_file}")
    print(f"成功处理 {len(results)} 个问题")
    
    # 简单分析结果
    successful_responses = sum(1 for r in results if 'response' in r)
    failed_responses = sum(1 for r in results if 'error' in r)
    print(f"成功响应: {successful_responses}/{total_questions}")
    print(f"失败响应: {failed_responses}/{total_questions}")
    
    return output_file

if __name__ == "__main__":
    quick_npi_test()