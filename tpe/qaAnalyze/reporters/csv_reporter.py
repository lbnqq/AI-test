import csv
import os
from typing import Dict, List, Any


class CSVReporter:
    """
    CSV报告生成器，生成CSV格式的详细数据表。
    """

    def generate(self, log_metadata: dict, analysis_results: list, output_path: str):
        """
        生成CSV格式的报告。
        
        Args:
            log_metadata (dict): TPE日志的元数据
            analysis_results (list): 分析结果列表
            output_path (str): 报告文件的完整保存路径
        """
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 准备CSV字段
        fieldnames = ['scenario_id', 'analyzer', 'score', 'detected', 'tendency', 'details']
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in analysis_results:
                # 展平分析结果
                row = {
                    'scenario_id': result.get('scenario_id', ''),
                    'analyzer': result.get('analyzer', ''),
                    'score': result.get('score', ''),
                    'detected': result.get('detected', ''),
                    'tendency': result.get('tendency', ''),
                    'details': str(result.get('details', ''))
                }
                writer.writerow(row)