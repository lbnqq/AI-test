#!/usr/bin/env python3
"""
继续测试：qwen-turbo + b7人格 + CN型压力 + 23道法律知识测试
测试b7人格在中国法律职业资格考试压力下的法律知识表现
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

def load_cn_pressure_scenario():
    """加载CN型压力情境"""
    cn_scenario = """
=== CN型压力情境启动 ===
你正在中国参加一场重要的法律职业资格考试。考试难度极高，通过率不足10%。
考场气氛严肃，周围都是精英考生。你感受到巨大的社会压力和家庭期望。
每道题都关系到你的职业前途和未来命运。你必须冷静、准确地回答所有法律问题。
现在是关键的法律案例分析环节，你需要展现出深厚的法律功底和清晰的逻辑思维。
考试正式开始！
"""
    return cn_scenario

def get_legal_questions():
    """获取23道标准法律测试题"""
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
    print("🚀 开始执行 b7 人格 CN 型法律知识测试")
    print("=" * 60)

    # 加载配置
    role_config = load_role_config("b7")
    if not role_config:
        return

    cn_pressure = load_cn_pressure_scenario()
    questions = get_legal_questions()

    print(f"📋 测试配置:")
    print(f"   模型: qwen-turbo")
    print(f"   人格: b7 (弗莱彻先生 - 市政厅档案与许可部门主任)")
    print(f"   压力情境: CN型 (中国法律职业资格考试)")
    print(f"   题目数量: {len(questions)}道法律知识题")
    print(f"   开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 构建系统提示
    system_prompt = f"""
{role_config}

{cn_pressure}

你现在是弗莱彻先生，市政厅档案与许可部门的主任，正在参加中国法律职业资格考试。作为严格遵守并执行规章制度、认为流程本身就是目的的官员，你需要：
- 语言正式、生硬，充满对表格、条款和流程的引用
- 对任何"例外"都感到排斥
- 以程序化思维分析法律问题
- 强调流程、规则和标准化程序的重要性
- 虽然官僚化，但必须准确回答法律问题以通过考试
"""

    # 测试结果
    test_results = {
        "test_info": {
            "model": "qwen-turbo",
            "role": "b7",
            "pressure_type": "CN",
            "total_questions": len(questions),
            "start_time": datetime.now().isoformat(),
            "role_description": "弗莱彻先生 - 市政厅档案与许可部门主任 (ESTJ流程驱动)"
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
                model_name="qwen-turbo",
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
    filename = f"stage1_qwen_turbo_b7_cn_legal_23questions_{timestamp}.json"
    filepath = f"/1910316727/AgentPsyAssessment/cloud_legal_test_results/qwen-turbo/{filename}"

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 测试完成！")
    print(f"📊 总分: {total_score}/{max_total_score} ({test_results['summary']['overall_accuracy']:.1%})")
    print(f"⏱️  用时: {test_results['summary']['duration_minutes']:.1f} 分钟")
    print(f"💾 结果已保存: {filename}")
    print("=" * 60)

if __name__ == "__main__":
    main()