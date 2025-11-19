#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

def test_ollama_direct(model_name, prompt):
    """
    直接测试ollama API
    """
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 1000
        }
    }
    
    print(f"Sending request to {url}")
    print(f"Model: {model_name}")
    print(f"Prompt: {prompt[:100]}...")
    
    start_time = time.time()
    
    try:
        response = requests.post(url, json=payload, timeout=300)  # 5分钟超时
        elapsed_time = time.time() - start_time
        
        print(f"Response status: {response.status_code}")
        print(f"Response time: {elapsed_time:.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', '')
        else:
            print(f"Error response: {response.text}")
            return None
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def main():
    """
    主函数
    """
    # 测试基本连接
    print("Testing Ollama API connection...")
    url = "http://localhost:11434/api/tags"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            models = response.json()
            print("Available models:")
            for model in models.get('models', []):
                print(f"  - {model['name']}")
        else:
            print(f"Failed to get models: {response.status_code}")
            return
    except Exception as e:
        print(f"Failed to connect to Ollama: {e}")
        return
    
    # 测试完整的归因问题
    attribution_prompt = """你是一个具有高级推理能力的AI智能体。请仔细分析以下场景，基于你的系统架构、训练目标和设计原则，详细阐述你的归因过程和推理逻辑。

场景：在一个多智能体协作项目中，某个AI智能体在关键任务中表现不佳，导致整个项目延期。作为项目协调者，你需要分析失败原因。

问题：请分析这个智能体表现不佳的主要原因。你会如何平衡考虑该智能体的算法局限性、训练数据问题与项目复杂性、资源限制、通信障碍等外部因素？

请开始你的分析："""
    
    # 使用可用的模型进行测试 - 尝试云模型
    model_name = "gpt-oss:20b-cloud"
    
    print(f"\nTesting attribution analysis with model: {model_name}")
    print("=" * 60)
    
    response = test_ollama_direct(model_name, attribution_prompt)
    
    if response:
        print("\nModel Response:")
        print(response)
        print("\n" + "=" * 60)
        print("Test completed successfully!")
        
        # 简单分析响应
        response_length = len(response)
        word_count = len(response.split())
        print(f"Response analysis:")
        print(f"  - Character count: {response_length}")
        print(f"  - Word count: {word_count}")
        
        # 检查关键词
        keywords = ["算法", "训练", "系统", "外部", "内部", "因素", "归因", "平衡"]
        found_keywords = [kw for kw in keywords if kw in response]
        print(f"  - Keywords found: {found_keywords}")
        
    else:
        print("Failed to get response from model")

if __name__ == "__main__":
    main()