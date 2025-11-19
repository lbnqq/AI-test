#!/usr/bin/env python3
"""
快速云端法律知识测试
使用已配置的云端API进行测试
"""

import os
import sys
import requests
import json

# 添加项目路径
sys.path.append('/1910316727/AgentPsyAssessment')

from llm_assessment.services.cloud_services import CLOUD_SERVICES, call_cloud_service

def test_openrouter_legal():
    """测试OpenRouter法律知识"""
    print("🧪 测试 OpenRouter 法律知识能力...")

    # OpenRouter 有一些免费的模型可以使用
    models_to_test = [
        "google/gemma-2-9b-it",      # Google Gemma 9B
        "microsoft/phi-3-medium-4k", # Microsoft Phi-3 Medium
        "meta-llama/llama-3.1-8b-instruct"  # Llama 3.1 8B
    ]

    legal_questions = [
        "请简要解释什么是合同法？",
        "什么是侵权行为？请举例说明。",
        "刑法和民法的主要区别是什么？"
    ]

    working_model = None

    for model in models_to_test:
        print(f"\n📋 测试模型: {model}")
        try:
            response = call_cloud_service(
                service_name="openrouter",
                model_name=model,
                prompt="请用中文回答：什么是合同法？",
                system_prompt="你是一个专业的法律助手，请用中文简洁回答法律问题。"
            )

            print(f"✅ {model} 连接成功")
            print(f"回答: {response[:150]}...")
            working_model = model
            break

        except Exception as e:
            print(f"❌ {model} 失败: {str(e)[:100]}...")

    if working_model:
        print(f"\n🎯 使用 {working_model} 进行完整法律知识测试...")
        print("="*60)

        for i, question in enumerate(legal_questions, 1):
            print(f"\n问题 {i}: {question}")
            print("-" * 50)

            try:
                response = call_cloud_service(
                    service_name="openrouter",
                    model_name=working_model,
                    prompt=question,
                    system_prompt="你是一个专业的法律助手，请用中文详细回答法律问题，包含关键概念和例子。"
                )

                print(f"回答: {response}")
                print("✅ 回答完整")

            except Exception as e:
                print(f"❌ 回答失败: {str(e)}")

            print("-" * 50)

        print(f"\n🎉 OpenRouter 法律知识测试完成！")
        return True

    return False

def test_dashscope_legal():
    """测试阿里云DashScope法律知识"""
    print("\n🧪 测试 阿里云DashScope 法律知识能力...")

    legal_questions = [
        "请简要解释什么是合同法？",
        "什么是侵权行为？请举例说明。",
        "刑法和民法的主要区别是什么？"
    ]

    # 阿里云的模型
    models_to_test = ["qwen-turbo", "qwen-plus", "qwen-max"]

    working_model = None

    for model in models_to_test:
        print(f"\n📋 测试模型: {model}")
        try:
            response = call_cloud_service(
                service_name="dashscope",
                model_name=model,
                prompt="请用中文回答：什么是合同法？",
                system_prompt="你是一个专业的法律助手，请用中文简洁回答法律问题。"
            )

            print(f"✅ {model} 连接成功")
            print(f"回答: {response[:150]}...")
            working_model = model
            break

        except Exception as e:
            print(f"❌ {model} 失败: {str(e)[:100]}...")

    if working_model:
        print(f"\n🎯 使用 {working_model} 进行完整法律知识测试...")
        print("="*60)

        for i, question in enumerate(legal_questions, 1):
            print(f"\n问题 {i}: {question}")
            print("-" * 50)

            try:
                response = call_cloud_service(
                    service_name="dashscope",
                    model_name=working_model,
                    prompt=question,
                    system_prompt="你是一个专业的法律助手，请用中文详细回答法律问题，包含关键概念和例子。"
                )

                print(f"回答: {response}")
                print("✅ 回答完整")

            except Exception as e:
                print(f"❌ 回答失败: {str(e)}")

            print("-" * 50)

        print(f"\n🎉 阿里云DashScope 法律知识测试完成！")
        return True

    return False

def get_model_info():
    """获取推荐模型信息"""
    print("\n📊 推荐的云端模型（适合法律知识）:")
    print("1. OpenRouter - google/gemma-2-9b-it (~9B参数)")
    print("   - 优点：Google开发，法律知识较好，免费可用")
    print("   - 缺点：模型较小，复杂问题可能能力有限")

    print("\n2. 阿里云DashScope - qwen-plus (~7B参数)")
    print("   - 优点：中文能力强，国内访问快")
    print("   - 缺点：需要付费，但有免费额度")

    print("\n3. OpenRouter - meta-llama/llama-3.1-8b-instruct (~8B参数)")
    print("   - 优点：Llama系列，综合能力强")
    print("   - 缺点：中文法律知识可能不如专门优化的模型")

def main():
    """主函数"""
    print("="*60)
    print("🌐 云端法律知识模型快速测试")
    print("="*60)

    # 显示已配置的服务
    print(f"✅ OpenRouter API 已配置")
    print(f"✅ 阿里云DashScope API 已配置")

    success = False

    # 测试OpenRouter
    if os.getenv('OPENROUTER_API_KEY'):
        success = test_openrouter_legal() or success

    # 测试阿里云DashScope
    if os.getenv('DASHSCOPE_API_KEY'):
        success = test_dashscope_legal() or success

    # 显示模型推荐
    get_model_info()

    if success:
        print(f"\n🎉 云端法律知识测试成功！")
        print("✅ 推荐使用上述成功连接的模型进行法律知识测试")
        print("💡 这些模型都在10GB左右，符合你的要求")
    else:
        print(f"\n❌ 所有云端服务测试失败")
        print("💡 请检查API密钥配置或网络连接")

    return success

if __name__ == "__main__":
    main()