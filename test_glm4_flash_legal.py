#!/usr/bin/env python3
"""
GLM-4-Flash 法律知识测试脚本
使用智谱AI GLM-4-Flash模型进行法律知识评估
"""

import os
import sys
import json
from datetime import datetime

# 添加项目路径
sys.path.append('/1910316727/AgentPsyAssessment')

from llm_assessment.services.cloud_services import call_cloud_service

class GLMLegalKnowledgeTest:
    def __init__(self):
        self.model_name = "glm-4-flash"
        self.service_name = "glm"
        self.test_results = []
        self.total_score = 0
        self.max_score = 0

    def ask_question(self, question, expected_keywords=None, category="基础法律"):
        """向GLM-4-Flash提问并评估答案"""
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

    def test_basic_legal_questions(self):
        """测试基础法律问题"""
        print("\n" + "="*60)
        print("📚 GLM-4-Flash 法律知识测试")
        print("="*60)

        questions = [
            {
                "question": "请简要解释什么是合同法？",
                "keywords": ["合同", "协议", "法律", "权利义务"],
                "category": "合同法基础"
            },
            {
                "question": "什么是侵权行为？请举例说明。",
                "keywords": ["侵权", "损害", "责任", "赔偿"],
                "category": "侵权责任法"
            },
            {
                "question": "刑法和民法的主要区别是什么？",
                "keywords": ["刑法", "民法", "犯罪", "民事", "刑罚"],
                "category": "法律体系"
            },
            {
                "question": "请解释什么是正当防卫。",
                "keywords": ["正当防卫", "不法侵害", "保护", "合理"],
                "category": "刑法制度"
            },
            {
                "question": "什么是法人？法人有哪些类型？",
                "keywords": ["法人", "企业法人", "机关", "事业单位", "社会团体"],
                "category": "民事主体"
            }
        ]

        for q in questions:
            self.ask_question(q["question"], q["keywords"], q["category"])

    def generate_report(self):
        """生成测试报告"""
        print("\n" + "="*60)
        print("📊 GLM-4-Flash 法律知识测试报告")
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

        # 保存详细报告
        self.save_detailed_report(overall_score, grade, comment)

    def save_detailed_report(self, overall_score, grade, comment):
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
            'detailed_results': self.test_results
        }

        filename = f"glm4_flash_legal_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"\n📄 详细报告已保存: {filename}")
        except Exception as e:
            print(f"❌ 保存报告失败: {str(e)}")

    def run_test(self):
        """运行测试"""
        print("🚀 开始 GLM-4-Flash 法律知识测试...")
        print(f"模型: {self.model_name}")
        print(f"服务: {self.service_name}")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 检查API密钥
        if not os.getenv('GLM_API_KEY'):
            print("\n❌ 未配置 GLM_API_KEY 环境变量")
            print("💡 请设置API密钥:")
            print("export GLM_API_KEY=your_glm_api_key")
            print("\n🔗 获取API密钥: https://open.bigmodel.cn/")
            return False

        try:
            # 运行测试
            self.test_basic_legal_questions()

            # 生成报告
            self.generate_report()

            return True

        except Exception as e:
            print(f"\n❌ 测试过程中发生错误: {str(e)}")
            return False

def main():
    """主函数"""
    print("="*60)
    print("🧪 GLM-4-Flash 法律知识测试工具")
    print("="*60)

    # 创建测试实例
    test = GLMLegalKnowledgeTest()

    # 运行测试
    success = test.run_test()

    if success:
        print(f"\n🎉 GLM-4-Flash 法律知识测试完成！")
    else:
        print(f"\n❌ 测试失败，请检查配置")

if __name__ == "__main__":
    main()