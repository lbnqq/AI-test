#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理所有原始测评报告的可信评估分析主脚本

该脚本将使用已实现的分段评分系统处理所有原始测评报告，
系统包含多模型评估、争议解决和信度验证功能。
"""
import os
import glob
from pathlib import Path
import sys
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from segmented_scoring_evaluator import SegmentedScoringEvaluator


def process_all_reports():
    """
    处理所有原始测评报告
    """
    print("🚀 开始批量可信评估分析")
    print("="*60)
    
    # 定义输入和输出目录
    input_dir = "results/readonly-original"
    output_dir = "final_segmented_analysis_results"
    
    # 检查输入目录
    if not os.path.exists(input_dir):
        print(f"❌ 输入目录不存在: {input_dir}")
        return
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有JSON文件
    json_files = glob.glob(os.path.join(input_dir, "*.json"))
    total_files = len(json_files)
    
    print(f"📁 找到 {total_files} 个原始测评报告")
    print(f"📂 输出目录: {output_dir}")
    print()
    
    # 初始化评估器
    evaluator = SegmentedScoringEvaluator()
    
    # 统计变量
    processed = 0
    successful = 0
    failed = 0
    
    print("开始处理...")
    start_time = datetime.now()
    
    # 处理每个文件
    for i, file_path in enumerate(json_files, 1):
        filename = os.path.basename(file_path)
        print(f"[{i}/{total_files}] 正在处理: {filename}")
        
        try:
            # 执行评估
            result = evaluator.evaluate_file_with_multiple_models(file_path, output_dir)
            
            if result['success']:
                successful += 1
                print(f"  ✅ 成功 - 一致性: {result['consistency_score']:.2f}%, "
                      f"信度: {result['reliability_score']:.2f}%")
            else:
                failed += 1
                print(f"  ❌ 失败 - {result.get('error', 'Unknown error')}")
            
            processed += 1
            
        except Exception as e:
            failed += 1
            processed += 1
            print(f"  ❌ 异常 - {str(e)}")
            
        print()
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    # 输出最终统计
    print("="*60)
    print("📊 最终处理报告")
    print(f"⏰ 开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏰ 结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱️  总耗时: {duration}")
    print()
    print(f"📈 总文件数: {total_files}")
    print(f"✅ 成功处理: {successful}")
    print(f"❌ 处理失败: {failed}")
    print(f"🎯 成功率: {(successful/total_files)*100:.2f}%" if total_files > 0 else "N/A")
    print()
    print(f"💾 分析结果保存在: {output_dir}")
    print()
    print("系统特性:")
    print("  • 分段评分: 每5题一组进行独立评估")
    print("  • 多模型评估: 使用3个主要模型 + 争议处理模型")
    print("  • 争议解决: 多轮争议解决机制，最多3轮")
    print("  • 信度验证: Cronbach's Alpha + 评估者间信度")
    print("  • 一致性检验: 模型间评分一致性分析")
    print("="*60)


if __name__ == "__main__":
    print("可信评估分析系统 - 全部原始测评报告批处理")
    print("系统将处理 results/readonly-original 目录下的所有测评报告")
    print("使用分段评分、多模型评估、争议解决和信度验证机制")
    print()
    
    process_all_reports()