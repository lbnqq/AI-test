#!/usr/bin/env python3
import time
import os
import glob

print("监控NPI测试进度...")
print("="*50)

last_count = 0
while True:
    # 查找最新的进度文件
    progress_files = glob.glob('results/npi_40_progress_*.json')
    complete_files = glob.glob('results/npi_40_complete_*.json')
    
    if complete_files:
        print(f"\n测试已完成！结果文件: {complete_files[-1]}")
        break
    
    if progress_files:
        latest_file = max(progress_files, key=os.path.getctime)
        
        try:
            import json
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            completed = len(data.get('assessment_results', []))
            total = data.get('test_summary', {}).get('total_questions', 40)
            
            if completed != last_count:
                print(f"[{time.strftime('%H:%M:%S')}] 已完成 {completed}/{total} 题")
                last_count = completed
                
                if completed >= total:
                    print("测试完成！")
                    break
                    
        except Exception as e:
            print(f"读取进度文件出错: {e}")
    
    # 检查进程是否还在运行
    import subprocess
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'run_npi_40_stepwise' not in result.stdout:
            print("\n测试进程已停止")
            break
    except:
        pass
    
    time.sleep(30)  # 每30秒检查一次