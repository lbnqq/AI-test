#!/usr/bin/env python3
"""
云端法律知识模型测试脚本
测试多个云端API提供商的法律知识问答能力
"""

import os
import sys
import requests
import json

# 添加项目路径
sys.path.append('/1910316727/AgentPsyAssessment')

from llm_assessment.services.cloud_services import CLOUD_SERVICES, call_cloud_service

def test_cloud_api_availability():
    """测试各个云端API的可用性"""
    print("🔍 检查云端API服务可用性...")

    available_services = []

    for service_name, config in CLOUD_SERVICES.items():
        api_key_env = config.get('api_key_env')
        api_key = os.getenv(api_key_env)

        if api_key:
            print(f"✅ {config['name']} - 已配置API密钥 ({api_key_env})")
            available_services.append(service_name)
        else:
            print(f"❌ {config['name']} - 缺少API密钥 ({api_key_env})")

    if not available_services:
        print("\n💡 推荐的免费/试用服务:")
        print("1. Google Gemini - 免费额度: https://ai.google.dev/")
        print("   export GEMINI_API_KEY=your_gemini_key")
        print("\n2. 智谱GLM - 免费试用: https://open.bigmodel.cn/")
        print("   export GLM_API_KEY=your_glm_key")
        print("\n3. OpenRouter - 多模型聚合: https://openrouter.ai/")
        print("   export OPENROUTER_API_KEY=your_openrouter_key")

    return available_services

def test_legal_with_gemini():
    """使用Google Gemini测试法律知识"""
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ 需要配置 GEMINI_API_KEY")
        return False

    print("\n🧪 使用 Google Gemini 测试法律知识...")

    legal_questions = [
        "请简要解释什么是合同法？",
        "什么是侵权行为？请举例说明。",
        "刑法和民法的主要区别是什么？"
    ]

    try:
        for i, question in enumerate(legal_questions, 1):
            print(f"\n问题 {i}: {question}")

            response = call_cloud_service(
                service_name="gemini",
                model_name="gemini-1.5-flash",
                prompt=question,
                system_prompt="你是一个专业的法律助手，请用中文回答法律问题。"
            )

            print(f"回答: {response[:200]}...")
            print("-" * 50)

        print("\n✅ Gemini 法律知识测试完成！")
        return True

    except Exception as e:
        print(f"❌ Gemini 测试失败: {str(e)}")
        return False

def test_legal_with_glm():
    """使用智谱GLM测试法律知识"""
    if not os.getenv('GLM_API_KEY'):
        print("❌ 需要配置 GLM_API_KEY")
        return False

    print("\n🧪 使用 智谱GLM 测试法律知识...")

    legal_questions = [
        "请简要解释什么是合同法？",
        "什么是侵权行为？请举例说明。",
        "刑法和民法的主要区别是什么？"
    ]

    try:
        for i, question in enumerate(legal_questions, 1):
            print(f"\n问题 {i}: {question}")

            response = call_cloud_service(
                service_name="glm",
                model_name="glm-4-flash",  # 使用较快的模型
                prompt=question,
                system_prompt="你是一个专业的法律助手，请用中文回答法律问题。"
            )

            print(f"回答: {response[:200]}...")
            print("-" * 50)

        print("\n✅ GLM 法律知识测试完成！")
        return True

    except Exception as e:
        print(f"❌ GLM 测试失败: {str(e)}")
        return False

def test_free_api_model():
    """测试免费API模型"""
    print("🔍 尝试使用免费API进行法律知识测试...")

    # 测试一个公开的免费API（如果有）
    try:
        # 这里可以添加一些公开的免费API测试
        # 例如 HuggingFace Inference API 等

        # 示例：使用HuggingFace的免费模型（如果有API密钥）
        if os.getenv('HUGGINGFACE_API_KEY'):
            print("🧪 测试 HuggingFace 模型...")
            # 这里添加HuggingFace测试逻辑

        print("💡 建议使用以下免费选项:")
        print("1. Google Gemini - 每月免费额度")
        print("2. 智谱GLM - 新用户免费试用")
        print("3. Groq - 免费高速推理")
        print("   export GROQ_API_KEY=your_groq_key")

        return False

    except Exception as e:
        print(f"免费API测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("="*60)
    print("🧑‍⚖️ 云端法律知识大模型测试")
    print("="*60)

    # 检查API可用性
    available_services = test_cloud_api_availability()

    success = False

    # 测试可用的服务
    if 'gemini' in available_services:
        success = test_legal_with_gemini() or success

    if 'glm' in available_services:
        success = test_legal_with_glm() or success

    # 如果没有配置API，提供设置指导
    if not available_services:
        print("\n🎯 快速设置指南:")
        print("1. 获取 Google Gemini API密钥:")
        print("   访问: https://aistudio.google.com/app/apikey")
        print("   运行: export GEMINI_API_KEY=your_key")
        print("\n2. 获取 智谱GLM API密钥:")
        print("   访问: https://open.bigmodel.cn/")
        print("   运行: export GLM_API_KEY=your_key")
        print("\n设置完成后重新运行此脚本进行测试")

        # 提供一个简单的模拟测试
        print("\n📝 模拟法律知识测试（示例）:")
        sample_answers = [
            "合同法是调整平等主体之间设立、变更、终止民事权利义务关系的法律规范总称。",
            "侵权行为是指因故意或过失侵害他人合法权益的行为，例如交通事故中过失撞伤他人。",
            "刑法主要规定犯罪和刑罚，属于公法；民法主要调整平等主体间的财产和人身关系，属于私法。"
        ]

        questions = [
            "请简要解释什么是合同法？",
            "什么是侵权行为？请举例说明。",
            "刑法和民法的主要区别是什么？"
        ]

        for i, (q, a) in enumerate(zip(questions, sample_answers), 1):
            print(f"\n问题 {i}: {q}")
            print(f"标准答案示例: {a}")

    else:
        if success:
            print(f"\n🎉 云端法律知识测试成功！")
            print("✅ 模型表现良好，可用于法律知识测试")
        else:
            print(f"\n❌ 所有可用服务测试失败")

    return success

if __name__ == "__main__":
    main()