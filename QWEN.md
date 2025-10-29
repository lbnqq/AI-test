## Qwen Added Memories
- 原始测评报告位置: results/readonly-original/ 目录中，包含各种模型和角色的测评结果文件，文件命名格式为 asses_{model}_{test}_{role}_e{emotional_stress}_t{cognitive_trap}_{context_tokens}_{date}_{sequence}.json
- 处理脚本: run_batch_segmented_analysis.py 使用新实现的分段评分系统批量处理原始测评报告，核心评估模块是 segmented_scoring_evaluator.py，包含多轮争议解决机制和信度验证功能
- 多轮争议解决机制: 在 segmented_scoring_evaluator.py 中实现，包括争议识别、多轮添加额外评估器、多数决策原则等，最多进行3轮争议解决，确保评分一致性
- 批量可信评估分析系统已完成实施，包含分段评分、多模型评估、多轮争议解决、信度验证等功能，可处理results/readonly-original目录中的544个原始测评报告文件，使用run_batch_segmented_analysis.py脚本进行批量处理
