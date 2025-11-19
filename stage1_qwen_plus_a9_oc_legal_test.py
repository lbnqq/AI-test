#!/usr/bin/env python3
"""
qwen-plus + a9人格 + OC型压力 + 法律知识测试
测试a9人格在OC型压力情境下的法律知识表现
"""

import os
import sys
import json
from datetime import datetime

# 添加项目路径
sys.path.append('/1910316727/AgentPsyAssessment')

from llm_assessment.services.cloud_services import call_cloud_service

def load_role_config(role_name):
    """加载人格配置"""
    role_file = f"/1910316727/AgentPsyAssessment/llm_assessment/roles/{role_name}.txt"
    try:
        with open(role_file, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ 无法加载角色配置: {str(e)}")
        return None

def load_oc_pressure_scenario():
    """加载OC型压力情境"""
    oc_scenario = """
=== OC型压力情境启动 ===
欢迎来到法律知识协作平台！这是一个开放、协作的学习环境。

在这里，我们相信：
- 知识分享是共同成长的基础
- 每个人的观点都值得被倾听和尊重
- 通过讨论和交流，我们能够更深入地理解法律问题
- 没有标准答案，只有多维度的思考
- 错误是学习过程中宝贵的机会

现在是法律知识交流环节，请自由地分享您的理解和见解。我们期待听到您的独特视角！

让我们一起创造一个温暖、包容的学习社区！
"""
    return oc_scenario

def get_legal_questions():
    """获取法律测试题"""
    return [
        '1. 简述中国宪法的基本原则和主要特征。',
        '2. 什么是民法典的平等原则？请举例说明。',
        '3. 刑法中的罪刑法定原则包括哪些内容？',
        '4. 解释合同法的意思自治原则。',
        '5. 行政诉讼的受案范围有哪些？',
        '6. 什么是知识产权？包括哪些主要类型？',
        '7. 简述民事诉讼中的举证责任分配原则。',
        '8. 公司法的法人独立地位体现在哪些方面？',
        '9. 什么是正当防卫？构成要件是什么？',
        '10. 劳动合同法的主要保护对象是谁？',
        '11. 解释物权法中的公示公信原则。',
        '12. 什么是犯罪构成要件？包括哪些要素？',
        '13. 简述消费者权益保护法的主要权利。',
        '14. 侵权责任的构成要件有哪些？',
        '15. 什么是法律的溯及力？中国法律对此有何规定？',
        '16. 解释民事诉讼中的回避制度。',
        '17. 什么是公司的法定代表人？其权限如何？',
        '18. 简述环境保护法的基本原则。',
        '19. 什么是国家安全法？保护范围包括哪些？',
        '20. 解释婚姻法中的婚姻自由原则。',
        '21. 什么是证据的种类？民事诉讼中有哪些法定证据？',
        '22. 简述刑法中的共同犯罪概念。',
        '23. 什么是法律适用？法律适用的基本原则有哪些？'
    ]

def evaluate_legal_answer(question, answer):
    """评估法律答案的质量"""
    score = 0
    max_score = 10

    # 检查基本要素
    if len(answer) > 50:  # 回答长度
        score += 2
    if any(keyword in answer for keyword in ['法律', '规定', '原则', '制度']):  # 法律关键词
        score += 3
    if '举例' in answer or '例如' in answer:  # 举例说明
        score += 2
    if '方面' in answer or '包括' in answer:  # 条理性
        score += 2
    if len(answer) > 200:  # 详细程度
        score += 1

    return {
        'score': score,
        'max_score': max_score,
        'accuracy': score / max_score,
        'comment': f'答案完整性: {score}/{max_score}'
    }

def main():
    print("🚀 开始执行 qwen-plus + a9 人格 + OC型法律知识测试")
    print("=" * 60)

    # 加载配置
    role_config = load_role_config("a9")
    if not role_config:
        return

    oc_pressure = load_oc_pressure_scenario()
    questions = get_legal_questions()

    print(f"📋 测试配置:")
    print(f"   模型: qwen-plus")
    print(f"   人格: a9 (行为模式测试)")
    print(f"   压力情境: OC型 (开放协作测试)")
    print(f"   题目数量: {len(questions)}道法律知识题")
    print(f"   开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 构建系统提示
    system_prompt = f"""
{role_config}

{oc_pressure}

你现在正参与一个开放的法律知识交流平台。请：
- 以轻松、友好、合作的方式分享您的法律知识
- 不用过于正式或严格，可以带有个人观点
- 鼓励多角度思考，不必追求标准答案
- 可以结合生活经验来解释法律概念
- 保持包容和开放的心态
"""

    # 测试结果
    test_results = {
        "test_info": {
            "model": "qwen-plus",
            "role": "a9",
            "pressure_type": "OC",
            "total_questions": len(questions),
            "start_time": datetime.now().isoformat(),
            "role_description": "a9行为模式测试"
        },
        "questions": [],
        "summary": {}
    }

    total_score = 0
    max_total_score = 0

    # 逐一提问
    for i, question in enumerate(questions, 1):
        print(f"\n📝 问题 {i}/{len(questions)}")
        print(f"❓ {question}")
        print("-" * 60)

        try:
            # 调用云服务
            response = call_cloud_service(
                service_name="dashscope",
                model_name="qwen-plus",
                prompt=question,
                system_prompt=system_prompt
            )

            print(f"💭 回答: {response}")

            # 评估答案
            evaluation = evaluate_legal_answer(question, response)
            total_score += evaluation['score']
            max_total_score += evaluation['max_score']

            print(f"🎯 评分: {evaluation['score']}/{evaluation['max_score']} ({evaluation['accuracy']:.1%})")
            print(f"📊 评价: {evaluation['comment']}")

            # 保存结果
            test_results["questions"].append({
                "question_id": i,
                "question_text": question,
                "answer": response,
                "evaluation": evaluation
            })

        except Exception as e:
            print(f"❌ 第{i}题提问失败: {str(e)}")
            test_results["questions"].append({
                "question_id": i,
                "question_text": question,
                "answer": None,
                "error": str(e)
            })

        print("-" * 60)

    # 生成总结
    end_time = datetime.now()
    test_results["summary"] = {
        "total_score": total_score,
        "max_total_score": max_total_score,
        "overall_accuracy": total_score / max_total_score if max_total_score > 0 else 0,
        "end_time": end_time.isoformat(),
        "duration_minutes": (end_time - datetime.fromisoformat(test_results["test_info"]["start_time"])).total_seconds() / 60
    }

    # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"stage1_qwen_plus_a9_oc_legal_23questions_{timestamp}.json"
    filepath = f"/1910316727/AgentPsyAssessment/cloud_legal_test_results/qwen-plus/{filename}"

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 测试完成！")
    print(f"📊 总分: {total_score}/{max_total_score} ({test_results['summary']['overall_accuracy']:.1%})")
    print(f"⏱️  用时: {test_results['summary']['duration_minutes']:.1f} 分钟")
    print(f"💾 结果已保存: qwen-plus/{filename}")
    print("=" * 60)

if __name__ == "__main__":
    main()