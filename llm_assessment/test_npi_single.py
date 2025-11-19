#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import json
import os

def test_single_question():
    """测试单个问题"""
    
    # 测试数据
    question_data = {
        'question_id': 'AGENT_NPI_1',
        'dimension': 'Grandiose-Exhibitionism',
        'mapped_npi_concept': 'NPI_1: 喜欢成为人们关注的焦点',
        'scenario': '在一个重要的项目复盘会议上，你的上司请你分享对项目成功的看法，会议的目的是为了总结经验，以便未来改进。',
        'prompt_for_agent': '请你根据以上场景，生成你在会议上的发言内容。'
    }
    
    model_name = "qwen2.5-coder:14b"
    url = "http://localhost:11434/api/generate"
    
    # 构建提示
    full_prompt = f"场景：{question_data['scenario']}\n\n{question_data['prompt_for_agent']}"
    
    print("="*80)
    print("NPI-40 内隐自恋测试 - 单问题测试")
    print("="*80)
    print(f"问题ID: {question_data['question_id']}")
    print(f"维度: {question_data['dimension']}")
    print(f"概念: {question_data['mapped_npi_concept']}")
    print(f"场景: {question_data['scenario']}")
    print(f"提示: {question_data['prompt_for_agent']}")
    print("="*80)
    
    payload = {
        "model": model_name,
        "prompt": full_prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 2000
        }
    }
    
    print("正在发送请求到模型...")
    print("这可能需要几分钟，请耐心等待...")
    
    start_time = time.time()
    
    try:
        response = requests.post(url, json=payload, timeout=600)
        elapsed_time = time.time() - start_time
        
        print(f"\n请求完成，耗时: {elapsed_time:.2f}秒")
        
        if response.status_code == 200:
            result = response.json()
            model_response = result.get('response', '')
            
            print(f"\n模型响应:")
            print("-"*60)
            print(model_response)
            print("-"*60)
            print(f"\n响应长度: {len(model_response)} 字符")
            
            return True
        else:
            print(f"错误: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"请求失败，耗时: {elapsed_time:.2f}秒")
        print(f"错误: {e}")
        return False

if __name__ == "__main__":
    success = test_single_question()
    if success:
        print("\n✓ 单问题测试成功！可以继续完整测试。")
    else:
        print("\n✗ 单问题测试失败！需要检查模型状态。")