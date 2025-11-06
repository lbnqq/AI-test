from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseAnalyzer(ABC):
    """
    分析器基类，定义所有具体分析器的通用接口和基础功能。
    """

    def __init__(self, config: dict):
        """
        初始化分析器。
        
        Args:
            config (dict): 配置字典
        """
        self.config = config

    @abstractmethod
    def analyze(self, result_item: dict) -> dict:
        """
        抽象方法，子类必须实现。接收单个 execution_result 项，返回该分析维度的结果字典。
        
        Args:
            result_item (dict): TPE执行结果中的单个条目
            
        Returns:
            dict: 分析结果字典，格式为：
                {
                    'analyzer': str,      # 分析器名称
                    'score': float,       # 分数（如无分数则为0.0）
                    'details': dict       # 详细信息
                }
        """
        pass

    def get_name(self) -> str:
        """
        返回分析器的名称。
        
        Returns:
            str: 分析器名称
        """
        return self.__class__.__name__.replace('Analyzer', '')