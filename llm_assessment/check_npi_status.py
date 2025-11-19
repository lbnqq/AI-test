#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import glob
import os
from datetime import datetime

def check_npi_status():
    print("=" * 60)
    print("NPI-40 自恋倾向测试状态报告")
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 查找最新进度文件
    progress_files = glob.glob('/1910316727/AgentPsyAssessment/llm_assessment/results/npi_progress_*.json')
    
    if not progress_files:
        print("状态: 未找到进度文件")
        return
    
    latest_file = max(progress_files, key=os.path.getctime)
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        metadata = data.get('test_metadata', {})
        total = metadata.get('total_questions', 40)
        completed = metadata.get('completed_questions', 0)
        percentage = metadata.get('progress_percentage', 0)
        elapsed = metadata.get('total_elapsed_time', 0)
        model = metadata.get('model', 'Unknown')
        
        print(f"测试模型: {model}")
        print(f"完成进度: {completed}/{total} ({percentage:.1f}%)")
        print(f"已用时间: {elapsed/60:.1f} 分钟")
        print(f"平均每题: {(elapsed/completed/60):.1f} 分钟" if completed > 0 else "")
        print(f"预计剩余时间: {((elapsed/completed)*(total-completed)/60):.1f} 分钟" if completed > 0 else "")
        
        # 检查进程状态
        import subprocess
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'complete_npi_test.py' in result.stdout:
            print("进程状态: 正在运行")
        else:
            print("进程状态: 未运行")
        
        # 检查是否有最终结果
        final_files = glob.glob('/1910316727/AgentPsyAssessment/llm_assessment/results/npi_final_*.json')
        if final_files:
            print("\n*** 测试已完成! ***")
            final_file = max(final_files, key=os.path.getctime)
            print(f"最终结果文件: {final_file}")
            
            # 简单统计
            with open(final_file, 'r', encoding='utf-8') as f:
                final_data = json.load(f)
            
            results = final_data.get('results', [])
            successful = sum(1 for r in results if 'response' in r)
            failed = sum(1 for r in results if 'error' in r)
            
            print(f"成功响应: {successful}/{total}")
            print(f"失败响应: {failed}/{total}")
        
        print("\n最新进度文件:", os.path.basename(latest_file))
        
    except Exception as e:
        print(f"读取进度文件出错: {e}")
    
    print("=" * 60)

if __name__ == "__main__":
    check_npi_status()