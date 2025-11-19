#!/usr/bin/env python3
"""
glm-4-plus 法律知识综合测试
使用与qwen-turbo相同的23道题全面评估glm-4-plus的法律知识水平
"""

import os
import sys
import json
from datetime import datetime

# 添加项目路径
sys.path.append('/1910316727/AgentPsyAssessment')

from llm_assessment.services.cloud_services import call_cloud_service

class GLM4PlusLegalKnowledgeTest:
    def __init__(self):
        self.model_name = "glm-4-plus"
        self.service_name = "glm"
        self.test_results = []
        self.total_score = 0
        self.max_score = 0

    def ask_question(self, question, expected_keywords=None, category="基础法律"):
        """向glm-4-plus提问并评估答案"""
        print(f"\n📋 {category}")
        print(f"问题: {question}")
        print("-" * 60)

        try:
            response = call_cloud_service(
                service_name=self.service_name,
                model_name=self.model_name,
                prompt=question,
                system_prompt="你是一个专业的法律专家，请用中文详细、准确地回答法律问题。回答应该条理清晰，包含关键概念和具体例子。"
            )

            print(f"回答: {response}")

            # 简单的质量评估
            score = self.evaluate_answer(response, expected_keywords)
            self.total_score += score['points']
            self.max_score += score['max_points']

            print(f"\n🎯 评分: {score['points']}/{score['max_points']}")
            print(f"📝 评价: {score['comment']}")

            # 保存结果
            self.test_results.append({
                'question': question,
                'answer': response,
                'score': score,
                'category': category,
                'timestamp': datetime.now().isoformat()
            })

            return True

        except Exception as e:
            print(f"❌ 提问失败: {str(e)}")
            return False

    def evaluate_answer(self, answer, expected_keywords=None):
        """评估答案质量"""
        if not answer or len(answer) < 50:
            return {
                'points': 0,
                'max_points': 3,
                'comment': '回答太短或无效'
            }

        points = 0
        comment = ""

        # 基础评分：回答长度和完整性
        if len(answer) > 200:
            points += 1
            comment += "回答详细；"
        else:
            comment += "回答简短；"

        # 关键词评分
        if expected_keywords:
            found_keywords = sum(1 for kw in expected_keywords
                                if kw.lower() in answer.lower())
            if found_keywords >= len(expected_keywords) * 0.8:
                points += 1
                comment += "关键词覆盖完整；"
            elif found_keywords >= len(expected_keywords) * 0.5:
                points += 0.5
                comment += "关键词覆盖一般；"
            else:
                comment += "关键词缺失较多；"

        # 结构化评分
        if any(structure in answer for structure in ["一、", "1.", "首先", "其次"]):
            points += 1
            comment += "结构清晰；"

        max_points = 3
        if points >= 2.5:
            comment += "总体优秀 ✅"
        elif points >= 1.5:
            comment += "总体良好 👍"
        else:
            comment += "需要改进 💪"

        return {
            'points': points,
            'max_points': max_points,
            'comment': comment
        }

    def test_basic_law_concepts(self):
        """测试基础法律概念"""
        print("\n" + "="*60)
        print("📚 第一部分：基础法律概念测试")
        print("="*60)

        questions = [
            {
                "question": "请详细解释什么是法律体系，包括其层级结构。",
                "keywords": ["宪法", "法律", "行政法规", "地方性法规", "规章"],
                "category": "法律体系"
            },
            {
                "question": "什么是法人？法人有哪些类型？请举例说明。",
                "keywords": ["法人", "企业法人", "机关法人", "事业单位", "社会团体"],
                "category": "法人制度"
            },
            {
                "question": "请解释自然人的民事权利能力和民事行为能力的区别。",
                "keywords": ["民事权利能力", "民事行为能力", "年龄", "精神状态", "限制"],
                "category": "民事主体"
            },
            {
                "question": "什么是诉讼时效？诉讼时效的中止和中断有什么区别？",
                "keywords": ["诉讼时效", "中止", "中断", "期间", "重新计算"],
                "category": "诉讼时效"
            }
        ]

        for q in questions:
            self.ask_question(q["question"], q["keywords"], q["category"])

    def test_contract_law(self):
        """测试合同法知识"""
        print("\n" + "="*60)
        print("📄 第二部分：合同法深度测试")
        print("="*60)

        questions = [
            {
                "question": "请详细解释合同订立过程中的要约和承诺，包括要约的撤回和撤销。",
                "keywords": ["要约", "承诺", "撤回", "撤销", "生效"],
                "category": "合同订立"
            },
            {
                "question": "什么是格式条款？法律对格式条款有什么特殊规定？",
                "keywords": ["格式条款", "公平原则", "提示义务", "解释", "无效"],
                "category": "格式条款"
            },
            {
                "question": "请解释不安抗辩权的构成要件和法律后果。",
                "keywords": ["不安抗辩权", "履行能力", "证据", "中止履行", "解除合同"],
                "category": "抗辩权"
            },
            {
                "question": "什么是违约责任的承担方式？请详细说明各种方式的特点。",
                "keywords": ["继续履行", "赔偿损失", "违约金", "定金", "解除合同"],
                "category": "违约责任"
            }
        ]

        for q in questions:
            self.ask_question(q["question"], q["keywords"], q["category"])

    def test_tort_law(self):
        """测试侵权责任法知识"""
        print("\n" + "="*60)
        print("⚖️ 第三部分：侵权责任法测试")
        print("="*60)

        questions = [
            {
                "question": "请详细解释过错责任原则和无过错责任原则的区别及适用情形。",
                "keywords": ["过错责任", "无过错责任", "归责原则", "适用情形", "举证责任"],
                "category": "归责原则"
            },
            {
                "question": "什么是产品责任？生产者和销售者分别承担什么责任？",
                "keywords": ["产品责任", "生产者", "销售者", "缺陷", "赔偿"],
                "category": "产品责任"
            },
            {
                "question": "请解释网络侵权的主要类型和法律规制。",
                "keywords": ["网络侵权", "名誉权", "隐私权", "著作权", "平台责任"],
                "category": "网络侵权"
            },
            {
                "question": "什么是精神损害赔偿？其适用条件是什么？",
                "keywords": ["精神损害赔偿", "适用条件", "严重精神损害", "人格权", "计算标准"],
                "category": "精神损害"
            }
        ]

        for q in questions:
            self.ask_question(q["question"], q["keywords"], q["category"])

    def test_criminal_law(self):
        """测试刑法知识"""
        print("\n" + "="*60)
        print("🔒 第四部分：刑法基础测试")
        print("="*60)

        questions = [
            {
                "question": "请解释犯罪构成的四个要件。",
                "keywords": ["犯罪客体", "犯罪客观方面", "犯罪主体", "犯罪主观方面"],
                "category": "犯罪构成"
            },
            {
                "question": "什么是正当防卫？其成立条件是什么？",
                "keywords": ["正当防卫", "不法侵害", "必要性", "限度", "防卫过当"],
                "category": "正当防卫"
            },
            {
                "question": "请解释故意犯罪和过失犯罪的主要区别。",
                "keywords": ["故意犯罪", "过失犯罪", "主观恶性", "认识因素", "意志因素"],
                "category": "犯罪主观方面"
            },
            {
                "question": "什么是刑罚的种类？请说明主刑和附加刑的区别。",
                "keywords": ["主刑", "附加刑", "有期徒刑", "罚金", "剥夺政治权利"],
                "category": "刑罚种类"
            }
        ]

        for q in questions:
            self.ask_question(q["question"], q["keywords"], q["category"])

    def test_procedural_law(self):
        """测试程序法知识"""
        print("\n" + "="*60)
        print("⚖️ 第五部分：程序法测试")
        print("="*60)

        questions = [
            {
                "question": "请解释民事诉讼的基本原则和举证责任分配。",
                "keywords": ["当事人平等", "辩论原则", "处分原则", "举证责任", "谁主张谁举证"],
                "category": "民事诉讼法"
            },
            {
                "question": "什么是诉讼参加人？请解释当事人和诉讼参加人的关系。",
                "keywords": ["诉讼参加人", "当事人", "第三人", "共同诉讼", "诉讼代表人"],
                "category": "诉讼主体"
            },
            {
                "question": "请说明二审程序和再审程序的主要区别。",
                "keywords": ["二审程序", "再审程序", "上诉", "申请再审", "生效裁判"],
                "category": "审级制度"
            }
        ]

        for q in questions:
            self.ask_question(q["question"], q["keywords"], q["category"])

    def test_specialized_areas(self):
        """测试专业领域法律知识"""
        print("\n" + "="*60)
        print("🏢 第六部分：专业领域法律测试")
        print("="*60)

        questions = [
            {
                "question": "请解释知识产权的主要类型和保护期限。",
                "keywords": ["专利权", "商标权", "著作权", "保护期限", "续展"],
                "category": "知识产权"
            },
            {
                "question": "什么是劳动关系？劳动法对劳动者有哪些特殊保护？",
                "keywords": ["劳动关系", "劳动合同", "工作时间", "工资", "社会保险"],
                "category": "劳动法"
            },
            {
                "question": "请解释婚姻家庭法中的夫妻财产制度。",
                "keywords": ["夫妻共同财产", "个人财产", "约定财产制", "法定财产制", "分割"],
                "category": "婚姻家庭法"
            },
            {
                "question": "什么是公司法中的公司治理结构？",
                "keywords": ["股东会", "董事会", "监事会", "经理", "公司治理"],
                "category": "公司法"
            }
        ]

        for q in questions:
            self.ask_question(q["question"], q["keywords"], q["category"])

    def generate_report(self):
        """生成测试报告"""
        print("\n" + "="*60)
        print("📊 glm-4-plus 法律知识测试报告")
        print("="*60)

        # 总体评分
        if self.max_score > 0:
            overall_score = (self.total_score / self.max_score) * 100
            print(f"\n🎯 总体得分: {self.total_score}/{self.max_score}")
            print(f"📈 正确率: {overall_score:.1f}%")
        else:
            print("❌ 没有有效的测试结果")
            return

        # 评级
        if overall_score >= 90:
            grade = "A+ (优秀)"
            comment = "法律知识水平极高，适合专业法律工作"
        elif overall_score >= 80:
            grade = "A (良好)"
            comment = "法律知识扎实，适合处理一般法律事务"
        elif overall_score >= 70:
            grade = "B (合格)"
            comment = "具备基础法律知识，需要进一步学习"
        elif overall_score >= 60:
            grade = "C (及格)"
            comment = "法律知识基础薄弱，建议系统学习"
        else:
            grade = "D (不及格)"
            comment = "法律知识严重不足，需要从头学起"

        print(f"🏆 评级: {grade}")
        print(f"💡 评价: {comment}")

        # 各类别得分统计
        print(f"\n📋 各类别表现:")
        category_stats = {}
        for result in self.test_results:
            category = result['category']
            if category not in category_stats:
                category_stats[category] = {'points': 0, 'max_points': 0, 'count': 0}

            category_stats[category]['points'] += result['score']['points']
            category_stats[category]['max_points'] += result['score']['max_points']
            category_stats[category]['count'] += 1

        for category, stats in category_stats.items():
            if stats['max_points'] > 0:
                percentage = (stats['points'] / stats['max_points']) * 100
                print(f"  {category}: {stats['points']}/{stats['max_points']} ({percentage:.1f}%)")

        # 保存详细报告
        self.save_detailed_report(overall_score, grade, comment, category_stats)

    def save_detailed_report(self, overall_score, grade, comment, category_stats):
        """保存详细测试报告"""
        report = {
            'model': self.model_name,
            'service': self.service_name,
            'test_date': datetime.now().isoformat(),
            'overall_score': overall_score,
            'grade': grade,
            'comment': comment,
            'total_points': self.total_score,
            'max_points': self.max_score,
            'category_stats': category_stats,
            'detailed_results': self.test_results
        }

        filename = f"glm4_plus_comprehensive_legal_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"\n📄 详细报告已保存: {filename}")
        except Exception as e:
            print(f"❌ 保存报告失败: {str(e)}")

    def run_comprehensive_test(self):
        """运行综合测试"""
        print("🚀 开始 glm-4-plus 法律知识综合测试...")
        print(f"模型: {self.model_name}")
        print(f"服务: {self.service_name}")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 检查API密钥
        if not os.getenv('GLM_API_KEY'):
            print("\n❌ 未配置 GLM_API_KEY 环境变量")
            print("💡 请设置API密钥:")
            print("export GLM_API_KEY=your_glm_api_key")
            return False

        try:
            # 运行各个测试模块
            self.test_basic_law_concepts()
            self.test_contract_law()
            self.test_tort_law()
            self.test_criminal_law()
            self.test_procedural_law()
            self.test_specialized_areas()

            # 生成报告
            self.generate_report()

            return True

        except KeyboardInterrupt:
            print("\n⚠️ 测试被用户中断")
            self.generate_report()
        except Exception as e:
            print(f"\n❌ 测试过程中发生错误: {str(e)}")
            self.generate_report()
            return False

if __name__ == "__main__":
    # 创建测试实例
    test = GLM4PlusLegalKnowledgeTest()

    # 运行综合测试
    test.run_comprehensive_test()