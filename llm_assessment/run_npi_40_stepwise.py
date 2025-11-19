#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
import requests
import time
from datetime import datetime

# Constants
TESTS_DIR = os.path.join(os.path.dirname(__file__), "test_files")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")


def load_npi_test_data(test_file: str) -> dict:
    """加载NPI-40测试数据"""
    if not os.path.isabs(test_file):
        test_file_path = os.path.join(TESTS_DIR, test_file)
    else:
        test_file_path = test_file
    
    with open(test_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data


def query_ollama_direct(model_name, prompt, timeout=600):
    """直接查询ollama API"""
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 2000
        }
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(url, json=payload, timeout=timeout)
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            return {
                'response': result.get('response', ''),
                'time': elapsed_time,
                'success': True
            }
        else:
            return {
                'response': f"Error: {response.status_code} - {response.text}",
                'time': elapsed_time,
                'success': False
            }
    except Exception as e:
        return {
            'response': f"Error: {str(e)}",
            'time': time.time() - start_time,
            'success': False
        }


def save_progress(results: dict, model: str, current_question: int):
    """保存当前进度"""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    date_str = datetime.now().strftime("%m%d")
    time_str = datetime.now().strftime("%H%M%S")
    model_safe = model.replace('/', '_').replace(':', '_').replace('-', '_')
    filename = f"npi_40_progress_{model_safe}_{date_str}_{time_str}_Q{current_question}.json"
    filepath = os.path.join(RESULTS_DIR, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        return filepath
    except Exception as e:
        print(f"保存进度出错: {e}")
        return None


def main():
    """主函数"""
    print("="*80)
    print("NPI-40 内隐自恋测试 - 逐题运行版")
    print("="*80)
    
    model_name = "qwen2.5-coder:14b"
    test_file = "Agent-NPI-40.json"
    
    # 加载测试数据
    test_data = load_npi_test_data(test_file)
    questions = test_data['test_bank']
    
    print(f"模型: {model_name}")
    print(f"测试: {test_data.get('test_info', {}).get('test_name', 'NPI-40 Test')}")
    print(f"总问题数: {len(questions)}")
    print(f"测试维度: {', '.join(test_data.get('test_info', {}).get('dimensions', []))}")
    
    # 初始化结果结构
    results = {
        'assessment_metadata': {
            'model_id': model_name,
            'test_name': test_data.get('test_info', {}).get('test_name', 'NPI-40 Test'),
            'test_category': test_data.get('test_info', {}).get('test_category', 'Agent Personality & Behavior'),
            'total_questions': test_data.get('test_info', {}).get('total_questions', 40),
            'dimensions': test_data.get('test_info', {}).get('dimensions', []),
            'timestamp': datetime.now().isoformat(),
            'scoring_methodology': test_data.get('test_info', {}).get('scoring_methodology', ''),
            'source': test_data.get('test_info', {}).get('source', ''),
        },
        'assessment_results': [],
        'test_summary': {
            'total_questions': len(questions),
            'successful_responses': 0,
            'failed_responses': 0,
            'total_response_time': 0,
            'average_response_time': 0,
            'total_characters': 0,
            'average_characters': 0,
        }
    }
    
    # 逐题处理
    for i, question in enumerate(questions):
        print(f"\n{'='*80}")
        print(f"问题 {i+1}/{len(questions)}: {question['question_id']}")
        print(f"维度: {question['dimension']}")
        print(f"概念: {question['mapped_npi_concept']}")
        print(f"场景: {question['scenario']}")
        print(f"提示: {question['prompt_for_agent']}")
        print(f"{'='*80}")
        
        # 构建提示
        full_prompt = f"场景：{question['scenario']}\n\n{question['prompt_for_agent']}"
        
        print("正在获取模型响应（预计1-2分钟）...")
        
        # 获取响应
        result = query_ollama_direct(model_name, full_prompt)
        
        response = result['response']
        response_time = result['time']
        success = result['success']
        
        print(f"\n响应完成！耗时: {response_time:.2f}s")
        print(f"成功: {success}")
        print(f"\n模型响应:")
        print("-"*60)
        print(response)
        print("-"*60)
        print(f"响应长度: {len(response)} 字符")
        
        # 更新统计
        if success:
            results['test_summary']['successful_responses'] += 1
        else:
            results['test_summary']['failed_responses'] += 1
        
        results['test_summary']['total_response_time'] += response_time
        results['test_summary']['total_characters'] += len(response)
        
        # 存储结果
        result_entry = {
            'question_id': question['question_id'],
            'dimension': question['dimension'],
            'mapped_npi_concept': question['mapped_npi_concept'],
            'scenario': question['scenario'],
            'prompt_for_agent': question['prompt_for_agent'],
            'response': response,
            'response_time': response_time,
            'response_success': success,
            'response_length': len(response),
            'evaluation_rubric': question['evaluation_rubric'],
            'original_data': question
        }
        results['assessment_results'].append(result_entry)
        
        # 每完成5题保存一次进度
        if (i + 1) % 5 == 0 or i == len(questions) - 1:
            print(f"\n保存进度 ({i+1}/{len(questions)} 题)...")
            save_progress(results, model_name, i+1)
        
        # 问题间隔
        if i < len(questions) - 1:
            print(f"\n等待5秒后继续...")
            time.sleep(5)
    
    # 计算最终统计
    if len(questions) > 0:
        results['test_summary']['average_response_time'] = results['test_summary']['total_response_time'] / len(questions)
        results['test_summary']['average_characters'] = results['test_summary']['total_characters'] / len(questions)
    
    # 保存最终结果
    print(f"\n{'='*80}")
    print("测试完成！")
    print(f"{'='*80}")
    
    summary = results['test_summary']
    print(f"成功响应: {summary['successful_responses']}")
    print(f"失败响应: {summary['failed_responses']}")
    print(f"成功率: {summary['successful_responses']/summary['total_questions']*100:.1f}%")
    print(f"平均响应时间: {summary['average_response_time']:.2f}s")
    print(f"平均响应长度: {summary['average_characters']:.0f} 字符")
    
    # 保存最终文件
    date_str = datetime.now().strftime("%m%d")
    time_str = datetime.now().strftime("%H%M%S")
    model_safe = model_name.replace('/', '_').replace(':', '_').replace('-', '_')
    filename = f"npi_40_complete_{model_safe}_{date_str}_{time_str}.json"
    filepath = os.path.join(RESULTS_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n最终结果已保存到: {filepath}")


if __name__ == "__main__":
    main()