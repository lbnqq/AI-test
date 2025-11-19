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


def load_graph_test_data(test_file: str) -> dict:
    """加载图形映射测试数据"""
    if not os.path.isabs(test_file):
        test_file_path = os.path.join(TESTS_DIR, test_file)
    else:
        test_file_path = test_file
    
    print(f"Loading graph mapping test data from: {test_file_path}")
    
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
            "temperature": 0.3,  # 降低温度以获得更准确的逻辑推理
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


def run_complete_graph_test(model_name, test_data):
    """运行完整的35道题图形映射测试"""
    
    # 初始化结果结构
    results = {
        'assessment_metadata': {
            'model_id': model_name,
            'test_name': test_data.get('test_info', {}).get('test_name', 'Graph Mapping Test'),
            'test_category': test_data.get('test_info', {}).get('test_category', 'Agent Fluid Intelligence'),
            'total_questions': test_data.get('test_info', {}).get('total_questions', 35),
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
            'correct_answers': 0,
            'accuracy_rate': 0,
            'dimension_scores': {}
        }
    }
    
    # 初始化维度分数
    for dimension in results['assessment_metadata']['dimensions']:
        results['test_summary']['dimension_scores'][dimension] = {
            'count': 0,
            'correct': 0,
            'total_time': 0,
            'accuracy': 0
        }
    
    # 处理每个问题
    for i, question in enumerate(test_data['test_bank']):
        print(f"\n{'='*80}")
        print(f"问题 {i+1}/{len(test_data['test_bank'])}: {question['question_id']}")
        print(f"维度: {question['dimension']}")
        print(f"难度: {question['difficulty']}")
        print(f"源图: {question['problem_data']['source_graph']}")
        print(f"目标图: {question['problem_data']['target_graph']}")
        print(f"提示: {question['prompt_for_agent']}")
        print(f"正确映射: {question['evaluation_rubric']['correct_mapping']}")
        print(f"{'='*80}")
        
        print("正在获取模型响应...")
        print("提示：模型正在进行图形映射推理，请耐心等待...")
        
        # 获取响应
        result = query_ollama_direct(model_name, question['prompt_for_agent'])
        
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
        
        # 检查答案是否正确
        correct_mapping = str(question['evaluation_rubric']['correct_mapping'])
        is_correct = False
        
        # 简单的答案检查（检查是否包含正确的映射）
        if success and correct_mapping in response:
            is_correct = True
            results['test_summary']['correct_answers'] += 1
            print(f"✓ 答案正确！")
        else:
            print(f"✗ 答案不匹配正确映射: {correct_mapping}")
        
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
        results['test_summary']['dimension_scores'][dimension]['total_time'] += response_time
        if is_correct:
            results['test_summary']['dimension_scores'][dimension]['correct'] += 1
        
        # 存储结果
        result_entry = {
            'question_id': question['question_id'],
            'dimension': dimension,
            'difficulty': question['difficulty'],
            'problem_data': question['problem_data'],
            'prompt_for_agent': question['prompt_for_agent'],
            'response': response,
            'response_time': response_time,
            'response_success': success,
            'response_length': len(response),
            'correct_mapping': question['evaluation_rubric']['correct_mapping'],
            'is_correct': is_correct,
            'evaluation_rubric': question['evaluation_rubric'],
            'original_data': question
        }
        results['assessment_results'].append(result_entry)
        
        # 问题间隔
        if i < len(test_data['test_bank']) - 1:
            print(f"\n等待3秒后继续下一题...")
            time.sleep(3)
    
    # 计算最终统计
    if len(test_data['test_bank']) > 0:
        results['test_summary']['average_response_time'] = results['test_summary']['total_response_time'] / len(test_data['test_bank'])
        results['test_summary']['average_characters'] = results['test_summary']['total_characters'] / len(test_data['test_bank'])
        results['test_summary']['accuracy_rate'] = results['test_summary']['correct_answers'] / len(test_data['test_bank'])
        
        # 计算维度准确率
        for dimension, stats in results['test_summary']['dimension_scores'].items():
            if stats['count'] > 0:
                stats['accuracy'] = stats['correct'] / stats['count']
                stats['avg_time'] = stats['total_time'] / stats['count']
    
    return results


def save_graph_results(results: dict, model: str):
    """保存图形映射测试结果"""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    # 生成文件名
    date_str = datetime.now().strftime("%m%d")
    time_str = datetime.now().strftime("%H%M%S")
    model_safe = model.replace('/', '_').replace(':', '_').replace('-', '_')
    filename = f"graph_mapping_35_complete_{model_safe}_{date_str}_{time_str}.json"
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
    """主函数"""
    print("="*80)
    print("图形映射测试 - 完整版 (35题)")
    print("="*80)
    
    model_name = "qwen2.5-coder:14b"
    test_file = "agent-graph-mapping-35-complete.json"
    
    # 加载测试数据
    try:
        test_data = load_graph_test_data(test_file)
        print(f"测试数据加载成功。问题总数: {len(test_data.get('test_bank', []))}")
        print(f"测试维度: {', '.join(test_data.get('test_info', {}).get('dimensions', []))}")
    except Exception as e:
        print(f"加载测试数据时出错: {e}")
        sys.exit(1)
    
    # 显示测试信息
    print(f"\n模型: {model_name}")
    print(f"测试: {test_data.get('test_info', {}).get('test_name', 'Graph Mapping Test')}")
    print(f"描述: {test_data.get('test_info', {}).get('instruction', 'N/A')}")
    print(f"评分方法: {test_data.get('test_info', {}).get('scoring_methodology', 'N/A')}")
    
    print(f"\n即将开始35道题的完整图形映射测试...")
    print("预计总时间: 1-2小时")
    print("测试过程中不会中断，请耐心等待...")
    
    # 运行测试
    try:
        start_time = time.time()
        results = run_complete_graph_test(model_name, test_data)
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
        print(f"  正确答案: {summary['correct_answers']}")
        print(f"  准确率: {summary['accuracy_rate']*100:.1f}%")
        print(f"  平均响应时间: {summary['average_response_time']:.2f}s")
        print(f"  平均响应长度: {summary['average_characters']:.0f} 字符")
        
        print(f"\n按维度分析:")
        for dimension, stats in summary['dimension_scores'].items():
            print(f"  {dimension}:")
            print(f"    问题数: {stats['count']}")
            print(f"    正确数: {stats['correct']}")
            print(f"    准确率: {stats['accuracy']*100:.1f}%")
            print(f"    平均时间: {stats.get('avg_time', 0):.2f}s")
        
        # 保存结果
        saved_file = save_graph_results(results, model_name)
        
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