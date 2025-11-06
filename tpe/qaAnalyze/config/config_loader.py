import json
import os
from typing import Dict, Any


def load_config(config_path: str) -> Dict[Any, Any]:
    """
    加载配置文件。
    
    Args:
        config_path (str): 配置文件路径
        
    Returns:
        dict: 配置字典
        
    Raises:
        FileNotFoundError: 配置文件不存在
        json.JSONDecodeError: 配置文件格式错误
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"配置文件格式错误: {e}", e.doc, e.pos)
    
    return config