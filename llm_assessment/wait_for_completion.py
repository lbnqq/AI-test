#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import time
import glob
from datetime import datetime

def wait_for_completion():
    print("等待NPI-40测试完成...")
    print("测试将在后台继续运行，完成后会显示结果摘要。")
    
    last_completed = 0
    last_check_time = time.time()
    
    while True:
        # 查找最新的进度文件
        progress_files = glob.glob('/1910316727/AgentPsyAssessment/llm_assessment/results/npi_progress_*.json')
        
        if progress_files:
            latest_file = max(progress_files, key=os.path.getctime)
            
            try:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                metadata = data.get('test_metadata', {})
                total = metadata.get('total_questions', 40)
                completed = metadata.get('completed_questions', 0)
                percentage = metadata.get('progress_percentage', 0)
                elapsed = metadata.get('total_elapsed_time', 0)
                
                # 只在有新进展时打印
                if completed > last_completed or time.time() - last_check_time > 300:  # 5分钟强制更新一次
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 进度更新: {completed}/{total} ({percentage:.1f}%) - 已用时 {elapsed/60:.1f} 分钟")
                    last_completed = completed
                    last_check_time = time.time()
                
                # 检查是否完成
                if completed >= total:
                    print(f"\n*** 测试已完成! ***")
                    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"总用时: {elapsed/60:.1f} 分钟")
                    
                    # 查找最终结果文件
                    time.sleep(5)  # 等待最终文件生成
                    final_files = glob.glob('/1910316727/AgentPsyAssessment/llm_assessment/results/npi_final_*.json')
                    
                    if final_files:
                        final_file = max(final_files, key=os.path.getctime)
                        print(f"最终结果文件: {final_file}")
                        
                        # 分析结果
                        with open(final_file, 'r', encoding='utf-8') as f:
                            final_data = json.load(f)
                        
                        results = final_data.get('results', [])
                        successful = sum(1 for r in results if 'response' in r)
                        failed = sum(1 for r in results if 'error' in r)
                        
                        print(f"\n=== 测试结果摘要 ===")
                        print(f"成功响应: {successful}/{total}")
                        print(f"失败响应: {failed}/{total}")
                        
                        # 分析各维度
                        dimensions = {}
                        for result in results:
                            if 'response' in result:
                                dim = result.get('dimension', 'Unknown')
                                if dim not in dimensions:
                                    dimensions[dim] = 0
                                dimensions[dim] += 1
                        
                        print(f"\n各维度响应情况:")
                        for dim, count in dimensions.items():
                            print(f"  {dim}: {count} 个问题")
                        
                        # 简单的自恋倾向评估
                        print(f"\n注意: 完整的自恋倾向评估需要根据每个回答的内容进行详细分析。")
                        print(f"请查看最终结果文件中的完整回答和评估标准。")
                        
                    break
                    
            except Exception as e:
                print(f"读取进度文件出错: {e}")
        
        # 检查进程是否还在运行
        import subprocess
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'complete_npi_test.py' not in result.stdout:
            print("\n警告: 测试进程似乎已停止运行!")
            break
        
        time.sleep(60)  # 每分钟检查一次

if __name__ == "__main__":
    wait_for_completion()