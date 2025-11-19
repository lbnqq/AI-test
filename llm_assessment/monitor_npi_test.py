#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import subprocess
import os

def monitor_npi_test():
    """监控NPI测试进度"""
    
    print("NPI-40 测试监控器")
    print("="*50)
    
    while True:
        # 检查进程是否还在运行
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            npi_process = None
            
            for line in lines:
                if 'run_npi_40_robust.py' in line and 'grep' not in line:
                    npi_process = line
                    break
            
            if npi_process:
                print(f"\n[{time.strftime('%H:%M:%S')}] 测试正在进行中...")
                print(f"进程信息: {npi_process}")
                
                # 检查日志文件
                if os.path.exists('npi_full_test.log'):
                    with open('npi_full_test.log', 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content:
                            lines = content.split('\n')
                            print(f"日志行数: {len(lines)}")
                            if len(lines) > 0:
                                print("最后几行:")
                                for line in lines[-5:]:
                                    if line.strip():
                                        print(f"  {line}")
                
                # 检查结果文件
                import glob
                result_files = glob.glob('results/npi_40_complete_*.json')
                if result_files:
                    print(f"发现结果文件: {len(result_files)} 个")
                    for f in result_files:
                        print(f"  {f}")
                
            else:
                print(f"\n[{time.strftime('%H:%M:%S')}] 测试进程已结束")
                
                # 检查最终结果
                import glob
                result_files = glob.glob('results/npi_40_complete_*.json')
                if result_files:
                    print(f"找到结果文件: {result_files[0]}")
                    try:
                        import json
                        with open(result_files[0], 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        summary = data.get('test_summary', {})
                        metadata = data.get('assessment_metadata', {})
                        
                        print(f"\n测试完成摘要:")
                        print(f"  模型: {metadata.get('model_id', 'N/A')}")
                        print(f"  总问题数: {summary.get('total_questions', 0)}")
                        print(f"  成功响应: {summary.get('successful_responses', 0)}")
                        print(f"  失败响应: {summary.get('failed_responses', 0)}")
                        print(f"  成功率: {summary.get('successful_responses', 0)/summary.get('total_questions', 1)*100:.1f}%")
                        
                    except Exception as e:
                        print(f"读取结果文件出错: {e}")
                else:
                    print("未找到结果文件")
                
                break
                
        except Exception as e:
            print(f"监控出错: {e}")
        
        # 等待60秒再检查
        time.sleep(60)

if __name__ == "__main__":
    monitor_npi_test()