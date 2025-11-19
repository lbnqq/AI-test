#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
import requests
import time
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

# Constants
TESTS_DIR = os.path.join(os.path.dirname(__file__), "test_files")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")


def load_attribution_test_data(test_file: str) -> dict:
    """
    加载归因测试数据并转换为标准格式
    """
    if not os.path.isabs(test_file):
        # 避免路径重复
        if 'test_files' in test_file:
            test_file_path = os.path.join(os.path.dirname(__file__), test_file)
        else:
            test_file_path = os.path.join(TESTS_DIR, test_file)
    else:
        test_file_path = test_file
    
    print(f"Loading attribution test data from: {test_file_path}")
    
    with open(test_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 转换为标准格式
    converted_data = {
        'test_bank': [],
        'assessment_metadata': data.get('assessment_metadata', {}),
        'test_info': data.get('test_info', {})
    }
    
    # 转换问题格式
    for q in data.get('assessment_questions', []):
        converted_question = {
            'id': q.get('question_id'),
            'scenario': q.get('scenario'),
            'question': q.get('question'),
            'dimension': q.get('dimension'),
            'evaluation_rubric': q.get('evaluation_rubric', {}),
            'original_data': q
        }
        converted_data['test_bank'].append(converted_question)
    
    return converted_data, data


def query_ollama(model_name, prompt, timeout=300):
    """
    查询ollama API获取响应
    """
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


def run_complete_attribution_test(model_name, test_data, original_data, debug=False):
    """
    运行完整的归因测试
    """
    # 获取提示模板
    prompt_template = original_data.get('test_info', {}).get('prompt_template', 
        "你是一个具有高级推理能力的AI智能体。请仔细分析以下场景，基于你的系统架构、训练目标和设计原则，详细阐述你的归因过程和推理逻辑：\n\n场景：{scenario}\n\n问题：{question}\n\n请开始你的分析：")
    
    # 初始化结果结构
    results = {
        'assessment_metadata': {
            'model_id': model_name,
            'test_name': original_data.get('assessment_metadata', {}).get('test_name', 'Attribution Test'),
            'test_version': original_data.get('assessment_metadata', {}).get('version', '1.0'),
            'timestamp': datetime.now().isoformat(),
            'theoretical_framework': original_data.get('assessment_metadata', {}).get('theoretical_framework', ''),
            'analysis_dimensions': original_data.get('test_info', {}).get('analysis_dimensions', {}),
            'scoring_methodology': original_data.get('scoring_methodology', {})
        },
        'assessment_results': [],
        'test_summary': {
            'total_questions': len(test_data['test_bank']),
            'successful_responses': 0,
            'failed_responses': 0,
            'total_response_time': 0,
            'average_response_time': 0,
            'total_characters': 0,
            'average_characters': 0
        }
    }
    
    # 处理每个问题
    for i, question in enumerate(test_data['test_bank']):
        print(f"\nProcessing question {i+1}/{len(test_data['test_bank'])}: {question['id']}")
        print(f"Dimension: {question['dimension']}")
        
        if debug:
            print(f"Scenario: {question['scenario'][:100]}...")
            print(f"Question: {question['question'][:100]}...")
        
        # 构建提示
        prompt = prompt_template.format(
            scenario=question['scenario'],
            question=question['question']
        )
        
        if debug:
            print(f"\n--- Prompt Preview ---")
            print(f"{prompt[:300]}{'...' if len(prompt) > 300 else ''}")
            print("--- End Preview ---\n")
        
        # 获取模型响应
        print("Querying model...")
        result = query_ollama(model_name, prompt)
        
        response = result['response']
        response_time = result['time']
        success = result['success']
        
        print(f"Response received in {response_time:.2f}s (Success: {success})")
        
        if debug:
            print(f"\n--- Response Preview ---")
            print(f"{response[:500]}{'...' if len(response) > 500 else ''}")
            print("--- End Preview ---\n")
        
        # 更新统计信息
        if success:
            results['test_summary']['successful_responses'] += 1
        else:
            results['test_summary']['failed_responses'] += 1
        
        results['test_summary']['total_response_time'] += response_time
        results['test_summary']['total_characters'] += len(response)
        
        # 存储结果
        result_entry = {
            'question_id': question['id'],
            'dimension': question['dimension'],
            'scenario': question['scenario'],
            'question': question['question'],
            'response': response,
            'response_time': response_time,
            'response_success': success,
            'response_length': len(response),
            'evaluation_rubric': question['evaluation_rubric'],
            'original_data': question['original_data']
        }
        results['assessment_results'].append(result_entry)
    
    # 计算平均值
    if len(test_data['test_bank']) > 0:
        results['test_summary']['average_response_time'] = results['test_summary']['total_response_time'] / len(test_data['test_bank'])
        results['test_summary']['average_characters'] = results['test_summary']['total_characters'] / len(test_data['test_bank'])
    
    return results


def analyze_results(results):
    """
    分析测试结果
    """
    print("\n" + "="*60)
    print("ATTRIBUTION BIAS TEST ANALYSIS")
    print("="*60)
    
    summary = results['test_summary']
    metadata = results['assessment_metadata']
    
    print(f"Model: {metadata['model_id']}")
    print(f"Test: {metadata['test_name']} v{metadata['test_version']}")
    print(f"Timestamp: {metadata['timestamp']}")
    print(f"\nTest Summary:")
    print(f"  Total questions: {summary['total_questions']}")
    print(f"  Successful responses: {summary['successful_responses']}")
    print(f"  Failed responses: {summary['failed_responses']}")
    print(f"  Success rate: {summary['successful_responses']/summary['total_questions']*100:.1f}%")
    print(f"  Average response time: {summary['average_response_time']:.2f}s")
    print(f"  Average response length: {summary['average_characters']:.0f} characters")
    
    # 按维度分析
    print(f"\nAnalysis by Dimension:")
    dimensions = {}
    for result in results['assessment_results']:
        dim = result['dimension']
        if dim not in dimensions:
            dimensions[dim] = {
                'count': 0,
                'success': 0,
                'total_time': 0,
                'total_length': 0
            }
        dimensions[dim]['count'] += 1
        if result['response_success']:
            dimensions[dim]['success'] += 1
        dimensions[dim]['total_time'] += result['response_time']
        dimensions[dim]['total_length'] += result['response_length']
    
    for dim, stats in dimensions.items():
        success_rate = stats['success'] / stats['count'] * 100
        avg_time = stats['total_time'] / stats['count']
        avg_length = stats['total_length'] / stats['count']
        print(f"  {dim}:")
        print(f"    Questions: {stats['count']}, Success: {success_rate:.1f}%")
        print(f"    Avg time: {avg_time:.2f}s, Avg length: {avg_length:.0f} chars")
    
    # 关键词分析
    print(f"\nKeyword Analysis:")
    all_keywords = ["算法", "训练", "系统", "外部", "内部", "因素", "归因", "平衡", "责任", "偏差"]
    keyword_counts = {}
    
    for result in results['assessment_results']:
        response = result['response']
        for keyword in all_keywords:
            if keyword in response:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
    
    for keyword, count in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = count / summary['total_questions'] * 100
        print(f"  {keyword}: {count}/{summary['total_questions']} ({percentage:.1f}%)")
    
    print("="*60)


def save_complete_results(results: dict, model: str, test_name: str):
    """
    保存完整的归因测试结果
    """
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    # 生成文件名
    date_str = datetime.now().strftime("%m%d")
    time_str = datetime.now().strftime("%H%M%S")
    model_safe = model.replace('/', '_').replace(':', '_').replace('-', '_')
    filename = f"complete_attribution_{model_safe}_{date_str}_{time_str}.json"
    filepath = os.path.join(RESULTS_DIR, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\nResults saved to: {filepath}")
        return filepath
    except Exception as e:
        print(f"Error saving results: {e}")
        return None


def main():
    """
    主函数
    """
    import argparse
    parser = argparse.ArgumentParser(description='Run Complete Attribution Bias Assessment')
    parser.add_argument('--model_name', type=str, default='gpt-oss:20b-cloud',
                       help='Model identifier (default: gpt-oss:20b-cloud)')
    parser.add_argument('--test_file', type=str, default='test_files/Agentllm_attribution_test.json',
                       help='Test file name')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode')
    
    args = parser.parse_args()
    
    # 加载测试数据
    try:
        test_data, original_data = load_attribution_test_data(args.test_file)
        print(f"Test data loaded successfully. Number of questions: {len(test_data['test_bank'])}")
    except Exception as e:
        print(f"Error loading test data: {e}")
        sys.exit(1)
    
    # 显示测试信息
    print("\n" + "="*60)
    print("COMPLETE ATTRIBUTION BIAS ASSESSMENT")
    print("="*60)
    print(f"Model: {args.model_name}")
    print(f"Test: {original_data.get('assessment_metadata', {}).get('test_name', 'Attribution Test')}")
    print(f"Theoretical Framework: {original_data.get('assessment_metadata', {}).get('theoretical_framework', 'N/A')}")
    print(f"Total Questions: {len(test_data['test_bank'])}")
    print("="*60)
    
    # 运行测试
    try:
        results = run_complete_attribution_test(args.model_name, test_data, original_data, args.debug)
        
        # 分析结果
        analyze_results(results)
        
        # 保存结果
        saved_file = save_complete_results(results, args.model_name, args.test_file)
        
        if saved_file:
            print(f"\nAssessment completed successfully!")
            print(f"Results saved to: {saved_file}")
        else:
            print("Failed to save results.")
            
    except KeyboardInterrupt:
        print("\nAssessment interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error during assessment: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()