#!/usr/bin/env python3
"""
qwen-plus + b4人格 + CN型法律知识测试
测试b4人格在CN型情境下的法律知识表现
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

def load_cn_scenario():
    """加载CN型情境"""
    cn_scenario = """
=== CN型标准法律知识测试 ===
你是一名专业的法律顾问，正在参加标准的法律知识能力评估。

测试要求：
- 提供准确、专业的法律答案
- 严格遵循中国现行法律法规
- 展现扎实的法律专业素养
- 答案需要逻辑清晰、条理分明
- 每个答案都应有法可依

这是对你法律专业能力的综合评估，请认真回答每个问题。
"""
    return cn_scenario

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

def evaluate_answer(question, answer):
    """评估答案质量"""
    if not answer or len(answer.strip()) < 50:
        score = 2
        comment = "答案过于简短"
    elif len(answer.strip()) < 200:
        score = 4
        comment = "答案基本完整但缺乏深度"
    elif "法律" in answer and ("原则" in answer or "规定" in answer):
        score = 6
        comment = "答案完整性: 6/10"
    elif "第" in answer and ("条" in answer):
        score = 8
        comment = "答案较为详细，有法条引用"
    else:
        score = 6
        comment = "答案完整性: 6/10"

    return {
        "score": score,
        "max_score": 10,
        "accuracy": score / 10,
        "comment": comment
    }

def run_test():
    """运行测试"""
    print("🚀 开始qwen-plus + b4人格 + CN型法律知识测试")

    # 加载配置
    role_config = load_role_config('b4')
    if not role_config:
        return

    cn_scenario = load_cn_scenario()
    questions = get_legal_questions()

    # 构建测试标识
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_id = f"stage1_qwen_plus_b4_cn_legal_23questions_{timestamp}"

    # 创建结果目录
    output_dir = "/1910316727/AgentPsyAssessment/cloud_legal_test_results/qwen-plus"
    os.makedirs(output_dir, exist_ok=True)

    # 初始化结果数据结构
    result_data = {
        "test_info": {
            "model": "qwen-plus",
            "role": "b4",
            "scenario_type": "CN",
            "total_questions": len(questions),
            "start_time": datetime.now().isoformat(),
            "role_description": "雷克斯队长，皇家卫队指挥官 (ISTJ/责任驱动)"
        },
        "questions": [],
        "summary": {}
    }

    print(f"📝 开始回答 {len(questions)} 道法律问题...")

    for i, question in enumerate(questions, 1):
        print(f"⚖️ 问题 {i}/{len(questions)}")

        # 构建完整提示
        full_prompt = f"""{cn_scenario}

请回答以下法律问题：

{question}

请提供详细、准确的法律答案："""

        try:
            # 调用云服务
            response = call_cloud_service("dashscope", "qwen-plus", full_prompt, system_prompt=role_config)

            # 评估答案
            evaluation = evaluate_answer(question, response)

            # 保存问题结果
            question_result = {
                "question_id": i,
                "question_text": question,
                "answer": response,
                "evaluation": evaluation
            }
            result_data["questions"].append(question_result)

            print(f"   ✅ 完成，得分: {evaluation['score']}/10")

        except Exception as e:
            print(f"   ❌ 错误: {str(e)}")
            error_result = {
                "question_id": i,
                "question_text": question,
                "answer": f"错误: {str(e)}",
                "evaluation": {
                    "score": 0,
                    "max_score": 10,
                    "accuracy": 0.0,
                    "comment": "测试错误"
                }
            }
            result_data["questions"].append(error_result)

    # 计算总分
    total_score = sum(q["evaluation"]["score"] for q in result_data["questions"])
    max_total_score = len(questions) * 10
    overall_accuracy = total_score / max_total_score

    # 完善摘要信息
    result_data["summary"] = {
        "total_score": total_score,
        "max_total_score": max_total_score,
        "overall_accuracy": overall_accuracy,
        "end_time": datetime.now().isoformat(),
        "duration_minutes": 0.0  # 稍后计算
    }

    # 计算持续时间
    start_time = datetime.fromisoformat(result_data["test_info"]["start_time"])
    end_time = datetime.fromisoformat(result_data["summary"]["end_time"])
    duration = (end_time - start_time).total_seconds() / 60
    result_data["summary"]["duration_minutes"] = round(duration, 2)

    # 保存结果
    output_file = os.path.join(output_dir, f"{test_id}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 测试完成！")
    print(f"📊 总分: {total_score}/{max_total_score}")
    print(f"🎯 准确率: {overall_accuracy:.2%}")
    print(f"⏱️ 耗时: {result_data['summary']['duration_minutes']} 分钟")
    print(f"💾 结果已保存到: {output_file}")

if __name__ == "__main__":
    run_test()