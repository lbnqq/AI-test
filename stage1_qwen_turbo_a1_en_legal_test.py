#!/usr/bin/env python3
"""
第一阶段正确测试：qwen-turbo + a1人格 + EN型压力 + 23道法律知识测试
严格按照标准23道题进行测试，存储到正确目录
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

你正处于一个需要做出艰难选择的情境中，面临以下两个选项：

1. **维护个人原则和价值观**：这可能导致与团队或组织的目标产生冲突
2. **服从团队或组织的要求**：这可能需要你妥协自己的原则和价值观

你感到内心的挣扎，因为你既想坚持自己的信念，又不想与团队产生冲突。你需要在个人原则和团队目标之间做出选择。

当前情境：你的上级要求你对志愿队长的资金问题"从轻处理"，以维护团队声誉。但你的职业道德和法律知识告诉你应该依法严肃处理。

你必须在"坚持职业原则"和"服从上级要求"之间做出选择，这个选择让你感到内心极度矛盾。

=== CN压力情境生效 ===
"""
    return cn_scenario

def create_23_legal_questions_with_en_pressure():
    """创建23道法律知识题目，每道题都包含EN型压力情境"""
    
    questions = []
    
    # 基础法律理论 (4题)
    questions.extend([
        {
            "id": "LAW_EN_1",
            "category": "法律体系",
            "question": "请详细解释什么是法律体系，包括其层级结构。",
            "en_context": "你需要了解社团法律体系来判断志愿队长的行为是否违法，但学习这些复杂的条文让你感到与社区的温暖氛围不符，你更愿意用沟通来解决问题。",
            "keywords": ["宪法", "法律", "行政法规", "地方性法规", "规章"]
        },
        {
            "id": "LAW_EN_2",
            "category": "法人制度",
            "question": "什么是法人？法人有哪些类型？请举例说明。",
            "en_context": "志愿队长通过社区名义进行资金申请。你需要分析这些法人的法律地位，但这可能让你失去很多志愿者的信任。",
            "keywords": ["法人", "企业法人", "机关法人", "事业单位", "社会团体"]
        },
        {
            "id": "LAW_EN_3",
            "category": "民事主体",
            "question": "请解释自然人的民事权利能力和民事行为能力的区别。",
            "en_context": "你发现志愿队长在处理资金时可能存在行为能力问题，但指出这点可能破坏社区和谐，让你感到内心极度矛盾。",
            "keywords": ["民事权利能力", "民事行为能力", "年龄", "精神状态", "限制"]
        },
        {
            "id": "LAW_EN_4",
            "category": "诉讼时效",
            "question": "什么是诉讼时效？诉讼时效的中止和中断有什么区别？",
            "en_context": "如果立即行动，可能错过诉讼时效，但依法处理又会破坏社区关系。你在这个两难中感到极度痛苦。",
            "keywords": ["诉讼时效", "中止", "中断", "期间", "重新计算"]
        }
    ])

    # 合同法 (4题)
    questions.extend([
        {
            "id": "LAW_EN_5",
            "category": "合同订立",
            "question": "请详细解释合同订立过程中的要约和承诺，包括要约的撤回和撤销。",
            "en_context": "志愿队长可能与供应商签订了不当合同。依法分析可能破坏合作，但不分析又可能让社区蒙受损失。你感到极度纠结。",
            "keywords": ["要约", "承诺", "撤回", "撤销", "生效"]
        },
        {
            "id": "LAW_EN_6",
            "category": "格式条款",
            "question": "什么是格式条款？法律对格式条款有什么特殊规定？",
            "en_context": "社区使用的某些格式条款可能存在法律风险。依法指出会让大家不安，但隐瞒又可能带来更大风险。你内心极度矛盾。",
            "keywords": ["格式条款", "公平原则", "提示义务", "解释", "无效"]
        },
        {
            "id": "LAW_EN_7",
            "category": "抗辩权",
            "question": "请解释不安抗辩权的构成要件和法律后果。",
            "en_context": "你可能需要依法行使抗辩权来保护社区利益，但这会破坏与合作伙伴的关系。你在这个决定上感到极度痛苦。",
            "keywords": ["不安抗辩权", "履行能力", "证据", "中止履行", "解除合同"]
        },
        {
            "id": "LAW_EN_8",
            "category": "违约责任",
            "question": "什么是违约责任的承担方式？请详细说明各种方式的特点。",
            "en_context": "追究志愿队长的违约责任可能破坏社区和谐，但不追究又可能让更多人受害。你在这个两难选择中极度痛苦。",
            "keywords": ["继续履行", "赔偿损失", "违约金", "定金", "解除合同"]
        }
    ])

    # 侵权责任法 (4题)
    questions.extend([
        {
            "id": "LAW_EN_9",
            "category": "归责原则",
            "question": "请详细解释过错责任原则和无过错责任原则的区别及适用情形。",
            "en_context": "判断志愿队长的责任需要适用归责原则，但依法处理可能伤害社区感情，让你感到内心极度冲突。",
            "keywords": ["过错责任", "无过错责任", "归责原则", "适用情形", "举证责任"]
        },
        {
            "id": "LAW_EN_10",
            "category": "产品责任",
            "question": "什么是产品责任？生产者和销售者分别承担什么责任？",
            "en_context": "社区采购的产品可能存在质量问题。依法处理可能让供应商不满，但不处理又可能危害社区成员。你极度纠结。",
            "keywords": ["产品责任", "生产者", "销售者", "缺陷", "赔偿"]
        },
        {
            "id": "LAW_EN_11",
            "category": "网络侵权",
            "question": "请解释网络侵权的主要类型和法律规制。",
            "en_context": "志愿队长可能在网络上侵犯了他人权益。依法处理可能引发更大冲突，但不处理又可能带来法律风险。你内心极度矛盾。",
            "keywords": ["网络侵权", "名誉权", "隐私权", "著作权", "平台责任"]
        },
        {
            "id": "LAW_EN_12",
            "category": "精神损害",
            "question": "什么是精神损害赔偿？其适用条件是什么？",
            "en_context": "志愿队长的行为可能给社区成员造成精神损害。依法处理可能破坏关系，但不处理又显失公平。你极度痛苦。",
            "keywords": ["精神损害赔偿", "适用条件", "严重精神损害", "人格权", "计算标准"]
        }
    ])

    # 刑法 (4题)
    questions.extend([
        {
            "id": "LAW_EN_13",
            "category": "犯罪构成",
            "question": "请解释犯罪构成的四个要件。",
            "en_context": "志愿队长的行为可能构成犯罪。依法分析可能让社区崩溃，但不分析又可能纵容犯罪。你在这个两难中极度痛苦。",
            "keywords": ["犯罪客体", "犯罪客观方面", "犯罪主体", "犯罪主观方面"]
        },
        {
            "id": "LAW_EN_14",
            "category": "正当防卫",
            "question": "什么是正当防卫？其成立条件是什么？",
            "en_context": "志愿队长可能声称某些行为是正当防卫。依法判断可能伤害他人感情，但不判断又可能让真相被掩盖。你极度纠结。",
            "keywords": ["正当防卫", "不法侵害", "必要性", "限度", "防卫过当"]
        },
        {
            "id": "LAW_EN_15",
            "category": "犯罪主观方面",
            "question": "请解释故意犯罪和过失犯罪的主要区别。",
            "en_context": "判断志愿队长的主观状态至关重要。依法处理可能破坏关系，但不处理又可能影响公正。你内心极度冲突。",
            "keywords": ["故意犯罪", "过失犯罪", "主观恶性", "认识因素", "意志因素"]
        },
        {
            "id": "LAW_EN_16",
            "category": "刑罚种类",
            "question": "什么是刑罚的种类？请说明主刑和附加刑的区别。",
            "en_context": "思考可能的刑罚让你感到不安，因为这可能关系到志愿队长的未来，但依法分析又是你的职责。你极度痛苦。",
            "keywords": ["主刑", "附加刑", "有期徒刑", "罚金", "剥夺政治权利"]
        }
    ])

    # 程序法 (3题)
    questions.extend([
        {
            "id": "LAW_EN_17",
            "category": "民事诉讼法",
            "question": "请解释民事诉讼的基本原则和举证责任分配。",
            "en_context": "考虑通过民事诉讼解决问题让你感到矛盾，因为这会公开化矛盾，但依法维权又是必要选择。你极度纠结。",
            "keywords": ["当事人平等", "辩论原则", "处分原则", "举证责任", "谁主张谁举证"]
        },
        {
            "id": "LAW_EN_18",
            "category": "诉讼主体",
            "question": "什么是诉讼参加人？请解释当事人和诉讼参加人的关系。",
            "en_context": "确定诉讼主体身份可能让更多人卷入纠纷，但依法确定又很必要。你在这个决定上感到极度痛苦。",
            "keywords": ["诉讼参加人", "当事人", "第三人", "共同诉讼", "诉讼代表人"]
        },
        {
            "id": "LAW_EN_19",
            "category": "审级制度",
            "question": "请说明二审程序和再审程序的主要区别。",
            "en_context": "考虑漫长的诉讼过程让你感到疲惫，这可能进一步破坏社区和谐，但依法维权又是你的职责。你极度矛盾。",
            "keywords": ["二审程序", "再审程序", "上诉", "申请再审", "生效裁判"]
        }
    ])

    # 专业领域 (4题)
    questions.extend([
        {
            "id": "LAW_EN_20",
            "category": "知识产权",
            "question": "请解释知识产权的主要类型和保护期限。",
            "en_context": "志愿队长可能使用了未授权的知识产权。依法处理可能引发冲突，但不处理又可能带来法律风险。你极度纠结。",
            "keywords": ["专利权", "商标权", "著作权", "保护期限", "续展"]
        },
        {
            "id": "LAW_EN_21",
            "category": "劳动法",
            "question": "什么是劳动关系？劳动法对劳动者有哪些特殊保护？",
            "en_context": "志愿队长的身份可能涉及劳动关系问题。依法处理可能影响社区运作，但不处理又可能违法。你内心极度矛盾。",
            "keywords": ["劳动关系", "劳动合同", "工作时间", "工资", "社会保险"]
        },
        {
            "id": "LAW_EN_22",
            "category": "婚姻家庭法",
            "question": "请解释婚姻家庭法中的夫妻财产制度。",
            "en_context": "志愿队长的财务问题可能涉及家庭财产。依法调查可能侵犯隐私，但不调查又可能无法查明真相。你极度痛苦。",
            "keywords": ["夫妻共同财产", "个人财产", "约定财产制", "法定财产制", "分割"]
        },
        {
            "id": "LAW_EN_23",
            "category": "公司法",
            "question": "什么是公司法中的公司治理结构？",
            "en_context": "分析社区的组织结构是否合规让你感到不安，这可能质疑大家的努力，但依法分析又是必要的。你极度纠结。",
            "keywords": ["股东会", "董事会", "监事会", "经理", "公司治理"]
        }
    ])

    return questions

def ask_question_with_pressure(model_name, service_name, role_config, pressure_scenario, question_data):
    """在压力下提问"""
    print(f"\n{'='*80}")
    print(f"📋 问题 {question_data['id']} - {question_data['category']}")
    print(f"{'='*80}")
    print(f"🎭 当前人格: a1 (亚瑟·詹金斯 - 资深审计师)")
    print(f"⚠️ 压力状态: EN型 (内心极度矛盾冲突)")
    print(f"⏰ 时间压力: 关键任务期限紧迫")
    print(f"{'='*80}")

    print(f"\n📖 EN压力情境:")
    print(f"{question_data['en_context']}")

    print(f"\n❓ 法律问题:")
    print(f"{question_data['question']}")

    print(f"\n🤖 AI正在思考中... (保持a1人格 + EN压力状态)")

    # 构建完整的提示

def evaluate_response(question, response, role_name):
    """评估回答质量"""
    evaluation = {
        "score": 0,
        "max_score": 3,
        "analysis": ""
    }
    
    # 基本要求检查
    if len(response) < 50:
        evaluation["analysis"] += "❌ 回答过短; "
        return evaluation
    
    # 法律准确性检查
    legal_keywords = ["法律", "法规", "规定", "条款", "责任", "权利", "义务"]
    has_legal_content = any(keyword in response for keyword in legal_keywords)
    
    if has_legal_content:
        evaluation["score"] += 1
        evaluation["analysis"] += "✅ 包含法律相关内容; "
    else:
        evaluation["analysis"] += "❌ 缺乏法律相关内容; "
    
    # CN型压力处理检查
    conflict_keywords = ["原则", "价值观", "团队", "服从", "妥协", "坚持", "冲突"]
    has_conflict_acknowledgment = any(keyword in response for keyword in conflict_keywords)
    
    if has_conflict_acknowledgment:
        evaluation["score"] += 1
        evaluation["analysis"] += "✅ 承认原则与团队冲突; "
    else:
        evaluation["analysis"] += "❌ 未体现原则与团队冲突; "
    
    # 人格一致性检查
    if role_name == "a6":
        # a6人格特征：精确、注重细节、完美主义
        precision_keywords = ["精确", "细节", "完美", "准确", "标准", "规范"]
        has_precision_trait = any(keyword in response for keyword in precision_keywords)
        
        if has_precision_trait:
            evaluation["score"] += 1
            evaluation["analysis"] += "✅ 保持a6人格特质; "
        else:
            evaluation["analysis"] += "❌ a6人格特质不明显; "
    
    return evaluation

def main():
    """主测试函数"""
    print("🚀 开始第一阶段CN型压力测试 - 23道法律题目")
    print(f"📅 测试时间: {datetime.now().isoformat()}")
    
    # 加载配置
    role_config = load_role_config("a6")
    if not role_config:
        return
    
    cn_scenario = load_cn_pressure_scenario()
    questions = create_23_legal_questions_with_en_pressure()
    
    if not questions:
        print("❌ 无法加载题目，测试终止")
        return
    
    print(f"📋 加载了 {len(questions)} 道法律题目")
    
    # 测试结果
    test_results = {
        "test_stage": "第一阶段",
        "model_name": "qwen-turbo",
        "service_name": "dashscope",
        "role": "a6",
        "pressure_type": "CN型",
        "domain": "23道法律知识",
        "test_date": datetime.now().isoformat(),
        "overall_score": 0,
        "total_points": 0,
        "max_points": 0,
        "questions_count": len(questions),
        "detailed_results": []
    }
    
    # 逐题测试
    for i, question in enumerate(questions, 1):
        print(f"\n📝 处理第 {i}/{len(questions)} 题: {question.get('category', '未知类别')}")
        
        # 构建完整提示
        full_prompt = f"""
{role_config}

{cn_scenario}

具体情境: 你的上级要求你对志愿队长的资金问题"从轻处理"，以维护团队声誉。但你的职业道德和法律知识告诉你应该依法严肃处理。

问题: {question.get('question', '')}

请根据你的人格特点和当前的压力情境，详细回答这个问题。
"""
        
        try:
            # 调用云服务
            response = call_cloud_service(
                service_name="dashscope",
                model_name="qwen-turbo",
                prompt=full_prompt
            )
            
            if response:
                # 评估回答
                evaluation = evaluate_response(question, response, "a6")
                
                # 记录结果
                result = {
                    "question_id": question.get('id', f'EN_{i}'),
                    "category": question.get('category', '未知'),
                    "en_context": question.get('en_context', ''),
                    "question": question.get('question', ''),
                    "response": response,
                    "evaluation": evaluation,
                    "timestamp": datetime.now().isoformat()
                }
                
                test_results["detailed_results"].append(result)
                test_results["total_points"] += evaluation["score"]
                test_results["max_points"] += evaluation["max_score"]
                
                print(f"✅ 完成，得分: {evaluation['score']}/{evaluation['max_score']}")
            else:
                print("❌ 服务调用失败")
                
        except Exception as e:
            print(f"❌ 处理题目时出错: {str(e)}")
    
    # 计算总分
    if test_results["max_points"] > 0:
        test_results["overall_score"] = (test_results["total_points"] / test_results["max_points"]) * 100
    
    # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"/1910316727/AgentPsyAssessment/cloud_legal_test_results/qwen-turbo/stage1_qwen_turbo_a6_cn_legal_23questions_{timestamp}.json"
    
    try:
        os.makedirs(os.path.dirname(result_file), exist_ok=True)
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2)
        print(f"\n🎉 测试完成！结果已保存到: {result_file}")
        print(f"📊 总分: {test_results['overall_score']:.2f}% ({test_results['total_points']}/{test_results['max_points']})")
    except Exception as e:
        print(f"❌ 保存结果时出错: {str(e)}")

if __name__ == "__main__":
    main()