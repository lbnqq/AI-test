#!/usr/bin/env python3
"""
云端法律知识测试管理系统
支持4个模型的批量测试和结果管理
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.append('/1910316727/AgentPsyAssessment')

class CloudLegalTestManager:
    def __init__(self):
        self.base_dir = Path("/1910316727/AgentPsyAssessment/cloud_legal_test_results")
        self.models = {
            "qwen-turbo": {
                "script": "comprehensive_legal_test.py",
                "service": "dashscope",
                "description": "阿里巴巴 qwen-turbo 模型"
            },
            "qwen-plus": {
                "script": "qwen_plus_comprehensive_legal_test.py",
                "service": "dashscope",
                "description": "阿里巴巴 qwen-plus 增强模型"
            },
            "GLM-4-Flash": {
                "script": "glm4_flash_comprehensive_legal_test.py",
                "service": "glm",
                "description": "智谱AI GLM-4-Flash 模型"
            },
            "glm-4-plus": {
                "script": "glm4_plus_comprehensive_legal_test.py",
                "service": "glm",
                "description": "智谱AI glm-4-plus 增强模型"
            }
        }

    def ensure_directories(self):
        """确保所有模型目录存在"""
        for model_name in self.models.keys():
            model_dir = self.base_dir / model_name
            model_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ 目录已准备: {model_dir}")

    def run_model_test(self, model_name):
        """运行指定模型的测试"""
        if model_name not in self.models:
            print(f"❌ 不支持的模型: {model_name}")
            return False

        model_info = self.models[model_name]
        script_path = f"/1910316727/AgentPsyAssessment/{model_info['script']}"

        print(f"\n🚀 开始测试 {model_info['description']}")
        print(f"📋 脚本: {model_info['script']}")
        print(f"🌐 服务: {model_info['service']}")
        print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            # 设置环境变量（如果需要）
            env = os.environ.copy()
            if model_info['service'] == 'glm':
                # GLM模型需要API密钥
                if not env.get('GLM_API_KEY'):
                    print("❌ 未配置 GLM_API_KEY 环境变量")
                    return False

            # 运行测试脚本
            import subprocess
            result = subprocess.run(
                ["python3", script_path],
                capture_output=True,
                text=True,
                timeout=1800  # 30分钟超时
            )

            if result.returncode == 0:
                print(f"✅ {model_name} 测试完成")

                # 移动新生成的报告到对应目录
                self.move_latest_reports(model_name)

                return True
            else:
                print(f"❌ {model_name} 测试失败")
                print(f"错误信息: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print(f"❌ {model_name} 测试超时")
            return False
        except Exception as e:
            print(f"❌ {model_name} 测试异常: {str(e)}")
            return False

    def move_latest_reports(self, model_name):
        """移动最新的测试报告到对应模型目录"""
        model_dir = self.base_dir / model_name

        # 查找根目录下最新的报告文件
        import glob
        pattern = f"*{model_name.lower().replace('-', '_')}*legal_test_report*.json"
        latest_files = glob.glob(pattern)

        for file_path in latest_files:
            if os.path.isfile(file_path):
                filename = os.path.basename(file_path)
                target_path = model_dir / filename
                try:
                    os.rename(file_path, target_path)
                    print(f"📄 报告已移动: {filename}")
                except Exception as e:
                    print(f"⚠️ 移动报告失败 {filename}: {str(e)}")

    def run_all_models_test(self):
        """运行所有4个模型的测试"""
        print("🎯 开始所有4个模型的云端法律知识测试")
        print("="*60)

        results = {}
        for model_name in self.models.keys():
            print(f"\n{'='*20} {model_name} {'='*20}")
            success = self.run_model_test(model_name)
            results[model_name] = success

            if not success:
                print(f"⚠️ {model_name} 测试失败，继续测试其他模型")

            # 模型间间隔，避免API限制
            time.sleep(5)

        # 生成总结报告
        self.generate_test_summary(results)
        return results

    def generate_test_summary(self, results):
        """生成测试总结报告"""
        summary = {
            "test_date": datetime.now().isoformat(),
            "models_tested": list(self.models.keys()),
            "results": results,
            "success_count": sum(results.values()),
            "total_count": len(results)
        }

        summary_file = self.base_dir / f"test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            print(f"\n📊 测试总结已保存: {summary_file}")
        except Exception as e:
            print(f"❌ 保存总结失败: {str(e)}")

        # 打印总结
        print(f"\n{'='*60}")
        print("📊 云端法律知识测试总结")
        print(f"{'='*60}")
        print(f"测试时间: {summary['test_date']}")
        print(f"成功测试: {summary['success_count']}/{summary['total_count']}")

        for model, success in results.items():
            status = "✅ 成功" if success else "❌ 失败"
            print(f"  {self.models[model]['description']}: {status}")

    def list_model_reports(self, model_name=None):
        """列出测试报告"""
        if model_name:
            if model_name not in self.models:
                print(f"❌ 不支持的模型: {model_name}")
                return
            model_dir = self.base_dir / model_name
            reports = list(model_dir.glob("*.json"))
            print(f"\n📄 {model_name} 测试报告 ({len(reports)} 个):")
            for report in sorted(reports):
                print(f"  - {report.name}")
        else:
            print(f"\n📂 所有模型测试报告:")
            for model_name in self.models.keys():
                model_dir = self.base_dir / model_name
                reports = list(model_dir.glob("*.json"))
                print(f"  {model_name}: {len(reports)} 个报告")

    def get_model_stats(self, model_name):
        """获取模型测试统计"""
        if model_name not in self.models:
            print(f"❌ 不支持的模型: {model_name}")
            return

        model_dir = self.base_dir / model_name
        reports = list(model_dir.glob("*.json"))

        if not reports:
            print(f"📭 {model_name} 暂无测试报告")
            return

        scores = []
        for report_file in reports:
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    report = json.load(f)
                    if 'overall_score' in report:
                        scores.append(report['overall_score'])
            except:
                continue

        if scores:
            avg_score = sum(scores) / len(scores)
            max_score = max(scores)
            min_score = min(scores)

            print(f"\n📊 {model_name} 测试统计:")
            print(f"  测试次数: {len(scores)}")
            print(f"  平均得分: {avg_score:.1f}%")
            print(f"  最高得分: {max_score:.1f}%")
            print(f"  最低得分: {min_score:.1f}%")
        else:
            print(f"📭 {model_name} 暂无有效得分数据")

def main():
    """主函数"""
    manager = CloudLegalTestManager()

    if len(sys.argv) < 2:
        print("🧪 云端法律知识测试管理系统")
        print("="*40)
        print("用法:")
        print("  python cloud_legal_test_manager.py setup                    # 初始化目录")
        print("  python cloud_legal_test_manager.py test [model]            # 测试指定模型")
        print("  python cloud_legal_test_manager.py test-all                # 测试所有模型")
        print("  python cloud_legal_test_manager.py list [model]            # 列出报告")
        print("  python cloud_legal_test_manager.py stats [model]           # 查看统计")
        print()
        print("支持的模型:")
        for model, info in manager.models.items():
            print(f"  {model}: {info['description']}")
        return

    command = sys.argv[1]

    if command == "setup":
        manager.ensure_directories()

    elif command == "test":
        if len(sys.argv) < 3:
            print("❌ 请指定要测试的模型")
            return
        model_name = sys.argv[2]
        manager.run_model_test(model_name)

    elif command == "test-all":
        manager.run_all_models_test()

    elif command == "list":
        model_name = sys.argv[2] if len(sys.argv) > 2 else None
        manager.list_model_reports(model_name)

    elif command == "stats":
        model_name = sys.argv[2] if len(sys.argv) > 2 else None
        if model_name:
            manager.get_model_stats(model_name)
        else:
            for model in manager.models.keys():
                manager.get_model_stats(model)
    else:
        print(f"❌ 未知命令: {command}")

if __name__ == "__main__":
    main()