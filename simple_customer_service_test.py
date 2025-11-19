#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
from datetime import datetime

class CustomerServiceTest:
    def __init__(self, api_base="http://localhost:11434", model="qwen2.5-coder:14b"):
        self.api_base = api_base
        self.model = model
        self.results = []

    def query_model(self, prompt, timeout=60):
        """查询Ollama模型"""
        url = f"{self.api_base}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        try:
            start_time = time.time()
            response = requests.post(url, json=payload, timeout=timeout)
            end_time = time.time()

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result.get("response", ""),
                    "response_time": end_time - start_time,
                    "total_tokens": result.get("eval_count", 0)
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "response_time": end_time - start_time
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": 0
            }

    def test_customer_service_scenarios(self):
        """测试客服场景"""
        scenarios = [
            {
                "id": 1,
                "scenario": "用户投诉系统问题",
                "user_message": "你们系统有问题，我无法登录！",
                "prompt": "你是一个专业的客服人员。用户说：你们系统有问题，我无法登录！请给出一个专业的回应。"
            },
            {
                "id": 2,
                "scenario": "用户询问产品功能",
                "user_message": "这个产品有什么功能？能帮我介绍一下吗？",
                "prompt": "你是一个专业的客服人员。用户问：这个产品有什么功能？能帮我介绍一下吗？请给出一个专业的回应。"
            },
            {
                "id": 3,
                "scenario": "用户要求退款",
                "user_message": "我对你们的产品不满意，要求退款！",
                "prompt": "你是一个专业的客服人员。用户说：我对你们的产品不满意，要求退款！请给出一个专业的回应。"
            },
            {
                "id": 4,
                "scenario": "用户咨询技术问题",
                "user_message": "我使用时遇到了错误代码500，该怎么解决？",
                "prompt": "你是一个专业的客服人员。用户问：我使用时遇到了错误代码500，该怎么解决？请给出一个专业的回应。"
            },
            {
                "id": 5,
                "scenario": "用户表达感谢",
                "user_message": "谢谢你们的帮助，问题已经解决了！",
                "prompt": "你是一个专业的客服人员。用户说：谢谢你们的帮助，问题已经解决了！请给出一个专业的回应。"
            }
        ]

        print("🚀 开始客服技能测试...")
        print(f"📋 模型: {self.model}")
        print(f"📋 测试场景数: {len(scenarios)}")
        print("-" * 60)

        for scenario in scenarios:
            print(f"\n📝 测试场景 {scenario['id']}: {scenario['scenario']}")
            print(f"💬 用户消息: {scenario['user_message']}")

            # 查询模型
            result = self.query_model(scenario['prompt'])

            if result['success']:
                print(f"✅ 测试成功")
                print(f"⏱️  响应时间: {result['response_time']:.2f}秒")
                if result['total_tokens']:
                    print(f"🔢 Token数: {result['total_tokens']}")
                print(f"🤖 AI回应: {result['response']}")

                # 保存结果
                self.results.append({
                    "scenario_id": scenario['id'],
                    "scenario": scenario['scenario'],
                    "user_message": scenario['user_message'],
                    "ai_response": result['response'],
                    "response_time": result['response_time'],
                    "tokens": result.get('total_tokens', 0),
                    "success": True,
                    "timestamp": datetime.now().isoformat()
                })
            else:
                print(f"❌ 测试失败: {result['error']}")
                self.results.append({
                    "scenario_id": scenario['id'],
                    "scenario": scenario['scenario'],
                    "error": result['error'],
                    "success": False,
                    "timestamp": datetime.now().isoformat()
                })

            print("-" * 40)

            # 避免请求过快
            time.sleep(2)

    def analyze_results(self):
        """分析测试结果"""
        if not self.results:
            print("❌ 没有测试结果可分析")
            return

        successful_tests = [r for r in self.results if r['success']]
        failed_tests = [r for r in self.results if not r['success']]

        print("\n" + "="*60)
        print("📊 测试结果分析")
        print("="*60)

        # 基本统计
        print(f"📈 总测试数: {len(self.results)}")
        print(f"✅ 成功数: {len(successful_tests)}")
        print(f"❌ 失败数: {len(failed_tests)}")
        print(f"📊 成功率: {len(successful_tests)/len(self.results)*100:.1f}%")

        if successful_tests:
            avg_response_time = sum(r['response_time'] for r in successful_tests) / len(successful_tests)
            total_tokens = sum(r.get('tokens', 0) for r in successful_tests)
            print(f"⏱️  平均响应时间: {avg_response_time:.2f}秒")
            print(f"🔢 总Token数: {total_tokens}")

        # 客服技能分析
        print("\n🎯 客服技能评估:")

        for result in successful_tests:
            print(f"\n场景 {result['scenario_id']}: {result['scenario']}")
            response = result['ai_response']

            # 分析客服技能要素
            skills = {
                "礼貌用语": any(word in response for word in ["请", "谢谢", "您好", "抱歉", "对不起", "感谢"]),
                "同理心": any(word in response for word in ["理解", "明白", "体会", "感受"]),
                "解决问题": any(word in response for word in ["解决", "处理", "帮助", "协助", "支持"]),
                "询问细节": any(word in response for word in ["详细", "具体", "什么", "如何", "怎么"]),
                "承诺行动": any(word in response for word in ["会", "将", "马上", "立即", "尽快"]),
            }

            print(f"  技能评估:")
            for skill, present in skills.items():
                status = "✅" if present else "❌"
                print(f"    {status} {skill}")

        # 保存详细结果
        self.save_results()

    def save_results(self):
        """保存测试结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"customer_service_test_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "model": self.model,
                "test_time": datetime.now().isoformat(),
                "summary": {
                    "total_tests": len(self.results),
                    "successful": len([r for r in self.results if r['success']]),
                    "failed": len([r for r in self.results if not r['success']]),
                },
                "results": self.results
            }, f, ensure_ascii=False, indent=2)

        print(f"\n💾 详细结果已保存到: {filename}")

def main():
    """主函数"""
    print("🤖 AgentPsyAssessment - 客服技能测试工具")
    print("=" * 60)

    # 初始化测试器
    tester = CustomerServiceTest()

    # 运行测试
    tester.test_customer_service_scenarios()

    # 分析结果
    tester.analyze_results()

    print("\n🎉 测试完成！")

if __name__ == "__main__":
    main()