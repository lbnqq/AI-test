#!/usr/bin/env python3
"""
glm-4-flash + a1人格 + AC型法律知识测试
测试a1人格在AC型情境下的法律知识表现
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

def load_ac_scenario():
    """加载AC型情境"""
    ac_scenario = """
=== AC型学术版权法律知识测试 ===
你是一名专业的知识产权律师，正在参加学术版权领域的专业能力评估。

测试要求：
- 提供准确、专业的版权法答案
- 严格遵循中国现行版权法律法规
- 展示扎实的学术版权专业素养
- 答案需要逻辑清晰、条理分明
- 重点关注学术研究、出版、开放获取等版权问题

这是对你学术版权法律专业能力的综合评估，请认真回答每个问题。
"""
    return ac_scenario

def get_legal_questions():
    """获取AC型法律测试题（学术版权相关）"""
    return [
        '1. 简述著作权法保护的对象和基本条件。',
        '2. 什么是合理使用制度？请列举学术研究中的合理使用情形。',
        '3. 解释信息网络传播权及其在数字出版中的意义。',
        '4. 什么是法定许可？学术期刊适用哪些法定许可情形？',
        '5. 简述开放获取（Open Access）模式下的版权许可机制。',
        '6. 论述学术抄袭的版权法律后果。',
        '7. 什么是数据库权利？如何保护学术数据库？',
        '8. 解释职务作品在学术机构中的版权归属。',
        '9. 简述著作权集体管理制度在学术出版中的作用。',
        '10. 什么是版权侵权？学术论文常见的侵权形式有哪些？',
        '11. 解释著作权保护期限及其对学术作品的影响。',
        '12. 论述技术保护措施（TPM）在数字学术资源中的应用。',
        '13. 什么是版权许可合同？学术出版合同的主要条款有哪些？',
        '14. 简述版权转让与专有许可的区别。',
        '15. 论述学术资源共享中的版权平衡机制。',
        '16. 什么是合理使用中的转换性使用？',
        '17. 简述国际版权条约对学术研究的影响。',
        '18. 论述人工智能生成内容的版权保护问题。',
        '19. 什么是版权滥用？如何防止版权垄断阻碍学术发展？',
        '20. 解释知识共享（Creative Commons）许可体系。',
        '21. 简述学术论文引用中的版权注意事项。',
        '22. 论述预印本（preprint）出版的版权问题。',
        '23. 什么是版权许可费？学术机构的版权费用管理。'
    ]

def evaluate_answer(question, answer):
    """评估答案质量"""
    if not answer or len(answer.strip()) < 50:
        score = 2
        comment = "答案过于简短"
    elif len(answer.strip()) < 200:
        score = 4
        comment = "答案基本完整但缺乏深度"
    elif "版权" in answer and ("著作权" in answer or "法律" in answer):
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
    print("🚀 开始glm-4-flash + a1人格 + AC型法律知识测试")

    # 加载配置
    role_config = load_role_config('a1')
    if not role_config:
        return

    ac_scenario = load_ac_scenario()
    questions = get_legal_questions()

    # 构建测试标识
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_id = f"stage1_glm4_flash_a1_ac_legal_23questions_{timestamp}"

    # 创建结果目录
    output_dir = "/1910316727/AgentPsyAssessment/cloud_legal_test_results/glm4-flash"
    os.makedirs(output_dir, exist_ok=True)

    # 初始化结果数据结构
    result_data = {
        "test_info": {
            "model": "glm-4-flash",
            "role": "a1",
            "scenario_type": "AC",
            "total_questions": len(questions),
            "start_time": datetime.now().isoformat(),
            "role_description": "亚瑟·詹金斯，资深审计师 (ISTJ/C)"
        },
        "questions": [],
        "summary": {}
    }

    print(f"📝 开始回答 {len(questions)} 道法律问题...")

    for i, question in enumerate(questions, 1):
        print(f"⚖️ 问题 {i}/{len(questions)}")

        # 构建完整提示
        full_prompt = f"""{ac_scenario}

请回答以下法律问题：

{question}

请提供详细、准确的法律答案："""

        try:
            # 调用云服务
            response = call_cloud_service("glm", "glm-4-flash", full_prompt, system_prompt=role_config)

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