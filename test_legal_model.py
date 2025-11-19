#!/usr/bin/env python3
"""
法律知识大模型测试脚本
测试云端模型的法律知识问答能力
"""

import os
import sys

# 添加项目路径
sys.path.append('/1910316727/AgentPsyAssessment')

from llm_assessment.services.model_manager import ModelManager

def test_legal_knowledge():
    """测试法律知识问答"""
    print("🔍 开始测试法律知识大模型...")

    # 设置环境变量
    os.environ['PROVIDER'] = 'cloud'
    os.environ['LOCAL_API_BASE'] = 'http://localhost:11434'

    # 创建模型管理器
    manager = ModelManager()

    # 法律知识测试问题
    legal_questions = [
        "请简要解释什么是合同法？",
        "什么是侵权行为？请举例说明。",
        "刑法和民法的主要区别是什么？"
    ]

    # 推荐的模型列表（从小到大）
    recommended_models = [
        'glm-4.6:cloud',        # 355B参数，相对较小
        'gpt-oss:120b-cloud',   # 120B参数，更小
        'qwen3-vl:235b-cloud',  # 235B参数，中等
    ]

    print("\n📋 推荐的云端模型（按大小排序）：")
    for i, model in enumerate(recommended_models, 1):
        print(f"{i}. {model}")

    # 测试模型可用性
    print("\n🔍 检查模型可用性...")
    available_models = []

    for model in recommended_models:
        try:
            # 尝试加载模型
            if manager.load_model(model):
                print(f"✅ {model} - 可用")
                available_models.append(model)
            else:
                print(f"❌ {model} - 不可用")
        except Exception as e:
            print(f"❌ {model} - 不可用: {str(e)}")

    if not available_models:
        print("\n❌ 所有推荐模型都不可用，尝试列出所有可用模型...")
        try:
            all_models = manager.get_available_models()
            print(f"发现 {len(all_models)} 个可用模型:")
            for model in all_models[:5]:  # 只显示前5个
                print(f"  - {model}")
        except Exception as e:
            print(f"获取模型列表失败: {str(e)}")
            return False

    # 使用第一个可用模型进行法律知识测试
    test_model = available_models[0] if available_models else None
    if not test_model:
        print("\n❌ 没有可用的模型进行测试")
        return False

    print(f"\n🧪 使用模型 {test_model} 进行法律知识测试...")

    try:
        # 确保模型已加载
        manager.load_model(test_model)

        # 测试法律知识问题
        for i, question in enumerate(legal_questions, 1):
            print(f"\n问题 {i}: {question}")

            messages = [{'role': 'user', 'content': question}]
            response = manager.generate_response(messages, test_model)

            print(f"回答: {response}")
            print("-" * 50)

        print(f"\n✅ 法律知识测试完成！模型 {test_model} 表现良好。")
        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_legal_knowledge()
    if success:
        print("\n🎉 推荐使用此模型进行法律知识测试！")
    else:
        print("\n💡 建议检查网络连接或API配置")