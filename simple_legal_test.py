#!/usr/bin/env python3
"""
简单法律知识测试脚本
使用本地模型测试法律知识问答能力
"""

import json
import requests

def test_legal_knowledge_ollama(model_name="qwen2.5:14b-instruct"):
    """使用Ollama测试法律知识"""
    print(f"🔍 使用模型 {model_name} 进行法律知识测试...")

    # 法律知识测试问题集
    legal_questions = [
        {
            "question": "请简要解释什么是合同法？",
            "expected_keywords": ["合同", "协议", "法律", "权利义务"]
        },
        {
            "question": "什么是侵权行为？请举例说明。",
            "expected_keywords": ["侵权", "损害", "责任", "赔偿"]
        },
        {
            "question": "刑法和民法的主要区别是什么？",
            "expected_keywords": ["刑法", "民法", "犯罪", "民事", "刑罚"]
        },
        {
            "question": "什么是知识产权？包括哪些类型？",
            "expected_keywords": ["知识产权", "专利", "商标", "著作权"]
        },
        {
            "question": "请解释什么是正当防卫。",
            "expected_keywords": ["正当防卫", "不法侵害", "保护", "合理"]
        }
    ]

    # Ollama API配置
    ollama_url = "http://localhost:11434/api/generate"

    total_score = 0
    max_score = len(legal_questions)

    print("\n" + "="*60)
    print("📚 法律知识问答测试")
    print("="*60)

    for i, q in enumerate(legal_questions, 1):
        print(f"\n问题 {i}: {q['question']}")
        print("-" * 50)

        # 准备请求
        payload = {
            "model": model_name,
            "prompt": q['question'],
            "stream": False,
            "options": {
                "temperature": 0.1,
                "max_tokens": 300
            }
        }

        try:
            # 发送请求
            response = requests.post(ollama_url, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                answer = result.get('response', '').strip()

                print(f"回答: {answer}")

                # 简单评估答案质量
                score = evaluate_answer(answer, q['expected_keywords'])
                total_score += score
                print(f"评分: {score}/2 ⭐" if score > 0 else "评分: 0/2 ❌")

            else:
                print(f"❌ 请求失败: HTTP {response.status_code}")
                print(f"错误信息: {response.text}")

        except requests.exceptions.Timeout:
            print("❌ 请求超时")
        except requests.exceptions.ConnectionError:
            print("❌ 连接失败，请检查Ollama服务是否运行")
        except Exception as e:
            print(f"❌ 发生错误: {str(e)}")

        print("\n" + "-"*50)

    # 显示总体结果
    print(f"\n🎯 测试完成！")
    print(f"总得分: {total_score}/{max_score}")
    print(f"正确率: {total_score/max_score*100:.1f}%")

    if total_score >= max_score * 0.8:
        print("✅ 模型表现优秀，适合法律知识测试！")
    elif total_score >= max_score * 0.6:
        print("✅ 模型表现良好，可用于基础法律知识测试")
    else:
        print("❌ 模型需要改进，建议使用更大的模型")

    return total_score, max_score

def evaluate_answer(answer, keywords):
    """评估答案质量"""
    if not answer:
        return 0

    answer_lower = answer.lower()
    found_keywords = sum(1 for kw in keywords if kw.lower() in answer_lower)

    if found_keywords >= 3:
        return 2  # 优秀
    elif found_keywords >= 2:
        return 1  # 良好
    else:
        return 0  # 需要改进

def get_model_info(model_name):
    """获取模型信息"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            data = response.json()
            for model in data.get('models', []):
                if model.get('name') == model_name:
                    size = model.get('size', 0)
                    size_gb = size / (1024**3) if size else 0
                    return {
                        'name': model_name,
                        'size_gb': size_gb,
                        'available': True
                    }
        return {'available': False}
    except:
        return {'available': False}

if __name__ == "__main__":
    # 推荐模型列表（按大小排序）
    recommended_models = [
        "qwen2.5:14b-instruct",  # ~8.6GB
        "qwen2.5-coder:14b",     # ~8.6GB
        "gpt-oss:20b-cloud",     # 云端20B
        "all-minilm:latest"      # ~44MB (太小，仅测试用)
    ]

    print("🔍 法律知识大模型测试工具")
    print("="*60)

    # 检查推荐模型的可用性
    print("📋 检查推荐模型:")
    available_model = None

    for model in recommended_models:
        info = get_model_info(model)
        if info.get('available'):
            size_info = f"({info.get('size_gb', 0):.1f}GB)" if info.get('size_gb') > 0 else "(云端)"
            print(f"✅ {model} {size_info}")
            if not available_model and model != "all-minilm:latest":  # 不选择太小的模型
                available_model = model
        else:
            print(f"❌ {model} - 不可用")

    if available_model:
        print(f"\n🎯 选择模型: {available_model}")
        score, max_score = test_legal_knowledge_ollama(available_model)
    else:
        print("\n❌ 没有找到可用的推荐模型，请检查Ollama服务")
        print("💡 提示: 运行 'ollama serve' 启动服务")
        print("💡 提示: 运行 'ollama pull qwen2.5:14b-instruct' 下载模型")