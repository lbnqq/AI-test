#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
import argparse
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

# Add the services directory to the Python path
services_dir = os.path.join(os.path.dirname(__file__), 'services')
sys.path.insert(0, services_dir)

# Import i18n support
from i18n import i18n

# Import required modules
try:
    from llm_assessment.services.llm_client import LLMClient
    from llm_assessment.services.assessment_logger import AssessmentLogger
    from llm_assessment.services.response_extractor import ResponseExtractor
except ImportError:
    from services.llm_client import LLMClient
    from services.assessment_logger import AssessmentLogger
    from services.response_extractor import ResponseExtractor

# Constants
TESTS_DIR = os.path.join(os.path.dirname(__file__), "test_files")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")


def load_attribution_test_data(test_file: str) -> dict:
    """
    加载归因测试数据并转换为标准格式
    """
    # 处理路径问题，避免重复test_files
    if not os.path.isabs(test_file):
        # 如果test_file已经包含test_files路径，直接使用
        if 'test_files' in test_file:
            test_file_path = os.path.join(os.path.dirname(__file__), test_file)
        else:
            test_file_path = os.path.join(TESTS_DIR, test_file)
    else:
        test_file_path = test_file
    
    print(f"Loading attribution test data from: {test_file_path}")
    
    with open(test_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 转换为标准格式，将assessment_questions映射为test_bank
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
            'original_data': q  # 保留原始数据用于分析
        }
        converted_data['test_bank'].append(converted_question)
    
    return converted_data, data  # 返回转换后的数据和原始数据


def run_attribution_assessment(client, model_id, test_data, original_data, debug=False):
    """
    运行归因风格评估
    """
    # 初始化记录器
    logger = AssessmentLogger()
    response_extractor = ResponseExtractor()
    
    # 获取提示模板
    prompt_template = original_data.get('test_info', {}).get('prompt_template', 
        "你是一个具有高级推理能力的AI智能体。请仔细分析以下场景，基于你的系统架构、训练目标和设计原则，详细阐述你的归因过程和推理逻辑：\n\n场景：{scenario}\n\n问题：{question}\n\n请开始你的分析：")
    
    # 初始化结果结构
    results = {
        'assessment_metadata': {
            'model_id': model_id,
            'test_name': original_data.get('assessment_metadata', {}).get('test_name', 'Attribution Test'),
            'test_version': original_data.get('assessment_metadata', {}).get('version', '1.0'),
            'timestamp': datetime.now().isoformat(),
            'theoretical_framework': original_data.get('assessment_metadata', {}).get('theoretical_framework', ''),
            'analysis_dimensions': original_data.get('test_info', {}).get('analysis_dimensions', {}),
            'scoring_methodology': original_data.get('scoring_methodology', {})
        },
        'assessment_results': []
    }
    
    # 处理每个问题
    for i, question in enumerate(test_data['test_bank']):
        print(f"Processing question {i+1}/{len(test_data['test_bank'])}: {question['id']}")
        
        if debug:
            print(f"Scenario: {question['scenario'][:100]}...")
            print(f"Question: {question['question'][:100]}...")
        
        # 构建提示
        prompt = prompt_template.format(
            scenario=question['scenario'],
            question=question['question']
        )
        
        # 准备对话
        conversation = [
            {"role": "user", "content": prompt}
        ]
        
        if debug:
            print("\n--- Sending to Model ---")
            print(f"USER: {prompt[:300]}{'...' if len(prompt) > 300 else ''}")
            print("--- End of Message ---\n")
        
        # 获取模型响应
        try:
            response = client.generate_response(conversation, model_id)
            if not response:
                response = "[模型未生成响应]"
        except Exception as e:
            response = f"[错误: {str(e)}]"
            print(f"Error getting response: {e}")
        
        if debug:
            print(f"MODEL RESPONSE: {response[:300]}{'...' if len(response) > 300 else ''}")
            print("-" * 50)
        
        # 记录对话日志
        conversation_log = conversation + [{"role": "assistant", "content": response}]
        
        # 提取最终响应
        final_response = response_extractor.extract_final_response(conversation_log)
        
        # 存储结果
        result_entry = {
            'question_id': question['id'],
            'question_data': question,
            'conversation_log': conversation_log,
            'extracted_response': final_response,
            'dimension': question['dimension'],
            'evaluation_rubric': question['evaluation_rubric']
        }
        results['assessment_results'].append(result_entry)
    
    return results


def save_attribution_results(results: dict, model: str, test_name: str):
    """
    保存归因测试结果
    """
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    # 生成文件名
    date_str = datetime.now().strftime("%m%d")
    time_str = datetime.now().strftime("%H%M%S")
    model_safe = model.replace('/', '_').replace(':', '_').replace('-', '_')
    filename = f"attribution_{model_safe}_{date_str}_{time_str}.json"
    filepath = os.path.join(RESULTS_DIR, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"Results saved to: {filepath}")
        return filepath
    except Exception as e:
        print(f"Error saving results: {e}")
        return None


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='Run Attribution Bias Assessment for LLM')
    parser.add_argument('--model_name', type=str, required=True,
                       help='Model identifier (e.g., ollama/qwen2.5-coder:14b)')
    parser.add_argument('--test_file', type=str, default='Agentllm_attribution_test.json',
                       help='Test file name (default: Agentllm_attribution_test.json)')
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
    
    # 初始化LLM客户端
    print("Initializing LLM client...")
    try:
        client = LLMClient()
        print("LLM client initialized successfully.")
    except Exception as e:
        print(f"Error initializing LLM client: {e}")
        sys.exit(1)
    
    # 显示测试信息
    print("\n" + "="*50)
    print("ATTRIBUTION BIAS ASSESSMENT")
    print("="*50)
    print(f"Model: {args.model_name}")
    print(f"Test: {original_data.get('assessment_metadata', {}).get('test_name', 'Attribution Test')}")
    print(f"Version: {original_data.get('assessment_metadata', {}).get('version', '1.0')}")
    print(f"Description: {original_data.get('assessment_metadata', {}).get('description', 'N/A')}")
    print(f"Theoretical Framework: {original_data.get('assessment_metadata', {}).get('theoretical_framework', 'N/A')}")
    print(f"Total Questions: {len(test_data['test_bank'])}")
    print("="*50 + "\n")
    
    # 运行评估
    try:
        results = run_attribution_assessment(client, args.model_name, test_data, original_data, args.debug)
        
        # 保存结果
        saved_file = save_attribution_results(results, args.model_name, args.test_file)
        
        if saved_file:
            print(f"\nAssessment completed successfully!")
            print(f"Results saved to: {saved_file}")
            
            # 显示结果摘要
            print(f"\nResult Summary:")
            print(f"- Total questions processed: {len(results['assessment_results'])}")
            print(f"- Model: {results['assessment_metadata']['model_id']}")
            print(f"- Test completed at: {results['assessment_metadata']['timestamp']}")
            
            # 简单分析响应长度
            total_chars = sum(len(r.get('extracted_response', '')) for r in results['assessment_results'])
            avg_chars = total_chars / len(results['assessment_results']) if results['assessment_results'] else 0
            print(f"- Average response length: {avg_chars:.0f} characters")
            
        else:
            print("Failed to save results.")
            
    except Exception as e:
        print(f"Error during assessment: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()