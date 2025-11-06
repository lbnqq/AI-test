import json
import os
from typing import Dict, List, Any


class JSONReporter:
    """
    JSON报告生成器，生成JSON格式的结构化数据报告。
    """

    def generate(self, log_metadata: dict, analysis_results: list, output_path: str):
        """
        生成JSON格式的报告。
        
        Args:
            log_metadata (dict): TPE日志的元数据
            analysis_results (list): 分析结果列表
            output_path (str): 报告文件的完整保存路径
        """
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 组合报告数据
        report_data = {
            'metadata': log_metadata,
            'analysis_results': analysis_results
        }
        
        # 写入JSON文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)