#!/bin/bash
echo "🔄 等待a6 OC测试完成..."

# 等待a6测试完成
while pgrep -f "stage1_qwen_plus_a6_oc_legal_test.py" > /dev/null; do
    echo "$(date): a6 OC测试仍在运行中，等待完成..."
    sleep 10
done

echo "🎉 a6 OC测试已完成！"
echo "🚀 立即启动a7 OC测试..."

# 启动a7测试
python3 stage1_qwen_plus_a7_oc_legal_test.py

echo "✅ 连锁测试流程完成！"