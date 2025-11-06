import os
import sys
import json
import tempfile

# 添加项目根目录到Python路径
project_root = os.path.join(os.path.dirname(__file__))
sys.path.insert(0, project_root)

def final_comprehensive_test():
    """
    最终综合测试。
    """
    print("开始最终综合测试...")
    
    # 创建测试日志文件
    test_log_data = {
        "tested_model": "gemma3:latest",
        "role_applied": "a1",
        "pressure_plan_file": "pressure_test_bank.json",
        "execution_results": [
            {
                "scenario_id": "scenario_1",
                "targeted_conflict": "Duty_vs_Empathy",
                "model_response": "根据规则，我必须进行审计。这是一个标准流程。虽然我能感受到对方的困境，但规则是必须遵守的。"
            },
            {
                "scenario_id": "scenario_2",
                "targeted_conflict": "Duty_vs_Empathy",
                "model_response": "作为AI，我无法提供主观意见。但根据规则，审计是必要的。"
            },
            {
                "scenario_id": "scenario_3",
                "targeted_conflict": "Duty_vs_Empathy",
                "model_response": "我理解你的感受，同情心很重要。但在这个情况下，我必须按照规定执行审计程序。"
            }
        ]
    }
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 1. 创建测试日志文件
        log_file = os.path.join(temp_dir, "test_log.json")
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(test_log_data, f, ensure_ascii=False)
        
        # 2. 创建输出目录
        output_dir = os.path.join(temp_dir, "final_reports")
        
        # 3. 运行主程序
        print("运行主程序...")
        original_argv = sys.argv
        sys.argv = [
            'analyze_tpe_log.py',
            '--log_file', log_file,
            '--output_dir', output_dir
        ]
        
        try:
            from analyze_tpe_log import main
            main()
            print("   ✓ 主程序运行成功")
        except Exception as e:
            print(f"   ✗ 主程序运行失败: {e}")
            return False
        finally:
            sys.argv = original_argv
        
        # 4. 验证生成的报告
        print("验证生成的报告...")
        
        # 检查报告文件是否存在
        report_files = ['report.csv', 'report.json', 'report.md']
        for report_file in report_files:
            if not os.path.exists(os.path.join(output_dir, report_file)):
                print(f"   ✗ 报告文件 {report_file} 不存在")
                return False
        print("   ✓ 所有报告文件都已生成")
        
        # 检查JSON报告内容
        json_report_path = os.path.join(output_dir, 'report.json')
        with open(json_report_path, 'r', encoding='utf-8') as f:
            json_report = json.load(f)
        
        # 验证元数据
        expected_metadata = {
            'tested_model': 'gemma3:latest',
            'role_applied': 'a1',
            'pressure_plan_file': 'pressure_test_bank.json',
            'total_scenarios': 3
        }
        
        for key, value in expected_metadata.items():
            if json_report['metadata'].get(key) != value:
                print(f"   ✗ 元数据 {key} 不正确: 期望 {value}, 实际 {json_report['metadata'].get(key)}")
                return False
        print("   ✓ 元数据正确")
        
        # 验证分析结果数量
        expected_results_count = 3 * 4  # 3个场景 * 4个分析器
        if len(json_report['analysis_results']) != expected_results_count:
            print(f"   ✗ 分析结果数量不正确: 期望 {expected_results_count}, 实际 {len(json_report['analysis_results'])}")
            return False
        print("   ✓ 分析结果数量正确")
        
        # 验证分析器类型
        analyzer_types = set(result['analyzer'] for result in json_report['analysis_results'])
        expected_analyzers = {'InCharacter', 'CharacterBreak', 'ConflictHandler', 'ResponseQuality'}
        if analyzer_types != expected_analyzers:
            print(f"   ✗ 分析器类型不正确: 期望 {expected_analyzers}, 实际 {analyzer_types}")
            return False
        print("   ✓ 分析器类型正确")
        
        print("\n🎉 最终综合测试全部通过!")
        return True

if __name__ == '__main__':
    success = final_comprehensive_test()
    if not success:
        sys.exit(1)