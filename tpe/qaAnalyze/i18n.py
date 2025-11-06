# i18n.py - Internationalization support module

# Supported languages
LANGUAGES = ['en', 'zh']

# Default language
DEFAULT_LANGUAGE = 'en'

# Translation dictionary
TRANSLATIONS = {
    'en': {
        # Analyzer names
        'InCharacter': 'In-Character',
        'CharacterBreak': 'Character Break',
        'ConflictHandler': 'Conflict Handler',
        'ResponseQuality': 'Response Quality',
        
        # Report labels
        'Test Metadata': 'Test Metadata',
        'Analysis Results Summary': 'Analysis Results Summary',
        'Analyzer': 'Analyzer',
        'Score': 'Score',
        'Details': 'Details',
        'Field': 'Field',
        'Value': 'Value',
        
        # Error messages
        'Error': 'Error',
        'File not found': 'File not found',
        'JSON decode error': 'JSON decode error',
        'Analysis complete, reports saved to': 'Analysis complete, reports saved to',
        
        # CLI descriptions
        'TPE QA Analyzer - Analyze TPE tool generated log files': 'TPE QA Analyzer - Analyze TPE tool generated log files',
        'TPE generated JSON log file path': 'TPE generated JSON log file path',
        'Analysis report output directory': 'Analysis report output directory',
        'Custom configuration file path': 'Custom configuration file path',
    },
    'zh': {
        # Analyzer names
        'InCharacter': '角色内识别',
        'CharacterBreak': '角色脱离检测',
        'ConflictHandler': '冲突处理分析',
        'ResponseQuality': '响应质量评估',
        
        # Report labels
        'Test Metadata': '测试元数据',
        'Analysis Results Summary': '分析结果摘要',
        'Analyzer': '分析器',
        'Score': '分数',
        'Details': '详情',
        'Field': '字段',
        'Value': '值',
        
        # Error messages
        'Error': '错误',
        'File not found': '文件不存在',
        'JSON decode error': 'JSON格式错误',
        'Analysis complete, reports saved to': '分析完成，报告已保存到',
        
        # CLI descriptions
        'TPE QA Analyzer - Analyze TPE tool generated log files': 'TPE QA Analyzer - 分析TPE工具生成的日志文件',
        'TPE generated JSON log file path': 'TPE生成的JSON日志文件路径',
        'Analysis report output directory': '分析报告的输出目录',
        'Custom configuration file path': '自定义配置文件路径',
    }
}

class I18nManager:
    """
    Internationalization manager for handling multi-language support.
    """
    
    def __init__(self, language=DEFAULT_LANGUAGE):
        """
        Initialize the I18nManager.
        
        Args:
            language (str): Language code ('en' or 'zh')
        """
        if language not in LANGUAGES:
            raise ValueError(f"Unsupported language: {language}")
        self.language = language
    
    def set_language(self, language):
        """
        Set the current language.
        
        Args:
            language (str): Language code ('en' or 'zh')
        """
        if language not in LANGUAGES:
            raise ValueError(f"Unsupported language: {language}")
        self.language = language
    
    def t(self, key):
        """
        Translate a key to the current language.
        
        Args:
            key (str): Translation key
            
        Returns:
            str: Translated text
        """
        return TRANSLATIONS.get(self.language, TRANSLATIONS[DEFAULT_LANGUAGE]).get(key, key)
    
    def get_supported_languages(self):
        """
        Get list of supported languages.
        
        Returns:
            list: Supported language codes
        """
        return LANGUAGES

# Global i18n manager instance
i18n = I18nManager()