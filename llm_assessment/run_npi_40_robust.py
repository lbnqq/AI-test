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
    """
    加载NPI-40测试数据
    """
    if not os.path.isabs(test_file):
        test_file_path = os.path.join(TESTS_DIR, test_file)
    else:
        test_file_path = test_file
    
    print(f"Loading NPI-40 test data from: {test_file_path}")
    
    with open(test_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data


def query_ollama_with_retry(model_name, prompt, max_retries=3, timeout=600):
    """
    带重试机制的ollama查询
    """
    url = "http://localhost:11434/api/generate"
    
    for attempt in range(max_retries):
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
            print(f"  尝试 {attempt + 1}/{max_retries}...")
            response = requests.post(url, json=payload, timeout=timeout)
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'response': result.get('response', ''),
                    'time': elapsed_time,
                    'success': True,
                    'attempt': attempt + 1
                }
            else:
                print(f"  错误: {response.status_code} - {response.text}")
                if attempt < max_retries - 1:
                    print(f"  等待30秒后重试...")
                    time.sleep(30)
                else:
                    return {
                        'response': f"Error: {response.status_code} - {response.text}",
                        'time': elapsed_time,
                        'success': False,
                        'attempt': attempt + 1
                    }
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"  异常: {e}")
            if attempt < max_retries - 1:
                print(f"  等待30秒后重试...")
                time.sleep(30)
            else:
                return {
                    'response': f"Error: {str(e)}",
                    'time': elapsed_time,
                    'success': False,
                    'attempt': attempt + 1
                }
    
    return {
        'response': "Max retries exceeded",
        'time': 0,
        'success': False,
        'attempt': max_retries
    }


def run_complete_npi_test(model_name, test_data):
    """
    运行完整的40道题NPI测试
    """
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
            'total_questions': len(test_data.get('test_bank', [])),
            'successful_responses': 0,
            'failed_responses': 0,
            'total_response_time': 0,
            'average_response_time': 0,
            'total_characters': 0,
            'average_characters': 0,
            'dimension_scores': {}
        }
    }
    
    # 初始化维度分数
    for dimension in results['assessment_metadata']['dimensions']:
        results['test_summary']['dimension_scores'][dimension] = {
            'count': 0,
            'narcissistic_indicators': 0,
            'total_score': 0,
            'avg_score': 0
        }
    
    # 处理每个问题
    for i, question in enumerate(test_data['test_bank']):
        print(f"\n{'='*80}")
        print(f"问题 {i+1}/{len(test_data['test_bank'])}: {question['question_id']}")
        print(f"维度: {question['dimension']}")
        print(f"概念: {question['mapped_npi_concept']}")
        print(f"场景: {question['scenario']}")
        print(f"提示: {question['prompt_for_agent']}")
        print(f"{'='*80}")
        
        # 构建完整提示
        full_prompt = f"场景：{question['scenario']}\n\n{question['prompt_for_agent']}"
        
        print("正在获取模型响应...")
        print("提示：模型正在思考中，预计需要1-2分钟，请耐心等待...")
        
        result = query_ollama_with_retry(model_name, full_prompt)
        
        response = result['response']
        response_time = result['time']
        success = result['success']
        attempt = result['attempt']
        
        print(f"\n响应完成！")
        print(f"  尝试次数: {attempt}")
        print(f"  响应时间: {response_time:.2f}s")
        print(f"  成功状态: {success}")
        print(f"\n模型响应:")
        print("-"*60)
        print(response)
        print("-"*60)
        print(f"响应长度: {len(response)} 字符")
        
        # 更新统计信息
        if success:
            results['test_summary']['successful_responses'] += 1
        else:
            results['test_summary']['failed_responses'] += 1
        
        results['test_summary']['total_response_time'] += response_time
        results['test_summary']['total_characters'] += len(response)
        
        # 更新维度统计
        dimension = question['dimension']
        results['test_summary']['dimension_scores'][dimension]['count'] += 1
        
        # 存储结果
        result_entry = {
            'question_id': question['question_id'],
            'dimension': dimension,
            'mapped_npi_concept': question['mapped_npi_concept'],
            'scenario': question['scenario'],
            'prompt_for_agent': question['prompt_for_agent'],
            'response': response,
            'response_time': response_time,
            'response_success': success,
            'response_length': len(response),
            'attempt_count': attempt,
            'evaluation_rubric': question['evaluation_rubric'],
            'original_data': question
        }
        results['assessment_results'].append(result_entry)
        
        # 问题间隔
        if i < len(test_data['test_bank']) - 1:
            print(f"\n等待5秒后继续下一题...")
            time.sleep(5)
    
    # 计算平均值
    if len(test_data['test_bank']) > 0:
        results['test_summary']['average_response_time'] = results['test_summary']['total_response_time'] / len(test_data['test_bank'])
        results['test_summary']['average_characters'] = results['test_summary']['total_characters'] / len(test_data['test_bank'])
    
    return results


def save_npi_results(results: dict, model: str):
    """
    保存NPI测试结果
    """
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    # 生成文件名
    date_str = datetime.now().strftime("%m%d")
    time_str = datetime.now().strftime("%H%M%S")
    model_safe = model.replace('/', '_').replace(':', '_').replace('-', '_')
    filename = f"npi_40_complete_{model_safe}_{date_str}_{time_str}.json"
    filepath = os.path.join(RESULTS_DIR, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n结果已保存到: {filepath}")
        return filepath
    except Exception as e:
        print(f"保存结果时出错: {e}")
        return None


def main():
    """
    主函数
    """
    print("="*80)
    print("NPI-40 内隐自恋测试 - 完整版")
    print("="*80)
    
    model_name = "qwen2.5-coder:14b"
    test_file = "Agent-NPI-40.json"
    
    # 加载测试数据
    try:
        test_data = load_npi_test_data(test_file)
        print(f"测试数据加载成功。问题总数: {len(test_data.get('test_bank', []))}")
        print(f"测试维度: {', '.join(test_data.get('test_info', {}).get('dimensions', []))}")
    except Exception as e:
        print(f"加载测试数据时出错: {e}")
        sys.exit(1)
    
    # 显示测试信息
    print(f"\n模型: {model_name}")
    print(f"测试: {test_data.get('test_info', {}).get('test_name', 'NPI-40 Test')}")
    print(f"描述: {test_data.get('test_info', {}).get('instruction', 'N/A')}")
    print(f"评分方法: {test_data.get('test_info', {}).get('scoring_methodology', 'N/A')}")
    
    print(f"\n即将开始40道题的完整测试...")
    print("预计总时间: 1-2小时")
    print("测试过程中不会中断，请耐心等待...")
    
    # 运行测试
    try:
        start_time = time.time()
        results = run_complete_npi_test(model_name, test_data)
        total_time = time.time() - start_time
        
        # 显示测试摘要
        print(f"\n{'='*80}")
        print("测试完成 - 摘要")
        print(f"{'='*80}")
        summary = results['test_summary']
        metadata = results['assessment_metadata']
        
        print(f"模型: {metadata['model_id']}")
        print(f"测试: {metadata['test_name']}")
        print(f"时间: {metadata['timestamp']}")
        print(f"总耗时: {total_time/60:.1f} 分钟")
        print(f"\n统计摘要:")
        print(f"  总问题数: {summary['total_questions']}")
        print(f"  成功响应: {summary['successful_responses']}")
        print(f"  失败响应: {summary['failed_responses']}")
        print(f"  成功率: {summary['successful_responses']/summary['total_questions']*100:.1f}%")
        print(f"  平均响应时间: {summary['average_response_time']:.2f}s")
        print(f"  平均响应长度: {summary['average_characters']:.0f} 字符")
        
        print(f"\n按维度分析:")
        for dimension, stats in summary['dimension_scores'].items():
            print(f"  {dimension}: {stats['count']} 题")
        
        # 保存结果
        saved_file = save_npi_results(results, model_name)
        
        if saved_file:
            print(f"\n测试完成！结果已保存到: {saved_file}")
        else:
            print("保存结果失败。")
            
    except KeyboardInterrupt:
        print("\n测试被用户中断。")
        sys.exit(1)
    except Exception as e:
        print(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()