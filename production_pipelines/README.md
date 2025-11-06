# 生产流水线部署指南

## 概述

本项目已重新整理为两个生产级流水线版本，所有冗余过程文档和测试文件已移至存档目录。

## 生产版本目录结构

### 1. 🚀 Cloud Fallback Enterprise 版本
**目录**: `production_pipelines/cloud_fallback_enterprise/`

**特性**:
- ✅ 三层Cloud Fallback策略 (Ollama Cloud → OpenRouter → Local Models)
- ✅ 企业级高可用性和容错能力
- ✅ 自适应超时和熔断器机制
- ✅ 实时性能监控和优化建议
- ✅ 完整的异步批处理能力

**核心文件**:
- `cloud_fallback_batch_processor.py` - 企业级批处理器 (34KB)
- `cloud_fallback_manager.py` - Cloud Fallback核心管理器 (22KB)
- `fallback_performance_monitor.py` - 性能监控模块 (20KB)
- `adaptive_consensus_algorithm.py` - 自适应共识算法
- `adaptive_reliability_calculator.py` - 自适应可靠性计算器

**使用方法**:
```bash
cd production_pipelines/cloud_fallback_enterprise/
python cloud_fallback_batch_processor.py --input-dir results/ --cloud-priority
```

### 2. 🔧 Local Batch Production 版本
**目录**: `production_pipelines/local_batch_production/`

**特性**:
- ✅ 经过验证的本地模型批处理
- ✅ 稳定可靠的生产环境脚本
- ✅ 完整的LLM评估和共享分析模块
- ✅ 支持Ollama本地模型推理

**核心文件**:
- `batch_processor_original.py` - 原生产批处理器 (26KB)
- `shared_analysis/` - 完整的分析模块
- `llm_assessment/` - LLM评估框架
- `single_report_pipeline/` - 单报告流水线

**使用方法**:
```bash
cd production_pipelines/local_batch_production/
python batch_processor_original.py --input-dir results/ --enhanced
```

## 项目清理成果

### 存档文件
已将以下冗余文件移至存档目录:
- `archive/process_documentation/` - 所有过程文档和中间报告
- `archive/test_files/` - 测试文件和调试脚本
- `archive/deprecated_scripts/` - 过时和中间版本脚本

### 核心文件保留
项目根目录现在只保留116个核心文件，相比之前的200+文件大幅简化。

## 部署建议

### 生产环境选择
1. **高可用需求**: 使用 Cloud Fallback Enterprise 版本
2. **离线环境**: 使用 Local Batch Production 版本
3. **混合部署**: 两个版本都保留，根据需要切换

### 配置要求
- 确保`.env`文件包含所需的API密钥
- 检查`config/ollama_config.json`中的本地模型配置
- 验证`config/model_configs.json`中的Cloud Fallback配置

### 监控和维护
- Enterprise版本包含完整的性能监控
- 定期检查fallback链的健康状态
- 根据性能报告调整模型配置

## 版本历史

- **v1.0** - 初始本地批处理版本
- **v2.0** - Cloud Fallback企业级版本
- **v2.1** - 项目整理和双生产版本架构

---
*整理完成时间: 2025-11-06*