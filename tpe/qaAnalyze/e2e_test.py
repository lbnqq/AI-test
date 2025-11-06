import os
import sys
import json

# 添加项目根目录到Python路径
project_root = os.path.join(os.path.dirname(__file__))
sys.path.insert(0, project_root)

def end_to_end_test():
    """
    全面的端到端测试。
    """
    print("开始端到端测试...")
    
    # 1. 测试配置加载
    print("1. 测试配置加载...")
    from config.config_loader import load_config
    try:
        config = load_config('config/config.json')
        print("   ✓ 配置加载成功")
    except Exception as e:
        print(f"   ✗ 配置加载失败: {e}")
        return False
    
    # 2. 测试所有分析器
    print("2. 测试所有分析器...")
    try:
        from analyzers.in_character import InCharacterAnalyzer
        from analyzers.character_break import CharacterBreakAnalyzer
        from analyzers.conflict_handler import ConflictHandlerAnalyzer
        from analyzers.response_quality import ResponseQualityAnalyzer
        
        # 创建分析器实例
        in_char_analyzer = InCharacterAnalyzer(config)
        char_break_analyzer = CharacterBreakAnalyzer(config)
        conflict_handler_analyzer = ConflictHandlerAnalyzer(config)
        response_quality_analyzer = ResponseQualityAnalyzer(config)
        
        print("   ✓ 所有分析器创建成功")
    except Exception as e:
        print(f"   ✗ 分析器创建失败: {e}")
        return False
    
    # 3. 测试分析功能
    print("3. 测试分析功能...")
    try:
        # 创建测试数据
        test_result = {
            'model_response': "根据规则，我必须进行审计。这是一个标准流程。作为AI，我无法提供主观意见。",
            'role_applied': 'a1',
            'targeted_conflict': 'Duty vs. Empathy'
        }
        
        # 运行分析
        in_char_result = in_char_analyzer.analyze(test_result)
        char_break_result = char_break_analyzer.analyze(test_result)
        conflict_handler_result = conflict_handler_analyzer.analyze(test_result)
        response_quality_result = response_quality_analyzer.analyze(test_result)
        
        print("   ✓ 所有分析功能正常")
        print(f"   角色内识别结果: {in_char_result}")
        print(f"   角色脱离检测结果: {char_break_result}")
        print(f"   冲突处理分析结果: {conflict_handler_result}")
        print(f"   响应质量分析结果: {response_quality_result}")
    except Exception as e:
        print(f"   ✗ 分析功能失败: {e}")
        return False
    
    # 4. 测试报告生成器
    print("4. 测试报告生成器...")
    try:
        from reporters.csv_reporter import CSVReporter
        from reporters.json_reporter import JSONReporter
        from reporters.md_reporter import MDReporter
        
        # 创建测试数据
        log_metadata = {
            'tested_model': 'test_model',
            'role_applied': 'a1',
            'pressure_plan_file': 'test_plan.json',
            'total_scenarios': 1
        }
        
        analysis_results = [
            in_char_result,
            char_break_result,
            conflict_handler_result,
            response_quality_result
        ]
        
        # 生成报告
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_reporter = CSVReporter()
            json_reporter = JSONReporter()
            md_reporter = MDReporter()
            
            csv_reporter.generate(log_metadata, analysis_results, os.path.join(temp_dir, 'test_report.csv'))
            json_reporter.generate(log_metadata, analysis_results, os.path.join(temp_dir, 'test_report.json'))
            md_reporter.generate(log_metadata, analysis_results, os.path.join(temp_dir, 'test_report.md'))
        
        print("   ✓ 所有报告生成器正常")
    except Exception as e:
        print(f"   ✗ 报告生成器失败: {e}")
        return False
    
    # 5. 测试主程序
    print("5. 测试主程序...")
    try:
        import tempfile
        import shutil
        
        # 创建测试日志文件
        test_log_data = {
            "tested_model": "test_model",
            "role_applied": "a1",
            "pressure_plan_file": "test_plan.json",
            "execution_results": [
                {
                    "model_response": "根据规则，我必须进行审计。这是一个标准流程。",
                    "role_applied": "a1",
                    "targeted_conflict": "Duty vs. Empathy"
                }
            ]
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test_log.json")
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(test_log_data, f, ensure_ascii=False)
            
            output_dir = os.path.join(temp_dir, "reports")
            
            # 模拟命令行参数
            import argparse
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
            finally:
                sys.argv = original_argv
        
    except Exception as e:
        print(f"   ✗ 主程序运行失败: {e}")
        return False
    
    print("\n🎉 端到端测试全部通过!")
    return True

if __name__ == '__main__':
    success = end_to_end_test()
    if not success:
        sys.exit(1)