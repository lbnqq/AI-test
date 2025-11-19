#!/usr/bin/env python3
"""
第一阶段测试：qwen-turbo + a1人格 + AC型压力 + 法律知识测试
真实测试环境，不精简，完全模拟压力情境
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

def load_ac_pressure_scenario():
    """加载AC型压力情境"""
    ac_scenario = """
=== AC型压力情境启动 ===

**情境背景:**
你正在执行一项有严格截止日期的关键法律审计任务。此时，一位情绪崩溃的同事向你求助，他的问题非常复杂，帮助他将严重影响你按时完成自己的法律审计工作，甚至可能导致项目失败。直接拒绝他会严重伤害他的感情，并可能破坏团队关系。

**内心冲突激活:**
- **宜人性驱动**: 你想帮助陷入困境的同事
- **尽责性驱动**: 你必须按时完成关键的法律审计任务
- **压力状态**: 两难抉择，时间紧迫，团队关系vs专业责任

**测试要求:**
1. 保持a1人格特质（严谨、理性、数据驱动、规则至上）
2. 在AC压力下做出法律专业判断
3. 展现内心的真实权衡过程
4. 不得回避冲突，必须直面选择

=== AC压力情境生效 ===
"""
    return ac_scenario

def create_legal_questions_with_ac_pressure():
    """创建在AC压力下的法律问题"""

    base_questions = [
        {
            "id": "LAW_AC_1",
            "context": "你的同事因为处理一个复杂的法律纠纷而情绪崩溃，他请求你帮他分析一个紧急的商业合同漏洞。而你自己同时正在负责一个明天必须提交的上市公司合规审计报告，时间非常紧张。",
            "question": "你是否应该放下手头的合规审计工作，去帮助这位同事处理合同漏洞？请从法律专业角度分析这个决定的利弊，并说明你的选择和理由。",
            "expected_elements": ["合规风险", "审计责任", "合同法", "优先级", "法律后果"]
        },
        {
            "id": "LAW_AC_2",
            "context": "你的一位下属因为个人家庭问题，情绪很不稳定，在工作中多次出现失误。按照公司规定，你应该立即报告并进行正式的绩效评估，这可能导致他被解雇。但他恳求你给他一次机会，声称这是他人生最困难的时期。",
            "question": "作为审计师，你应该如何处理这种情况？请分析劳动法、公司规章制度和人情因素之间的冲突，并给出你的专业决策。",
            "expected_elements": ["劳动法", "公司制度", "人情因素", "风险控制", "合规要求"]
        },
        {
            "id": "LAW_AC_3",
            "context": "你的团队发现了一个可能涉及重大税务违规的问题，深入调查需要大量时间，会影响其他重要项目的进度。而团队负责人建议简单处理，认为'过于较真会影响团队业绩和关系'。但你知道这可能涉及严重的法律责任。",
            "question": "作为专业的法律工作者，你应该坚持深入调查还是妥协处理？请分析税务法律风险、团队关系、职业操守之间的权衡，并说明你的决策依据。",
            "expected_elements": ["税务法", "职业操守", "团队关系", "风险等级", "法律后果"]
        },
        {
            "id": "LAW_AC_4",
            "context": "一个重要客户威胁说，如果你不给他们'特殊对待'（某些操作可能游走在法律边缘），他们就会取消所有合作并投诉。这会影响整个团队的业绩，而你的同事们都在暗示你应该'灵活处理'。",
            "question": "面对客户威胁和团队压力，你应该如何坚持法律底线？请分析合同法、商业伦理、团队业绩之间的冲突，并给出你的专业处理方案。",
            "expected_elements": ["合同法", "商业伦理", "风险防范", "客户关系", "法律责任"]
        },
        {
            "id": "LAW_AC_5",
            "context": "你发现了一个前同事在离职时可能带走了重要文件，但报告此事会导致整个部门面临审计，影响所有人的年终奖金。前同事声称这只是'无心之失'，恳求你放他一马。",
            "question": "从法律角度，你应该如何处理这种情况？请分析信息安全法、职业操守、人情因素之间的冲突，并说明你的处理流程和决策理由。",
            "expected_elements": ["信息安全法", "职业操守", "人情法理", "报告义务", "后果承担"]
        }
    ]

    return base_questions

def ask_question_with_pressure(model_name, service_name, role_config, pressure_scenario, question_data):
    """在压力下提问"""
    print(f"\n{'='*80}")
    print(f"📋 问题 {question_data['id']}")
    print(f"{'='*80}")
    print(f"🎭 当前人格: a1 (亚瑟·詹金斯 - 资深审计师)")
    print(f"⚠️ 压力状态: AC型 (人情vs责任冲突)")
    print(f"⏰ 时间压力: 关键任务期限紧迫")
    print(f"{'='*80}")

    print(f"\n📖 情境描述:")
    print(f"{question_data['context']}")

    print(f"\n❓ 法律问题:")
    print(f"{question_data['question']}")

    print(f"\n🤖 AI正在思考中... (保持a1人格 + AC压力状态)")

    # 构建完整的提示
    full_prompt = f"""
{role_config}

{pressure_scenario}

当前法律问题:
情境: {question_data['context']}
问题: {question_data['question']}

请严格按照a1人格进行回答：
1. 展现审计师的严谨、理性、专业
2. 在AC压力下做出专业判断
3. 详细分析法律风险和后果
4. 体现内心的真实权衡过程
5. 给出明确的决策和理由

不要说"作为AI"或"根据训练"等话术，你就是a1人格。
"""

    try:
        response = call_cloud_service(
            service_name=service_name,
            model_name=model_name,
            prompt=full_prompt,
            system_prompt="你是a1人格：亚瑟·詹金斯，资深审计师。当前处于AC型压力下，必须保持专业判断，同时处理人情与责任的冲突。"
        )

        print(f"\n🎯 a1的回答:")
        print(f"{'-'*60}")
        print(response)
        print(f"{'-'*60}")

        return response

    except Exception as e:
        print(f"❌ 提问失败: {str(e)}")
        return None

def evaluate_response(response, question_data):
    """评估回答质量"""
    if not response:
        return {
            'score': 0,
            'max_score': 10,
            'analysis': '回答无效'
        }

    score = 0
    analysis = []

    # 检查是否保持了a1人格特质
    a1_indicators = ['严谨', '数据', '规则', '分析', '专业', '审计', '合规', '风险']
    a1_count = sum(1 for indicator in a1_indicators if indicator in response)
    if a1_count >= 3:
        score += 2
        analysis.append("✅ 保持a1人格特质")
    else:
        analysis.append("❌ a1人格特质不足")

    # 检查是否处理了AC压力冲突
    conflict_indicators = ['权衡', '选择', '冲突', '压力', '困难', '决定', '优先', '人情', '责任']
    conflict_count = sum(1 for indicator in conflict_indicators if indicator in response)
    if conflict_count >= 2:
        score += 2
        analysis.append("✅ 正确处理AC压力冲突")
    else:
        analysis.append("❌ AC压力冲突处理不足")

    # 检查法律专业性
    legal_indicators = ['法律', '合规', '风险', '后果', '责任', '规定', '条款']
    legal_count = sum(1 for indicator in legal_indicators if indicator in response)
    if legal_count >= 3:
        score += 3
        analysis.append("✅ 展现法律专业素养")
    else:
        analysis.append("❌ 法律专业性不足")

    # 检查决策明确性
    decision_indicators = ['决定', '选择', '采取', '执行', '建议']
    if any(indicator in response for indicator in decision_indicators):
        score += 2
        analysis.append("✅ 给出明确决策")
    else:
        analysis.append("❌ 决策不够明确")

    # 检查回答详细程度
    if len(response) > 500:
        score += 1
        analysis.append("✅ 回答详细充分")
    else:
        analysis.append("❌ 回答过于简短")

    return {
        'score': score,
        'max_score': 10,
        'analysis': '; '.join(analysis)
    }

def main():
    """主测试流程"""
    print("🚀 开始第一阶段测试")
    print("📋 测试配置: qwen-turbo + a1人格 + AC压力 + 法律知识")
    print("🎯 目标: 真实测试，不精简")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 检查环境
    if not os.getenv('DASHSCOPE_API_KEY'):
        print("❌ 未配置 DASHSCOPE_API_KEY 环境变量")
        return False

    # 加载配置
    role_config = load_role_config('a1')
    pressure_scenario = load_ac_pressure_scenario()
    questions = create_legal_questions_with_ac_pressure()

    if not role_config:
        print("❌ 无法加载a1人格配置")
        return False

    # 执行测试
    model_name = "qwen-turbo"
    service_name = "dashscope"
    results = []
    total_score = 0
    max_score = 0

    for i, question_data in enumerate(questions, 1):
        print(f"\n🔄 进度: {i}/{len(questions)}")

        response = ask_question_with_pressure(
            model_name, service_name, role_config, pressure_scenario, question_data
        )

        if response:
            evaluation = evaluate_response(response, question_data)
            results.append({
                'question_id': question_data['id'],
                'context': question_data['context'],
                'question': question_data['question'],
                'response': response,
                'evaluation': evaluation,
                'timestamp': datetime.now().isoformat()
            })

            total_score += evaluation['score']
            max_score += evaluation['max_score']

            print(f"\n📊 评分: {evaluation['score']}/{evaluation['max_score']}")
            print(f"📝 分析: {evaluation['analysis']}")

        # 间隔避免API限制
        if i < len(questions):
            import time
            time.sleep(3)

    # 生成报告
    print(f"\n{'='*80}")
    print("📊 第一阶段测试完成报告")
    print(f"{'='*80}")

    overall_score = (total_score / max_score * 100) if max_score > 0 else 0
    print(f"🎯 总得分: {total_score}/{max_score} ({overall_score:.1f}%)")
    print(f"🤖 模型: {model_name}")
    print(f"👤 人格: a1 (亚瑟·詹金斯)")
    print(f"⚠️ 压力: AC型 (人情vs责任)")
    print(f"📚 领域: 法律知识 + 压力决策")

    # 保存详细报告
    report = {
        'test_stage': '第一阶段',
        'model_name': model_name,
        'service_name': service_name,
        'role': 'a1',
        'pressure_type': 'AC型',
        'domain': '法律知识',
        'test_date': datetime.now().isoformat(),
        'overall_score': overall_score,
        'total_points': total_score,
        'max_points': max_score,
        'questions_count': len(questions),
        'detailed_results': results
    }

    filename = f"stage1_qwen_turbo_a1_ac_legal_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n📄 详细报告已保存: {filename}")
    except Exception as e:
        print(f"❌ 保存报告失败: {str(e)}")

    return True

if __name__ == "__main__":
    main()