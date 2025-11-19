#!/bin/bash

echo "NPI-40 自恋测试实时监控"
echo "========================="

while true; do
    # 查找最新的进度文件
    LATEST_FILE=$(ls -t /1910316727/AgentPsyAssessment/llm_assessment/results/npi_progress_*.json 2>/dev/null | head -1)
    
    if [ -n "$LATEST_FILE" ]; then
        echo "[$(date '+%H:%M:%S')] 最新进度文件: $(basename $LATEST_FILE)"
        
        # 提取进度信息
        python3 -c "
import json
import sys
try:
    with open('$LATEST_FILE', 'r', encoding='utf-8') as f:
        data = json.load(f)
    metadata = data.get('test_metadata', {})
    total = metadata.get('total_questions', 40)
    completed = metadata.get('completed_questions', 0)
    percentage = metadata.get('progress_percentage', 0)
    elapsed = metadata.get('total_elapsed_time', 0)
    print(f'  进度: {completed}/{total} ({percentage:.1f}%)')
    print(f'  用时: {elapsed/60:.1f} 分钟')
    
    # 检查进程是否还在运行
    import subprocess
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    if 'complete_npi_test.py' in result.stdout and 'grep' not in result.stdout:
        print('  状态: 测试进行中...')
    else:
        print('  状态: 测试进程未运行!')
except Exception as e:
    print(f'  错误: {e}')
"
    else
        echo "[$(date '+%H:%M:%S')] 未找到进度文件"
    fi
    
    echo "----------------------------------------"
    sleep 30
done